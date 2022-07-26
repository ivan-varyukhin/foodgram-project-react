# Generated by Django 2.2.16 on 2022-07-29 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20220729_1506'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='favourrecipe',
            name='уникальность подписки пользователя на рецепт',
        ),
        migrations.RemoveConstraint(
            model_name='product',
            name='уникальность пары продукт - единица измерения',
        ),
        migrations.AddConstraint(
            model_name='favourrecipe',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_recipe_favour'),
        ),
        migrations.AddConstraint(
            model_name='product',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='unique_product_unit'),
        ),
    ]
