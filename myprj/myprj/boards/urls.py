from django.conf.urls import url

from . import views
from django.contrib.auth import views as auth_views

# app_name = 'boards'
urlpatterns = [
    # path('', views.main, name='main'),
    url(r'^$', views.BoardListView.as_view(), name='main'),
    url(r'^accounts/profile/$', views.BoardListView.as_view() , name='main'),
    url(r'^boards/(?P<pk>\d+)/new/$', views.new_topic, name='new_topic'),
    url(r'^boards/(?P<pk>\d+)/topics/(?P<topic_pk>\d+)/reply/$', views.reply_topic, name='reply_topic'),
    url(r'^boards/(?P<pk>\d+)/topics/(?P<topic_pk>\d+)/posts/(?P<post_pk>\d+)/edit/$', views.PostUpdateView.as_view(),
        name='edit_post'),
    url(r'^boards/(?P<pk>\d+)/$', views.TopicListView.as_view(), name='board_topics'),
    url(r'^boards/(?P<pk>\d+)/topics/(?P<topic_pk>\d+)/$', views.PostListView.as_view(), name='topic_posts'),
]
