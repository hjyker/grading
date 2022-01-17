from rest_framework.routers import DefaultRouter
from .views import AuthorViewSet

router = DefaultRouter()
router.register('author', AuthorViewSet)
urlpatterns = [
    *router.urls,
]
