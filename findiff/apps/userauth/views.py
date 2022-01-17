from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import LoginSerializer, TokenRefreshSerializer


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class TokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer
