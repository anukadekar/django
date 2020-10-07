from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.test import TestCase
from django.urls import reverse, resolve
from .forms import NewTopicForm, PostForm

from . import models, views
from .models import Board, Topic, Post
from .templatetags.form_tags import input_class, field_type
from .views import TopicListView, BoardListView, reply_topic, PostUpdateView, PostListView


class MainTest(TestCase) :

    def setUp(self) :
        models.Board.objects.create(name='django', description="django link")
        url = reverse('main')
        self.response = self.client.get(url)

    def test_main_view_status(self) :
        self.assertEquals(self.response.status_code, 200)

    def test_main_url_resolves_main_view(self) :
        view = resolve('/')
        self.assertEquals(view.func.view_class, BoardListView)

    def test_main_view_contains_link(self) :
        board_topics_url = reverse('board_topics', kwargs={'pk' : 1})
        self.assertContains(self.response, 'href="{0}'.format(board_topics_url))


class BoardTopicsTest(TestCase) :
    def setUp(self) :
        models.Board.objects.create(name='django', description="django link")

    def test_board_topics_view_status(self) :
        url = reverse('board_topics', kwargs={'pk' : 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_board_topics_view_nf_status(self) :
        url = reverse('board_topics', kwargs={'pk' : 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_board_topics_resolves_url(self) :
        view = resolve('/boards/1/')
        self.assertEquals(view.func.view_class, TopicListView)

    def test_board_topics_contains_links(self) :
        board_topics_url = reverse('board_topics', kwargs={'pk' : 1})
        mainpage_url = reverse('main')
        new_topic_url = reverse('new_topic', kwargs={'pk' : 1})
        response = self.client.get(board_topics_url)
        self.assertContains(response, 'href="{0}'.format(mainpage_url))
        self.assertContains(response, 'href="{0}'.format(new_topic_url))


class NewTopicTests(TestCase) :
    def setUp(self) :
        models.Board.objects.create(name='django', description="django link")
        User.objects.create_user(username='admin1', email='admin1@123', password='admin1@123')
        self.client.login(username='admin1', password='admin1@123')

    def test_new_topic_view_status(self) :
        url = reverse('new_topic', kwargs={'pk' : 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_new_topic_view_nf_status(self) :
        url = reverse('new_topic', kwargs={'pk' : 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_new_topic_resolves_url(self) :
        view = resolve('/boards/1/new/')
        self.assertEquals(view.func, views.new_topic)

    def test_new_topic_contains_link_back_to_board_topics(self) :
        new_topic_url = reverse('new_topic', kwargs={'pk' : 1})
        response = self.client.get(new_topic_url)
        board_topics_url = reverse('board_topics', kwargs={'pk' : 1})
        self.assertContains(response, 'href="{0}'.format(board_topics_url))

    def test_csrf(self) :
        url = reverse('new_topic', kwargs={'pk' : 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self) :
        url = reverse('new_topic', kwargs={'pk' : 1})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)

    def test_new_topic_valid_post_data(self) :
        url = reverse('new_topic', kwargs={'pk' : 1})
        data = {
            'subject' : 'Test title',
            'message' : 'testing'
        }
        response = self.client.post(url, data)
        self.assertTrue(models.Topic.objects.exists())
        self.assertTrue(models.Post.objects.exists())

    def test_new_topic_invalid_post_data(self) :
        url = reverse('new_topic', kwargs={'pk' : 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_new_topic_invalid_post_data_empty_fields(self) :
        url = reverse('new_topic', kwargs={'pk' : 1})
        data = {
            'subject' : '',
            'message' : ''
        }
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(models.Topic.objects.exists())
        self.assertFalse(models.Post.objects.exists())


class ReplyTopicTestCase(TestCase) :
    def setUp(self) :
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.username = 'admin1'
        self.password = 'admin1@123'
        user = User.objects.create_user(username=self.username, email='admn1@123.com', password=self.password)
        self.topic = Topic.objects.create(subject='Hello, world', board=self.board, starter=user)
        Post.objects.create(message='hello', topic=self.topic, created_by=user)
        self.url = reverse('reply_topic', kwargs={'pk' : self.board.pk, 'topic_pk' : self.topic.pk})


class LoginRequiredReplyTopicTests(ReplyTopicTestCase) :
    def test_redirection(self) :
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))


class ReplyTopicTests(ReplyTopicTestCase) :
    def setUp(self) :
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.get(self.url)

    def test_status_code(self) :
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self) :
        view = resolve('/boards/1/topics/1/reply/')
        self.assertEquals(view.func, reply_topic)

    def test_csrf(self) :
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self) :
        form = self.response.context.get('form')
        self.assertIsInstance(form, PostForm)

    def test_form_inputs(self) :
        self.assertContains(self.response, '<input', 1)
        self.assertContains(self.response, '<textarea', 1)


class SuccessfulReplyTopicTests(ReplyTopicTestCase) :
    def setUp(self) :
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {'message' : 'hello, world!'})

    def test_redirection(self) :
        url = reverse('topic_posts', kwargs={'pk' : self.board.pk, 'topic_pk' : self.topic.pk})
        topic_posts_url = '{url}?page=1#2'.format(url=url)
        self.assertRedirects(self.response, topic_posts_url)

    def test_reply_created(self) :
        self.assertEquals(Post.objects.count(), 2)


class InvalidReplyTopicTests(ReplyTopicTestCase) :
    def setUp(self) :
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {})

    def test_status_code(self) :
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self) :
        form = self.response.context.get('form')
        self.assertTrue(form.errors)


class PostUpdateViewTestCase(TestCase) :
    def setUp(self) :
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.username = 'admin1'
        self.password = 'admin1@123'
        user = User.objects.create_user(username=self.username, email='admin1@123.com', password=self.password)
        self.topic = Topic.objects.create(subject='Hello, world', board=self.board, starter=user)
        self.post = Post.objects.create(message='hello', topic=self.topic, created_by=user)
        self.url = reverse('edit_post', kwargs={
            'pk' : self.board.pk,
            'topic_pk' : self.topic.pk,
            'post_pk' : self.post.pk
        })


class LoginRequiredPostUpdateViewTests(PostUpdateViewTestCase) :
    def test_redirection(self) :
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))


class UnauthorizedPostUpdateViewTests(PostUpdateViewTestCase) :
    def setUp(self) :
        super().setUp()
        username = 'admin2'
        password = 'admin2@123'
        user = User.objects.create_user(username=username, email='admin2@123.com', password=password)
        self.client.login(username=username, password=password)
        self.response = self.client.get(self.url)

    def test_status_code(self) :
        self.assertEquals(self.response.status_code, 404)


class PostUpdateViewTests(PostUpdateViewTestCase) :
    def setUp(self) :
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.get(self.url)

    def test_status_code(self) :
        self.assertEquals(self.response.status_code, 200)

    def test_view_class(self) :
        view = resolve('/boards/1/topics/1/posts/1/edit/')
        self.assertEquals(view.func.view_class, PostUpdateView)

    def test_csrf(self) :
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self) :
        form = self.response.context.get('form')
        self.assertIsInstance(form, ModelForm)

    def test_form_inputs(self) :
        self.assertContains(self.response, '<input', 1)
        self.assertContains(self.response, '<textarea', 1)


