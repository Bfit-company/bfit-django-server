# Generated by Django 4.0.4 on 2022-05-13 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coach_app', '0013_rename_price_coachdb_from_price_coachdb_to_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='coachdb',
            name='gender_coach_type',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('FM', 'Female and Male')], default='FM', max_length=2),
            preserve_default=False,
        ),
    ]
