# Generated by Django 3.0.7 on 2020-06-23 12:12

import apps.books.models
import easy_thumbnails.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('books', '0012_auto_20200623_1017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='cover_image',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True,
                                                               upload_to=apps.books.models.Book.get_path),
        ),
    ]