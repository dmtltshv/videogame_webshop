from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model

# Получаем текущую модель пользователя
User = get_user_model()

@receiver(post_migrate)
def create_groups_and_admin_user(sender, **kwargs):
    # Создание групп
    Group.objects.get_or_create(name='Владелец')
    Group.objects.get_or_create(name='Модератор')

    # Создание суперпользователя, если его нет
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(username='admin', email='admin@example.com', password='admin')
        print("Суперпользователь создан: admin/admin")