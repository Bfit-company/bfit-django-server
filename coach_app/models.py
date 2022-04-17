from django.db import models
from person_app.models import PersonDB
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.
class CoachDB(models.Model):
    person = models.OneToOneField(PersonDB, on_delete=models.CASCADE, related_name='coach_detail')
    rating = models.FloatField(validators=[MaxValueValidator(10.0), MinValueValidator(1.0)], blank=True, default=0)
    number_of_rating = models.IntegerField(blank=True, default=0)
    price = models.IntegerField(blank=True, default=0)
    is_train_at_home = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True)
    date_joined = models.DateTimeField(verbose_name='date_joined', auto_now_add=True)

    # todo:
    # post_id , practice
    def __str__(self):
        return "coach - " + self.person.full_name
