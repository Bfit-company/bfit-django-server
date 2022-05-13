from django.db import models
from person_app.models import PersonDB
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.
class CoachDB(models.Model):
    GENDER_COACH_TYPE = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('FM', 'Female and Male'),
    )
    person = models.OneToOneField(PersonDB, on_delete=models.CASCADE, related_name='coach_detail')
    rating = models.FloatField(validators=[MaxValueValidator(10.0), MinValueValidator(1.0)], blank=True, default=0)
    number_of_rating = models.IntegerField(blank=True, default=0)
    from_price = models.IntegerField(blank=True, default=0)
    to_price = models.IntegerField(blank=True, default=0)
    is_train_at_home = models.BooleanField(default=False)
    gender_coach_type = models.CharField(max_length=2, choices=GENDER_COACH_TYPE)
    description = models.CharField(max_length=255, blank=True)
    date_joined = models.DateTimeField(verbose_name='date_joined', auto_now_add=True)


    # todo:
    # post_id , practice
    def __str__(self):
        return "coach - " + self.person.full_name
