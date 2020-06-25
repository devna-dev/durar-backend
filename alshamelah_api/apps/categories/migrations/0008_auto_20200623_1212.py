# Generated by Django 3.0.7 on 2020-06-23 12:12

import apps.categories.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('categories', '0007_auto_20200623_1017'),
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