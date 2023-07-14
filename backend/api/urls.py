"""URL конфигурация для приложения api."""
from django.urls import include, path
from rest_framework import routers

from api.views import IngredientViewSet, RecipesViewSet, TagsViewSet

router = routers.DefaultRouter()
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
]
