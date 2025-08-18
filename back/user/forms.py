from django import forms
from allauth.account.forms import SignupForm
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import *


class AvatarForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar']

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=65,
        label="Имя пользователя",
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'})
    )
    password = forms.CharField(
        max_length=65,
        widget=forms.PasswordInput,
        label="Пароль"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, value in self.fields.items():
            value.widget.attrs['placeholder'] = value.label

class ChangeEmailForm(forms.Form):
    new_email = forms.EmailField(label="Новая почта")

# class RegisterForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for _, value in self.fields.items():
#             value.widget.attrs['placeholder'] = value.label

# class SignupForm(SignupForm):
#     agree_to_terms = forms.BooleanField(
#         required=True,
#         label=mark_safe(
#             'Я соглашаюсь с <a href="/privacy-policy/" target="_blank">Политикой конфиденциальности</a> '
#             'и <a href="/terms/" target="_blank">Пользовательским соглашением</a>'
#         )
#     )

#     def clean_agree_to_terms(self):
#         agreed = self.cleaned_data.get("agree_to_terms")
#         if not agreed:
#             raise ValidationError("Вы должны принять условия, чтобы зарегистрироваться.")
#         return agreed

#     def save(self, request):
#         user = super().save(request)
#         return user