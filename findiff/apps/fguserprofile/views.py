# Create your views here.
from rest_framework import mixins, viewsets
from .models import FgUserProfile
from .serializers import FgUserProfileSerializer


class FgUserProfileViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """前台用户列表"""
    queryset = FgUserProfile.objects.all()
    serializer_class = FgUserProfileSerializer
    # 支持昵称,用户名,邮箱查询
    search_fields = ('nickname','user__username','user__email')
