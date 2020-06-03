# Generated by Django 3.0.6 on 2020-06-02 11:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='membership',
            field=models.CharField(blank=True,
                                   choices=[('N', 'New'), ('A', 'Active'), ('G', 'Golden'), ('U', 'Ultimate')],
                                   max_length=1, null=True, verbose_name='Membership'),
        ),
    ]
