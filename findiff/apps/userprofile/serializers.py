# from django.db import transaction
from django.contrib.auth.models import Group, Permission
from rest_framework import serializers

from findiff.common.custom_validations import NonFieldError

from findiff.models import UserProfile


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = (
            'id',
            'name',
            'codename',
        )
        read_only_fields = ('id',)


class EmbedGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = (
            'id',
            'name',
        )


class UserProfileLiteSerializer(serializers.ModelSerializer):

    user_id = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')

    class Meta:
        model = UserProfile
        fields = (
            'id',
            'user_id',
            'username',
            'nickname',
        )


class UserProfileSerializer(serializers.ModelSerializer):

    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    created_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    is_active = serializers.BooleanField(
        source='user.is_active', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    date_joined = serializers.DateTimeField(
        source='user.date_joined', read_only=True)
    groups = EmbedGroupSerializer(
        source='user.groups', many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            'id',
            'user_id',
            'username',
            'nickname',
            'phone',
            'email',
            'date_joined',
            'groups',
            'created_time',
            'updated_time',
            'is_active',
        )


class UserResetPasswordSerializer(serializers.Serializer):
    """修改当前用户密码"""

    origin_passwd = serializers.CharField(required=True)
    new_passwd = serializers.CharField(required=True)
    repeat_new_passwd = serializers.CharField(required=True)

    def validate(self, data):
        if not getattr(self.context['request'], 'user'):
            raise NonFieldError('当前用户不存在')

        user = self.context['request'].user
        if not user.check_password(data['origin_passwd']):
            raise serializers.ValidationError({'origin_passwd': '原密码不正确'})

        if data['new_passwd'] != data['repeat_new_passwd']:
            raise serializers.ValidationError(
                {'repeat_new_passwd': '请输入相同新密码'})

        data['user'] = user
        return data

    def set_password(self, validated_data):
        user = validated_data.pop('user')
        user.set_password(validated_data['repeat_new_passwd'])
        user.save()


class RoleSerializer(serializers.ModelSerializer):

    perms_detail = PermissionSerializer(
        source='permissions', many=True, read_only=True)
    perms = serializers.SerializerMethodField()

    def get_perms(self, obj):
        return list(obj.permissions.all().values_list('codename', flat=True))

    class Meta:
        model = Group
        fields = (
            'id',
            'name',
            'perms',
            'perms_detail',
        )


class UpsertRoleSerializer(serializers.ModelSerializer):

    name = serializers.CharField()
    perms = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
    )

    def create(self, validated_data):
        permissions = validated_data.pop('perms', [])
        group = Group.objects.create(**validated_data)
        perms_ins = Permission.objects.filter(codename__in=permissions)
        group.permissions.set(perms_ins)
        return group

    def update(self, instance, validated_data):
        permissions = validated_data.pop('perms', [])
        instance.name = validated_data.get('name', instance.name)
        perms_ins = Permission.objects.filter(codename__in=permissions)
        instance.permissions.set(perms_ins)
        return instance

    class Meta:
        model = Group
        fields = ('id', 'name', 'perms')


class UserProfileWithRoleSerializer(serializers.Serializer):
    """用户管理"""

    user_list = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(), many=True)
    role_list = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), many=True)

    def save(self):
        users = self.validated_data['user_list']
        roles = self.validated_data['role_list']

        for user in users:
            user.user.groups.set(roles)
            user.save()
