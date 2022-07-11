from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.
class SportTypeDB(models.Model):
    name = models.CharField(verbose_name='name', max_length=255, unique=True)
    rating = models.IntegerField(default=1, validators=[MaxValueValidator(5), MinValueValidator(1)])
    # sport_image = models.ImageField(null=False, blank=False, upload_to="images/")
    image = models.URLField(null=False, blank=False)


    def __str__(self):
        return self.name
