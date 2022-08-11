from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, NewUserViewSet, RecipeViewSet,
                    SubscriptionCreateDestroyView, SubscriptionViewSet,
                    TagViewSet)

app_name = 'api'

router = DefaultRouter()
router.register(r'users/subscriptions', SubscriptionViewSet,
                basename='subscriptions')
router.register(r'users', NewUserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include(router.urls)),
    path(
        'users/<int:id>/subscribe/',
        SubscriptionCreateDestroyView.as_view(),
        name='subscribe'
    ),
    path('auth/', include('djoser.urls.authtoken')),
]
