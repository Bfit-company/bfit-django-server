# Generated by Django 3.2.7 on 2021-11-05 13:57

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('person_app', '0003_persondb_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='persondb',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None),
        ),
    ]
