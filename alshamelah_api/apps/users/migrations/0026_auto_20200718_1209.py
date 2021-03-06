# Generated by Django 3.0.8 on 2020-07-18 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_auto_20200716_0353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('book_approved', 'Book Approved'), ('paper_approved', 'Paper Approved'), ('thesis_approved', 'Thesis Approved'), ('audio_approved', 'Audio Approved'), ('payment_success', 'Payment Success'), ('payment_rejected', 'Payment Rejected'), ('support_request', 'Support Request'), ('points_awarded', 'Points awarded'), ('achievement_awarded', 'Achievement awarded'), ('admin_notification', 'Admin Notification')], max_length=20, verbose_name='Type'),
        ),
    ]
