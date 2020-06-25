# Generated by Django 3.0.7 on 2020-06-23 13:44

import apps.users.models
import easy_thumbnails.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0009_auto_20200623_1212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True,
                                                               upload_to=apps.users.models.User.get_path),
        ),
    ]