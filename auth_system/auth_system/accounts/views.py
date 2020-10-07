from datetime import datetime

from django.conf.global_settings import DEFAULT_FROM_EMAIL
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.template import loader
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from django import forms
from .forms import SignUpForm, PasswordResetRequestForm, ChangePasswordForm
from django.views.generic import FormView, UpdateView


def home(request) :
    return render(request, 'home.html')


def signup(request) :
    if request.method == 'POST' :
        form = SignUpForm(request.POST)
        if form.is_valid() :
            user = form.save()
            login(request, user)
            return redirect('home')
    else :
        form = SignUpForm()
    return render(request, 'signup.html', {'form' : form})


def password_change(request) :
    form = ChangePasswordForm(request.POST or None)
    if request.method == 'POST' :
        cur_password = request.user.password
        user = User.objects.get(username=request.user.username)
        if form.is_valid() :
            old_password = form.cleaned_data.get("old_password")
            new_password1 = form.cleaned_data.get("new_password1")
            new_password2 = form.cleaned_data.get("new_password2")
            check = check_password(old_password, cur_password)
            if check and new_password1 == new_password2 and old_password != new_password1 :
                user.set_password(new_password1)
                user.save()
                update_session_auth_hash(request, user)
                return redirect('password_change_done')
            else :
                return render(request, 'password_recheck_message.html')
    return render(request, 'password_change.html', {"form" : form})


class ResetPasswordRequestView(FormView) :
    template_name = 'password_reset.html'
    success_url = 'reset/done'
    form_class = PasswordResetRequestForm

    def reset_password(self, user, request) :
        u = {
            'email' : user.email,
            'domain' : self.request.META['HTTP_HOST'],
            'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
            'user' : user,
            'token' : default_token_generator.make_token(user),
            'protocol' : self.request.scheme,
        }
        email_template_name = 'password_reset_email.html'
        subject = "Reset Your Password"
        email = loader.render_to_string(email_template_name, u)
        send_mail(subject, email, DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)

    def post(self, request, *args, **kwargs) :
        resp = render(request, 'invalid_user.html')
        form = self.form_class(request.POST)
        if form.is_valid() :
            user_name = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            try :
                user = User.objects.get(email=email, username=user_name)
                if user :
                    self.reset_password(user, request)
                    result = self.form_valid(form)
                    return result
            except ObjectDoesNotExist :
                print("Object Does not exist ERROR")
        return resp


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView) :
    model = User
    fields = ('first_name', 'last_name', 'email',)
    template_name = 'my_account.html'
    success_url = reverse_lazy('my_account')

    def get_object(self) :
        return self.request.user
