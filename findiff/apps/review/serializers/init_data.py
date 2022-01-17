from pathlib import Path

from django.conf import settings
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from findiff.common.filehash import filehash
from findiff.models.audit import AuditOrder
from findiff.models.content import Article, Book


class InitAuditOrderSerializer(serializers.Serializer):
    """用于接口批量创建初始工单"""

    book_id = serializers.CharField(required=True, write_only=True)
    book_page = serializers.IntegerField(required=True, write_only=True)
    writing_mode = serializers.CharField(required=True, write_only=True)
    content_image = serializers.FileField(required=True, write_only=True)
    content_text = serializers.CharField(required=True, write_only=True, allow_blank=True)

    def validate_upload_file(self, value):
        if value.content_image not in ('image/png', 'image/jpeg'):
            raise serializers.ValidationError(
                '仅支持 png、jpg、jpeg 图片', 'upload_file')
        return value

    def create(self, validated_data):
        upload_file = validated_data.pop('content_image')
        file_rename = '%s%s' % (filehash(file=upload_file.file),
                                Path(upload_file.name).suffix)
        with open(Path(settings.MEDIA_ROOT) / file_rename, 'wb+') as fp:
            for chunk in upload_file.chunks():
                fp.write(chunk)

        validated_data['content_image'] = f'{settings.MEDIA_URL}{file_rename}'
        book = get_object_or_404(Book, pk=validated_data['book_id'])
        article = Article.objects.create(
            book=book,
            book_page=validated_data['book_page'],
            writing_mode=validated_data['writing_mode'],
            content_text=validated_data['content_text'],
            content_image=validated_data['content_image'],
        )
        order = AuditOrder.objects.create(article=article)
        order.serial_id = order.make_serial_id()
        order.save()
        return order


class InitBookSerializer(serializers.ModelSerializer):
    book_snum = serializers.CharField(required=True)
    book_name = serializers.CharField(required=True)
    book_pages = serializers.IntegerField(
        required=True,
        min_value=0,
        max_value=3000,
    )

    def create(self, validated_data):
        return Book.objects.create(**validated_data)

    class Meta:
        model = Book
        fields = (
            'id',
            'book_snum',
            'book_name',
            'book_pages',
        )
