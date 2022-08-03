# Generated by Django 4.0.4 on 2022-08-03 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sport_type_app', '0003_auto_20211016_1338'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sporttypedb',
            name='image',
        ),
        migrations.AddField(
            model_name='sporttypedb',
            name='image_s3_path',
            field=models.CharField(default='hey', max_length=255, unique=True, verbose_name='image_s3_path'),
            preserve_default=False,
        ),
    ]