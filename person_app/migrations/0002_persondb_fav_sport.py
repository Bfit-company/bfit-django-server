# Generated by Django 3.2.7 on 2021-10-16 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sport_type_app', '0002_auto_20211007_0920'),
        ('person_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='persondb',
            name='fav_sport',
            field=models.ManyToManyField(to='sport_type_app.SportTypeDB'),
        ),
    ]
