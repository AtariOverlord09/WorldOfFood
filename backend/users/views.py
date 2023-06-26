"""Обработчики приложения users."""
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework import permissions
from rest_framework.response import Response

from users.models import User
from users.serializers import CustomUserCreateSerializer, CustomUserSerializer


class CustomUserViewSet(UserViewSet):

    queryset = User.objects.all()
    serializer_class = CustomUserCreateSerializer