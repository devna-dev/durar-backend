# Generated by Django 3.0.7 on 2020-07-03 02:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PointBadge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_update_time', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=500, verbose_name='Name')),
                ('point_num', models.PositiveSmallIntegerField(verbose_name='Required points')),
            ],
            options={
                'verbose_name_plural': 'Point Badges',
            },
        ),
        migrations.CreateModel(
            name='PointSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_update_time', models.DateTimeField(auto_now=True, null=True)),
                ('donation', models.PositiveSmallIntegerField(verbose_name='Points per USD')),
                ('book_approved', models.PositiveSmallIntegerField(verbose_name='Points per book approved')),
                ('paper_approved', models.PositiveSmallIntegerField(verbose_name='Points per paper approved')),
                ('thesis_approved', models.PositiveSmallIntegerField(verbose_name='Points per thesis approved')),
                ('audio_approved', models.PositiveSmallIntegerField(verbose_name='Points per book audio approved')),
            ],
            options={
                'verbose_name_plural': 'Point Settings',
            },
        ),
        migrations.CreateModel(
            name='UserPoints',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_update_time', models.DateTimeField(auto_now=True, null=True)),
                ('point_num', models.PositiveSmallIntegerField(verbose_name='Awarded points')),
                ('type', models.CharField(choices=[('donation', 'Donation'), ('book_approved', 'Book Approval'),
                                                   ('paper_approved', 'Paper Approval'),
                                                   ('thesis_approved', 'Thesis Approval'),
                                                   ('audio_approved', 'Book Audio Approval')], max_length=20,
                                          verbose_name='Awarded For')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='points',
                                           to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name_plural': 'User Points',
            },
        ),
    ]
