from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.test import TestCase

# Create your tests here.
from django.urls import reverse, resolve

from .forms import SignUpForm
from .views import signup


class SignUpTests(TestCase) :
    def setUp(self) :
        url = reverse('signup')
        self.response = self.client.get(url)

    def test_signup_status_code(self) :
        self.assertEquals(self.response.status_code, 200)

    def test_status_url_resolves_view(self) :
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


# class SuccessfulSignUpTests(TestCase) :
#     def setUp(self) :
#         url = reverse('signup')
#         data = {
#             'username' : 'testuser',
#             'email' : 'abcd@123.com',
#             'password1' : 'Abcd@123',
#             'password2' : 'Abcd@123',
#         }
#         self.response = self.client.post(url, data)
#         self.home_url = reverse('home')
#
#     def test_redirect(self) :
#         print(self.response)
#         self.assertRedirects(self.response, self.home_url)
#
#     def test_user_creation(self) :
#         self.assertTrue(User.objects.exists())
#
#     def test_user_auth(self) :
#         response = self.client.get(self.home_url)
#         user = response.context.get('user')
#         self.assertTrue(user.is_authenticated)


class InvalidSignUpTests(TestCase) :
    def setUp(self) :
        url = reverse('signup')
        self.response = self.client.post(url, {})

    def test_signup_status_code(self) :
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self) :
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_no_user(self) :
        self.assertFalse(User.objects.exists())


class SignUpFormTest(TestCase) :
    def test_form_has_fields(self) :
        form = SignUpForm()
        expected = ['username', 'email', 'password1', 'password2']
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)
