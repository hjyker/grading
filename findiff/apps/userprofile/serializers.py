from rest_framework import serializers
# from django.db import transaction
from django.contrib.auth.models import Group, Permission
from .models import UserProfile


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


class UserProfileSerializer(serializers.ModelSerializer):

    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.usernanme', read_only=True)
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
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
            'create_time',
            'update_time',
            'is_active',
        )


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
