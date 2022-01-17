from django.db import models
from .abstract import AbsTimeAndOper
from .model_constant import KPI_TYPES, KPI_TRIGGER_STEPS


class UserKPI(AbsTimeAndOper):
    """校对人绩效"""

    class Meta:
        verbose_name = '绩效'
        verbose_name_plural = verbose_name

    user = models.ForeignKey(
        'userprofile.UserProfile',
        on_delete=models.PROTECT,
        help_text='校对人',
        verbose_name='校对人',
        db_index=True,
    )
    type = models.CharField(
        '绩效类型',
        max_length=50,
        choices=KPI_TYPES,
        default='',
    )
    count = models.IntegerField(
        '绩效统计次数',
        default=0,
    )
    trigger_step = models.CharField(
        '绩效统计所在流程',
        max_length=50,
        null=True,
        blank=True,
        default=None,
        choices=KPI_TRIGGER_STEPS,
    )

    def __str__(self):
        return f'{self.id}-{self.user.user.username}-{self.type}({self.count})'
