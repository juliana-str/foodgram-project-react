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

from .serializers import (
    SubscribeSerializer,
    # PasswordSetSerializer,
    UserGetSerializer,
    UserPostSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeGetSerializer,
    RecipePostUpdateSerializer,
    TagSerializer,
    Shopping_cartSerializer,
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


class SubscribeViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    """Вьюсет для просмотра, создания подписки на авторов."""
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPaginator
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('following__username',)

    def get_queryset(self):
        """Метод получения определенного автора."""
        return self.request.user.follower.all()

    def perform_create(self, request):
        """Метод создания подписки на автора."""
        serializer = SubscribeSerializer(
            author=request.author,
            data=request.data,
            context={"request": request})
        serializer.is_valid(raise_exception=True)
        Subscribe.objects.create(user=request.user, author=request.author)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def perform_destroy(self, request):
        get_object_or_404(Subscribe, user=request.user,
                          author=request.author).delete()
        return Response({'detail': 'Успешная отписка'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,),
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

    def get_ingredient(self):
        """Метод получения определенного ингредиента."""
        return get_object_or_404(Ingredient,
                                 id=self.kwargs.get('ingredient_id'))


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.CreateModelMixin,
                 GenericViewSet):
    """Вьюсет для просмотра тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_tag(self):
        """Метод получения определенного тега."""
        return get_object_or_404(Tag, pk=self.kwargs.get('tag_id'))


class RecipeViewSet(ModelViewSet):
    """Вьюсет для просмотра рецептов."""
    queryset = Recipe.objects.all()
    pagination_class = CustomPaginator
    filter_backends = (DjangoFilterBackend,)
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipePostUpdateSerializer

    @action(detail=False, methods=['get'],
            permission_classes=[AllowAny])
    def get_recipe(self):
        """Метод просмотра информации о рецепте."""
        serializer = RecipeGetSerializer
        serializer.is_valid(raise_exception=True)
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        return Response(recipe.data, status=status.HTTP_200_OK)

    # @action(detail=True, methods=['post', 'patch', 'delete'],
    #         permission_classes=(IsAuthenticated, IsAuthorOrReadOnly))
    # def recipe_create_update_delete(self, request):
    #     """Метод для сoздания, редактирования, удаления рецепта."""
    #     serializer = RecipePostUpdateSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     if request.method in ['post', 'patch']:
    #         image = serializer.validated_data["image"]
    #         ingredients = serializer.validated_data["ingredients"]
    #         tags = serializer.validated_data["tags"]
    #         Recipe.objects.get_or_create(
    #             author=request.user,
    #             image=image,
    #             ingredients=ingredients,
    #             tags=tags
    #         )
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     else:
    #         recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
    #         recipe.delete()
    #         return Response('Рецепт успешно удален.', status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'],
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
        serializer = Shopping_cartSerializer
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

