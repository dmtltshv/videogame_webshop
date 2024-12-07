from django import forms
from .models import CustomUser, Game, Category
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import check_password

class CustomUserCreationForm(UserCreationForm):
    secret_key = forms.CharField(
        label="Секретное слово (для модераторов)",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'avatar', 'password1', 'password2', 'secret_key']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
        def clean_secret_key(self):
            secret_key = self.cleaned_data.get('secret_key')
            if secret_key and secret_key != 'easy':
                raise forms.ValidationError("Неверное секретное слово.")
            return secret_key

def clean(self):
    cleaned_data = super().clean()
    password = cleaned_data.get("password")
    confirm_password = cleaned_data.get("confirm_password")

    if password != confirm_password:
        self.add_error('confirm_password', "Пароли не совпадают")

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
    class Meta:
        model = Game
        fields = ['title', 'description', 'price', 'category', 'image', 'release_date']
        release_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
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