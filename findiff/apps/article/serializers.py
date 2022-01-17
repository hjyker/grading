import datetime
from rest_framework import serializers
from findiff.models.content import Article
from findiff.models.model_constant import CONTENT_STATUS


class ArticleSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField(source='author.id', allow_null=True)
    author_name = serializers.CharField(source='author.name', allow_null=True)
    book_id = serializers.IntegerField(source='book.id')
    book_snum = serializers.CharField(source='book.book_snum')
    book_name = serializers.CharField(source='book.book_name')
    book_pages = serializers.CharField(source='book.book_pages')
    operator_cn = serializers.SerializerMethodField()
    status_cn = serializers.SerializerMethodField()

    def get_status_cn(self, obj):
        return dict(CONTENT_STATUS).get(obj.status)

    def get_operator_cn(self, obj):
        if obj.operator:
            return getattr(obj.operator, 'nickname', obj.operator.user.username)
        return None

    class Meta:
        model = Article
        fields = (
            'id',
            'author_id',
            'author_name',
            'book_id',
            'book_snum',
            'book_name',
            'book_pages',
            'article_snum',
            'article_title',
            'book_page',
            'article_page',
            'status',
            'status_cn',
            'writing_mode_origin',
            'writing_mode',
            'content_image',
            'content_text',
            'created_time',
            'updated_time',
            'operator_cn',
        )


class UpdateArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_time = datetime.datetime.now()
        instance.operator = self.context['request'].user.userprofile
        instance.save()
        return instance
