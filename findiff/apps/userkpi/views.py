from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from findiff.common.permissions.perms import PermsRequired
from findiff.models.user_kpi import UserKPI

from .filters import UserKPIFilter
from .serializers import UserKpiSerializer


class UserKPIView(ListAPIView):
    "获取用户的绩效列表"

    queryset = UserKPI.objects.all()
    serializer_class = UserKpiSerializer
    permission_classes = [PermsRequired('userprofile.list_user_kpi')]
    pagination_class = None
    filterset_class = UserKPIFilter
    search_fields = ('user__user__username', 'user__nickname')

    def get(self, request):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer()
        data = serializer.sum_kpi(queryset)
        return Response({'results': data}, status=status.HTTP_200_OK)
