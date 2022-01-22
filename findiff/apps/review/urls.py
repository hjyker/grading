from django.urls import path, re_path

from .views import (ApplyAuditOrderView, AuditOrderDetailView,
                    AuditOrderListView, AuditOrderSubmitView,
                    MarkResultExportView, AuditOrderDataView)

urlpatterns = [
    path('audit/', AuditOrderListView.as_view()),
    path('audit/apply/', ApplyAuditOrderView.as_view()),
    re_path(r'^audit/dtl/(?P<pk>\d+)/$', AuditOrderDetailView.as_view()),
    path('audit/submit/', AuditOrderSubmitView.as_view()),
    path('audit/export/', MarkResultExportView.as_view()),
    path('audit/dataview/', AuditOrderDataView.as_view())
]
