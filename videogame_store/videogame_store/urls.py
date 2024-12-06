from django.contrib import admin
from django.urls import path
from shop import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from shop.views import CustomLoginView
from .views import owner_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.game_list, name='game_list'),
    path('cart/', views.view_cart, name='cart'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile_edit/', views.profile_edit, name='profile_edit'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('moderator-panel/', views.moderator_panel, name='moderator_panel'),
    path('add-game/', views.add_game, name='add_game'),
    path('edit-game/<int:game_id>/', views.edit_game, name='edit_game'),
    path('delete-game/<int:game_id>/', views.delete_game, name='delete_game'),
    path('add-to-favorites/<int:game_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('remove-from-favorites/<int:game_id>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('add-to-cart/<int:game_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('place-order/', views.place_order, name='place_order'),
    path('moderator-orders/', views.moderator_orders, name='moderator_orders'),
    path('update-order/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('owner-dashboard/', owner_dashboard, name='owner_dashboard'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)