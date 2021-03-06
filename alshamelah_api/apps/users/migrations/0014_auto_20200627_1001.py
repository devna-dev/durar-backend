# Generated by Django 3.0.7 on 2020-06-27 10:01

import apps.users.models
import easy_thumbnails.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0013_remove_user_phone_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=easy_thumbnails.fields.ThumbnailerImageField(null=True, upload_to=apps.users.models.User.get_path),
        ),
    ]
