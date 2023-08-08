from sqlite3 import IntegrityError
# from weasyprint import HTML
# from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import PasswordSerializer, TokenSerializer
from djoser.social import token

from rest_framework import (filters, status, serializers,
                            mixins, viewsets)
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .serializers import (
    SubscribeSerializer,
    UserGetSerializer,
    UserPostSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeGetSerializer,
    RecipePostSerializer,
    TagSerializer,
)
from recipes.models import Recipe, Ingredient, IngredientInRecipe, Tag
from users.models import User
from .permissions import IsAuthorOrReadOnly, IsAuthorOnly


class UserViewSet(ModelViewSet):
    """Вьюсет для модели пользователей."""
    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('username', 'email')
    lookup_field = "username"
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserGetSerializer
        return UserPostSerializer

    @action(detail=True, methods=['get'],url_path='me',
            permission_classes=IsAuthenticated)
    def profile(self, request):
        """Метод для просмотра личной информации."""
        serializer = UserGetSerializer(user=request.user)
        User.objects.get(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'],
            permission_classes=[AllowAny])
    def get_user_profile(self, request):
        """Метод просмотра информации о пользователе."""
        serializer = UserGetSerializer()
        serializer.is_valid(raise_exception=True)
        user = User.objects.get_object_or_404(id=self.kwargs.get('user_id'))
        return Response(user.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'],
            permission_classes=AllowAny)
    def user_create(self, request):
        """Метод для регистрации пользователей."""
        serializer = UserPostSerializer(data=request.data)
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
    def token_create(request):
        """Метод получения токена."""
        serializer = TokenSerializer()
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = get_object_or_404(User, email=email, password=password)
        if user:
            return Response({"token": token}, status=status.HTTP_200_OK)
        raise serializers.ValidationError("Введены неверные данные.")

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
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name', )

    def get_ingredient(self):
        """Метод получения определенного ингредиента."""
        return get_object_or_404(Ingredient,
                                 id=self.kwargs.get('ingredient_id'))


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
    """Вьюсет для просмотра рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipePostSerializer

    @action(detail=True, methods=['get'],
            permission_classes=[AllowAny])
    def get_recipe(self):
        """Метод просмотра информации о рецепте."""
        serializer = RecipeGetSerializer
        serializer.is_valid(raise_exception=True)
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        return Response(recipe.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'patch', 'delete'],
            permission_classes=(IsAuthenticated, IsAuthorOrReadOnly))
    def recipe_create(self, request):
        """Метод для сoздания, редактирования, удаления рецепта."""
        serializer = RecipePostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = serializer.validated_data["image"]
        ingredients = serializer.validated_data["ingredients"]
        tag = serializer.validated_data["tag"]
        Recipe.objects.get_or_create(
            author=request.user,
            image=image,
            ingredients=ingredients,
            tag=tag
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class FavoriteViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      GenericViewSet):
    """Вьюсет для создания и удаления рецептов из избранного."""
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('following__username',)

    def get_queryset(self):
        """Метод получения определенного рецепта."""
        return get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))

    def perform_create(self, serializer):
        """Метод добавления рецепта в избранное."""
        serializer.save(user=self.request.user,
                        recipe=self.get_queryset())


class ShoppingCartViewSet(ModelViewSet):
    """Вьюсет для просмотра, создания, списка продуктов для рецептов."""
    serializer_class = RecipeGetSerializer
    permission_classes = (IsAuthorOnly,)
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        return Recipe.objects.filter(is_in_shopping_cart=True).all()

    def create_shopping_cart(self):
        """Метод создания списка покупок."""
        shopping_cart = []
        recipes = self.get_queryset()
        for recipe in recipes:
            shopping_cart.append(recipe.get('ingredients'))
        with open('shopping_cart.txt', 'w', encoding='utf-8') as file:
            file.write('\n'.join(map(str, shopping_cart)))
        return Response('shopping_list.txt', status=status.HTTP_200_OK)
        # shopping_list = render_to_string(
        #     "shopping_cart.html",
        #     context={"shopping_cart": shopping_cart}
        # )
        # pdf_list = HTML('path_of_html').write_pdf()