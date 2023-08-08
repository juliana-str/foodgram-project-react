from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FavoriteViewSet,
    IngredientViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    SubscribeViewSet,
    TagViewSet,
    UserViewSet
)

app_name = 'api'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
# router.register(r'users/<int:id>/subscribes',
#                 SubscribeViewSet, basename='subscribes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')
# router.register(r'recipes/<int:id>/favorite',
#                 FavoriteViewSet, basename='favorite')
# router.register(r'recipes/<int:id>/shopping_cart',
#                 ShoppingCartViewSet, basename='shopping_cart')

urlpatterns = [
        path('', include(router.urls)),
        path('', include('djoser.urls')),
        path(r'auth/', include('djoser.urls.authtoken')),
]
