from rest_framework import serializers
from .models import FgUserProfile


# TODO 权限

# TODO 分组

class FgUserProfileSerializer(serializers.ModelSerializer):
    # 不加这个拿不到Django User的信息
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.usernanme', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    is_stuff = serializers.BooleanField(source='user.is_stuff', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = FgUserProfile
        fields = (
            'id',
            'user_id',
            'username',
            'nickname',
            'phone',
            'email',
            'join_time',
            'operate_time',
            'operator',
            'is_active',
            'is_stuff'
        )
