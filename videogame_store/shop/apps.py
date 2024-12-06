from django.apps import AppConfig
from django.contrib.auth.models import Group, User

class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'

    def ready(self):
        Group.objects.get_or_create(name='Владелец')
        Group.objects.get_or_create(name='Модератор')
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(username='admin', email='admin@example.com', password='admin')
            print("Суперпользователь создан: admin/admin")