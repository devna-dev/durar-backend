# Generated by Django 3.0.8 on 2020-07-13 11:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0023_dailylogin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='membership',
        ),
    ]
