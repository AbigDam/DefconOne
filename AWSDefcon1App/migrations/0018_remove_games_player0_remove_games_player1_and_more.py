# Generated by Django 5.0.7 on 2025-07-21 18:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AWSDefcon1App', '0017_remove_map_url_remove_map_deleteurl'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='games',
            name='player0',
        ),
        migrations.RemoveField(
            model_name='games',
            name='player1',
        ),
        migrations.RemoveField(
            model_name='games',
            name='player2',
        ),
        migrations.RemoveField(
            model_name='games',
            name='player3',
        ),
        migrations.RemoveField(
            model_name='games',
            name='player4',
        ),
        migrations.RemoveField(
            model_name='games',
            name='player5',
        ),
        migrations.RemoveField(
            model_name='games',
            name='player6',
        ),
        migrations.RemoveField(
            model_name='games',
            name='player7',
        ),
        migrations.RemoveField(
            model_name='games',
            name='players',
        ),
    ]
