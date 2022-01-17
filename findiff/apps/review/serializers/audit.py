import datetime

from django.db.models import Q
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from findiff.apps.review.constants import MAX_RETURNED_COUNT
from findiff.common.custom_validations import NonFieldError
from findiff.models.audit import AuditOrder, AuditProfile, QAOrder
from findiff.models.content import Article, Author, Book
from findiff.models.model_constant import (AUDIT_ORDER_STATUS, AUDIT_STATUS,
                                           CONTENT_STATUS, WRITING_MODE)
from findiff.models.user_kpi import UserKPI


def get_audit_instance(obj):
    audit_ins = None
    if obj.order_status in ('1100', '1101', '1102', '1104', '1105', '1203'):
        audit_ins = obj.first_audit
    elif obj.order_status in ('1200', '1201', '1202', '1204', '1205', '2103'):
        audit_ins = obj.second_audit
    return audit_ins


class ArticleSerializer(serializers.ModelSerializer):
    """文章源数据"""

    status_cn = serializers.SerializerMethodField()
    writing_mode_cn = serializers.SerializerMethodField()

    def get_status_cn(self, obj):
        return dict(CONTENT_STATUS).get(obj.status)

    def get_writing_mode_cn(self, obj):
        return dict(WRITING_MODE).get(obj.writing_mode)

    class Meta:
        model = Article
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    """书籍源数据"""

    class Meta:
        model = Book
        fields = '__all__'


class AuditProfileSerializer(serializers.ModelSerializer):
    """校对工单详情"""

    status_cn = serializers.SerializerMethodField()
    audit_user_cn = serializers.SerializerMethodField()
    operator_cn = serializers.SerializerMethodField()

    def get_status_cn(self, obj):
        return dict(AUDIT_STATUS).get(obj.status)

    def get_audit_user_cn(self, obj):
        return obj.audit_user.user.username if obj.audit_user else None

    def get_operator_cn(self, obj):
        return obj.operator.user.username if obj.operator else None

    class Meta:
        model = AuditProfile
        fields = (
            'id',
            'audit_user_cn',
            'status',
            'status_cn',
            'content_text',
            'article_title',
            'article_page',
            'article_author',
            'writing_mode',
            'remark',
            'created_time',
            'updated_time',
            'operator_cn',
        )


class QAProfileSerializer(serializers.ModelSerializer):
    """质检工单详情"""

    status_cn = serializers.SerializerMethodField()
    qa_user_cn = serializers.SerializerMethodField()
    operator_cn = serializers.SerializerMethodField()

    def get_status_cn(self, obj):
        return dict(AUDIT_STATUS).get(obj.status)

    def get_qa_user_cn(self, obj):
        return obj.qa_user.user.username if obj.qa_user else None

    def get_operator_cn(self, obj):
        return obj.operator.user.username if obj.operator else None

    class Meta:
        model = QAOrder
        fields = (
            'id',
            'bulk_id',
            'qa_user_cn',
            'status',
            'status_cn',
            'remark',
            'created_time',
            'updated_time',
            'operator',
            'operator_cn',
        )


class ApplyAuditOrderSerializer(serializers.Serializer):
    """校对领单"""

    audit_status = serializers.ChoiceField(
        choices=AUDIT_STATUS,
        required=False,
    )
    next_order_id = serializers.IntegerField(
        read_only=True,
    )

    def validate(self, attrs):
        data = super().validate(attrs)
        current_user = self.context['request'].user.userprofile
        audit_status = data.get('audit_status', 'no_data')
        status_mappings = {
            'unaudit': ('1101', '1201'),
            'suspend': ('1105', '1205'),
            'returned': ('1103', '1203'),
        }
        self_audit_status = status_mappings.get(audit_status, None)

        # 1. 如果用户传递audit_status in [unaudit, suspend, returned]，则优先下发
        if self_audit_status:
            self_status_order = AuditOrder.objects.filter(
                Q(order_status=self_audit_status[0],
                    first_audit__audit_user=current_user) |
                Q(order_status=self_audit_status[1],
                    second_audit__audit_user=current_user)
            ).order_by('created_time').first()

            if self_status_order:
                data['next_order_id'] = self_status_order.id
                return data

        # 2. 当前用户被驳回工单
        query1 = Q(first_audit__audit_user=current_user, order_status='1203')
        query2 = Q(second_audit__audit_user=current_user, order_status='2103')
        returned_order = AuditOrder.objects.filter(
            query1 | query2).order_by('created_time').first()

        if returned_order:
            data['next_order_id'] = returned_order.id
            return data

        # 2. 所有待审工单
        self_unaudit_order = AuditOrder.objects.filter(
            Q(first_audit__audit_user=current_user, order_status='1101') |
            Q(second_audit__audit_user=current_user, order_status='1201'),
        ).order_by('created_time').first()

        if self_unaudit_order:
            data['next_order_id'] = self_unaudit_order.id
            return data

        # 3. 所有待分配工单
        second_unassign_order = AuditOrder.objects.filter(
            ~Q(first_audit__audit_user=current_user),
            order_status='1200'
        ).first()
        if second_unassign_order:
            second_audit = second_unassign_order.second_audit
            if not second_audit:
                second_audit = AuditProfile(
                    audit_user=current_user,
                    status='unaudit',
                )
            second_audit.audit_user = current_user
            second_audit.save()
            second_unassign_order.second_audit = second_audit
            second_unassign_order.order_status = '1201'
            second_unassign_order.save()
            data['next_order_id'] = second_unassign_order.id
            return data

        first_unassign_order = AuditOrder.objects.filter(
            order_status='1100').first()
        if first_unassign_order:
            first_audit = first_unassign_order.first_audit
            if not first_audit:
                first_audit = AuditProfile(
                    audit_user=current_user,
                    status='unaudit',
                )
            first_audit.audit_user = current_user
            first_audit.save()
            first_unassign_order.first_audit = first_audit
            first_unassign_order.order_status = '1101'
            first_unassign_order.save()
            data['next_order_id'] = first_unassign_order.id
            return data

        raise NonFieldError('暂无可领工单')


