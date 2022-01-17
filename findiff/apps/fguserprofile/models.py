from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class FgUserProfile(models.Model):
    # 前台用户表,扩展Django自带user表
    # null=True表明数据库该字段可以为空,on_delete=SET_NULL表明删除关联数据,与之关联的值设置为null
    # verbose_name就是在后台显示的名称
    user = models.OneToOneField(
        User,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='前台用户',
        help_text='前台用户',
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
    join_time = models.DateTimeField(
        '注册时间',
        help_text='注册时间',
        auto_now_add=True
    )
    operate_time = models.DateTimeField(
        '操作时间',
        help_text='操作时间',
        auto_now=True
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
        username = getattr(self.user, 'username',
                           None)  # 防止 user on_delete= SET_NULL
        return f'{self.id}-{self.nickname}/{username}'

    def save(self, *args, **kwargs):
        if not self.nickname:
            self.nickname = self.user.username
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '前台用户'
        # 复数
        verbose_name_plural = verbose_name
        # 按注册时间降序
        ordering = ['-join_time']
        # TODO 前台用户权限
        # default_permissions = []
        # permissions = ALL_PERMS
