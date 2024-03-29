from django.db import models


class CountryDB(models.Model):
    name = models.CharField(max_length=120, unique=True)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.name


class CityDB(models.Model):
    country = models.ForeignKey(CountryDB, on_delete=models.CASCADE, related_name='city_location')
    name = models.CharField(max_length=120)
    # long = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # place_id = models.CharField(max_length=100, primary_key=True)

    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('country', 'name',)

    def __str__(self):
        return self.name


# Create your models here.
class LocationDB(models.Model):
    # coach = models.ForeignKey(CoachDB, on_delete=models.CASCADE, related_name='location_coach')
    city = models.ForeignKey(CityDB, on_delete=models.CASCADE, related_name='location_city')
    formatted_address = models.CharField(max_length=500, null=True, blank=True)
    # todo: when doing the map add lat long
    # place_id = models.CharField(max_length=100, primary_key=True)
    long = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    lat = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)

    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)

    # class Meta:
    #     unique_together = (('city', 'formatted_address','long','lat'),)

    def __str__(self):
        return 'formatted_address:' + self.formatted_address + ' city: ' + self.city.name
