from django.db import models

from .model_constant import (AUDIT_STATUS_CHOICES, OPEN_STATUS,
                             READING_MODE, WRITING_MODE)


class Author(models.Model):
    '''作者表，存储书籍或者文章作者'''

    name = models.CharField(
        '作者姓名',
        max_length=50,
    )
    dynasty = models.CharField(
        '作者朝代',
        max_length=50,
        null=True,
        blank=True,
        default=None,
    )
    writing_school = models.CharField(
        '作者流派',
        max_length=50,
        null=True,
        blank=True,
        default=None,
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
        default=None,
        blank=True,
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
        default=None,
        blank=True,
    )
    book_name = models.CharField(
        '书籍名称',
        max_length=200,
        db_index=True,
    )
    writing_mode = models.CharField(
        '书籍排版',
        help_text='书籍印刷的排版方向',
        max_length=10,
        choices=WRITING_MODE,
    )
    reading_mode = models.CharField(
        '阅读方向',
        max_length=10,
        choices=READING_MODE,
    )
    book_genre = models.CharField(
        '书籍体裁',
        max_length=50,
        default=None,
        blank=True,
        null=True,
    )
    book_dynasty = models.CharField(
        '书籍朝代',
        max_length=50,
        default=None,
        blank=True,
        null=True,
        help_text='书籍编纂朝代',
    )
    book_open_status = models.CharField(
        '书籍状态',
        default=True,
        null=True,
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
        default=None,
        blank=True,
    )

    def __str__(self):
        return f'{self.id}-{self.book_name}'

    class Meta:
        verbose_name = '书籍'
        verbose_name_plural = verbose_name


class Article(models.Model):
    '''文章表'''

    book_id = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        help_text='书籍',
    )
    author_id = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,
        help_text='作者',
    )
    article_snum = models.CharField(
        '文章编号',
        max_length=200,
        default=None,
        blank=True,
    )
    article_title = models.CharField(
        '文章标题',
        max_length=200,
        default=None,
        blank=True,
    )
    book_page = models.IntegerField(
        '书籍页码',
        blank=True,
        null=True,
        default=None,
        help_text='文章在书籍中的页码'
    )
    article_page = models.IntegerField(
        '文章页码',
        blank=True,
        null=True,
        default=None,
        help_text='文章的相对页码',
    )
    article_review_status = models.CharField(
        '文章校对状态',
        max_length=20,
        choices=AUDIT_STATUS_CHOICES,
        default='unssign',
    )
    article_open_status = models.CharField(
        '文章状态',
        max_length=20,
        choices=OPEN_STATUS,
        default='close',
    )
    article_genre = models.CharField(
        '文章体裁',
        max_length=50,
        default=None,
        blank=True,
        null=True,
    )
    article_dynasty = models.CharField(
        '文章朝代',
        max_length=50,
        default=None,
        blank=True,
        null=True,
    )
    content_image = models.CharField(
        '文章扫描件',
        help_text='文章所在页原件图片路径或URL',
        max_length=400,
    )
    content_text = models.TextField('文章内容', help_text='文章所在页 OCR 识别后的文字内容')
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
        default=None,
        blank=True,
    )

    def __str__(self):
        return f'{self.id}-{self.article_title}'

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
