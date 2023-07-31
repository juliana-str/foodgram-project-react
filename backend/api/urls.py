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
router.register(r'users', UserViewSet, basename='users')
router.register(r'users/me', UserViewSet, basename='me')
router.register(r'users/set_password', UserViewSet, basename='set_password')
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


# auth_path = [
#     path('auth/token/login', login, name='login'),
#     path('auth/token/logout', logout, name='logout')
# ]

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),

]
