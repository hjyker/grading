from django.contrib import admin
from findiff.models.audit import AuditOrder, QAOrder, AuditProfile

admin.site.register(AuditOrder)
admin.site.register(AuditProfile)
admin.site.register(QAOrder)
