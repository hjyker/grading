from django.contrib import admin
from .models import UserProfile, FgUserProfile
from findiff.models.user_kpi import UserKPI


admin.site.register(UserProfile)
admin.site.register(FgUserProfile)
