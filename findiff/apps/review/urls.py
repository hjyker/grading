from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (ApplyAuditOrderView, AuditOrderViewSet,
                    QAOrderApplyView, QAOrderDetailView, QAOrderSubmitView, QAOrderReturnedView,
                    QAOrderView, QAOrderStaffView, QAOrderAssignView, QAOrderSampleView)

router = DefaultRouter()
router.register('audit', AuditOrderViewSet)

urlpatterns = [
    path('audit/apply/', ApplyAuditOrderView.as_view()),
    path('audit/qa/', QAOrderView.as_view()),
    path('audit/qa/assign/', QAOrderAssignView.as_view()),
    path('audit/qa/detail/', QAOrderDetailView.as_view()),
    path('audit/qa/apply/', QAOrderApplyView.as_view()),
    path('audit/qa/apply/sample/', QAOrderSampleView.as_view()),
    path('audit/qa/submit/', QAOrderSubmitView.as_view()),
    path('audit/qa/returned/', QAOrderReturnedView.as_view()),
    path('audit/qa/staff/', QAOrderStaffView.as_view()),
    path('', include(router.urls)),
]
