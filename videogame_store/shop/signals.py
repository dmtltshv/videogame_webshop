from django.contrib.auth.models import Group, User
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_groups(sender, **kwargs):
    # Создаем группу "Владелец"
    Group.objects.get_or_create(name='Владелец')
    # Создаем группу "Модератор"
    Group.objects.get_or_create(name='Модератор')

@receiver(post_migrate)
def create_admin_user(sender, **kwargs):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(username='admin', email='admin@example.com', password='admin')
        print("Суперпользователь создан: admin/admin")