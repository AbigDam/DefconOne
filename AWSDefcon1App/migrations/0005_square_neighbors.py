# Generated by Django 5.0.6 on 2024-08-09 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AWSDefcon1App', '0004_rename_capital_square_coastal'),
    ]

    operations = [
        migrations.AddField(
            model_name='square',
            name='neighbors',
            field=models.JSONField(default=list),
        ),
    ]