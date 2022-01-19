from django.db import models

from .model_constant import LABEL_WORD_STATUS
from .abstract import AbsTimeAndOper


class Comments(AbsTimeAndOper):

    music_no = models.IntegerField(
        '歌曲编号',
        db_index=True,
        null=True,
        default=None,
    )
    comment = models.TextField(
        '评论内容',
        blank=True,
        default='',
    )
    likes = models.IntegerField(
        '点赞数',
        blank=True,
        default=0,
    )

    def __str__(self):
        return f'{self.id}-{self.music_no}-{self.comment[:15]}...'

    class Meta:
        verbose_name = '歌曲评论'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']


class Labels(AbsTimeAndOper):

    music_no = models.IntegerField(
        '歌曲编号',
        db_index=True,
        null=True,
        default=None,
    )
    label = models.CharField(
        '候选词',
        max_length=100,
        default='',
    )
    is_matched = models.IntegerField(
        '是否匹配',
        choices=LABEL_WORD_STATUS,
        null=True,
        blank=True,
        default=None,
    )

    def __str__(self):
        return f'{self.id}-{self.music_no}-{self.label}'

    class Meta:
        verbose_name = '歌曲标注词'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']
