import django_filters
from findiff.models import AuditOrder
from findiff.common.filters import DateTimeRangeFilter, ChartInFilter


class AuditOrderFilter(django_filters.rest_framework.FilterSet):
    created_time__range = DateTimeRangeFilter(
        field_name='created_time',
        lookup_expr='range',
    )
    updated_time__range = DateTimeRangeFilter(
        field_name='updated_time',
        lookup_expr='range',
    )
    status__in = ChartInFilter(
        field_name='status',
        lookup_expr='in',
    )

    class Meta:
        model = AuditOrder
        fields = ['operator']
