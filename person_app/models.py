from django.db import models
from abc import ABC, abstractmethod

from job_type_app.models import JobTypeDB
from sport_type_app.models import SportTypeDB
from phonenumber_field.modelfields import PhoneNumberField

# from trainee_app.models import TraineeDB
from user_app.models import UserDB
from django.conf import settings

User = settings.AUTH_USER_MODEL


# Create your models here.
class PersonDB(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('D', 'Different'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    full_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone_number = PhoneNumberField(blank=True)
    fav_sport = models.ManyToManyField(SportTypeDB)
    profile_image = models.URLField(null=True,
                                    blank=True,
                                    default="https://www.essd.eu/wp-content/uploads/2020/07/ESSD_Hungary-12.jpg")
    business_email = models.EmailField(null=True, blank=False)
    instagram_url = models.URLField(null=True, blank=True)
    youtube_url = models.URLField(null=True, blank=True)
    tiktok_url = models.URLField(null=True, blank=True)
    facebook_url = models.URLField(null=True, blank=True)
    job_type = models.ManyToManyField(JobTypeDB)

    def __str__(self):
        return self.full_name