# Generated by Django 3.0.7 on 2020-06-25 13:05

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0019_auto_20200624_2247'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='searchbook',
            options={'ordering': ['-creation_time']},
        ),
        migrations.AlterField(
            model_name='searchbook',
            name='has_audio',
            field=models.BooleanField(default=None, null=True, verbose_name='Has Audio'),
        ),
        migrations.CreateModel(
            name='ListenProgress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_update_time', models.DateTimeField(auto_now=True, null=True)),
                ('progress', models.PositiveSmallIntegerField(null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Progress')),
                ('audio', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='file_progress', to='books.BookAudio', verbose_name='Audio')),
                ('listen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='file_progress', to='books.ListenBook', verbose_name='File Progress')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]