from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm, PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.forms import ModelForm
from django.test import TestCase

# Create your tests here.
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .forms import SignUpForm
from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse, resolve
from django.contrib.auth import views as auth_views

from .views import UserUpdateView, signup


class SignUpFormTest(TestCase) :
    def test_form_has_fields(self) :
        form = SignUpForm()
        expected = ['username', 'email', 'password1', 'password2', ]
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)


class PasswordResetMailTests(TestCase) :
    def setUp(self) :
        User.objects.create_user(username='john', email='john@doe.com', password='123')
        self.response = self.client.post(reverse('password_reset'), {'email' : 'john@doe.com'})
        self.email = mail.outbox[0]

    def test_email_subject(self) :
        self.assertEqual('[Django Boards] Reset your password', self.email.subject)

    def test_email_body(self) :
        context = self.response.context
        token = context.get('token')
        uid = context.get('uid')
        password_reset_token_url = reverse('password_reset_confirm', kwargs={
            'uidb64' : uid,
            'token' : token
        })
        self.assertIn(password_reset_token_url, self.email.body)
        self.assertIn('john', self.email.body)
        self.assertIn('john@doe.com', self.email.body)

    def test_email_to(self) :
        self.assertEqual(['john@doe.com', ], self.email.to)


class MyAccountTestCase(TestCase) :
    def setUp(self) :
        self.username = 'john'
        self.password = 'secret123'
        self.user = User.objects.create_user(username=self.username, email='john@doe.com', password=self.password)
        self.url = reverse('my_account')


class MyAccountTests(MyAccountTestCase) :
    def setUp(self) :
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.get(self.url)

    def test_status_code(self) :
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_correct_view(self) :
        view = resolve('/settings/account/')
        self.assertEquals(view.func.view_class, UserUpdateView)

    def test_csrf(self) :
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self) :
        form = self.response.context['form']
        self.assertIsInstance(form, ModelForm)

    def test_form_inputs(self) :
        self.assertContains(self.response, '<input', 4)
        self.assertContains(self.response, 'type="text"', 2)
        self.assertContains(self.response, 'type="email"', 1)


class LoginRequiredMyAccountTests(TestCase) :
    def test_redirection(self) :
        url = reverse('my_account')
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=url))


class SuccessfulMyAccountTests(MyAccountTestCase) :
    def setUp(self) :
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {
            'first_name' : 'John',
            'last_name' : 'Doe',
            'email' : 'johndoe@example.com',
        })

    def test_redirection(self) :
        self.assertRedirects(self.response, self.url)

    def test_data_changed(self) :
        self.user.refresh_from_db()
        self.assertEquals('John', self.user.first_name)
        self.assertEquals('Doe', self.user.last_name)
        self.assertEquals('johndoe@example.com', self.user.email)


class InvalidMyAccountTests(MyAccountTestCase) :
    def setUp(self) :
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {
            'first_name' : 'longstring' * 100
        })

    def test_status_code(self) :
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self) :
        form = self.response.context['form']
        self.assertTrue(form.errors)


class PasswordChangeTests(TestCase) :
    def setUp(self) :
        username = 'john'
        password = 'secret123'
        User.objects.create_user(username=username, email='john@doe.com', password=password)
        url = reverse('password_change')
        self.client.login(username=username, password=password)
        self.response = self.client.get(url)

    def test_status_code(self) :
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_correct_view(self) :
        view = resolve('/settings/password/')
        self.assertEquals(view.func.view_class, auth_views.PasswordChangeView)

    def test_csrf(self) :
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self) :
        form = self.response.context.get('form')
        self.assertIsInstance(form, PasswordChangeForm)

    def test_form_inputs(self) :
        self.assertContains(self.response, '<input', 4)
        self.assertContains(self.response, 'type="password"', 3)


class LoginRequiredPasswordChangeTests(TestCase) :
    def test_redirection(self) :
        url = reverse('password_change')
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, f'{login_url}?next={url}')


class PasswordChangeTestCase(TestCase) :
    def setUp(self, data={}) :
        self.user = User.objects.create_user(username='john', email='john@doe.com', password='old_password')
        self.url = reverse('password_change')
        self.client.login(username='john', password='old_password')
        self.response = self.client.post(self.url, data)


class SuccessfulPasswordChangeTests(PasswordChangeTestCase) :
    def setUp(self) :
        super().setUp({
            'old_password' : 'old_password',
            'new_password1' : 'new_password',
            'new_password2' : 'new_password',
        })

    def test_redirection(self) :
        self.assertRedirects(self.response, reverse('password_change_done'))

    def test_password_changed(self) :
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new_password'))

    def test_user_authentication(self) :
        response = self.client.get(reverse('main'))
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)


class InvalidPasswordChangeTests(PasswordChangeTestCase) :
    def test_status_code(self) :
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self) :
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_didnt_change_password(self) :
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('old_password'))


