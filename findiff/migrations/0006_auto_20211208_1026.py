# Generated by Django 3.2.5 on 2021-12-08 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('findiff', '0005_auto_20211207_2223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='article_review_status',
            field=models.CharField(choices=[('unassign', '未分配'), ('unaudit', '待校对'), ('success', '成功'), ('fail', '失败'), ('returned', '驳回'), ('suspend', '挂起')], default='unassign', max_length=20, verbose_name='文章校对状态'),
        ),
        migrations.AlterField(
            model_name='auditorder',
            name='order_status',
            field=models.CharField(choices=[('1100', '一审未分配'), ('1101', '一审待校对'), ('1102', '一审成功'), ('1103', '一审驳回'), ('1104', '一审失败'), ('1105', '一审挂起'), ('1200', '二审未分配'), ('1201', '二审待校对'), ('1202', '二审成功'), ('1203', '二审驳回'), ('1204', '二审失败'), ('1205', '二审挂起'), ('2100', '质检未分配'), ('2101', '质检待审核'), ('2102', '质检成功'), ('2103', '质检驳回'), ('2104', '质检失败'), ('2105', '质检挂起')], default='1100', max_length=10, verbose_name='工单状态'),
        ),
        migrations.AlterField(
            model_name='auditprofile',
            name='status',
            field=models.CharField(choices=[('unassign', '未分配'), ('unaudit', '待校对'), ('success', '成功'), ('fail', '失败'), ('returned', '驳回'), ('suspend', '挂起')], default='unassign', max_length=50, null=True, verbose_name='审核状态'),
        ),
        migrations.AlterField(
            model_name='qaorder',
            name='status',
            field=models.CharField(choices=[('unassign', '未分配'), ('unaudit', '待校对'), ('success', '成功'), ('fail', '失败'), ('returned', '驳回'), ('suspend', '挂起')], default='unassign', max_length=50, verbose_name='质检状态'),
        ),
    ]
