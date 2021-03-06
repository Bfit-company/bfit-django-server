# Generated by Django 3.2.9 on 2021-12-23 06:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coach_app', '0011_alter_coachdb_rating'),
        ('person_app', '0007_persondb_instagram_url'),
        ('rating_app', '0002_auto_20211223_0619'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='ratingdb',
            name='unique_rates',
        ),
        migrations.AlterUniqueTogether(
            name='ratingdb',
            unique_together={('person_id', 'rating_coach_id')},
        ),
    ]
