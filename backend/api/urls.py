import djoser
from django.contrib.auth import login, logout
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet

from api.views import (
    RecipeViewSet,
    RecipeListViewSet,
    IngredientViewSet,
    TagViewSet,
    ShoppingCartViewSet
)


app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register(r'ingredients', IngredientViewSet, basename='recipes')
router_v1.register(r'recipes/(?P<recipe_id>\d+)', RecipeViewSet, basename='recipes')
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart/',
    ShoppingCartViewSet,
    basename='shopping_cart')
router_v1.register(r'tags/(?P<tags_id>\d+)', TagViewSet, basename='tag')


auth_path = [
    # path(r'v1/', include('djoser.urls')),
    # path(r'v1/token/login', include('djoser.urls.authtoken'))
    path('auth/token/login', login, name='login'),
    path('auth/token/logout', logout, name='logout')
]


urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/', include(auth_path))
]
