from django.urls import path

from .views import UserKPIView

urlpatterns = [
    path('user/', UserKPIView.as_view()),
]
