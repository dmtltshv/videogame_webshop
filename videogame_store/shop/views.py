from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm as RegistrationForm
from .forms import ProfileUpdateForm, PasswordResetForm, GameForm, GameFilterForm
from django.db.models import Sum
from .models import Game, Category, Cart, Order, OrderItem, Favorite

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            secret_word = form.cleaned_data.get('secret_word')
            if secret_word == 'MODERATOR_SECRET':
                moderator_group, _ = Group.objects.get_or_create(name='Модератор')
                user.groups.add(moderator_group)
            elif secret_word == 'OWNER_SECRET':
                owner_group, _ = Group.objects.get_or_create(name='Владелец')
                user.groups.add(owner_group)

            login(request, user)
            messages.success(request, "Вы успешно зарегистрированы!")
            return redirect('shop/game_list')

    else:
        form = RegistrationForm()

    return render(request, 'shop/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'shop/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('game_list')

    def form_valid(self, form):
        messages.success(self.request, 'Вы успешно вошли в аккаунт!')
        return super().form_valid(form)

def logout_view(request):
    logout(request)
    return redirect('game_list')  # Перенаправление после выхода

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/profile.html', {'orders': orders})

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш профиль был успешно обновлён.')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'shop/profile_edit.html', {'form': form})

@login_required
def reset_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST, user=request.user)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            # Устанавливаем новый пароль
            request.user.password = make_password(new_password)
            request.user.save()
            messages.success(request, "Пароль успешно изменён.")
            return redirect('game_list')
    else:
        form = PasswordResetForm(user=request.user)

    return render(request, 'shop/reset_password.html', {'form': form})

def is_moderator(user):
    # Проверка, является ли пользователь модератором
    return user.is_authenticated and user.groups.filter(name='Модератор').exists()


def game_list(request):
    games = Game.objects.all()
    form = GameFilterForm(request.GET)
    user = request.user

    context = {}

    # Обработка избранных игр для авторизованных пользователей
    if user.is_authenticated:
        # Получаем избранные игры для авторизованного пользователя
        favorite_games = user.favorites.all()  # или user.favorites.values_list('game', flat=True)
        context['favorite_games'] = favorite_games
    else:
        context['favorite_games'] = []  # Если пользователь не авторизован, передаем пустой список

    # Обработка фильтров
    if form.is_valid():
        # Фильтрация по названию
        search_query = form.cleaned_data.get('search')
        if search_query:
            games = games.filter(title__icontains=search_query)

        # Фильтрация по категории
        category = form.cleaned_data.get('category')
        if category:
            games = games.filter(category=category)

        # Сортировка
        sort_by = form.cleaned_data.get('sort_by')
        if sort_by == 'price_asc':
            games = games.order_by('price')
        elif sort_by == 'price_desc':
            games = games.order_by('-price')
        elif sort_by == 'title_asc':
            games = games.order_by('title')
        elif sort_by == 'title_desc':
            games = games.order_by('-title')

    # Проверка статуса модератора
    is_moderator_status = is_moderator(request.user)

    # Передаем все данные в контекст
    context.update({
        'games': games,
        'form': form,
        'is_moderator': is_moderator_status,  # Информация о том, является ли пользователь модератором
    })

    return render(request, 'shop/game_list.html', context)

# Панель управления
@login_required
@user_passes_test(is_moderator)
def moderator_panel(request):
    games = Game.objects.all()
    return render(request, 'shop/moderator_panel.html', {'games': games})

# Добавить игру
@login_required
@user_passes_test(is_moderator)
def add_game(request):
    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES)
        if form.is_valid():
            game = form.save(commit=False)
            game.save()
            messages.success(request, "Игра успешно добавлена!")
            return redirect('moderator_panel')
    else:
        form = GameForm()
    return render(request, 'shop/add_game.html', {'form': form})

# Редактировать игру
@login_required
@user_passes_test(is_moderator)
def edit_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES, instance=game)
        if form.is_valid():
            form.save()
            messages.success(request, "Игра успешно обновлена!")
            return redirect('moderator_panel')
    else:
        form = GameForm(instance=game)
    return render(request, 'shop/edit_game.html', {'form': form, 'game': game})

# Удалить игру
@login_required
@user_passes_test(is_moderator)
def delete_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    game.delete()
    messages.success(request, "Игра успешно удалена!")
    return redirect('moderator_panel')

def add_to_cart(request, game_id):
    if request.user.is_authenticated:
        game = get_object_or_404(Game, id=game_id)
        cart_item, created = Cart.objects.get_or_create(user=request.user, game=game)
        if not created:
            cart_item.quantity += 1
        cart_item.save()
        return redirect('cart')
    return redirect('login')

def view_cart(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(item.total_price() for item in cart_items)
        return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total_price': total_price})
    else:
        return redirect('login')

def remove_from_cart(request, cart_item_id):
    Cart.objects.filter(id=cart_item_id, user=request.user).delete()
    return redirect('cart')

def place_order(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items:
            return redirect('cart')

        order = Order.objects.create(user=request.user)
        total_price = 0

        for item in cart_items:
            total_price += item.quantity * item.game.price
            OrderItem.objects.create(
                order=order,
                game=item.game,
                quantity=item.quantity,
                price=item.game.price
            )
            item.delete()

        order.total_price = total_price
        order.save()
        return redirect('order_detail', order_id=order.id)

    return redirect('login')

@login_required
@user_passes_test(is_moderator)
def moderator_orders(request):
    orders = Order.objects.all().order_by('-created_at')  # Все заказы, отсортированные по дате
    return render(request, 'shop/moderator_orders.html', {'orders': orders})

@login_required
@user_passes_test(is_moderator)
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):  # Проверка, что статус корректный
            order.status = new_status
            order.save()
    return redirect('moderator_orders')

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})

@login_required
def add_to_favorites(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    Favorite.objects.get_or_create(user=request.user, game=game)
    return redirect('game_list')  # Замените на имя вашей страницы игр

@login_required
def remove_from_favorites(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    Favorite.objects.filter(user=request.user, game=game).delete()
    return redirect('game_list')

def is_owner(user):
    return user.groups.filter(name='Владелец').exists()

@login_required
@user_passes_test(is_owner)
def owner_dashboard(request):
    # Примерные данные для статистики
    user_count = CustomUser.objects.count()
    total_profit = Order.objects.aggregate(total=Sum('total_price'))['total'] or 0
    balance_profit = total_profit * 0.8  # Пример чистой прибыли (80%)

    context = {
        'user_count': user_count,
        'total_profit': total_profit,
        'balance_profit': balance_profit,
    }
    return render(request, 'shop/owner_dashboard.html', context)