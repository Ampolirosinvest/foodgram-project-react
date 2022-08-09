from django.db import models
from django_filters.rest_framework import (AllValuesMultipleFilter,
                                           BooleanFilter, CharFilter,
                                           FilterSet)

from recipes.models import Ingredient, ListShop, Recipe


class SearchIngrFilter(FilterSet):
    name = CharFilter(method='search_by_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def search_by_name(self, queryset, name, value):
        if not value:
            return queryset
        start_with_queryset = (
            queryset.filter(name__istartswith=value).annotate(
                order=models.Value(0, models.IntegerField())
            )
        )
        contain_queryset = (
            queryset.filter(name__icontains=value).exclude(
                pk__in=(ingredient.pk for ingredient in start_with_queryset)
            ).annotate(
                order=models.Value(1, models.IntegerField())
            )
        )
        return start_with_queryset.union(contain_queryset).order_by('order')


class RecipeFilter(FilterSet):
    is_favorited = BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='get_is_in_shopping_cart')
    tags = AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('author', 'is_in_shopping_cart',)

    def get_is_favorited(self, queryset, name, value):
        if not value:
            return queryset
        favorites = self.request.user.favorites.all()
        return queryset.filter(
            pk__in=(favorite.recipe.pk for favorite in favorites)
        )

    def get_is_in_shopping_cart(self, queryset, name, value):
        if bool(value) and not self.request.user.is_anonymous:
            return queryset.filter(in_shopping_cart__user=self.request.user)
        return queryset.exclude(in_shopping_cart__user=self.request.user)
