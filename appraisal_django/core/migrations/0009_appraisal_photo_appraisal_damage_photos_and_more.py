# Generated by Django 5.0.6 on 2024-07-09 03:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_dealerprofile_is_active_dealership_is_active_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Appraisal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('customer_first_name', models.CharField(max_length=50)),
                ('customer_last_name', models.CharField(max_length=50)),
                ('customer_email', models.EmailField(max_length=254)),
                ('customer_phone', models.CharField(max_length=15)),
                ('vehicle_make', models.CharField(max_length=50)),
                ('vehicle_model', models.CharField(max_length=50)),
                ('vehicle_year', models.IntegerField()),
                ('vehicle_vin', models.CharField(max_length=17)),
                ('vehicle_registration', models.CharField(max_length=7)),
                ('color', models.CharField(max_length=50)),
                ('odometer_reading', models.IntegerField()),
                ('engine_type', models.CharField(max_length=100)),
                ('transmission', models.CharField(max_length=100)),
                ('body_type', models.CharField(max_length=20)),
                ('fuel_type', models.CharField(max_length=20)),
                ('damage_description', models.TextField()),
                ('damage_location', models.CharField(max_length=100)),
                ('repair_cost_estimate', models.DecimalField(decimal_places=2, max_digits=10)),
                ('general_comments', models.TextField(blank=True)),
                ('privacy_comments', models.TextField(blank=True)),
                ('comment_date_time', models.DateTimeField(auto_now_add=True)),
                ('reserve_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('commented_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL)),
                ('dealership', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appraisals', to='core.dealership')),
                ('initiating_dealer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='initiated_appraisals', to='core.dealerprofile')),
                ('last_updating_dealer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='last_updated_appraisals', to='core.dealerprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='photos/')),
                ('description', models.CharField(blank=True, max_length=100)),
                ('location', models.CharField(blank=True, max_length=100)),
                ('appraisal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='core.appraisal')),
            ],
        ),
        migrations.AddField(
            model_name='appraisal',
            name='damage_photos',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='damage_appraisals', to='core.photo'),
        ),
        migrations.AddField(
            model_name='appraisal',
            name='vehicle_photos',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vehicle_appraisals', to='core.photo'),
        ),
    ]
