from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from .models import TodoModels


def home(request) :
    return render(request, 'home.html')


def listItems(request) :
    items = TodoModels.objects.all()
    return render(request, 'todo.html', {'items' : items})


def addItem(request) :
    value = request.POST['content']
    new_item = TodoModels(content=value)
    new_item.save()
    return HttpResponseRedirect('listItems')


def delItem(request, i) :
    value = TodoModels.objects.get(id=i)
    value.delete()
    return HttpResponseRedirect('/listItems')



