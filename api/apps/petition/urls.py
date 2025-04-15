from django.urls import path
from .views import create_petition_api

urlpatterns = [
    path("petitions/", create_petition_api, name="create_petition_api"),
]
