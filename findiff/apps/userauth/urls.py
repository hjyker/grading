from django.urls import path
from .views import LoginView, TokenRefreshView

urlpatterns = [
    path('token/', LoginView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view())
]
