# Generated by Django 5.0.7 on 2025-07-16 11:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AWSDefcon1App', '0016_map_deleteurl'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='map',
            name='URL',
        ),
        migrations.RemoveField(
            model_name='map',
            name='deleteURL',
        ),
    ]
