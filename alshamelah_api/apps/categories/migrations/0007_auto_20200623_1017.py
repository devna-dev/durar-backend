# Generated by Django 3.0.7 on 2020-06-23 10:17

import apps.categories.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('categories', '0006_auto_20200622_2252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=apps.categories.models.Category.get_path),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=apps.categories.models.SubCategory.get_path),
        ),
    ]
