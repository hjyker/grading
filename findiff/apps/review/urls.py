from django.urls import path, re_path

from .views import (ApplyAuditOrderView, AuditOrderDetailView,
                    AuditOrderResultExportView, AuditOrderSubmitView,
                    MarkResultExportView)

urlpatterns = [
    path('audit/apply/', ApplyAuditOrderView.as_view()),
    re_path(r'^audit/dtl/(?P<pk>\d+)/$', AuditOrderDetailView.as_view()),
    path('audit/submit/', AuditOrderSubmitView.as_view()),
    path('audit/', AuditOrderResultExportView.as_view()),
    path('audit/export/', MarkResultExportView.as_view()),
]
