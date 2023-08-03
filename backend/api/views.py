from sqlite3 import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import PasswordSerializer
from rest_framework import (status, serializers,
                            mixins, viewsets)
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .serializers import (
    SubscribeSerializer,
    UserGetSerializer,
    UserCreateSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    IngredientInRecipeSerializer,
    RecipeSerializer,
    TagSerializer
)
from recipes.models import Recipe, Ingredient, IngredientInRecipe, Tag
from users.models import User
from .permissions import IsAuthorOrReadOnly


class UserGetViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     GenericViewSet):
    """Вьюсет для модели пользователей."""
    queryset = User.objects.all()
    serializer_class = UserGetSerializer
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('username', 'email')
    lookup_field = "username"

    @action(detail=True, methods=['get'],
            permission_classes=IsAuthenticated)
    def me(self, request):
        """Метод для просмотра личной информации."""
        serializer = UserGetSerializer(user=request.user)
        User.objects.get(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'],
            permission_classes=[AllowAny])
    def get_user(request):
        """Метод просмотра информации о пользователе."""
        serializer = UserGetSerializer()
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, id=id)
        return Response(user.data, status=status.HTTP_200_OK)


class UserCreateViewSet(mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        GenericViewSet):
    """Вьюсет для создания, редактирования, удаления пользователей."""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('username', 'email')
    lookup_field = "username"

    @action(detail=True, methods=['post'],
            permission_classes=AllowAny)
    def signup(self, request):
        """Метод для регистрации пользователей."""
        serializer = UserCreateSerializer(data=request.data)
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
            permission_classes=IsAuthenticated)
    def set_password(self, request):
        """Метод для смены пароля."""
        user = self.get_object()
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({'status': 'Пароль успешно сменен.'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


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


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        GenericViewSet):
    """Вьюсет для просмотра ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)

    def get_ingredient(self):
        """Метод получения определенного ингредиента."""
        return get_object_or_404(Ingredient, pk=self.kwargs.get('ingredient_id'))


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 GenericViewSet):
    """Вьюсет для просмотра тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)

    def get_tag(self):
        """Метод получения определенного тега."""
        return get_object_or_404(Tag, pk=self.kwargs.get('tag_id'))


class RecipeViewSet(ModelViewSet):
    """Вьюсет для просмотра, создания, изменения, удаления рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_recipe(self):
        """Метод получения определенного рецепта."""
        return get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))

    def perform_create(self, serializer):
        """Метод создания рецепта."""
        serializer.save(author=self.request.user)


class FavoriteViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      GenericViewSet):
    """Вьюсет для создания и удаления рецептов из избранного."""
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('following__username',)

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.favorite_count = None

    def get_queryset(self):
        """Метод получения определенного рецепта."""
        return get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))


    def perform_create(self, serializer):
        """Метод добавления рецепта в избранное."""
        serializer.save(user=self.request.user,
                        recipe=self.get_queryset(),
                        favorite_count=(self.favorite_count+1))


class ShoppingCartViewSet(ModelViewSet):
    """Вьюсет для просмотра, создания, списка продуктов для рецептов."""
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)

    def create_shopping_cart(self):
        """Метод создания списка покупок."""
        shopping_cart = []
        recipes = Recipe.objects.filter(is_in_shopping_cart=True).all()
        for recipe in recipes:
            shopping_cart.append(recipe.get('ingredients'))
        with open('shopping_cart.txt', 'w', encoding='utf-8') as file:
            file.write('\n'.join(map(str,shopping_cart)))
        return Response('shopping_cart.txt', status=status.HTTP_200_OK)
