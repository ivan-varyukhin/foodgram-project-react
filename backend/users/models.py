from django.contrib import admin
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, username, **extra_fields):
        if not email:
            raise ValueError('Необходимо указать Email')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if not extra_fields.get('is_staff'):
            raise ValueError(
                'Для суперпользователя обязательно значение is_staff=True'
            )
        if not extra_fields.get('is_superuser'):
            raise ValueError(
                'Для суперпользователя обязательно значение is_superuser=True'
            )
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.EmailField(
        unique=True,
        db_index=True,
        max_length=150,
        verbose_name='Email'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        verbose_name='Логин'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль'
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name='Администратор'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
        'password'
    ]

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
        constraints = (
            models.UniqueConstraint(
                fields=('username', 'email',),
                name='unique_user_email'
            ),
        )

    def __str__(self):
        return self.username

    @property
    @admin.display(
        description='Подписан на',
    )
    def follows(self):
        return self.follower.count()

    @property
    def is_not_active(self):
        return (not self.is_active)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор рецепта',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author',), name='unique_follower'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='forbidden_self_follow'
            ),
        )
        ordering = ('author',)
        verbose_name = 'Подписка пользователя'
        verbose_name_plural = 'Подписки пользователей'

    def __str__(self):
        return (f'Подписчик {self.user.username[:15]}'
                f' на автора {self.author.username[:15]}')

    @property
    @admin.display(
        description='Имеет подписчиков',
    )
    def folower_count(self):
        return self.user.following.count()

    @property
    @admin.display(
        description='Подписан на',
    )
    def folowing_count(self):
        return self.user.follower.count()
