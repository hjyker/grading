from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet

router = DefaultRouter()
router.register('article', ArticleViewSet)
urlpatterns = [
    *router.urls,
]
