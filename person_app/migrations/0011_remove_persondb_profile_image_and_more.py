# Generated by Django 4.0.4 on 2022-07-26 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('person_app', '0010_remove_persondb_is_coach'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='persondb',
            name='profile_image',
        ),
        migrations.AddField(
            model_name='persondb',
            name='profile_image_s3_path',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
