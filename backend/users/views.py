from sqlite3 import IntegrityError

from django.contrib.auth.tokens import default_token_generator
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import PasswordSerializer, TokenSerializer
from rest_framework import (status, serializers,
                            mixins, viewsets)
from rest_framework.decorators import permission_classes, action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import (AllowAny, IsAuthenticated, IsAdminUser)
from rest_framework.viewsets import GenericViewSet

from .models import User

from .serializers import (
    UserSerializer, SubscribeSerializer)


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  GenericViewSet):
    """Вьюсет для просмотра, создания, удаления пользователей."""
    queryset = User.objects.all()
    permission_classes = (IsAdminUser,)
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('username', 'email')
    lookup_field = "username"

    @action(detail=True, methods=['post'],
            permission_classes=(AllowAny,))
    def signup(self, request):
        """Метод для регистрации пользователей."""
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        email = serializer.validated_data["email"]
        try:
            User.objects.get_or_create(
                username=username, email=email)
        except IntegrityError:
            raise serializers.ValidationError(
                "Данные имя пользователя или Email уже зарегистрированы"
            )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'],
            permission_classes=(IsAuthenticated))
    def set_password(self, request):
        """Метод для смены пароля."""
        user = self.get_object()
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['password'])
            serializer.save()
            return Response({'status': 'password set'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'],
              permission_classes=[AllowAny])
    def get_token(request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        user = get_object_or_404(User, username=username)
        token = default_token_generator.make_token(user)
        return Response({"token": token, "user": user}, status=status.HTTP_200_OK)



    @action(detail=True, methods=['get'],
            permission_classes=(IsAuthenticated))
    def me(self, request):
        """Метод для просмотра личной информации."""
        serializer = UserSerializer(user=request.user)
        User.objects.get(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscribeViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    """Вьюсет для просмотра, создания подписки на авторов."""
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('following__username',)

    def get_queryset(self):
        """Метод получения определенного автора."""
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        """Метод создания подписки на автора."""
        serializer.save(user=self.request.user)
