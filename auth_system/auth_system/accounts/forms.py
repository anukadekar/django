from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class SignUpForm(UserCreationForm) :
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())

    class Meta :
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class PasswordResetRequestForm(forms.Form) :
    username = forms.CharField(label="Username", max_length=15)
    email = forms.CharField(label="Email", max_length=254)


class ChangePasswordForm(forms.Form) :
    old_password = forms.CharField(label="Old Password", min_length=6, widget=forms.PasswordInput())
    new_password1 = forms.CharField(label="New Password", min_length=6, widget=forms.PasswordInput())
    new_password2 = forms.CharField(label="Re-type New Password", min_length=6, widget=forms.PasswordInput())

