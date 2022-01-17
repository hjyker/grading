from rest_framework.viewsets import ModelViewSet

from findiff.common.permissions.perms import PermsRequired
from findiff.models.content import Article

from .filters import ArticleFilter
from .serializers import ArticleSerializer, UpdateArticleSerializer


class ArticleViewSet(ModelViewSet):
    """内容管理"""

    queryset = Article.objects.all().order_by('created_time')
    serializer_class = ArticleSerializer
    permission_classes = [PermsRequired('userprofile.list_content_mgmt')]
    filterset_class = ArticleFilter
    search_fields = (
        'author__name', 'article_title', 'book__book_name', 'content_text',
    )

    def get_permissions(self):
        actions_perms = {
            'list': ['userprofile.list_content_mgmt'],
            'create': ['userprofile.create_content_article'],
            'retrieve': ['userprofile.detail_content_article'],
            'update': ['userprofile.modify_content_article'],
            'partial_update': ['userprofile.modify_content_article'],
            'destroy': ['userprofile.delete_content_article'],
        }
        perms = actions_perms.get(self.action)
        if perms:
            self.permission_classes = [PermsRequired(*perms)]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return UpdateArticleSerializer
        return self.serializer_class
