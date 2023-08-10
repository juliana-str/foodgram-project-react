# from sqlite3 import IntegrityError
from django.db.models import Sum, F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import PasswordSerializer, TokenSerializer

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
    RecipePostUpdateSerializer,
    TagSerializer,
    Shopping_cart,
)
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Tag
)
from users.models import Subscribe, User
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

    @action(detail=True, methods=['get'], url_path='me',
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

@action(detail=True, methods=['post'],
        permission_classes=IsAuthenticated)
def token_login(request):
    """Метод получения токена."""
    serializer = TokenSerializer()
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"]
    password = serializer.validated_data["password"]
    try:
        user = User.objects.get(email=email, password=password)
    except:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    user_token = user.auth_token.key
    data = {'token': user_token}
    return Response(data=data, status=status.HTTP_200_OK)

@action(detail=True, methods=['post'],
        permission_classes=IsAuthenticated)
def token_logout(request):
    """Метод удаления токена."""
    serializer = TokenSerializer()
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"]
    password = serializer.validated_data["password"]
    try:
        user = User.objects.get(email=email, password=password)
    except:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    user_token = user.auth_token.key
    user_token.destroy()
    return Response('Вы успешно вышли из системы.', status=status.HTTP_200_OK)


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


    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        queryset = User.objects.filter(
            subscribed_by__user=self.request.user).all()
        return queryset


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
        return RecipePostUpdateSerializer

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
        serializer = RecipePostUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.method in ['post', 'pach']:
            image = serializer.validated_data["image"]
            ingredients = serializer.validated_data["ingredients"]
            tags = serializer.validated_data["tag"]
            Recipe.objects.get_or_create(
                author=request.user,
                image=image,
                ingredients=ingredients,
                tags=tags
            )
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
            recipe.delete()
            return Response('Рецепт успешно удален.', status=status.HTTP_200_OK)

    @action(detail=False, methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,))
    def favorite(self, request):
        """Метод для создания и удаления рецептов из избранного."""
        serializer = FavoriteSerializer
        if request.method == 'post':
            favorite_recipe = get_object_or_404(
                Recipe, pk=self.kwargs.get('recipe_id')
            )
            serializer.save(user=self.request.user,
                            recipe=favorite_recipe)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            favorite_recipe = get_object_or_404(
                Favorite, id=self.kwargs.get('recipe_id'))
            favorite_recipe.delete()
            return Response('Рецепт успешно удален из избранного.',
                            status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated, IsAuthorOnly,))
    def download_shopping_cart(self, request):
        """Метод для просмотра списка покупок."""
        items = IngredientInRecipe.objects.select_related(
            'recipe', 'ingredient'
        )
        items = items.filter(
            recipe__shopping_carts__user=request.user
        )
        shopping_cart = items.values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            name=F('ingredient__name'),
            units=F('ingredient__measurement_unit'),
            total=Sum('amount'),
        ).order_by('-total')

        text = '\n'.join([
                f"{item['name']} ({item['units']}) - {items['total']}"
                for item in shopping_cart
        ])
        filename = 'foodgram_shopping_cart.txt'
        response = HttpResponse(text, content_type='text/plan')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthorOnly,))
    def shopping_cart(self, request, pk=None):
        """Метод для создания, удаления списка продуктов для рецептов."""
        serializer = Shopping_cart
        if request.method == 'post':
            serializer.save(user=self.request.user,
                            shopping_cart=self.shopping_cart)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            favorite_recipe = get_object_or_404(
                Favorite, id=self.kwargs.get('recipe_id'))
            favorite_recipe.delete()
            return Response('Рецепт успешно удален из избранного.',
                            status=status.HTTP_200_OK)
