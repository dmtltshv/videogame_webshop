from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import check_password


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(label="Имя", max_length=30, required=True)
    last_name = forms.CharField(label="Фамилия", max_length=30, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'avatar', 'first_name', 'last_name']

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