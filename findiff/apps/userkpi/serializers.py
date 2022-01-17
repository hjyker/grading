from functools import reduce
from django.db.models import Sum
from rest_framework import serializers
from findiff.apps.userprofile.models import UserProfile


class UserKpiSerializer(serializers.Serializer):
    """获取用户的绩效列表"""

    def _sum_type(self, result, data):
        userpro_id = data['user']
        if userpro_id not in result:
            result[userpro_id] = {}
            userpro = UserProfile.objects.filter(id=userpro_id).first()
            result[userpro_id]['username'] = userpro.nickname if userpro.nickname else userpro.user.username

        type = data['type']
        result[userpro_id][type] = data['type_total']
        return result

    def sum_kpi(self, queryset):
        dataset = queryset.values('user', 'type').annotate(
            type_total=Sum('count')).order_by('user')
        results = reduce(self._sum_type, dataset, {})
        return results.values()
