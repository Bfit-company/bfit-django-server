# Generated by Django 4.0.4 on 2023-01-18 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rating_app', '0005_alter_ratingdb_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='ratingdb',
            name='review',
            field=models.TextField(default=''),
        ),
    ]