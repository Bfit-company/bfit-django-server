from django.contrib import admin
from location_app.models import LocationDB,CityDB,CountryDB


admin.site.register(LocationDB)
admin.site.register(CityDB)
admin.site.register(CountryDB)