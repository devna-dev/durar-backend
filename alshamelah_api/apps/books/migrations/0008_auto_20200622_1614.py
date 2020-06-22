# Generated by Django 3.0.7 on 2020-06-22 16:14

import apps.books.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('books', '0007_auto_20200622_1458'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookhighlight',
            name='end',
        ),
        migrations.RemoveField(
            model_name='bookhighlight',
            name='line',
        ),
        migrations.AddField(
            model_name='bookhighlight',
            name='highlighted_text',
            field=models.TextField(default='', verbose_name='Highlighted Text'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='book',
            name='cover_image',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to=apps.books.models.Book.path),
        ),
        migrations.CreateModel(
            name='SearchBook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='searches', to='books.Book', verbose_name='Book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='searches', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
        migrations.CreateModel(
            name='ReadBook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='readers', to='books.Book', verbose_name='Book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reads', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
        migrations.CreateModel(
            name='ListenBook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listens', to='books.Book', verbose_name='Book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listens', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
        migrations.CreateModel(
            name='FavoriteBook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_books', to='books.Book', verbose_name='Book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_books', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
        migrations.CreateModel(
            name='DownloadBook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='downloads', to='books.Book', verbose_name='Book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='downloads', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
        migrations.CreateModel(
            name='BookSuggestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('author', models.CharField(max_length=1000, verbose_name='Author')),
                ('publish_date', models.DateField(blank=True, null=True, verbose_name='Publish Date')),
                ('url', models.URLField(verbose_name='Book Url')),
                ('creation_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suggestions', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
        migrations.CreateModel(
            name='BookReviewLike',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='books.BookReview', verbose_name='Review')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
    ]
