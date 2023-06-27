"""URL-роутинг приложения api."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import RecipeViewSet

app_name = "api"

router = DefaultRouter()

router.register("recipes", viewset=RecipeViewSet, basename="recipes")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]
