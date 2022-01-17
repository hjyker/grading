"""findiff URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf.urls.static import static
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
import debug_toolbar


# NOTE API docs, only used in the development
schema_view = get_schema_view(
    openapi.Info(
        title="Findiff API",
        default_version='v1.0.0',
        description="Find differences in text.",
        license=openapi.License(name="Apache License 2.0"),
    ),
    public=True,
    permission_classes=[permissions.DjangoModelPermissions],
)


urlpatterns = [
    path('captcha/', include('captcha.urls')),
    path('admin/', admin.site.urls),
    path('auth/', include('findiff.apps.userauth.urls')),
    path('user/', include('findiff.apps.userprofile.urls')),
    path('order/', include('findiff.apps.review.urls')),
    path('article/', include('findiff.apps.article.urls')),
    path('author/', include('findiff.apps.author.urls')),
    path('kpi/', include('findiff.apps.userkpi.urls'))
]


if settings.DEBUG:
    urlpatterns = [
        *urlpatterns,
        *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
        path('__debug__/', include(debug_toolbar.urls)),
        re_path(r'^docs/$',
                schema_view.with_ui('swagger', cache_timeout=0),
                name='schema-swagger-ui'),
    ]