class AuditOrderSerializer(serializers.ModelSerializer):
    """审核详情"""

    audit = serializers.SerializerMethodField()
    qa_audit = serializers.SerializerMethodField()
    raw_data = serializers.SerializerMethodField()
    raw_data_extra = serializers.SerializerMethodField()
    order_status_cn = serializers.SerializerMethodField()

    def get_audit(self, obj):
        audit_ins = get_audit_instance(obj)
        if audit_ins:
            audit_ins.content_text = obj.first_audit.content_text
            audit_ins.writing_mode = obj.first_audit.writing_mode

            if obj.order_status == '1201':
                audit_ins.article_title = obj.first_audit.article_title
                audit_ins.article_page = obj.first_audit.article_page
            return AuditProfileSerializer(audit_ins).data
        return None

    def get_qa_audit(self, obj):
        if obj.qa_audit:
            qa_data = QAProfileSerializer(obj.qa_audit).data
            qa_data['content_text'] = obj.second_audit.content_text
            qa_data['article_title'] = obj.second_audit.article_title
            qa_data['article_page'] = obj.second_audit.article_page
            qa_data['writing_mode'] = obj.second_audit.writing_mode
            qa_data['writing_mode_cn'] = dict(
                WRITING_MODE).get(obj.second_audit.writing_mode)
            return qa_data
        return None

    def get_raw_data(self, obj):
        return ArticleSerializer(obj.article).data

    def get_raw_data_extra(self, obj):
        return BookSerializer(
            obj.article.book).data if obj.article.book else None

    def get_order_status_cn(self, obj):
        return dict(AUDIT_ORDER_STATUS).get(obj.order_status)

    class Meta:
        model = AuditOrder
        fields = (
            'id',
            'serial_id',
            'order_status',
            'order_status_cn',
            'raw_data',
            'raw_data_extra',
            'audit',
            'qa_audit',
            'returned_count',
            'returned_remark',
            'created_time',
            'updated_time',
            'operator',
        )


