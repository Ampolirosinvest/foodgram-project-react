from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from djoser.views import viewsets
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from rest_framework import filters, mixins
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)
from rest_framework.views import APIView

from api.filters import RecipeFilter, SearchIngrFilter
from api.mixins import RetrivelistViewSet
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAuthorOrAdminOrReadOnly
from recipes.models import (CountOfIngredient, Favorite, Ingredient, ListShop,
                            Recipe, Tag)
from users.models import Subscription, User

from .serializers import (AddRecipeSerializer, IngredientSerializer,
                          NewUserSerializer, RecipeListSerializer,
                          SmallRecipeSerializer,
                          SubscriptionCreateDeleteSerializer,
                          SubscriptionSerializer, TagSerializer)


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

    def get_serializer_class(self):
        """
        функция выбора сериалайзера изходя из вид запроса
        """
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return AddRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=('post', 'delete',),
            detail=True, permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """
        Метод `favorite` вызывает метод добавления или удаления рецепта
        из списка избранного.
        """
        if request.method == 'POST':
            return self.add_recipe(Favorite, request, pk)
        return self.delete_recipe(Favorite, request, pk)

    @action(methods=('post', 'delete',),
            detail=True, permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        """
        Метод `shopping_cart` вызывает метод добавления или удаления рецепта
        из списка покупок.
        """
        if request.method == 'POST':
            return self.add_recipe(ListShop, request, pk)
        return self.delete_recipe(ListShop, request, pk)

    def add_recipe(self, model, request, pk):
        """
        Метод `add_recipe` добавляет рецепт
        в список избранного или список покупок.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(recipe=recipe, user=request.user).exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        model.objects.create(recipe=recipe, user=request.user)
        serializer = SmallRecipeSerializer(recipe)
        return Response(data=serializer.data, status=HTTP_201_CREATED)

    def delete_recipe(self, model, request, pk):
        """
        Метод `delete_recipe` удаляет рецепт
        из списка избранного или списка покупок.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            model.objects.filter(
                user=request.user, recipe=recipe
            ).delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(status=HTTP_400_BAD_REQUEST)

    def canvas_method(self, listshop):
        """
        функция выгрузки списка покупок в PDF
        """
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
        for number, item in enumerate(listshop, start=1):
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


class NewUserViewSet(DjoserUserViewSet):
    """
    Вьюсет для работы с пользователями
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = NewUserSerializer
    pagination_class = LimitPageNumberPagination


class SubscriptionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Вьюсет для работы с отображением подписчиков
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering = ('following__first_name',)
    pagination_class = LimitPageNumberPagination
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return Subscription.objects.filter(follower=self.request.user)


class SubscriptionCreateDestroyView(APIView):
    """
    Вьюсет для удаления и добавления подписчиков
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        data = {'follower': request.user.id, 'following': id}
        serializer = SubscriptionCreateDeleteSerializer(
            data=data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)

    def delete(self, request, id):
        follower = request.user
        following = get_object_or_404(User, id=id)
        instance = Subscription.objects.filter(
            follower=follower,
            following=following)
        if instance.exists():
            instance.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'У вас нет подписки на этого автора!'},
            status=HTTP_400_BAD_REQUEST)
