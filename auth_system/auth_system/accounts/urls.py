from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views
from .views import ResetPasswordRequestView

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^signup/', views.signup, name='signup'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout', ),
    # url(r'^settings/password/$', PasswordChangeView.as_view(),name='password_change'),
    url(r'^settings/password/$', views.password_change, name='password_change'),
    url(r'^settings/password/done/$',
        auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'),
        name='password_change_done'),
    url(r'^reset/done', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
        name='password_reset_confirm'),
    url(r'^reset/complete/$',
        auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
        name='password_reset_complete'),
    url(r'^reset', ResetPasswordRequestView.as_view(), name="password_reset"),
    url(r'^settings/account/$', views.UserUpdateView.as_view(), name='my_account'),
]
