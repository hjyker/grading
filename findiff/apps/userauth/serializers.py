from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework.serializers import ValidationError


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['perms'] = self.user.get_all_permissions()
        userprofile = getattr(self.user, 'userprofile', None)
        if not userprofile:
            raise ValidationError('用户不存在，请联系管理员注册')
        data['nickname'] = self.user.userprofile.nickname
        return data


class TokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        return data
