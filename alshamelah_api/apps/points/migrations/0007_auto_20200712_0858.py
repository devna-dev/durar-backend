# Generated by Django 3.0.8 on 2020-07-12 08:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('points', '0006_auto_20200712_0818'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='achievement',
            options={'ordering': ['creation_time']},
        ),
    ]