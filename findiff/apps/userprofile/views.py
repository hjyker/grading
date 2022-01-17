from django.contrib.auth.models import Group
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from findiff.common.permissions.perm_config import PERMS_CONFIG
from findiff.common.permissions.perms import PermsRequired

from .models import UserProfile
from .serializers import (
    EmbedGroupSerializer,
    RoleSerializer,
    UpsertRoleSerializer,
    UserProfileSerializer,
    UserProfileWithRoleSerializer,
)


class UserProfileViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """用户列表"""

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [PermsRequired('userprofile.check_user_list')]
    search_fields = ('nickname', 'user__username', 'user__email')


class RoleViewSet(viewsets.ModelViewSet):
    """角色管理，直接使用 Django Group
        1. 角色的增删改查
        2. 角色分配
    """

    queryset = Group.objects.all()
    serializer_class = RoleSerializer
    search_fields = ('name',)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return UpsertRoleSerializer
        return self.serializer_class

    def get_permissions(self):
        actions_perms = {
            'list': ['userprofile.check_user_group'],
            'create': ['userprofile.add_user_group'],
            'assign_role': ['userprofile.assign_role'],
            'destroy': ['userprofile.delete_user_group'],
        }
        perms = actions_perms.get(self.action)
        if perms:
            self.permission_classes = [PermsRequired(*perms)]
        return super().get_permissions()

    @action(
        methods=['get'],
        detail=False,
        serializer_class=EmbedGroupSerializer)
    def options(self, request, *args, **kwargs):
        request.GET._mutable = True
        request.GET['page_size'] = 1000
        request.GET['page'] = 1
        request.GET._mutable = False
        return self.list(request, *args, **kwargs)

    @action(
        methods=['post'],
        detail=False,
        serializer_class=UserProfileWithRoleSerializer)
    def assign_role(self, request):
        res = self.get_serializer(data=request.data)
        res.is_valid(raise_exception=True)
        res.save()
        return Response(res.data)


class OwnPermsView(APIView):
    """自定义权限列表"""

    permission_classes = [PermsRequired(
        'userprofile.check_user_group', 'userprofile.add_user_group',
        'userprofile.edit_user_group', 'userprofile.delete_user_group')]

    def get(self, request, format=None):
        return Response(PERMS_CONFIG)
