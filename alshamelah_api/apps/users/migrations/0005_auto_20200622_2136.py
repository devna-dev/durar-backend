# Generated by Django 3.0.7 on 2020-06-22 21:36

import apps.users.models
from django.db import migrations
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20200622_1614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to=apps.users.models.User.path),
        ),
    ]
