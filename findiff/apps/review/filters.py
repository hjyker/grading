from django_filters.rest_framework import FilterSet
from .models import AuditOrder


class AuditAssignFilter(FilterSet):
    class Meta:
        model = AuditOrder
        fields = {
            '': ['in'],
            'machine_audit_time': ['range'],
        }
