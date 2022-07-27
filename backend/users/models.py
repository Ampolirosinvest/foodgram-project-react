from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ADMIN = 'admin'
    GUEST = 'guest'
    USER = 'user'
    USER_ROLES = [
        (USER, 'user'),
        (GUEST, 'guest'),
        (ADMIN, 'admin'),
    ]
    username = models.CharField(
        'Логин',
        help_text='Логин',
        max_length=150,
        unique=True,
    )
    first_name = models.CharField(
        'Имя пользователя',
        help_text='Имя пользователя',
        max_length=150,
        unique=False,
    )
    last_name = models.CharField(
        'Фамилия пользователя',
        help_text='Фамилия пользователя',
        max_length=150,
        unique=False,
    )
    email = models.EmailField(
        'Электронная почта',
        help_text='Электронная почта пользователя',
        max_length=254,
        unique=True,
    )
    role = models.CharField(
        'Роль',
        help_text='Роль пользователя',
        max_length=150,
        blank=False,
        choices=USER_ROLES,
        default='user',
    )
    password = models.CharField(
        'Пароль',
        help_text='Пароль',
        max_length=150,
        unique=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-pk']

    def __str__(self):
        return self.username


class Subscription(models.Model):
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор'
    )

    @property
    def email(self):
        return self.following.email

    @property
    def username(self):
        return self.following.username

    @property
    def first_name(self):
        return self.following.first_name

    @property
    def last_name(self):
        return self.following.last_name

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('following', 'follower',),
                name='unique_subscribe',
            ),
        )

    def __str__(self):
        return f'{self.following} -> {self.follower}'
