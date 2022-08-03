from django.conf import settings
from django.contrib import admin
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from pytils.translit import slugify

User = settings.AUTH_USER_MODEL


class Product(models.Model):
    name = models.CharField(
        max_length=150,
        verbose_name='Название продукта'
    )
    measurement_unit = models.CharField(
        max_length=150,
        verbose_name='Единица измерения'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit',),
                name='unique_product_unit'
            ),
        )
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Component(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='components',
        verbose_name='Ингридиент для рецепта'
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='recipe_components',
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество продукта',
        default=1,
        validators=(
            MinValueValidator(
                settings.MIN_AMOUNT_VALUE, message=settings.MIN_AMOUNT_MESSAGE
            ),
        )
    )

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'

    def __str__(self):
        return (f'{self.product.name} - {self.amount} '
                f'({self.product.measurement_unit})')


class Tag(models.Model):
    name = models.CharField(
        unique=True,
        max_length=20,
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=7,
        validators=[
            RegexValidator(
                regex=r'#[a-f\d]{6}',
                message='Укажите цвет в HEX кодировке.'
            )
        ],
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        unique=True,
        blank=True, null=True,
        verbose_name='Идентификатор'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.color})'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:20]
        return super().save(*args, **kwargs)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    picture = models.ImageField(
        upload_to='images/',
        verbose_name='Картинка блюда'
    )
    text = models.TextField(
        max_length=3000,
        verbose_name='Описание рецепта'
    )
    components = models.ManyToManyField(
        Product,
        through='Component',
        related_name='recipes',
        verbose_name='Ингридиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='recipes',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        validators=(
            MinValueValidator(
                settings.MIN_COOKING_VALUE,
                message=settings.MIN_COOKING_MESSAGE
            ),
        ),
        verbose_name='Время на приготовление (мин)'
    )
    pub_date = pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.title[:20]}, {self.author.username}'

    @property  # type: ignore
    @admin.display(
        description='Добавлен в избранное раз',
    )
    def in_favor_count(self):
        return self.favourite.count()


class FavourRecipe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favour_recipes',
        verbose_name='Владелец списка избранного'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favourite',
        verbose_name='Избранные рецепты'
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_recipe_favour',
            ),
        )

    def __str__(self):
        return (f'{self.user.username}, '
                f'в избранном рецептов: {self.recipes_count}')

    @property
    @admin.display(
        description='Рецептов в избранном',
    )
    def recipes_count(self):
        return self.user.favour_recipes.count()


class Basket(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='basket',
        verbose_name='Список покупок'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='basket_recipes',
        verbose_name='Рецепты в списке покупок'
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return (f'{self.user.username}, '
                f'в списке покупок: {self.recipes_count}')

    @property
    @admin.display(
        description='Рецептов к покупке',
    )
    def recipes_count(self):
        return self.user.basket.count()
