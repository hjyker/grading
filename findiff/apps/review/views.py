from django.contrib.auth.models import UserManager
from django.db.models import Count, F, Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from findiff.apps.userprofile.models import UserProfile
from findiff.apps.userprofile.serializers import UserProfileLiteSerializer
from findiff.common.permissions.perms import PermsRequired
from findiff.models.audit import AuditOrder
from findiff.models.content import Book

from .filters import AuditAssignFilter
from .serializers.init_data import InitAuditOrderSerializer, InitBookSerializer
from .serializers.audit import (ApplyAuditOrderSerializer, AuditOrderSerializer,
                                ReturnAuditOrderSerializer,
                                SuspendAuditOrderSerializer,
                                UpdateAuditOrderSerializer)
from .serializers.qa import (QAOrderApplySerializer, QAOrderAssignSerializer,
                             QAOrderReturnedSerializer, QAOrderSampleSerializer,
                             QAOrderSerializer, QAOrderSubmitSerializer)


class ApplyAuditOrderView(CreateAPIView):
    """校对领单"""

    queryset = AuditOrder.objects.filter()
    serializer_class = ApplyAuditOrderSerializer
    permission_classes = [PermsRequired('userprofile.apply_audit_order')]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({'next_order_id': serializer.data.get('next_order_id')})


class AuditOrderViewSet(ModelViewSet):
    """工单校对"""

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
        methods=['put'],
        detail=True,
        serializer_class=SuspendAuditOrderSerializer,
        permission_classes=[
            PermsRequired('userprofile.submit_audit_order')],
    )
    def suspend(self, request, pk=None):
        """挂起校对工单"""

        audit = self.get_object()
        serializer = self.get_serializer(audit, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=False,
        serializer_class=ReturnAuditOrderSerializer,
        permission_classes=[
            PermsRequired('userprofile.returned_audit_order')],
    )
    def returned(self, request):
        """驳回校对工单"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.return_order(serializer.validated_data)
        return Response(result, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=False,
        parser_classes=[MultiPartParser],
        serializer_class=InitAuditOrderSerializer,
        permission_classes=[PermsRequired('userprofile.create_audit_order')],
    )
    def init_audit(self, request):
        """初始化校对工单"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=['post'],
        detail=False,
        serializer_class=InitBookSerializer,
        permission_classes=[PermsRequired('userprofile.create_audit_order')],
    )
    def init_book(self, request):
        """初始化书籍"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class QAOrderView(ListAPIView):
    """质检领单列表"""

    queryset = Book.objects.all()
    serializer_class = QAOrderSerializer
    permission_classes = [PermsRequired('userprofile.list_qa_order')]
    search_fields = ('book_name', 'book_snum')

    def get_queryset(self):
        """ 质检领单逻辑
        1. 普通质检员可以看到所有待分配工单(2100)，和自己待质检(2101)工单关联的书籍.
        2. 具备分配质检工单权限(assign_qa_order)，可以看到所有2100、2101工单关联的书籍.

        TODO 属于自己的所有类型工单，应该在个人校对中心去查看.
        """

        # 统计所有满足质检条件的书籍:待分配、待质检
        audit_results = AuditOrder.objects.values('article__book') \
            .annotate(qa_count=Count('id', filter=Q(order_status__in=['2100', '2101']))) \
            .annotate(total=Count('id')) \
            .order_by('article__book') \
            .filter(qa_count__gte=F('total'))
        books_id = [res['article__book'] for res in audit_results]

        if self.request.user.has_perm('userprofile.assign_qa_order'):
            return Book.objects.filter(id__in=books_id)

        return Book.objects.filter(
            Q(article__auditorder__qa_order__qa_user=self.request.user.userprofile) | Q(
                article__auditorder__order_status='2100'),
            id__in=books_id,
        ).distinct()


class QAOrderApplyView(CreateAPIView):
    """质检领单
    质检步骤:
        1. 质检领单，按一本书籍的维度，将整个书籍关联的工单，批量创建 qa_audit 并修改对应字段数据；
        2. 抽样质检，输入抽样比例，随机将抽样工单返回审核。
    """

    queryset = AuditOrder.objects.filter(order_status='2100')
    serializer_class = QAOrderApplySerializer
    permission_classes = [PermsRequired('userprofile.apply_qa_order')]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.apply_qa_order()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            headers=self.get_success_headers(serializer.validated_data),
        )


class QAOrderSampleView(CreateAPIView):
    """抽样质检
    质检步骤:
        1. 质检领单，按一本书籍的维度，将整个书籍关联的工单，批量创建 qa_audit 并修改对应字段数据；
        2. 抽样质检，输入抽样比例，随机将抽样工单返回审核。
    """

    queryset = AuditOrder.objects.filter(order_status='2100')
    serializer_class = QAOrderSampleSerializer
    permission_classes = [PermsRequired('userprofile.apply_qa_order')]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.apply_sample()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            headers=self.get_success_headers(serializer.validated_data),
        )


class QAOrderAssignView(CreateAPIView):
    """质检手动分单"""

    queryset = AuditOrder.objects.all()
    serializer_class = QAOrderAssignSerializer
    permission_classes = [PermsRequired('userprofile.assign_qa_order')]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.assign_order()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            headers=self.get_success_headers(serializer.validated_data),
        )


class QAOrderStaffView(ListAPIView):
    """质检员列表
    返回拥有质检权限的用户
    """

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileLiteSerializer
    permission_classes = [PermsRequired('userprofile.assign_qa_order')]
    pagination_class = None

    def get_queryset(self):
        users = UserManager().with_perm(perm='userprofile.apply_qa_order')
        return UserProfile.objects.filter(user__in=users)


class QAOrderDetailView(ListAPIView):
    """质检详情"""

    queryset = AuditOrder.objects.filter(order_status='2101')
    serializer_class = AuditOrderSerializer
    permission_classes = [PermsRequired('userprofile.list_qa_order')]
    filterset_class = AuditAssignFilter
    ordering = ['qa_audit__created_time']

    def get_queryset(self):
        current_user = getattr(self.request.user, 'userprofile', None)

        if not current_user:
            raise NotFound(detail='当前用户不存在或数据异常')

        return self.queryset.filter(qa_audit__qa_user=current_user)


class QAOrderSubmitView(CreateAPIView):
    """质检提交"""

    queryset = AuditOrder.objects.all()
    serializer_class = QAOrderSubmitSerializer
    permission_classes = [PermsRequired('userprofile.submit_qa_order')]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class QAOrderReturnedView(CreateAPIView):
    """质检退回"""

    queryset = AuditOrder.objects.all()
    serializer_class = QAOrderReturnedSerializer
    permission_classes = [PermsRequired('userprofile.returned_qa_order')]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
