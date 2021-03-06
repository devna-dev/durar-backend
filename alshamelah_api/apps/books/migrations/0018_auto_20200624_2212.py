# Generated by Django 3.0.7 on 2020-06-24 22:12

import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authors', '0002_auto_20200624_2115'),
        ('categories', '0012_auto_20200624_2115'),
        ('books', '0017_auto_20200624_2115'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='searchbook',
            name='book',
        ),
        migrations.AddField(
            model_name='searchbook',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='searches', to='authors.Author', verbose_name='Author'),
        ),
        migrations.AddField(
            model_name='searchbook',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='searches', to='categories.Category', verbose_name='Category'),
        ),
        migrations.AddField(
            model_name='searchbook',
            name='content',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True, verbose_name='Content'),
        ),
        migrations.AddField(
            model_name='searchbook',
            name='from_year',
            field=models.IntegerField(null=True, verbose_name='From Year'),
        ),
        migrations.AddField(
            model_name='searchbook',
            name='has_audio',
            field=models.BooleanField(null=True, verbose_name='Has Audio'),
        ),
        migrations.AddField(
            model_name='searchbook',
            name='page',
            field=models.IntegerField(null=True, verbose_name='Page'),
        ),
        migrations.AddField(
            model_name='searchbook',
            name='page_size',
            field=models.IntegerField(null=True, verbose_name='Page Size'),
        ),
        migrations.AddField(
            model_name='searchbook',
            name='sort',
            field=models.CharField(max_length=100, null=True, verbose_name='Sort'),
        ),
        migrations.AddField(
            model_name='searchbook',
            name='sub_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='searches', to='categories.SubCategory', verbose_name='Sub Category'),
        ),
        migrations.AddField(
            model_name='searchbook',
            name='title',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Title'),
        ),
        migrations.AddField(
            model_name='searchbook',
            name='to_year',
            field=models.IntegerField(null=True, verbose_name='To Year'),
        ),
    ]
