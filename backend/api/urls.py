import djoser
from django.contrib.auth import login, logout
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import SubscribeViewSet, UserViewSet

from api.views import (
    FavoriteViewSet,
    IngredientViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    TagViewSet
)

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('users/set_password', UserViewSet, basename='set_password')
router.register('users/me', UserViewSet, basename='me')
router.register(r'users/(?P<id>\d+)/subscribes', SubscribeViewSet, basename='subscribes')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tag')
router.register(
    r'recipes/(?P<id>\d+)/shopping_cart',
    ShoppingCartViewSet,
    basename='shopping_cart')
router.register('recipes/download_shopping_cart',
    ShoppingCartViewSet,
    basename='download_shopping_cart')
router.register(
    r'recipes/(?P<id>\d+)/favorite',
    FavoriteViewSet,
    basename='favorite')

# auth_path = [
#     #
#     # path(r'auth/', ),
#     path('auth/token/login', login, name='login'),
#     path('auth/token/logout', logout, name='logout')
# ]

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.authtoken'))
]
