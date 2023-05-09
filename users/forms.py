from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from .models import Profile
from django.forms import TextInput


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = UsernameField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Логин',
            'style': 'border: 3px solid orangered;'
                     'border-radius: 10px;'
                     'font-size: 14px;'
                     'line-height: 16px;'
                     'padding-left: 10px;'
        }),
        label=False)
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Пароль',
            'style': 'border: 3px solid orangered;'
                     'border-radius: 10px;'
                     'font-size: 14px;'
                     'line-height: 16px;'
                     'padding-left: 10px;'
        }),
        label=False)


class UserRegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].label = False

    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email',
        'style': 'border: 3px solid orangered;'
                 'border-radius: 10px;'
                 'font-size: 14px;'
                 'line-height: 16px;'
                 'padding-left: 10px;'
    }))

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Пароль',
        'style': 'border: 3px solid orangered;'
                 'border-radius: 10px;'
                 'font-size: 14px;'
                 'line-height: 16px;'
                 'padding-left: 10px;'
    }))

    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Повторите пароль',
        'style': 'border: 3px solid orangered;'
                 'border-radius: 10px;'
                 'font-size: 14px;'
                 'line-height: 16px;'
                 'padding-left: 10px;'
    }))

    class Meta:
        model = User
        fields = ['username']

        widgets = {
            "username": TextInput(attrs={
                "placeholder": "Логин"
            })
        }


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile

        fields = ['image']


class LearningWords(forms.Form):
    word = forms.CharField()
    word_to_check = ""
    error_message = ""

    def set_word_to_check(self, word_to_check):
        self.word_to_check = word_to_check

    def set_error_message(self, message):
        self.error_message = message
