from django.contrib import admin
from .models import AuditOrder, RawData

admin.site.register(AuditOrder)
admin.site.register(RawData)
