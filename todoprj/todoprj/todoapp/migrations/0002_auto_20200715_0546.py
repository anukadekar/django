# Generated by Django 3.0.6 on 2020-07-15 05:46

import datetime
from django.db import migrations, models
import django.utils.timezone
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('todoapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='todomodels',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='todomodels',
            name='title',
            field=models.CharField(default=datetime.datetime(2020, 7, 15, 5, 46, 28, 382931, tzinfo=utc), max_length=50),
            preserve_default=False,
        ),
    ]
