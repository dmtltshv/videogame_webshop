from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Order, Game

# Получаем вашу кастомную модель пользователя
User = get_user_model()

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')

class GameAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'category']
    search_fields = ['title', 'category']

    def has_change_permission(self, request, obj=None):
        return request.user.groups.filter(name='Модераторы').exists() or super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return request.user.groups.filter(name='Модераторы').exists() or super().has_delete_permission(request, obj)

admin.site.register(Game, GameAdmin)