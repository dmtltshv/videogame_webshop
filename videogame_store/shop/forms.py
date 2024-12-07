from django import forms
from .models import CustomUser, Game, Category
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import check_password

class CustomUserCreationForm(UserCreationForm):
    secret_key = forms.CharField(
        label="Секретное слово (для модераторов или владельцев)",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    is_moderator = forms.BooleanField(
        label="Модератор?",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    is_owner = forms.BooleanField(
        label="Владелец?",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'avatar', 'password1', 'password2', 'is_moderator', 'is_owner', 'secret_key']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password1")
        confirm_password = cleaned_data.get("password2")

        # Проверка совпадения паролей
        if password != confirm_password:
            self.add_error('password2', "Пароли не совпадают.")

        # Проверка введенного секретного слова
        is_moderator = cleaned_data.get('is_moderator')
        is_owner = cleaned_data.get('is_owner')
        secret_key = cleaned_data.get('secret_key')

        if (is_moderator and secret_key != 'MODERATOR_SECRET') or (is_owner and secret_key != 'OWNER_SECRET'):
            if secret_key:
                self.add_error('secret_key', "Неверное секретное слово.")
        return cleaned_data

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'avatar']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

class PasswordResetForm(forms.Form):
    current_password = forms.CharField(
        label="Текущий пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )
    new_password = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )
    confirm_password = forms.CharField(
        label="Подтвердите новый пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get("current_password")
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        # Проверяем текущий пароль
        if self.user and not check_password(current_password, self.user.password):
            self.add_error('current_password', "Неверный текущий пароль.")

        # Проверяем совпадение нового пароля
        if new_password != confirm_password:
            self.add_error('confirm_password', "Пароли не совпадают.")

        return cleaned_data

class GameForm(forms.ModelForm):
    release_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), label='Дата выхода')

    class Meta:
        model = Game
        fields = ['title', 'description', 'price', 'category', 'image', 'release_date']
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'price': 'Цена',
            'category': 'Категория',
            'image': 'Изображение',
            'release_date': 'Дата выхода',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class GameFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        label="Поиск по названию",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название...'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label="Категория",
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label = "Выберите категорию...",
    )
    sort_by = forms.ChoiceField(
        required=False,
        label="Сортировать по",
        choices=[
            ('price_asc', 'Цена (возрастание)'),
            ('price_desc', 'Цена (убывание)'),
            ('title_asc', 'Название (А-Я)'),
            ('title_desc', 'Название (Я-А)'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )