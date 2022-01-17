from rest_framework.routers import DefaultRouter
from .views import FgUserProfileViewSet

router = DefaultRouter()
router.register('fgUsers', FgUserProfileViewSet)
urlpatterns = [
    *router.urls,
]
