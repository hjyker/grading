import datetime

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from .model_constant import (
    AUDIT_STATUS,
    AUDIT_ORDER_STATUS,
    QA_TYPE,
    READING_MODE,
    WRITING_MODE,
)


class AuditProfile(models.Model):

    audit_user = models.ForeignKey(
        'userprofile.UserProfile',
        on_delete=models.PROTECT,
        verbose_name='审核人',
        null=True,
        default=None,
        related_name='auditprofile_audit_user',
    )
    status = models.CharField(
        '审核状态',
        max_length=50,
        choices=AUDIT_STATUS,
        null=True,
        default='unassign',
    )
    content_text = models.TextField('内容校对结果')
    article_title = models.CharField(
        '文章标题校对结果',
        max_length=200,
        blank=True,
        default='',
    )
    article_page = models.IntegerField(
        '文章页码校对结果',
        blank=True,
        null=True,
        default=None,
        validators=[MinValueValidator(0)],
        help_text='文章的相对页码',
    )
    article_author = models.ForeignKey(
        'Author',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None,
        help_text='文章作者',
    )
    writing_mode = models.CharField(
        '文章排版',
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
    remark = models.TextField(
        '审核备注',
        max_length=2000,
        blank=True,
        default='',
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
    )

    def __str__(self):
        return f'{self.id}-{self.status}'

    class Meta:
        verbose_name = '校对工单结果'
        verbose_name_plural = verbose_name


class QAOrder(models.Model):

    serial_id = models.CharField(
        '质检工单编号',
        max_length=200,
        db_index=True,
        null=True,
        default=None,
    )
    bulk_id = models.CharField(
        '质检工单批次号',
        max_length=200,
        db_index=True,
        null=True,
        default=None,
    )
    qa_user = models.ForeignKey(
        'userprofile.UserProfile',
        on_delete=models.PROTECT,
        verbose_name='质检人',
        null=True,
        default=None,
        related_name='qaorder_user',
    )
    qa_type = models.CharField(
        '质检类型',
        max_length=50,
        choices=QA_TYPE,
        default='',
    )
    status = models.CharField(
        '质检状态',
        max_length=50,
        choices=AUDIT_STATUS,
        default='unassign',
    )
    remark = models.TextField(
        '质检备注',
        max_length=2000,
        blank=True,
        default='',
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
    )

    def make_serial_id(self):
        return 'QA%s%.6d' % (
            datetime.datetime.now().strftime('%Y%m%d'),
            int(str(self.id)[-6:]),
        )

    def __str__(self):
        return f'{self.id}-{self.serial_id}'

    class Meta:
        verbose_name = '质检工单'
        verbose_name_plural = verbose_name


class AuditOrder(models.Model):

    serial_id = models.CharField(
        '校对工单编号',
        max_length=200,
        db_index=True,
    )
    article = models.ForeignKey(
        'Article',
        on_delete=models.PROTECT,
        verbose_name='原内容信息',
    )
    first_audit = models.ForeignKey(
        AuditProfile,
        related_name='auditorder_first',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None,
        verbose_name='一审结果',
    )
    second_audit = models.ForeignKey(
        AuditProfile,
        related_name='auditorder_second',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None,
        verbose_name='二审结果',
    )
    qa_audit = models.ForeignKey(
        QAOrder,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None,
        verbose_name='质检结果',
    )
    order_status = models.CharField(
        '工单状态',
        max_length=10,
        choices=AUDIT_ORDER_STATUS,
        default='1100',
    )
    returned_count = models.IntegerField(
        '驳回次数',
        validators=[MinValueValidator(0), MaxValueValidator(3)],
        default=0,
    )
    returned_remark = models.TextField(
        '驳回备注',
        max_length=2000,
        blank=True,
        default='',
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
        null=True,
        blank=True,
        default=None,
        related_name='auditorder_operator',
    )

    def make_serial_id(self):
        return 'AUDIT%s%.6d' % (
            datetime.datetime.now().strftime('%Y%m%d'),
            int(str(self.id)[-6:]),
        )

    def __str__(self):
        return f'{self.id}-{self.serial_id}'

    class Meta:
        verbose_name = '校对工单'
        verbose_name_plural = verbose_name
