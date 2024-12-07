# context_processors.py
def user_roles(request):
    if request.user.is_authenticated:
        return {
            'is_owner': request.user.groups.filter(name='Владелец').exists(),
            'is_moderator': request.user.groups.filter(name='Модератор').exists(),
        }
    return {}