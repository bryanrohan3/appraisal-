# Generated by Django 5.0.6 on 2024-07-11 04:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_remove_dealerprofile_dealership_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dealership',
            name='management_dealers',
        ),
        migrations.RemoveField(
            model_name='dealership',
            name='sales_dealers',
        ),
    ]
