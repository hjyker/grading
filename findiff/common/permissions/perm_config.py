import itertools
from functools import reduce
from django.contrib.auth.models import Permission, ContentType

# BUG NOTIFY_AUTH 不存在的时候，无法分配该权限给角色
# from django.conf import settings
# NOTIFY_AUTH = getattr(settings, 'NOTIFY_AUTH', '')

PERMS_CONFIG = (
    {
        'business_module': '校对领单',
        'perms': (
            {
                'name': '校对工单列表',
                'codename': 'list_audit_order',
            },
            {
                'name': '校对工单详情',
                'codename': 'scan_audit_order',
            },
            {
                'name': '校对领单',
                'codename': 'apply_audit_order',
            },
            {
                'name': '提交校对工单',
                'codename': 'submit_audit_order',
            },
            {
                'name': '创建校对工单',
                'codename': 'create_audit_order',
            },
            {
                'name': '修改校对工单',
                'codename': 'modify_audit_order',
            },
            {
                'name': '删除校对工单',
                'codename': 'delete_audit_order',
            },
        ),
    },
    {
        'business_module': '内容管理',
        'perms': (
            {
                'name': '查看内容管理列表',
                'codename': 'list_content_mgmt',
            },
            {
                'name': '导出标注数据',
                'codename': 'export_marked_result',
            },
        ),
    },
    {
        'business_module': '用户列表',
        'perms': (
            {
                'name': '查看用户列表',
                'codename': 'check_user_list',
            },
            {
                'name': '分配用户角色',
                'codename': 'assign_role_action',
            },
        )
    },
    {
        'business_module': '角色管理',
        'perms': (
            {
                'name': '查看角色',
                'codename': 'check_user_group',
            },
            {
                'name': '增加角色',
                'codename': 'add_user_group',
            },
            {
                'name': '编辑角色',
                'codename': 'edit_user_group',
            },
            {
                'name': '删除角色',
                'codename': 'delete_user_group',
            },
        )
    },
)

# ALL_PERMS 数据格式
# [
#    ('perms_code1', 'perms1 description'),
#    ('perms_code2', 'perms2 description'),
#    ...
# ]
ALL_PERMS = list(itertools.chain.from_iterable([
    [(perm['codename'], perm['name']) for perm in perm_config['perms']]
    for perm_config in PERMS_CONFIG
]))


# PERMS_OPTIONS 数据格式
# {
#     'check_user_list': {
#         'business_module': '用户角色管理',
#         'perms': ({'name': '查看用户角色', 'codename': 'check_user_list'},)
#     },
#     'assign_role_action': {
#         'business_module': '用户角色管理',
#         'perms': ({'name': '分配用户角色', 'codename': 'assign_role_action'}, )
#     },
#     ...
# }
PERMS_OPTIONS = reduce(lambda x, y: dict(list(x.items()) + list(y.items())), [
    {perm['codename']: {'business_module': perm_config['business_module'],
                        'perms':(perm,)} for perm in perm_config['perms']}
    for perm_config in PERMS_CONFIG
])


# NOTE 使用自定义权限，需要单独运行以下代码，保证权限存储到数据库
def insert_perms_to_db():
    content_type = ContentType.objects.filter(
        app_label='findiff', model='userprofile').first()
    if not content_type:
        raise ValueError()
    for codename, name in ALL_PERMS:
        default = {
            "name": name,
            "codename": codename,
            "content_type": content_type
        }
        Permission.objects.update_or_create(defaults=default, codename=codename)
