from django.core.validators import MinValueValidator
from django.db import models

from .model_constant import (AUDIT_STATUS, CONTENT_STATUS,
                             OPEN_STATUS, READING_MODE, WRITING_MODE)


class Author(models.Model):
    '''作者表，存储书籍或者文章作者'''

    name = models.CharField(
        '作者姓名',
        max_length=50,
    )
    detail = models.TextField(
        '作者介绍',
        max_length=3000,
        blank=True,
        default='',
    )
    dynasty = models.CharField(
        '作者朝代',
        max_length=50,
        blank=True,
        default='',
    )
    writing_school = models.CharField(
        '作者流派',
        max_length=50,
        blank=True,
        default='',
    )
    created_time = models.DateTimeField(
        '创建时间',
        help_text='数据入库时间',
        db_index=True,
        auto_now=True,
    )
    updated_time = models.DateTimeField(
        '更新时间',
        help_text='数据更新时间',
        auto_now=True,
    )
    operator = models.ForeignKey(
        'userprofile.UserProfile',
        on_delete=models.PROTECT,
        help_text='数据操作人',
        verbose_name='操作人',
        null=True,
        blank=True,
        default=None,
    )

    def __str__(self):
        return f'{self.id}-{self.name}-{self.dynasty}'

    class Meta:
        verbose_name = '作者'
        verbose_name_plural = verbose_name


class Book(models.Model):
    '''书籍'''

    authors = models.ManyToManyField(Author)
    book_snum = models.CharField(
        '书籍编号',
        max_length=200,
        null=True,
        blank=True,
        default=None,
    )
    book_name = models.CharField(
        '书籍名称(PDF)',
        max_length=200,
        db_index=True,
    )
    detail = models.TextField(
        '书籍介绍(PDF)',
        max_length=3000,
        blank=True,
        default='',
    )
    book_pages = models.IntegerField(
        '书籍页数(PDF)',
        blank=True,
        default=0,
    )
    # DEPRECATED 业务暂不需要该字段
    writing_mode = models.CharField(
        '书籍排版',
        help_text='书籍印刷的排版方向',
        max_length=10,
        choices=WRITING_MODE,
        blank=True,
        default='',
    )
    # DEPRECATED 业务暂不需要该字段
    reading_mode = models.CharField(
        '阅读方向',
        max_length=10,
        choices=READING_MODE,
        blank=True,
        default='',
    )
    # DEPRECATED 业务暂不需要该字段
    book_genre = models.CharField(
        '书籍体裁',
        max_length=50,
        blank=True,
        default='',
    )
    # DEPRECATED 业务暂不需要该字段
    book_dynasty = models.CharField(
        '书籍朝代',
        max_length=50,
        blank=True,
        default='',
        help_text='书籍编纂朝代',
    )
    book_open_status = models.CharField(
        '书籍状态',
        default='close',
        max_length=20,
        choices=OPEN_STATUS,
        help_text='书籍是否开放给查询',
    )
    created_time = models.DateTimeField(
        '创建时间',
        help_text='数据入库时间',
        db_index=True,
        auto_now=True,
    )
    updated_time = models.DateTimeField(
        '更新时间',
        help_text='数据更新时间',
        auto_now=True,
    )
    operator = models.ForeignKey(
        'userprofile.UserProfile',
        on_delete=models.PROTECT,
        help_text='数据操作人',
        verbose_name='操作人',
        null=True,
        blank=True,
        default=None,
    )

    def __str__(self):
        return f'{self.id}-{self.book_name}'

    class Meta:
        verbose_name = '书籍'
        verbose_name_plural = verbose_name


class Article(models.Model):
    '''文章表'''

    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        help_text='书籍',
        null=True,
        blank=True,
        default=None,
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,
        help_text='作者',
        null=True,
        blank=True,
        default=None,
    )
    article_snum = models.CharField(
        '文章编号',
        max_length=200,
        blank=True,
        default='',
    )
    article_title = models.CharField(
        '文章标题',
        max_length=200,
        blank=True,
        default='',
    )
    book_page = models.IntegerField(
        '书籍页码(PDF)',
        blank=True,
        null=True,
        default=None,
        validators=[MinValueValidator(0)],
        help_text='文章在书籍中的页码'
    )
    article_page = models.IntegerField(
        '文章页码(非PDF)',
        blank=True,
        null=True,
        default=None,
        validators=[MinValueValidator(0)],
        help_text='文章的相对页码',
    )
    status = models.CharField(
        '文章状态',
        max_length=30,
        choices=CONTENT_STATUS,
        default='unaudit',
    )
    # DEPRECATED 合并为 status
    article_review_status = models.CharField(
        '文章校对状态',
        max_length=20,
        choices=AUDIT_STATUS,
        default='unassign',
    )
    # DEPRECATED 业务暂不需要该字段
    article_open_status = models.CharField(
        '文章状态',
        max_length=20,
        choices=OPEN_STATUS,
        default='close',
    )
    # DEPRECATED 业务暂不需要该字段
    article_genre = models.CharField(
        '文章体裁',
        max_length=50,
        blank=True,
        default='',
    )
    # DEPRECATED 业务暂不需要该字段
    article_dynasty = models.CharField(
        '文章朝代',
        max_length=50,
        blank=True,
        default='',
    )
    writing_mode_origin = models.CharField(
        '文章排版原始值',
        help_text='文章印刷的排版方向',
        max_length=10,
        choices=WRITING_MODE,
        blank=True,
        default='',
    )
    writing_mode = models.CharField(
        '文章排版校对值',
        help_text='文章印刷的排版方向',
        max_length=10,
        choices=WRITING_MODE,
        blank=True,
        default='',
    )
    # DEPRECATED 业务暂不需要该字段
    reading_mode = models.CharField(
        '阅读方向',
        help_text='文章阅读方向',
        max_length=10,
        choices=READING_MODE,
        blank=True,
        default='',
    )
    content_image = models.CharField(
        '文章扫描件',
        help_text='文章所在页原件图片路径或URL',
        max_length=400,
    )
    content_text = models.TextField(
        '文章内容',
        help_text='文章所在页 OCR 识别后的文字内容',
        blank=True,
        default='',
    )
    created_time = models.DateTimeField(
        '创建时间',
        help_text='数据入库时间',
        db_index=True,
        auto_now=True,
    )
    updated_time = models.DateTimeField(
        '更新时间',
        help_text='数据更新时间',
        auto_now=True,
    )
    operator = models.ForeignKey(
        'userprofile.UserProfile',
        on_delete=models.PROTECT,
        help_text='数据操作人',
        verbose_name='操作人',
        null=True,
        blank=True,
        default=None,
    )

    def __str__(self):
        return f'{self.id}-{self.article_title}'

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
