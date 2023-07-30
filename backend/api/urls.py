import djoser
from django.contrib.auth import login, logout
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import SubscribeViewSet, UserViewSet

from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    TagViewSet
)


app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register(r'users/set_password', UserViewSet, basename='set_password')
router_v1.register(r'users/me', UserViewSet, basename='me')
router_v1.register(r'users/(?P<user_id>\d+)/subscribes', SubscribeViewSet, basename='subscribes')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'tags', TagViewSet, basename='tag')
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartViewSet,
    basename='shopping_cart')



auth_path = [
    path(r'auth', include('djoser.urls')),
    # path(r'auth/', include('djoser.urls.authtoken')),
    path('auth/token/login', login, name='login'),
    path('auth/token/logout', logout, name='logout')
]

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include(auth_path))
]
