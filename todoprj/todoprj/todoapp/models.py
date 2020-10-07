from django.db import models


# Create your models here.
class TodoModels(models.Model) :
    content = models.TextField(default="Enter the tasks",max_length=200)
