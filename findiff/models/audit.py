from django.db import models

from .abstract import AbsTimeAndOper
from .model_constant import AUDIT_STATUS


class AuditOrder(AbsTimeAndOper):

    music_no = models.IntegerField(
        '歌曲编号',
        db_index=True,
        null=True,
        default=None,
    )
    status = models.CharField(
        '标注状态',
        blank=True,
        max_length=30,
        choices=AUDIT_STATUS,
        default='unassign',
        db_index=True,
    )
    maker = models.ForeignKey(
        'UserProfile',
        on_delete=models.PROTECT,
        help_text='标注人',
        verbose_name='标注人',
        null=True,
        blank=True,
        default=None,
    )

    def __str__(self):
        return f'id:{self.id}-{self.music_no}-{self.status}'

    class Meta:
        verbose_name = '校对工单'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']
