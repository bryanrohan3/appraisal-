# Generated by Django 5.0.6 on 2024-07-09 04:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_appraisal_photo_appraisal_damage_photos_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appraisal',
            name='last_updated',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='appraisal',
            name='start_date',
            field=models.DateTimeField(null=True),
        ),
    ]