class UpdateAuditOrderSerializer(serializers.Serializer):
    """提交工单"""

    content_text = serializers.CharField(required=True, write_only=True)
    article_title = serializers.CharField(write_only=True)
    article_page = serializers.IntegerField(write_only=True)
    writing_mode = serializers.ChoiceField(
        write_only=True, choices=WRITING_MODE)
    article_author = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )

    def validate(self, attrs):
        current_audit = get_audit_instance(self.instance)
        if not current_audit.audit_user.user == self.context['request'].user:
            raise NonFieldError('无权限操作此单')
        return attrs

    def update(self, instance, validated_data):
        result_content_text = validated_data['content_text']
        result_article_title = validated_data.get('article_title', '')
        result_article_page = validated_data.get('article_page', '')
        order_status = instance.order_status
        updated_time = datetime.datetime.now()
        operator = self.context['request'].user.userprofile

        if order_status in ('1101', '1104', '1105', '1203'):
            instance.first_audit.content_text = result_content_text
            instance.first_audit.article_title = result_article_title
            instance.first_audit.article_page = result_article_page
            instance.first_audit.writing_mode = validated_data['writing_mode']
            instance.first_audit.article_author = validated_data['article_author']
            instance.first_audit.status = 'success'
            instance.first_audit.updated_time = updated_time
            instance.first_audit.operator = operator
            instance.first_audit.save()
            # NOTE 如果本单是驳回状态，提交后变为下一阶段的待审核状态
            # NOTE 同时修改下一阶段已经提交过的数据
            instance.order_status = '1200'
            if order_status == '1203':
                instance.order_status = '1201'
                instance.second_audit.content_text = result_content_text
                instance.second_audit.article_title = result_article_title
                instance.second_audit.article_page = result_article_page
                instance.second_audit.writing_mode = validated_data['writing_mode']
                instance.second_audit.article_author = validated_data['article_author']
                instance.second_audit.status = 'unaudit'
                instance.second_audit.updated_time = updated_time
                instance.second_audit.operator = operator
                instance.second_audit.save()

            instance.updated_time = updated_time
            instance.operator = operator
            instance.save()
            return instance

        if instance.order_status in ('1201', '1204', '1205', '2103'):
            instance.second_audit.content_text = result_content_text
            instance.second_audit.article_title = result_article_title
            instance.second_audit.article_page = result_article_page
            instance.second_audit.writing_mode = validated_data['writing_mode']
            instance.second_audit.article_author = validated_data['article_author']
            instance.second_audit.status = 'success'
            instance.second_audit.updated_time = updated_time
            instance.second_audit.operator = operator
            instance.second_audit.save()

            # NOTE 二审结束立即进入质检待分配，2100是进入质检的标志
            instance.order_status = '2101' if order_status == '2103' else '2100'

            instance.updated_time = updated_time
            instance.operator = operator
            instance.save()
            return instance

        raise NonFieldError('工单状态错误')


class SuspendAuditOrderSerializer(serializers.Serializer):
    """挂起工单"""

    content_text = serializers.CharField(required=False, allow_blank=True)
    article_title = serializers.CharField(required=False, allow_blank=True)
    article_page = serializers.IntegerField(required=False, default=0)
    writing_mode = serializers.ChoiceField(
        required=False, choices=WRITING_MODE, allow_blank=True)
    article_author = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.filter(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    suspend_remark = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        current_audit = get_audit_instance(self.instance)
        if current_audit.audit_user != self.context['request'].user.userprofile:
            raise NonFieldError('无权限操作此单')
        if self.instance.order_status not in ['1101', '1103', '1105', '1201',
                                              '1203', '1205']:
            raise NonFieldError('当前工单状态不能挂起')
        return attrs

    def update(self, instance, validated_data):
        current_audit = get_audit_instance(instance)
        current_audit.content_text = validated_data['content_text']
        current_audit.article_title = validated_data.get('article_title', '')
        current_audit.article_page = validated_data.get('article_page', '')
        current_audit.article_author = validated_data['article_author']
        current_audit.writing_mode = validated_data['writing_mode']
        current_audit.status = 'suspend'
        current_audit.save()

        if instance.order_status in ('1101', '1104', '1105', '1203'):
            instance.order_status = '1105'
        elif instance.order_status in ('1201', '1204', '1205', '2103'):
            instance.order_status = '1205'

        instance.updated_time = datetime.datetime.now()
        instance.operator = self.context['request'].user.userprofile
        instance.save()
        return instance


class ReturnAuditOrderSerializer(serializers.Serializer):
    """工单驳回处理
    工单驳回: 当前流程失败，并驳回上一流程；
    驳回工单重提: 本流程成功，下一流程待校对（谁驳回谁重审）；

    NOTE 此处操作只能二审驳回到一审
    """

    order_id = serializers.IntegerField(required=True)
    remark = serializers.CharField()

    def return_order(self, validated_data):
        order = get_object_or_404(
            AuditOrder,
            pk=validated_data['order_id'],
        )

        if order.order_status != '1201':
            raise NonFieldError('当前工单状态，不能驳回')

        audit = order.first_audit
        audit.status = 'returned'

        order.order_status = '1203'
        order.returned_remark = validated_data['remark']
        order.returned_count += 1
        if order.returned_count > MAX_RETURNED_COUNT:
            # NOTE 将二审人员驳回两次的数据插入绩效表
            UserKPI.objects.create(
                user=audit.audit_user,
                type='order_returned_shuffle',
                count=1,
                trigger_step='first_audit',
            )
            audit.audit_user = None
            audit.status = 'unassign'

            order.returned_count = 0
            order.returned_remark = ''
            order.order_status = '1100'  # 重新放回一审领单池

        audit.updated_time = datetime.datetime.now()
        audit.operator = self.context['request'].user.userprofile
        audit.save()

        order.updated_time = datetime.datetime.now()
        order.operator = self.context['request'].user.userprofile
        order.save()
