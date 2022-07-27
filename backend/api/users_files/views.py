from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from djoser.views import viewsets
from rest_framework import filters, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)
from rest_framework.views import APIView

from api.titles.pagination import LimitPageNumberPagination
from users.models import Subscription, User

from .serializers import (NewUserSerializer,
                          SubscriptionCreateDeleteSerializer,
                          SubscriptionSerializer)


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
        if data['follower'] == data['following']:
            return Response(
                {'errors': 'Нельзя подписаться на себя'},
                status=HTTP_400_BAD_REQUEST)
        if Subscription.objects.filter(
            follower=data['follower'],
            following=data['following']
        ).exists():
            return Response(
                {'errors': 'Вы уже подписаны на данного пользователя'},
                status=HTTP_400_BAD_REQUEST)
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
                {'errors': 'У вас нет подписки на данного автора!'},
                status=HTTP_400_BAD_REQUEST)
