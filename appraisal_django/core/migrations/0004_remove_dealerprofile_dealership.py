# Generated by Django 5.0.6 on 2024-07-03 03:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_dealerprofile_dealership'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dealerprofile',
            name='dealership',
        ),
    ]