class PasswordResetTests(TestCase) :
    def setUp(self) :
        url = reverse('password_reset')
        self.response = self.client.get(url)

    def test_status_code(self) :
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self) :
        view = resolve('/reset/')
        self.assertEquals(view.func.view_class, auth_views.PasswordResetView)

    def test_csrf(self) :
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self) :
        form = self.response.context.get('form')
        self.assertIsInstance(form, PasswordResetForm)

    def test_form_inputs(self) :
        self.assertContains(self.response, '<input', 2)
        self.assertContains(self.response, 'type="email"', 1)


class SuccessfulPasswordResetTests(TestCase) :
    def setUp(self) :
        email = 'john@doe.com'
        User.objects.create_user(username='john', email=email, password='123abcdef')
        url = reverse('password_reset')
        self.response = self.client.post(url, {'email' : email})

    def test_redirection(self) :
        url = reverse('password_reset_done')
        self.assertRedirects(self.response, url)

    def test_send_password_reset_email(self) :
        self.assertEqual(1, len(mail.outbox))


class InvalidPasswordResetTests(TestCase) :
    def setUp(self) :
        url = reverse('password_reset')
        self.response = self.client.post(url, {'email' : 'donotexist@email.com'})

    def test_redirection(self) :
        url = reverse('password_reset_done')
        self.assertRedirects(self.response, url)

    def test_no_reset_email_sent(self) :
        self.assertEqual(0, len(mail.outbox))


class PasswordResetDoneTests(TestCase) :
    def setUp(self) :
        url = reverse('password_reset_done')
        self.response = self.client.get(url)

    def test_status_code(self) :
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self) :
        view = resolve('/reset/done/')
        self.assertEquals(view.func.view_class, auth_views.PasswordResetDoneView)


class PasswordResetConfirmTests(TestCase) :
    def setUp(self) :
        user = User.objects.create_user(username='john', email='john@doe.com', password='123abcdef')
        self.uid = urlsafe_base64_encode(force_bytes(user.pk))
        self.token = default_token_generator.make_token(user)

        url = reverse('password_reset_confirm', kwargs={'uidb64' : self.uid, 'token' : self.token})
        self.response = self.client.get(url, follow=True)

    def test_status_code(self) :
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self) :
        view = resolve('/reset/{uidb64}/{token}/'.format(uidb64=self.uid, token=self.token))
        self.assertEquals(view.func.view_class, auth_views.PasswordResetConfirmView)

    def test_csrf(self) :
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self) :
        form = self.response.context.get('form')
        self.assertIsInstance(form, SetPasswordForm)

    def test_form_inputs(self) :
        self.assertContains(self.response, '<input', 3)
        self.assertContains(self.response, 'type="password"', 2)


class InvalidPasswordResetConfirmTests(TestCase) :
    def setUp(self) :
        user = User.objects.create_user(username='john', email='john@doe.com', password='123abcdef')
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        user.set_password('abcdef123')
        user.save()

        url = reverse('password_reset_confirm', kwargs={'uidb64' : uid, 'token' : token})
        self.response = self.client.get(url)

    def test_status_code(self) :
        self.assertEquals(self.response.status_code, 200)

    def test_html(self) :
        password_reset_url = reverse('password_reset')
        self.assertContains(self.response, 'invalid password reset link')
        self.assertContains(self.response, 'href="{0}"'.format(password_reset_url))


class PasswordResetCompleteTests(TestCase) :
    def setUp(self) :
        url = reverse('password_reset_complete')
        self.response = self.client.get(url)

    def test_status_code(self) :
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self) :
        view = resolve('/reset/complete/')
        self.assertEquals(view.func.view_class, auth_views.PasswordResetCompleteView)


class SignUpTests(TestCase) :
    def setUp(self) :
        url = reverse('signup')
        self.response = self.client.get(url)

    def test_signup_status_code(self) :
        self.assertEquals(self.response.status_code, 200)

    def test_signup_url_resolves_signup_view(self) :
        view = resolve('/signup/')
        self.assertEquals(view.func, signup)

    def test_csrf(self) :
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self) :
        form = self.response.context.get('form')
        self.assertIsInstance(form, SignUpForm)

    def test_form_inputs(self) :
        self.assertContains(self.response, '<input', 5)
        self.assertContains(self.response, 'type="text"', 1)
        self.assertContains(self.response, 'type="email"', 1)
        self.assertContains(self.response, 'type="password"', 2)


class SuccessfulSignUpTests(TestCase) :
    def setUp(self) :
        url = reverse('signup')
        data = {
            'username' : 'john',
            'email' : 'john@doe.com',
            'password1' : 'abcdef123456',
            'password2' : 'abcdef123456'
        }
        self.response = self.client.post(url, data)
        self.home_url = reverse('main')

    def test_redirection(self) :
        self.assertRedirects(self.response, self.home_url)

    def test_user_creation(self) :
        self.assertTrue(User.objects.exists())

    def test_user_authentication(self) :
        response = self.client.get(self.home_url)
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)


class InvalidSignUpTests(TestCase) :
    def setUp(self) :
        url = reverse('signup')
        self.response = self.client.post(url, {})  # submit an empty dictionary

    def test_signup_status_code(self) :
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self) :
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_dont_create_user(self) :
        self.assertFalse(User.objects.exists())
