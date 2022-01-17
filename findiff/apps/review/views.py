from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from findiff.common.permissions.perms import PermsRequired

from .models import AuditOrder
from .serializers import (
    ApplyAuditOrderSerializer,
    AuditOrderSerializer,
    CreateAuditOrderSerializer,
    UpdateAuditOrderSerializer,
)


class ApplyAuditOrderView(ListAPIView):
    """校对领单"""

    queryset = AuditOrder.objects.filter()
    serializer_class = ApplyAuditOrderSerializer
    permission_classes = [PermsRequired('userprofile.apply_audit_order')]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='audit_status',
                in_=openapi.IN_QUERY,
                description='初审/复审状态',
                type=openapi.TYPE_STRING
            )
        ])
    def get(self, request):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        return Response({'next_order_id': serializer.data.get('next_order_id')})


class AuditOrderViewSet(ModelViewSet):
    """校对工单"""

    queryset = AuditOrder.objects.all()
    serializer_class = AuditOrderSerializer

    def get_permissions(self):
        actions_perms = {
            'list': ['userprofile.list_audit_order'],
            'create': ['userprofile.create_audit_order'],
            'retrieve': ['userprofile.scan_audit_order'],
            'update': ['userprofile.modify_audit_order'],
            'partial_update': ['userprofile.submit_audit_order'],
            'destroy': ['userprofile.delete_audit_order'],
        }
        perms = actions_perms.get(self.action)
        if perms:
            self.permission_classes = [PermsRequired(*perms)]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return UpdateAuditOrderSerializer
        return self.serializer_class

    @action(
        methods=['post'],
        detail=False,
        parser_classes=[MultiPartParser],
        serializer_class=CreateAuditOrderSerializer,
        permission_classes=[PermsRequired('userprofile.create_audit_order')])
    def init(self, request, *args, **kwargs):
        res = self.get_serializer(data=request.data)
        res.is_valid(raise_exception=True)
        res.save()
        return Response(status=201)
