# Generated by Django 3.2.7 on 2021-10-16 14:00

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('coach_app', '0004_alter_coachdb_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='coachdb',
            name='date_joined',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='date joined'),
            preserve_default=False,
        ),
    ]
