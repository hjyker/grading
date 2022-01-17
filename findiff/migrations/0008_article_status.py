# Generated by Django 3.2.5 on 2021-12-26 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('findiff', '0007_auto_20211219_1039'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='status',
            field=models.CharField(choices=[('unaudit', '待校对'), ('auditing', '校对中'), ('release', '内容发布'), ('forbid', '内容隐藏')], default='unaudit', max_length=30, verbose_name='文章状态'),
        ),
    ]
