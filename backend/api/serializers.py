from rest_framework import serializers
from djoser.serializers import TokenCreateSerializer, UserCreateSerializer

from users.models import User


class CustomUserSerializer(UserCreateSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password"
        )

