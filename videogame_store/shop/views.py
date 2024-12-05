from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm as RegistrationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import ProfileUpdateForm, PasswordResetForm, GameForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import user_passes_test

from .models import Game, Category, Cart, Order, OrderItem

def game_list(request):
    category_id = request.GET.get('category')
    query = request.GET.get('q')

    games = Game.objects.all()
    if category_id:
        games = games.filter(category_id=category_id)
    if query:
        games = games.filter(title__icontains=query)

    categories = Category.objects.all()
    return render(request, 'shop/game_list.html', {'games': games, 'categories': categories})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            secret_key = form.cleaned_data.get('secret_key')
            user.save()

            # Назначение группы "Модератор", если введено секретное слово
            if secret_key == 'MODERATOR_SECRET':
                moderator_group, created = Group.objects.get_or_create(name='Модераторы')
                user.groups.add(moderator_group)

            messages.success(request, "Регистрация прошла успешно.")
            login(request, user)
            return redirect('game_list')
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
    return render(request, 'shop/profile.html')

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
    return user.groups.filter(name='Модераторы').exists()

def game_list(request):
    games = Game.objects.all()
    context = {
        'games': games,
        'is_moderator': is_moderator(request.user) if request.user.is_authenticated else False
    }
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
            game.seller = request.user
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
        game = Game.objects.get(id=game_id)
        cart_item, created = Cart.objects.get_or_create(user=request.user, game=game)
        if not created:
            cart_item.quantity += 1
        cart_item.save()
        return redirect('cart')
    else:
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
            return redirect('cart')  # Если корзина пуста, возвращаем на страницу корзины

        # Создаем заказ
        order = Order.objects.create(user=request.user)
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                game=item.game,
                quantity=item.quantity,
                price=item.game.price
            )
            item.delete()  # Удаляем элемент из корзины после переноса в заказ
        return redirect('order_detail', order_id=order.id)

    return redirect('login')

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/profile.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})


