from sqlite3 import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import PasswordSerializer
from rest_framework import (filters, status, serializers,
                            mixins, viewsets)
from rest_framework.decorators import permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import (AllowAny, IsAuthenticated)

from rest_framework.viewsets import ModelViewSet

from .models import User
from .permissions import IsAuthorOnly

from .serializers import (
    UserSerializer, SubscribeSerializer)


class UserViewSet(ModelViewSet):
    """Вьюсет для просмотра, создания, удаления пользователей."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )
    search_fields = ('username', 'email')
    lookup_field = "username"

    @permission_classes([AllowAny])
    @action(detail=True, methods=['post'])
    def signup(self, request):
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

    @permission_classes([IsAuthenticated])
    @action(detail=True, methods=['post'])
    def set_password(self, request):
        user = self.get_object()
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({'status': 'password set'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @permission_classes([IsAuthorOnly])
    @action(detail=True, methods=['get'])
    def me(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        User.objects.get(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscribeViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       viewsets.GenericViewSet):
    """Вьюсет для просмотра, создания подписки на авторов."""
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        """Метод получения определенного автора."""
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        """Метод создания подписки на автора."""
        serializer.save(user=self.request.user)
