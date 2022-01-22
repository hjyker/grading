import datetime

from rest_framework import status
from rest_framework.generics import (CreateAPIView, GenericAPIView, ListAPIView,
                                     RetrieveAPIView, get_object_or_404)
from rest_framework.response import Response

from findiff.common.permissions.perms import PermsRequired
from findiff.models.audit import AuditOrder
from findiff.models.content import Labels

from .filters import AuditOrderFilter
from .serializers import (ApplyAuditOrderSerializer, AuditOrderMgmtSerializer,
                          AuditOrderSerializer, MarkResultExportSerializer,
                          SubmitAuditOrderSerializer)


class ApplyAuditOrderView(CreateAPIView):
    """校对领单"""

    queryset = AuditOrder.objects.filter()
    serializer_class = ApplyAuditOrderSerializer
    permission_classes = [PermsRequired('findiff.apply_audit_order')]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuditOrderDetailView(RetrieveAPIView):
    """标注详情"""

    queryset = AuditOrder.objects.filter()
    serializer_class = AuditOrderSerializer
    permission_classes = [PermsRequired('findiff.scan_audit_order')]

    def retrieve(self, request, pk=None):
        serializer = self.get_serializer(
            get_object_or_404(self.get_queryset(), pk=pk),
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class AuditOrderSubmitView(CreateAPIView):
    """提交标注"""

    queryset = AuditOrder.objects.filter()
    serializer_class = SubmitAuditOrderSerializer
    permission_classes = [PermsRequired('findiff.submit_audit_order')]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuditOrderListView(ListAPIView):
    """工单列表"""

    queryset = AuditOrder.objects.all()
    serializer_class = AuditOrderMgmtSerializer
    filterset_class = AuditOrderFilter
    permission_classes = [PermsRequired('findiff.list_content_mgmt')]


class AuditOrderDataView(GenericAPIView):
    """审核统计"""

    queryset = AuditOrder.objects.all()
    permission_classes = [PermsRequired('findiff.scan_audit_order')]

    def get(self, request):
        queryset = self.get_queryset()
        total_audit = queryset.filter(
            maker=request.user.userprofile,
            status='success',
        )

        now = datetime.datetime.now()
        today_audit = total_audit.filter(
            updated_time__range=(now.strftime(
                '%Y-%m-%d 00:00:00'), now.strftime('%Y-%m-%d 23:59:59')),
        )
        return Response({'total': total_audit.count(), 'today': today_audit.count()})


class MarkResultExportView(CreateAPIView):
    """导出所有标记数据
    按每一个 music_no 输出一个result文件
    """

    queryset = Labels.objects.filter()
    serializer_class = MarkResultExportSerializer
    permission_classes = [PermsRequired('findiff.export_marked_result')]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
