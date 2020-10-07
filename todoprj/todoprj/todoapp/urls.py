from django.urls import path

from . import views

urlpatterns = [
    path('listItems/', views.listItems, name='listItems'),
    path('addItem', views.addItem, name='addItem'),
    path('delItem/<int:i>', views.delItem, name='delItem'),
]
