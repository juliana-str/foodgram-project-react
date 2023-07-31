from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from users.models import Subscribe, User

from .validators import validate_username


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели пользователей."""
    username = serializers.CharField(
        max_length=150,
        validators=(validate_username,),
    ),
    first_name = serializers.CharField(
        max_length=150,
    ),
    last_name = serializers.CharField(
        max_length=150,
    ),
    email = serializers.EmailField(
        max_length=254,
    ),

    class Meta:
        fields = '__all__'
        required_fields = fields
        model = User


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели подписок на авторов.."""
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=CurrentUserDefault(),
    )

    def validate_following(self, data):
        """Проверка подписки на самого себя."""
        if self.context['request'].user == data:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя!')
        return data

    class Meta:
        fields = '__all__'
        model = Subscribe
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'following'),
                message='Вы уже подписаны на этого автора!'
            ),
        )

