# Generated by Django 3.0.7 on 2020-07-03 03:14

from django.db import migrations


def insert_settings(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    point_setting = apps.get_model("points", "PointSetting")
    point_setting.objects.create(donation=10, book_approved=5, paper_approved=5, thesis_approved=5, audio_approved=10)


class Migration(migrations.Migration):
    dependencies = [
        ('points', '0002_userpoints_action_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pointbadge',
            options={'ordering': ['-point_num'], 'verbose_name_plural': 'Point Badges'},
        ),
        migrations.RunPython(insert_settings),
    ]