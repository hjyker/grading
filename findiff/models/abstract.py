from django.db import models


class AbsTimeAndOper(models.Model):
    """抽象类: 创建时间、更新时间、操作人"""

    class Meta:
        abstract = True

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
        'UserProfile',
        on_delete=models.PROTECT,
        help_text='数据操作人',
        verbose_name='操作人',
        null=True,
        blank=True,
        default=None,
        related_name='%(app_label)s_%(class)s_operator',
    )
