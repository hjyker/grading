# Generated by Django 3.2.5 on 2021-12-07 10:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0002_alter_userprofile_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'default_permissions': [], 'ordering': ['-create_time'], 'permissions': [('list_audit_order', '校对工单列表'), ('scan_audit_order', '校对工单详情'), ('apply_audit_order', '校对领单'), ('submit_audit_order', '提交校对工单'), ('returned_audit_order', '驳回校对工单'), ('create_audit_order', '创建校对工单'), ('modify_audit_order', '修改校对工单'), ('delete_audit_order', '删除校对工单'), ('list_qa_order', '查看质检工单'), ('apply_qa_order', '质检领单'), ('submit_qa_order', '提交质检工单'), ('returned_qa_order', '质检驳回'), ('create_qa_order', '创建质检工单'), ('modify_qa_order', '修改质检工单'), ('delete_qa_order', '删除质检工单'), ('list_content_mgmt', '查看内容管理列表'), ('detail_content_author', '查看作者详情'), ('create_content_author', '创建作者'), ('modify_content_author', '修改作者'), ('delete_content_author', '删除作者'), ('detail_content_book', '查看书籍详情'), ('create_content_book', '创建书籍'), ('modify_content_book', '修改书籍'), ('delete_content_book', '删除书籍'), ('detail_content_article', '查看文章详情'), ('create_content_article', '创建文章'), ('modify_content_article', '修改文章'), ('delete_content_article', '删除文章'), ('check_user_list', '查看用户列表'), ('assign_role_action', '分配用户角色'), ('check_user_group', '查看角色'), ('add_user_group', '增加角色'), ('edit_user_group', '编辑角色'), ('delete_user_group', '删除角色')], 'verbose_name': '系统用户', 'verbose_name_plural': '系统用户'},
        ),
    ]
