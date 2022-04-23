# Generated by Django 3.2.7 on 2021-11-20 00:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coach_app', '0006_alter_coachdb_date_joined'),
        ('location_app', '0004_locationdb_formatted_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locationdb',
            name='coach',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location_coach', to='coach_app.coachdb'),
        ),
    ]