from rest_framework.viewsets import ModelViewSet
from findiff.models.content import Author
from .serializers import AuthorSerializer


class AuthorViewSet(ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    search_fields = (
        'name', 'dynasty', 'writing_school'
    )
