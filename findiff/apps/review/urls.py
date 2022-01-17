from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ApplyAuditOrderView, AuditOrderViewSet

router = DefaultRouter()
router.register('audit', AuditOrderViewSet)

urlpatterns = [
    path('audit/apply/', ApplyAuditOrderView.as_view()),
    *router.urls,
]
