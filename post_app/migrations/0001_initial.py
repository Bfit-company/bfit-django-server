# Generated by Django 3.2.7 on 2021-10-30 15:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('person_app', '0003_persondb_profile_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostDB',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('slug', models.SlugField(unique=True)),
                ('image', models.URLField(blank=True, default='https://www.essd.eu/wp-content/uploads/2020/07/ESSD_Hungary-12.jpg', null=True)),
                ('body', models.TextField()),
                ('post_date', models.DateField(auto_now_add=True)),
                ('updated', models.DateField()),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_detail', to='person_app.persondb')),
            ],
        ),
    ]