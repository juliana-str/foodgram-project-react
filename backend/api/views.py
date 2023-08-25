from django.db.models import Sum, F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet
from rest_framework import (filters, status, mixins)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .exeptions import NoDataException
from .filters import RecipeFilter, IngredientFilter
from .serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeListSerializer,
    RecipeCreateUpdateSerializer,
    TagSerializer,
    ShoppingCartSerializer,
    SubscribeSerializer,
    SubscriptionsSerializer,
    UserGetSerializer,
    UserPostSerializer
)
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Tag,
    ShoppingCart
)
from users.models import Subscribe, User
from .permissions import IsAuthorOnly
from .pagination import CustomPaginator


class CustomUserViewSet(UserViewSet):
    """Вьюсет для модели пользователей."""
    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend,)
    pagination_class = CustomPaginator
    search_fields = ('username', 'email')
    lookup_fields = ('name', 'id')
    http_method_names = ['get', 'post', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserGetSerializer
        return UserPostSerializer

    @action(detail=False, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, **kwargs):
        """Метод создания подписки на автора."""
        author = get_object_or_404(User, id=kwargs['id'])
        user = request.user
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data={'user': user.id, 'author': author.id},
                context={"request": request})
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        try:
            Subscribe.objects.get(user=user, author=author).delete()
        except NoDataException:
            'Подписки на этого автора нет!'
        finally:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            pagination_class=CustomPaginator,
            permission_classes=[IsAuthorOnly])
    def subscriptions(self, request):
        """Метод получения всех подписок."""
        queryset = self.filter_queryset(User.objects.filter(
            following__user=request.user).all())
        page = self.paginate_queryset(queryset)
        if page:
            serializer = SubscriptionsSerializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionsSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        GenericViewSet):
    """Вьюсет для просмотра ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPaginator
    filter_backends = (filters.SearchFilter,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 GenericViewSet):
    """Вьюсет для просмотра тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Вьюсет для просмотра рецептов."""
    queryset = Recipe.objects.all()
    pagination_class = CustomPaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeCreateUpdateSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, **kwargs):
        """Метод добавления рецепта в избранное."""
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = request.user
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'user': user.id, 'recipe': recipe.id})
            serializer.is_valid(raise_exception=True)
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        try:
            Favorite.objects.get(user=user.id, recipe=recipe.id).delete()
        except NoDataException:
            'Этого рецепта нет в избранном!'
        finally:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthorOnly])
    def download_shopping_cart(self, request):
        """Метод для просмотра списка покупок."""
        items = IngredientInRecipe.objects.select_related(
            'recipe', 'ingredient'
        )
        items = items.filter(recipe__shopping_carts__user=request.user).all()
        shopping_cart = items.values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            name=F('ingredient__name'),
            units=F('ingredient__measurement_unit'),
            total=Sum('amount')
        ).order_by('-total')
        text = '\n'.join(
            [f"{item.get('name')} ({item.get('units')}) - {item.get('total')}"
             for item in shopping_cart]
        )
        filename = 'foodgram_shopping_cart.txt'
        response = HttpResponse(text, content_type='text/plan')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        """Метод для создания, удаления списка продуктов для рецептов."""
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = request.user
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                    data={'user': user.id, 'recipe': recipe.id})
            serializer.is_valid(raise_exception=True)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_200_OK)

        try:
            ShoppingCart.objects.get(recipe=recipe).delete()
        except NoDataException:
            'Этого рецепта нет в списке покупок!'
        finally:
            return Response(status=status.HTTP_204_NO_CONTENT)
