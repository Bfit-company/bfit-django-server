# Generated by Django 4.0.4 on 2022-08-18 23:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdb',
            name='auth_provider',
            field=models.CharField(default='email', max_length=255),
        ),
    ]
