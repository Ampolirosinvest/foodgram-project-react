
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import Recipe
from users.models import Subscription, User


class NewUserSerializer(UserSerializer):
    """
    Сериалайзер для отображения пользователей
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        user = request.user
        return Subscription.objects.filter(
            following=obj,
            follower=user,
        ).exists()


class NewUserCreateSerializer(UserCreateSerializer):
    """
    Сериалайзер для создания пользователей
    """
    pass


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для краткого отображения рецептов
    """

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time'
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для отображения подписчиков
    """
    email = serializers.ReadOnlyField()
    id = serializers.SerializerMethodField(read_only=True)
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]

    def get_id(self, obj):
        return obj.following.id

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        user = request.user
        return Subscription.objects.filter(
            following=obj.following,
            follower=user
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('limit')
        if limit is not None:
            queryset = Recipe.objects.filter(
                author=obj.following
            )[:int(limit)]
        else:
            queryset = Recipe.objects.filter(author=obj.following)
        return RecipeMinifiedSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.following).count()


class SubscriptionCreateDeleteSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для добавления и удаления подписчиков
    """

    class Meta:
        model = Subscription
        fields = [
            'following',
            'follower'
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SubscriptionSerializer(instance, context=context).data
