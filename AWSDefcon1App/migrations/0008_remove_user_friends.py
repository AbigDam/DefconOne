# Generated by Django 5.0.6 on 2024-08-10 04:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AWSDefcon1App', '0007_achievements_freindrequest_delete_alliancerequest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='friends',
        ),
    ]