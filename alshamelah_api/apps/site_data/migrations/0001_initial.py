# Generated by Django 3.0.7 on 2020-06-27 23:09

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Legal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_update_time', models.DateTimeField(auto_now=True, null=True)),
                ('policy', models.TextField(verbose_name='Privacy Policy')),
                ('terms', models.TextField(verbose_name='Terms & Conditions')),
            ],
            options={
                'verbose_name_plural': 'Privacy Policy, Terms & Conditions',
            },
        ),
    ]
