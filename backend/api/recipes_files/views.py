from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import viewsets
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST)

from api.titles.filters import RecipeFilter, SearchIngrFilter
from api.titles.mixins import RetrivelistViewSet
from api.titles.pagination import LimitPageNumberPagination
from api.titles.permissions import IsAuthorOrAdminOrReadOnly
from recipes.models import (CountOfIngredient, Favorite, Ingredient, ListShop,
                            Recipe, Tag)

from .serializers import (AddRecipeSerializer, IngredientSerializer,
                          RecipeListSerializer, SmallRecipeSerializer,
                          TagSerializer)


class TagViewSet(RetrivelistViewSet):
    """
    Вьюсет для тегов
    """
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    http_method_names = ['get', ]


class IngredientViewSet(RetrivelistViewSet):
    """
    Вьюсет для ингридиентов
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SearchIngrFilter
    http_method_names = ['get', ]


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с рецептами
    """
    queryset = Recipe.objects.all()
    pagination_class = LimitPageNumberPagination
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', ]

    # выбор сериалайзера изходя из вид запроса
    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return AddRecipeSerializer

    # работа с рецептами
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = RecipeListSerializer(
            instance=serializer.instance,
            context={'request': self.request})
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        serializer = RecipeListSerializer(
            instance=serializer.instance,
            context={'request': self.request})
        return Response(
            serializer.data, status=HTTP_200_OK)

    # избранные рецепты
    def add_to_favorite(self, request, recipe):
        try:
            Favorite.objects.create(user=request.user, recipe=recipe)
        except IntegrityError:
            return Response(
                {'errors': 'Рецепт уже есть в избранном!'},
                status=HTTP_400_BAD_REQUEST)
        serializer = SmallRecipeSerializer(recipe)
        return Response(
            serializer.data,
            status=HTTP_201_CREATED)

    def delete_from_favorite(self, request, recipe):
        favorite = Favorite.objects.filter(user=request.user, recipe=recipe)
        if not favorite.exists():
            return Response(
                {'errors': 'Вы уже удалили этот рецепт из избранного!'},
                status=HTTP_400_BAD_REQUEST)
        favorite.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(methods=('post', 'delete',),
            detail=True, permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            return self.add_to_favorite(request, recipe)
        return self.delete_from_favorite(request, recipe)

    # список покупок
    def add_to_shopping_cart(self, request, recipe, shopping_cart):
        if shopping_cart.recipes.filter(pk__in=(recipe.pk,)).exists():
            return Response(
                {'errors': 'Нельзя подписаться дважды!'},
                status=HTTP_400_BAD_REQUEST)
        shopping_cart.recipes.add(recipe)
        serializer = SmallRecipeSerializer(recipe)
        return Response(
            serializer.data,
            status=HTTP_201_CREATED)

    def remove_from_shopping_cart(self, request, recipe, shopping_cart):
        if not shopping_cart.recipes.filter(pk__in=(recipe.pk,)).exists():
            return Response(
                {'errors': ('Нельзя удалить покупку,'
                 + 'так как ее нет в списке покупок')},
                status=HTTP_400_BAD_REQUEST)
        shopping_cart.recipes.remove(recipe)
        return Response(
            status=HTTP_204_NO_CONTENT)

    @action(methods=('post', 'delete',), detail=True)
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        shopping_cart = (ListShop.objects.get_or_create(user=request.user)[0])
        if request.method == 'POST':
            return self.add_to_shopping_cart(request, recipe, shopping_cart)
        return self.remove_from_shopping_cart(request, recipe, shopping_cart)

    # выгрузка спискапокупок в pdf
    def canvas_method(self, dictionary):
        begin_position_x, begin_position_y = 30, 730
        response = HttpResponse(
            content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.pdf"')
        canvas = Canvas(response, pagesize=A4)
        pdfmetrics.registerFont(TTFont('FreeSans', 'data/FreeSans.ttf'))
        canvas.setFont('FreeSans', 25)
        canvas.setTitle('Список покупок')
        canvas.drawString(begin_position_x,
                          begin_position_y + 40, 'Список покупок: ')
        canvas.setFont('FreeSans', 18)
        for number, item in enumerate(dictionary, start=1):
            if begin_position_y < 100:
                begin_position_y = 730
                canvas.showPage()
                canvas.setFont('FreeSans', 18)
            canvas.drawString(
                begin_position_x,
                begin_position_y,
                f'{number}: {item["ingredient__name"]} - '
                f'{item["ingredient_total"]}'
                f'{item["ingredient__measurement_unit"]}')
            begin_position_y -= 30
        canvas.showPage()
        canvas.save()
        return response

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = CountOfIngredient.objects.filter(
            recipe__in_shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(ingredient_total=Sum('amount'))
        return self.canvas_method(ingredients)
