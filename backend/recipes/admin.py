from django.contrib import admin
from recipes.models import Basket, Component, FavourRecipe
from recipes.models import Product, Recipe, Tag


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    ordering = ('name',)


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ('product', 'amount',)
    list_filter = ('product__measurement_unit', 'recipe__tags',)
    search_fields = ('product__name',)
    ordering = ('product',)


class ComponentRecipeInline(admin.TabularInline):
    model = Component
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (ComponentRecipeInline,)
    readonly_fields = ('pub_date', 'in_favor_count', )
    fields = (
        'in_favor_count', 'pub_date', 'author', 'title', 'text',
        'picture', 'tags', 'cooking_time'
    )

    list_display = ('title', 'author', 'in_favor_count')
    list_display_links = ('title',)
    list_filter = ('tags',)
    search_fields = ('title', 'author__username', 'author__email',)
    ordering = ('pub_date',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(FavourRecipe)
class FavourRecipesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'recipes_count')
    list_display_links = ('user', )
    list_filter = ('recipe__tags', )
    fieldsets = (
        (None, {'fields': ('user', 'recipe')}),
    )
    search_fields = ('recipe__title', )
    ordering = ('user', )


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipes_count')
    list_display_links = ('user', )
    list_filter = ('recipe__tags', )
    fieldsets = (
        (None, {'fields': ('user', 'recipe')}),
    )
    search_fields = ('recipe__title', 'author__username', 'author__email', )
    ordering = ('user', )
