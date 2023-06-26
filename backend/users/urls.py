"""URL-роутинг приложения API."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet

app_name = "users"

router = DefaultRouter()

router.register("users", CustomUserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
]
