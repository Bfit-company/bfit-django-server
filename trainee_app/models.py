from django.db import models
from abc import ABC, abstractmethod
from sport_type_app.models import SportTypeDB
from person_app.models import PersonDB
from django.conf import settings


# Create your models here.
class TraineeDB(models.Model):
    person = models.OneToOneField(PersonDB, on_delete=models.CASCADE,related_name='person',unique=True)

    def __str__(self):
        return self.person.full_name
