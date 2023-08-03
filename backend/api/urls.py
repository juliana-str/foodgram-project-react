from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FavoriteViewSet,
    IngredientViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    SubscribeViewSet,
    TagViewSet,
    UserGetViewSet,
    UserCreateViewSet
)

app_name = 'api'

router = DefaultRouter()
router.register(r'users', UserGetViewSet, basename='users')
router.register(r'users', UserCreateViewSet, basename='create')
router.register(r'users/subscriptions', SubscribeViewSet, basename='subscriptions')
router.register(r'users/<int:id>/subscribes', SubscribeViewSet, basename='subscribes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'recipes/<int:id>/favorite',
                FavoriteViewSet,
                basename='favorite')
router.register(r'recipes/<int:id>/shopping_cart',
                ShoppingCartViewSet,
                basename='shopping_cart')
router.register(r'recipes/download_shopping_cart',
                ShoppingCartViewSet,
                basename='download_shopping_cart')

urlpatterns = [
        path('', include(router.urls)),
        path('', include('djoser.urls')),  # Работа с пользователями
        path(r'auth/', include('djoser.urls.authtoken')),  # Работа с токенами
]
