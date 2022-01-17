import datetime
from pathlib import Path
from django.conf import settings
from django.db.models import Q
from django.utils.encoding import force_text
from rest_framework import serializers, status
from rest_framework.exceptions import APIException

from findiff.common.filehash import filehash
from .models import AuditOrder, RawData, AUDIT_STATUS_CHOICES, WRITING_MODE


class CustomValidation(APIException):

    def __init__(self, detail, field, status_code):
        self.status_code = status_code or status.HTTP_400_BAD_REQUEST
        self.detail = {field: force_text(detail)} if detail else {
            'detail': force_text('请求有误')}


class RawDataSerializer(serializers.ModelSerializer):
    """原始书籍数据"""

    class Meta:
        model = RawData
        fields = '__all__'


class ApplyAuditOrderSerializer(serializers.Serializer):
    """校对领单"""

    audit_status = serializers.MultipleChoiceField(
        choices=AUDIT_STATUS_CHOICES,
    )
    next_order_id = serializers.CharField(read_only=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        current_user = self.context['request'].user.userprofile
        self_audit_status = data.get('audit_status')

        # 0. 如果用户传递audit_status in [unaudit, suspend]，则优先下发
        if self_audit_status:
            self_audit_status = list(self_audit_status)
            self_status_orders = AuditOrder.objects.filter(
                Q(first_order_status__in=self_audit_status)
                | Q(second_order_status__in=self_audit_status),
                Q(first_audit_user=current_user) | Q(
                    second_audit_user=current_user),
            ).order_by('created_time')

            if self_status_orders.count() > 0:
                data['next_order_id'] = self_status_orders.first().id
                return data

        # 1. 当前用户unaudit suspend优先
        self_suspend_orders = AuditOrder.objects.filter(
            Q(first_order_status__in=('suspend', 'unaudit'))
            | Q(second_order_status__in=('suspend', 'unaudit')),
            Q(first_audit_user=current_user)
            | Q(second_audit_user=current_user),
        ).order_by('created_time')

        if self_suspend_orders.count() > 0:
            data['next_order_id'] = self_suspend_orders.first().id
            return data

        # 2. 复审unaudit订单优先
        self_sec_orders = AuditOrder.objects.filter(
            ~Q(first_audit_user=current_user),
            first_order_status='success',
            second_order_status='unassign'
        ).order_by('created_time')

        if self_sec_orders.count() > 0:
            order = self_sec_orders.first()
            order.second_audit_user = current_user
            order.second_audit_time = datetime.datetime.now()
            order.second_order_status = 'unaudit'
            order.save()
            data['next_order_id'] = order.id
            return data

        # 3. 最低优先级，分配初审待分配订单
        self_default_orders = AuditOrder.objects.filter(
            first_order_status='unassign',
        ).order_by('created_time')

        if self_default_orders.count() > 0:
            order = self_default_orders.first()
            order.first_audit_user = current_user
            order.first_audit_time = datetime.datetime.now()
            order.first_order_status = 'unaudit'
            order.save()
            data['next_order_id'] = order.id
            return data

        raise CustomValidation('暂无可领订单', 'non_field_error',
                               status.HTTP_400_BAD_REQUEST)


class AuditOrderSerializer(serializers.ModelSerializer):
    """工单详情"""

    audit_status = serializers.SerializerMethodField()
    audit_user = serializers.SerializerMethodField()
    audit_step = serializers.SerializerMethodField()
    audit_result = serializers.SerializerMethodField()
    raw_data = RawDataSerializer(read_only=True)

    def get_audit_status(self, obj):
        step = self.get_audit_step(obj)
        status = obj.first_order_status if step == 'first_audit' else obj.second_order_status
        return dict(AUDIT_STATUS_CHOICES).get(status, status)

    def get_audit_user(self, obj):
        user = obj.second_audit_user or obj.first_audit_user
        return user.nickname if user else None

    def get_audit_step(self, obj):
        return 'second_audit' if obj.second_order_status != 'unassign' else 'first_audit'

    def get_audit_result(self, obj):
        step = self.get_audit_step(obj)
        if step == 'first_audit' and not obj.first_audit_result:
            return obj.raw_data.content_text
        if step == 'second_audit' and not obj.second_audit_result:
            return obj.first_audit_result
        return obj.first_audit_result if step == 'first_audit' else obj.second_audit_result

    class Meta:
        model = AuditOrder
        fields = (
            'id',
            'order_id',
            'audit_status',
            'audit_user',
            'audit_result',
            'audit_step',
            'raw_data',
        )


class UpdateAuditOrderSerializer(serializers.Serializer):
    """提交工单"""

    audit_step = serializers.ChoiceField(
        choices=(('first_audit', '初审'), ('second_audit', '复审')),
        required=True,
        write_only=True,
    )
    audit_result = serializers.CharField(required=True, write_only=True)
    need_suspend = serializers.BooleanField(required=False, write_only=True)

    def validate(self, attrs):
        return super().validate(attrs)

    def update(self, instance, validated_data):
        step = validated_data['audit_step']
        result = validated_data['audit_result']
        suspend = validated_data.pop('need_suspend', False)

        if step == 'first_audit':
            instance.first_audit_result = result
            instance.first_order_status = 'suspend' if suspend else 'success'
        elif step == 'second_audit':
            instance.second_audit_result = result
            instance.second_order_status = 'suspend' if suspend else 'success'

        instance.save()
        return instance


class CreateAuditOrderSerializer(serializers.Serializer):
    """用于接口批量创建初始工单"""

    book_name = serializers.CharField(write_only=True)
    writing_mode = serializers.ChoiceField(choices=WRITING_MODE, write_only=True)
    content_image = serializers.FileField(required=True, write_only=True)
    content_text = serializers.CharField()
    content_text_name = serializers.CharField()
    content_image_name = serializers.CharField()

    def validate_upload_file(self, value):
        if value.content_image not in ('image/png', 'image/jpeg'):
            raise serializers.ValidationError(
                '仅支持 png、jpg、jpeg 图片', 'upload_file')
        return value

    def create(self, validated_data):
        upload_file = validated_data.pop('content_image')
        file_rename = '%s%s' % (filehash(file=upload_file.file),
                                Path(upload_file.name).suffix)
        with open(Path(settings.MEDIA_ROOT) / file_rename, 'wb+') as fp:
            for chunk in upload_file.chunks():
                fp.write(chunk)

        validated_data['content_image'] = f'{settings.MEDIA_URL}{file_rename}'
        raw_data = RawData.objects.create(**validated_data)
        raw_data.save()
        order = AuditOrder.objects.create(raw_data=raw_data)
        order.order_id = order.make_order_id()
        order.save()
        return order
