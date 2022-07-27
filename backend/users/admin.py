from django.contrib.admin import ModelAdmin, register

from .models import Subscription, User


@register(User)
class UserAdmin(ModelAdmin):
    list_display = ('pk', 'username')
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')


@register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = ('pk', 'following', 'follower')
    search_fields = ('following',)
