from django.contrib import admin
from findiff.models import AuditOrder, Comments, Labels

admin.site.register(AuditOrder)
admin.site.register(Comments)
admin.site.register(Labels)
