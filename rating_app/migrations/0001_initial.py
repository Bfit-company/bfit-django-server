# Generated by Django 3.2.9 on 2021-12-22 23:35

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('person_app', '0007_persondb_instagram_url'),
        ('coach_app', '0011_alter_coachdb_rating'),
    ]

    operations = [
        migrations.CreateModel(
            name='RatingDB',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(default=3, validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(1)])),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('person_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rating', to='person_app.persondb')),
                ('rating_coach_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rates', to='coach_app.coachdb')),
            ],
            options={
                'unique_together': {('person_id', 'rating_coach_id')},
            },
        ),
    ]
