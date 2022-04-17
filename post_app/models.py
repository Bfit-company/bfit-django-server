from django.db import models
from django.utils.text import slugify

from person_app.models import PersonDB
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.
class PostDB(models.Model):
    person = models.ForeignKey(PersonDB, on_delete=models.CASCADE, related_name='post')
    title = models.CharField(max_length=120)
    # slug = models.SlugField(unique=True)
    image = models.URLField(null=True,
                            blank=True,
                            default="https://www.essd.eu/wp-content/uploads/2020/07/ESSD_Hungary-12.jpg")
    # height_field = models.IntegerField(default=0)
    # width_field = models.IntegerField(default=0)
    # draft = models.BooleanField(default=False)
    body = models.TextField(null=True, blank=True)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)

    # updated = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.title

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = slugify(self.title)
    #     return super().save(*args, **kwargs)


