from django.db import models
from django.contrib.auth.models import User
from findiff.common.permissions.perm_config import ALL_PERMS


class UserProfile(models.Model):
    ''' 用户扩展表，扩展于Django User'''

    user = models.OneToOneField(
        User,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='DjangoAdmin用户',
        help_text='DjangoAdmin用户',
    )
    nickname = models.CharField(
        '昵称',
        unique=True,
        max_length=30,
        null=True,
        blank=True,
        help_text='昵称支持最多30个字符',
    )
    phone = models.CharField(
        '联系电话',
        max_length=30,
        blank=True,
        help_text='联系电话',
    )
    create_time = models.DateTimeField(
        '添加时间',
        help_text='添加时间',
        auto_now_add=True
    )
    update_time = models.DateTimeField(
        '更新时间',
        help_text='更新时间',
        auto_now=True,
    )
    operator = models.ForeignKey(
        'userprofile.UserProfile',
        on_delete=models.PROTECT,
        verbose_name='操作人',
        default=None,
        null=True,
        blank=True,
    )

    def __str__(self):
        username = getattr(self.user, 'username', None)  # 防止 user on_delete= SET_NULL
        return f'{self.id}-{self.nickname}/{username}'

    def save(self, *args, **kwargs):
        if not self.nickname:
            self.nickname = self.user.username
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '系统用户'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']
        default_permissions = []
        permissions = ALL_PERMS
