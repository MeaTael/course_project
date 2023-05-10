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

    username = UsernameField(widget=forms.TextInput(
        attrs={
            'style': 'border: 3px solid orangered;'
                     'border-radius: 10px;'
                     'font-size: 14px;'
                     'line-height: 16px;'
                     'padding-left: 10px;'
        }),
        label=False)

    email = forms.EmailField(widget=forms.TextInput(
        attrs={
            'style': 'border: 3px solid orangered;'
                     'border-radius: 10px;'
                     'font-size: 14px;'
                     'line-height: 16px;'
                     'padding-left: 10px;'
        }
    ), label=False)

    class Meta:
        model = User
        fields = ["username", "email"]


class ProfileUpdateForm(forms.ModelForm):

    image = forms.FileField(widget=forms.FileInput(
        attrs={
            'style': 'border: 3px solid orangered;'
                     'border-radius: 10px;'
                     'font-size: 14px;'
                     'line-height: 16px;'
                     'padding-left: 10px;'
            }), label=False)

    class Meta:
        model = Profile

        fields = ['image']


class LearningWords(forms.Form):
    def __init__(self, *args, **kwargs):
        super(LearningWords, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].label = False

    word = forms.CharField(widget=TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите перевод слова',
        'style': 'border: 3px solid orangered;'
                 'border-radius: 10px;'
                 'font-size: 20px;'
                 'line-height: 25px;'
                 'width: 70%;'
                 'margin-left: 15%;'
    }))

    word_to_check = ""
    error_message = ""

    def set_word_to_check(self, word_to_check):
        self.word_to_check = word_to_check

    def set_error_message(self, message):
        self.error_message = message