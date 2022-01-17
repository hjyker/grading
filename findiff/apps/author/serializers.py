from rest_framework import serializers
from findiff.models.content import Author


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = "__all__"
