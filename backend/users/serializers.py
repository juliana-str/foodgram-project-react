from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели пользователей."""

    class Meta:
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
        )
        model = User


# class SignUpSerializer(serializers.Serializer):
#     """Сериализатор объектов типа User при регистрации."""
#     username = serializers.CharField(
#         required=True,
#         max_length=150,
#         validators=(validate_username,)
#     )
#     email = serializers.EmailField(required=True, max_length=254)
#
#
# class TokenSerializer(serializers.Serializer):
#     """Сериализатор объектов типа User при получении токена."""
#     username = serializers.CharField()
#     confirmation_code = serializers.CharField()
