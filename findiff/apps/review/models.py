import datetime

from django.db import models

from findiff.models.model_constant import AUDIT_STATUS_CHOICES, WRITING_MODE


class RawData(models.Model):
    """NOTE: 弃用原始数据"""

    book_id = models.CharField(
        '书籍ID',
        max_length=10,
        blank=True,
        default='',
        db_index=True,
    )
    book_name = models.CharField(
        '书名',
        help_text='书名',
        max_length=200,
    )
    writing_mode = models.CharField(
        '书籍排版',
        help_text='排版方向',
        max_length=2,
        choices=WRITING_MODE,
        db_index=True,
    )
    content_image = models.CharField(
        '每页扫描件',
        help_text='每页原始的扫描图片',
        max_length=400,
    )
    content_text = models.TextField('每页文字', help_text='OCR 识别之后的文字内容')
    content_text_name = models.CharField(  # TODO 当前为服务器path，接入云存储后存放 URL
        '每页文件名',
        help_text='每页原始文件上传前的文件名',
        max_length=200,
    )
    content_image_name = models.CharField(
        '每页扫描件名',
        help_text='扫描件上传前的文件名',
        max_length=200,
    )

    def __str__(self):
        return f'{self.id}-{self.book_name}'

    class Meta:
        verbose_name = '原始校对数据'
        verbose_name_plural = verbose_name


class AuditOrder(models.Model):
    order_id = models.CharField(
        '订单号',
        help_text='订单号',
        db_index=True,
        max_length=40,
        blank=True,
        default='',
    )
    raw_data = models.ForeignKey(
        RawData,
        verbose_name='文件原始数据',
        on_delete=models.PROTECT,
    )
    first_audit_user = models.ForeignKey(
        'userprofile.UserProfile',
        on_delete=models.PROTECT,
        help_text='初审人',
        verbose_name='初审人',
        default=None,
        null=True,
        blank=True,
        related_name='auditorder_first_audit_user_set',
    )
    first_audit_time = models.DateTimeField(
        '初审时间',
        help_text='初审时间',
        db_index=True,
        blank=True,
        null=True,
    )
    first_audit_result = models.TextField(
        '初审提交内容',
        help_text='初审提交内容',
        blank=True,
        default='',
    )
    first_order_status = models.CharField(
        '初审状态',
        help_text='初审状态',
        db_index=True,
        max_length=30,
        choices=AUDIT_STATUS_CHOICES,
        blank=True,
        default='unassign',
    )
    second_audit_user = models.ForeignKey(
        'userprofile.UserProfile',
        on_delete=models.PROTECT,
        help_text='复审人',
        verbose_name='复审人',
        default=None,
        null=True,
        blank=True,
        related_name='auditorder_second_audit_user_set',
    )
    second_audit_time = models.DateTimeField(
        '复审时间',
        help_text='复审时间',
        db_index=True,
        blank=True,
        null=True,
    )
    second_audit_result = models.TextField(
        '复审提交内容',
        help_text='复审提交内容',
        blank=True,
        default='',
    )
    second_order_status = models.CharField(
        '复审状态',
        help_text='复审状态',
        db_index=True,
        max_length=30,
        choices=AUDIT_STATUS_CHOICES,
        blank=True,
        default='unassign',
    )
    created_time = models.DateTimeField(
        '创建时间',
        help_text='创建时间',
        db_index=True,
        auto_now=True,
    )
    updated_time = models.DateTimeField(
        '更新时间',
        help_text='更新时间',
        auto_now=True,
    )
    operator = models.ForeignKey(
        'userprofile.UserProfile',
        on_delete=models.PROTECT,
        help_text='操作人',
        verbose_name='操作人',
        default=None,
        null=True,
        blank=True,
        related_name='auditorder_operator_set',
    )

    def make_order_id(self):
        return 'AUDIT%s%.6d' % (
            datetime.datetime.now().strftime('%Y%m%d'),
            int(str(self.id)[-6:]),
        )

    def __str__(self):
        return f'{self.id}-{self.order_id}'

    class Meta:
        verbose_name = '校对订单'
        verbose_name_plural = verbose_name
