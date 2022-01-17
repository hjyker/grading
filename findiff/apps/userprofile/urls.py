from django.urls import re_path
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, RoleViewSet, OwnPermsView

router = DefaultRouter()
router.register('users', UserProfileViewSet)
router.register('roles', RoleViewSet)

urlpatterns = [
    re_path(r'^perms/config/$', OwnPermsView.as_view()),
    *router.urls,
]
