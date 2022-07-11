from django.db import models
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class JobTypeDB(models.Model):
    name = models.CharField(verbose_name='name', max_length=255, unique=True)
    content_type = models.OneToOneField(ContentType, on_delete=models.CASCADE, unique=True)


    def __str__(self):
        return self.name
