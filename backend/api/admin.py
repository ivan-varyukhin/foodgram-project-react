from django.contrib import admin
from django.contrib.auth.models import Group

admin.site.site_header = 'Администрирование Foodgram'
admin.site.index_title = 'Добро пожаловать в Администрирование сайта'
admin.site.site_title = 'FoodGram Административный портал'


admin.site.unregister(Group)
