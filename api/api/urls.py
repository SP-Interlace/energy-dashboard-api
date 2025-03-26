"""
URL configuration for api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include, re_path
from django.conf import settings
from django.utils.translation import gettext_lazy as _


from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from apps.carbon_intensity.urls import router as carbon_intensity_router
from apps.octopus.urls import router as octopus_router

router = DefaultRouter()

router.registry.extend(carbon_intensity_router.registry)
router.registry.extend(octopus_router.registry)


api_info = openapi.Info(
    title="Energy Dashboard API",
    default_version="v1",
    description="This is the documentation for the Energy Dashboard API",
    license=openapi.License(name="MIT License"),
)
settings.SWAGGER_SETTINGS["DEFAULT_INFO"] = api_info

# Schema
schema_view = get_schema_view(
    public=True,
    permission_classes=[permissions.AllowAny],
)

admin.site.site_title = _("END Admin")
admin.site.site_header = _("Energy Dashboard Administration")
admin.site.index_title = _("Control Center Home")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^docs/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
    path(
        "",
        lambda _: HttpResponse(
            '<div style="max-width: 400px;font-family: Helvetica, Sans-Serif;font-size: 1.2em;margin: 20vh '
            'auto;"><p>"<strong>200 OK.</strong> Welcome to the Energy Dashboard API."</p></div>',
            headers={"content-type": "text/html"},
            status=200,
        ),
        name="api-test",
    ),
]
