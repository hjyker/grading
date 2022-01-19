from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (OwnPermsView, RoleViewSet,
                    UserProfileViewSet, UserResetPasswdView)

router = DefaultRouter()
router.register('users', UserProfileViewSet)
router.register('roles', RoleViewSet)


urlpatterns = [
    re_path(r'^perms/config/$', OwnPermsView.as_view()),
    path('set_passwd/', UserResetPasswdView.as_view()),
    path('', include(router.urls)),
]
