import django_filters

from findiff.common.filters import DateTimeRangeFilter
from findiff.models.user_kpi import UserKPI


class UserKPIFilter(django_filters.rest_framework.FilterSet):
    created_time__range = DateTimeRangeFilter(
        field_name='created_time',
        lookup_expr='range',
    )

    class Meta:
        model = UserKPI
        fields = []
