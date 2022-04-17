from django.db import models
from abc import ABC, abstractmethod
# from person_app.models import PersonDB
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator

from django.conf import settings

from coach_app.models import CoachDB
from person_app.models import PersonDB


# Create your models here.
class RatingDB(models.Model):
    person_id = models.ForeignKey(PersonDB, related_name="rating", on_delete=models.CASCADE)
    rating_coach_id = models.ForeignKey(CoachDB, related_name="rates", on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MaxValueValidator(10), MinValueValidator(1)],
                                 blank=False, null=False, default=3)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        # unique_together = [['person_id', 'rating_coach_id']]
        constraints = [
            models.UniqueConstraint(fields=['person_id', 'rating_coach_id'], name="unique_rates")
        ]

    ordering = ["-created"]

    def __str__(self):
        return f"{self.person_id} rates {self.rating_coach_id}"
