# Generated by Django 3.0.8 on 2020-07-20 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('points', '0011_achievement_default_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pointbadge',
            name='point_num',
            field=models.PositiveIntegerField(verbose_name='Required points'),
        ),
        migrations.AlterField(
            model_name='userachievement',
            name='points',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
