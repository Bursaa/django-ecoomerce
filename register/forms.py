from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django import forms
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=200, required=False)
    last_name = forms.CharField(max_length=200, required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']