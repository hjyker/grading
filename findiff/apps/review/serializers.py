import csv
import datetime
import shutil

from pathlib import Path
from django.conf import settings
from rest_framework import serializers

from findiff.common.custom_validations import NonFieldError
from findiff.models import AuditOrder, Comments, Labels
from findiff.models.model_constant import AUDIT_STATUS


class AuditOrderMgmtSerializer(serializers.Serializer):
    """工单管理列表"""

    id = serializers.IntegerField(read_only=True)
    music_no = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)
    maker = serializers.IntegerField(
        source='maker.id', read_only=True, allow_null=True)
    created_time = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', read_only=True)
    updated_time = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', read_only=True)

    maker_cn = serializers.CharField(
        source='maker.user.username', allow_null=True)
    status_cn = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    label_count = serializers.SerializerMethodField()

    def get_status_cn(self, obj):
        return dict(AUDIT_STATUS).get(obj.status, obj.status)

    def get_comment_count(self, obj):
        return Comments.objects.filter(music_no=obj.music_no).count()

    def get_label_count(self, obj):
        return Labels.objects.filter(music_no=obj.music_no).count()


class ApplyAuditOrderSerializer(serializers.Serializer):
    """校对领单"""

    next_order_id = serializers.IntegerField(
        read_only=True,
    )

    def validate(self, attrs):

        unassign_orders = AuditOrder.objects.filter(status='unassign').count()
        if unassign_orders == 0:
            raise NonFieldError('暂无可领工单')

        return attrs

    def save(self):
        has_orders = AuditOrder.objects.filter(
            status='unaudit',
            maker=self.context['request'].user.userprofile,
        ).first()
        if has_orders:
            self.validated_data['next_order_id'] = has_orders.id
        else:
            next_order = AuditOrder.objects.filter(status='unassign').first()
            next_order.status = 'unaudit'
            next_order.maker = self.context['request'].user.userprofile
            next_order.save()
            self.validated_data['next_order_id'] = next_order.id


class AuditOrderSerializer(serializers.Serializer):
    """标注详情"""

    comments = serializers.ListField(read_only=True)
    labels = serializers.ListField(read_only=True)
    order_info = AuditOrderMgmtSerializer(read_only=True)

    def save(self):
        comments = Comments.objects.filter(music_no=self.instance.music_no)
        self.validated_data['comments'] = [
            {'id': cmt.id, 'comment': cmt.comment, 'likes': cmt.likes} for cmt in comments]
        labels = Labels.objects.filter(music_no=self.instance.music_no)
        self.validated_data['labels'] = [
            {'id': lb.id, 'label': lb.label, 'is_matched': lb.is_matched} for lb in labels]
        self.validated_data['order_info'] = AuditOrderMgmtSerializer(self.instance).data


class SubmitAuditOrderSerializer(serializers.Serializer):
    """提交标注"""

    order = serializers.PrimaryKeyRelatedField(
        queryset=AuditOrder.objects.all(),
    )
    labels = serializers.ListField(write_only=True)

    def validate(self, attrs):
        order = attrs['order']
        if order.status is not 'unaudit':
            raise NonFieldError('当前状态不能提单')
        return attrs

    def save(self):
        labels = []
        for label in self.validated_data['labels']:
            lb = Labels.objects.get(id=label['id'])
            lb.is_matched = label['is_matched']
            labels.append(lb)
        Labels.objects.bulk_update(labels, ['is_matched'])
        order = self.validated_data['order']
        order.status = 'success'
        order.save()


class MarkResultExportSerializer(serializers.Serializer):
    """导出标记数据"""

    # updated_time = serializers.DateTimeField(
    #     format='%Y-%m-%d %H:%M:%S', write_only=True)
    download_url = serializers.CharField(read_only=True)

    def save(self):
        titles = ['候选词', '是否为这首歌的标签']
        finished_orders = [
            od.music_no for od in AuditOrder.objects.filter(status='success')]
        dir_name = datetime.datetime.now().strftime('%Y%d%m%H%M%S')
        save_path = Path(f'{settings.MEDIA_ROOT}') / dir_name
        if not save_path.exists():
            save_path.mkdir()

        for music_no in finished_orders:
            file_name = save_path / f'{music_no}_results.csv'
            results = Labels.objects.filter(music_no=music_no)
            if results.count() > 0:
                with file_name.open('w', encoding='utf-8') as fp:
                    writer = csv.writer(fp)
                    writer.writerow(titles)
                    for result in results:
                        writer.writerow([result.label, result.is_matched])

        shutil.make_archive(save_path, 'zip', save_path)
        self.validated_data['download_url'] = f'{settings.MEDIA_URL}{dir_name}.zip'
