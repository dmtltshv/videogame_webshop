from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Order, Game

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass

def setup_moderator_group():
    moderator_group, created = Group.objects.get_or_create(name='Модераторы')
    game_ct = ContentType.objects.get_for_model(Game)

    # Добавление прав для управления играми
    permissions = Permission.objects.filter(content_type=game_ct, codename__in=[
        'add_game', 'change_game', 'delete_game'
    ])
    moderator_group.permissions.set(permissions)

setup_moderator_group()

class GameAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'category']
    search_fields = ['title', 'category']

    def has_change_permission(self, request, obj=None):
        return request.user.groups.filter(name='Модераторы').exists() or super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return request.user.groups.filter(name='Модераторы').exists() or super().has_delete_permission(request, obj)

admin.site.register(Game, GameAdmin)