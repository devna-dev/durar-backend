# Generated by Django 3.0.8 on 2020-07-20 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('points', '0012_auto_20200720_1159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpoints',
            name='point_num',
            field=models.PositiveIntegerField(verbose_name='Awarded points'),
        ),
    ]
