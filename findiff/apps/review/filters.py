import django_filters
from findiff.models.audit import AuditOrder


class AuditAssignFilter(django_filters.rest_framework.FilterSet):
    bulk_id = django_filters.CharFilter(
        field_name='qa_audit__bulk_id',
        lookup_expr='exact',
        required=True,
    )

    class Meta:
        model = AuditOrder
        fields = []