class SuccessfulPostUpdateViewTests(PostUpdateViewTestCase) :
    def setUp(self) :
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {'message' : 'edited message'})

    def test_redirection(self) :
        topic_posts_url = reverse('topic_posts', kwargs={'pk' : self.board.pk, 'topic_pk' : self.topic.pk})
        self.assertRedirects(self.response, topic_posts_url)

    def test_post_changed(self) :
        self.post.refresh_from_db()
        self.assertEquals(self.post.message, 'edited message')


class InvalidPostUpdateViewTests(PostUpdateViewTestCase) :
    def setUp(self) :
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {})

    def test_status_code(self) :
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self) :
        form = self.response.context.get('form')
        self.assertTrue(form.errors)


class ExampleForm(forms.Form) :
    name = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta :
        fields = ('name', 'password')


class FieldTypeTests(TestCase) :
    def test_field_widget_type(self) :
        form = ExampleForm()
        self.assertEquals('TextInput', field_type(form['name']))
        self.assertEquals('PasswordInput', field_type(form['password']))


class InputClassTests(TestCase) :
    def test_unbound_field_initial_state(self) :
        form = ExampleForm()
        self.assertEquals('form-control ', input_class(form['name']))

        def test_valid_bound_field(self) :
            form = ExampleForm({'name' : 'john', 'password' : '123'})  # bound form (field + data)
            self.assertEquals('form-control is-valid', input_class(form['name']))
            self.assertEquals('form-control ', input_class(form['password']))

        def test_invalid_bound_field(self) :
            form = ExampleForm({'name' : '', 'password' : '123'})  # bound form (field + data)
            self.assertEquals('form-control is-invalid', input_class(form['name']))


class LoginRequiredNewTopicTests(TestCase) :
    def setUp(self) :
        Board.objects.create(name='Django', description='Django board.')
        self.url = reverse('new_topic', kwargs={'pk' : 1})
        self.response = self.client.get(self.url)

    def test_redirection(self) :
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))


class TopicPostsUpdate(TestCase) :
    def setUp(self) :
        board = Board.objects.create(name='Django', description='Django board.')
        user = User.objects.create_user(username='john', email='john@doe.com', password='123')
        topic = Topic.objects.create(subject='Hello, world', board=board, starter=user)
        Post.objects.create(message='hello', topic=topic, created_by=user)
        url = reverse('topic_posts', kwargs={'pk' : board.pk, 'topic_pk' : topic.pk})
        self.response = self.client.get(url)

    def test_status_code(self) :
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self) :
        view = resolve('/boards/1/topics/1/')
        self.assertEquals(view.func.view_class, PostListView)
