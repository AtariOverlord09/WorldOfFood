"""Конфигурация роутингов основного приложения foodgram."""
from django.contrib import admin
from django.urls import path
from django.urls import include

app_name = "foodgram"

urlpatterns = [
    path("api/", include("api.urls")),
    path("api/", include("users.urls")),
    path("admin/", admin.site.urls),
]
