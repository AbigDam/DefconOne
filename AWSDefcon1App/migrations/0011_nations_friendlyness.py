# Generated by Django 5.0.6 on 2024-08-10 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AWSDefcon1App', '0010_rename_acheivements_user_achievements'),
    ]

    operations = [
        migrations.AddField(
            model_name='nations',
            name='friendlyness',
            field=models.IntegerField(blank=True, default=10, null=True),
        ),
    ]
