from django.shortcuts import render
from .models import Game, Category
from django.shortcuts import redirect
from .models import Cart
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from django.shortcuts import get_object_or_404
from .forms import SellerRegistrationForm
from .forms import ReviewForm
from .models import SellerProfile, Review

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

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'shop/register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'shop/profile.html')

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

@login_required
def register_seller(request):
    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST)
        if form.is_valid():
            seller_profile = form.save(commit=False)
            seller_profile.user = request.user
            seller_profile.save()
            return redirect('seller_dashboard')
    else:
        form = SellerRegistrationForm()
    return render(request, 'shop/register_seller.html', {'form': form})

@login_required
def seller_dashboard(request):
    if not hasattr(request.user, 'seller_profile') or not request.user.seller_profile.is_active:
        return redirect('register_seller')  # Перенаправляем на регистрацию

    games = Game.objects.filter(seller=request.user)
    orders = OrderItem.objects.filter(game__in=games)

    return render(request, 'shop/seller_dashboard.html', {
        'games': games,
        'orders': orders,
    })

@login_required
def add_review(request, store_id):
    store = get_object_or_404(SellerProfile, id=store_id, is_active=True)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.seller = store
            review.user = request.user
            review.save()
            return redirect('store_detail', store_id=store.id)
    else:
        form = ReviewForm()
    return render(request, 'shop/add_review.html', {'form': form, 'store': store})

def store_list(request):
    # Получаем минимальный рейтинг из GET-запроса
    min_rating = request.GET.get('min_rating', 0)

    # Фильтруем магазины по рейтингу
    stores = SellerProfile.objects.filter(is_active=True)
    filtered_stores = [store for store in stores if store.average_rating() >= float(min_rating)]

    # Передаем минимальный рейтинг в контекст
    return render(request, 'shop/store_list.html', {
        'stores': filtered_stores,
        'min_rating': min_rating,
    })