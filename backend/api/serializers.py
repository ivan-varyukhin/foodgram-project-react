from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from recipes.models import FavourRecipe, Component, Product, Recipe, Tag
from users.models import CustomUser, Follow


class TagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=200, read_only=True)
    color = serializers.CharField(max_length=7, read_only=True)
    slug = serializers.SlugField(max_length=200, read_only=True)

    class Meta:
        model = Tag
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    measurement_unit = serializers.CharField(max_length=200)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('id', )


class ComponentSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='product.id')
    name = serializers.ReadOnlyField(source='product.name')
    measurement_unit = serializers.ReadOnlyField(
        source='product.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = Component
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = (
            UniqueTogetherValidator(
                queryset=Component.objects.all(),
                fields=('product', 'recipe')
            ),
        )
        read_only_fields = ('id', )


class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, allow_blank=False)
    username = serializers.CharField(max_length=150, allow_blank=False)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
        if user and user.is_authenticated:
            return Follow.objects.filter(user=user, author=obj.id).exists()
        return False


class RecipeWriteSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='title')
    image = Base64ImageField(
        source='picture',
        max_length=None, use_url=True
    )
    ingredients = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        source='components'
    )
    tags = serializers.ListField(
        child=serializers.SlugRelatedField(
            slug_field='id',
            queryset=Tag.objects.all(),
        ),
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags',
            'image', 'name', 'text', 'cooking_time',
        )

    def validate(self, data):
        if data['cooking_time'] < settings.MIN_COOKING_VALUE:
            raise serializers.ValidationError(
                settings.MIN_COOKING_MESSAGE
            )

        if not data['tags']:
            raise serializers.ValidationError(
                'Ошибка: Создание рецепта без тега невозможно'
            )
        if len(data['tags']) != len(set(data['tags'])):
            raise serializers.ValidationError(
                'Ошибка: Тег для рецепта указывается единожды'
            )

        for tag in data['tags']:
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError(
                    f'Ошибка: Тега с указанным id = {tag.id} не существует'
                )

        if not data['components']:
            raise serializers.ValidationError(
                'Ошибка: Невозможно создание рецепта без ингредиента'
            )
        compnt_ids = []
        for component in data['components']:
            cur_id, cur_amount = component['id'], component['amount']
            if not Product.objects.filter(id=cur_id).exists():
                raise serializers.ValidationError(
                    'Ошибка: Ингредиента '
                    f'с указанным id = {cur_id} не существует')
            if int(cur_amount) < settings.MIN_AMOUNT_VALUE:
                raise serializers.ValidationError(settings.MIN_AMOUNT_MESSAGE)
            compnt_ids.append(cur_id)
        if len(compnt_ids) != len(set(compnt_ids)):
            raise serializers.ValidationError(
                'Ошибка: Ингредиент для рецепта указывается единожды'
            )
        return data

    def add_components_and_tags(self, recipe, validated_data):
        components, tags = (
            validated_data.pop('components'), validated_data.pop('tags')
        )
        for component in components:
            _, created = Component.objects.get_or_create(
                product=get_object_or_404(Product, id=component['id']),
                amount=component['amount'],
                recipe=recipe
            )
            if not created:
                raise serializers.ValidationError(
                    'Ошибка: Ингредиент для рецепта указывается единожды'
                )
        recipe.tags.set(tags)
        return recipe

    def create(self, validated_data):
        m2m_data = {}
        m2m_data['components'] = validated_data.pop('components')
        m2m_data['tags'] = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        return self.add_components_and_tags(recipe, m2m_data)

    def update(self, instance, validated_data):
        instance.components.clear()
        instance.tags.clear()
        instance = self.add_components_and_tags(instance, validated_data)
        return super().update(instance, validated_data)


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class RecipeReadSerializer(DynamicFieldsModelSerializer):
    name = serializers.CharField(source='title')
    image = Base64ImageField(max_length=None, use_url=True, source='picture')
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(
        source='picture',
        max_length=None, use_url=True
    )
    ingredients = ComponentSerializer(
        many=True, source='recipe_components',
        read_only=True
    )
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_user(self):
        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
        return user

    def get_is_favorited(self, obj):
        user = self.get_user()
        if user and user.is_authenticated:
            return obj.favourite.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.get_user()
        if user and user.is_authenticated:
            return obj.basket_recipes.exists()
        return False


class FavouriteSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
        required=False
    )
    recipe = serializers.SlugRelatedField(
        slug_field='recipe_id', read_only=True,
        required=False
    )

    class Meta:
        model = FavourRecipe
        fields = ('user', 'recipe')

    def validate(self, data):
        user = self.context['request'].user
        recipe_id = self.context.get('view').kwargs.get('recipe_id')

        if FavourRecipe.objects.filter(
            user=user.id, recipe=recipe_id
        ).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже в избранном.')
        return data


class SubscribeSerializer(serializers.ModelSerializer):
    email = serializers.CharField(
        source='author.email',
        required=False
    )
    id = serializers.IntegerField(
        source='author.id',
        required=False
    )
    username = serializers.CharField(
        source='author.username',
        required=False
    )
    first_name = serializers.CharField(
        source='author.first_name',
        required=False
    )
    last_name = serializers.CharField(
        source='author.last_name',
        required=False
    )
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    recipe_fields = ('id', 'name', 'image', 'cooking_time')

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        is_subscribed = Follow.objects.filter(
            user=obj.user, author=obj.author).exists()
        return is_subscribed

    def get_recipes(self, obj):
        request = self.context['request']
        recipes_per_user = None
        if 'recipes_limit' in request.query_params:
            recipes_per_user = int(request.query_params['recipes_limit'])
        queryset = Recipe.objects.filter(
            author=obj.author
        )[:recipes_per_user]
        serializer = RecipeReadSerializer(queryset, many=True,
                                          fields=self.recipe_fields)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()
