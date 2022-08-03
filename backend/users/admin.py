from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from rest_framework.authtoken.admin import TokenAdmin
from users.forms import CustomUserCreationForm, CustomUserChangeForm
from users.models import CustomUser, Follow

TokenAdmin.raw_id_fields = ['user']


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = (
        'email', 'username', 'first_name', 'last_name', 'follows',
        'is_staff', 'is_active'
    )
    list_display_links = ('email', 'username')
    list_filter = ('is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password',
                           'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2',
                'username', 'is_staff', 'is_active', 'first_name', 'last_name'
            )
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author', 'folowing_count', 'folower_count')
    list_display_links = ('user',)
    fieldsets = (
        (None, {'fields': ('user', 'author')}),
    )
    search_fields = ('user__email', 'author__email')
    ordering = ('user', 'author',)
