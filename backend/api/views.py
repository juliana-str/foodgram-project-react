from django.db.models import Sum, F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer

from djoser.views import UserViewSet

from rest_framework import (filters, status, serializers,
                            mixins, viewsets, request)

from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .filters import RecipeFilter
from .serializers import (
    SubscribeSerializer,
    UserGetSerializer,
    UserPostSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeListSerializer,
    RecipeCreateUpdateSerializer,
    TagSerializer,
    Shopping_cartSerializer
)
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Tag,
    Shopping_cart
)
from users.models import Subscribe, User
from .permissions import IsAuthorOrReadOnly, IsAuthorOnly
from .pagination import CustomPaginator


class CustomUserViewSet(UserViewSet):
    """Вьюсет для модели пользователей."""
    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend,)
    pagination_class = CustomPaginator
    search_fields = ('username', 'email')
    lookup_fields = ('name', 'id')
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserGetSerializer
        return UserPostSerializer

    @action(detail=False, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data,
                                           context={'request': request})
        if serializer.is_valid(raise_exception=True):
            self.request.user.save()
        return Response({'detail': 'Пароль успешно изменен!'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            pagination_class=CustomPaginator,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        """Метод создания подписки на автора."""
        author = get_object_or_404(User, id=kwargs['id'])
        user = request.user
        if request.method == 'POST':
            print(author, user)
            serializer = SubscribeSerializer(
                data={'user': user.id, 'author': author.id},
                context={"request": request})
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        else:
            get_object_or_404(Subscribe, user=request.user,
                              author=request.author).delete()
            return Response({'detail': 'Успешная отписка'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthorOnly,),
            pagination_class=CustomPaginator)
    def subscriptions(self, request):
        """Метод получения всех подписок."""
        queryset = User.objects.filter(
            subscribed_by__user=self.request.user).all()
        page = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(page, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        GenericViewSet):
    """Вьюсет для просмотра ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPaginator
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name', )


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.CreateModelMixin,
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
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        """Метод добавления рецепта в избранное."""
        recipe = get_object_or_404(Recipe, id=kwargs['id'])
        user = request.user
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'user': user.id, 'recipe': recipe.id})
            serializer.is_valid(raise_exception=True)
            if not Favorite.objects.filter(user=user,
                                           recipe=recipe).exists():
                Favorite.objects.create(user=user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в избранном.'},
                            status=status.HTTP_400_BAD_REQUEST)

        else:
            get_object_or_404(Favorite, user=user.id,
                              recipe=recipe.id).delete()
            return Response({'detail': 'Рецепт успешно удален из избранного.'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthorOnly,))
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
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        """Метод для создания, удаления списка продуктов для рецептов."""
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = request.user
        if request.method == 'POST':
            serializer = Shopping_cartSerializer(
                data={'user': user.id, 'recipe': recipe.id})
            serializer.is_valid(raise_exception=True)
            if not Shopping_cart.objects.filter(user=user,
                                           recipe=recipe).exists():
                Shopping_cart.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            shopping_cart = get_object_or_404(
                Shopping_cart, recipe=recipe)
            shopping_cart.delete()
            return Response({'detail': 'Список покупок успешно удален.'},
                            status=status.HTTP_200_OK)
