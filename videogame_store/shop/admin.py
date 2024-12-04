from django.contrib import admin
from .models import Game, Category

admin.site.register(Category)
admin.site.register(Game)