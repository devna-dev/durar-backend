# Generated by Django 3.0.7 on 2020-06-23 13:44

import apps.books.models
import django.db.models.deletion
import easy_thumbnails.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('books', '0013_auto_20200623_1212'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookreview',
            name='rating',
            field=models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
                                                   default=3, verbose_name='Rating'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='book',
            name='cover_image',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True,
                                                               upload_to=apps.books.models.Book.get_path),
        ),
        migrations.AlterField(
            model_name='bookreview',
            name='book',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews',
                                    to='books.Book', verbose_name='Book'),
        ),
        migrations.AlterField(
            model_name='bookreview',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews',
                                    to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.DeleteModel(
            name='BookRating',
        ),
    ]
