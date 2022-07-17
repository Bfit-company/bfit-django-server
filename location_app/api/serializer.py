from rest_framework import serializers

# from coach_app.api.serializer import CoachSerializer
from location_app.models import LocationDB, CountryDB, CityDB
from django.db.models import Q
from django.db import IntegrityError


# def isCoachInCity(city, coach_id):
#     if LocationDB.objects.filter(city=city, coach=coach_id).exists():
#         return True
#     return False


def isLongAndLatExist(long, lat):
    if LocationDB.objects.filter(lat=lat, long=long).exists():
        return True
    return False

def isAddressExist(address,city_pk):
    if LocationDB.objects.filter(Q(city=city_pk), Q(formatted_address=address)).exists():
        return True
    return False



def checkCountry(country):
    country_obj = CountryDB.objects.filter(name=country.name)
    if not country_obj.exists():
        country_obj = CountryDB(name=country.name)
        country_obj.save()
    else:
        country_obj = country_obj.first()
    return country_obj


def checkCity(city):
    if city:
        city_serializer = CitySerializer(data=city)
        city_obj = CityDB.objects.filter(name=city.name,
                                         country=city.country)
        if not city_obj.exists():
            if city_serializer.is_valid():
                city_obj = city_serializer.save()
                print("city saved")
        else:
            city_obj = city_obj.first()
        return city_obj
    return None


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryDB
        fields = "__all__"


class CitySerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    class Meta:
        model = CityDB
        fields = "__all__"

    def create(self, validated_data):
        country = validated_data.pop("country")
        city = validated_data
        country_query = CountryDB.objects.filter(name=country["name"])
        if country_query.exists():  # check if country exists, yes, find country and create city
            country_db = list(country_query)[0]
            city.update({"country":country_db})
            try:
                city_obj = CityDB.objects.create(**city)
            except IntegrityError:
                raise serializers.ValidationError({"error": "city already exists"})

        else: # if country does not exists create new and create city
            country_serializer = CountrySerializer(data=country)
            if country_serializer.is_valid():
                country_obj = country_serializer.save()
                city.update({"country": country_obj})
                city_obj = CityDB.objects.create(**city)
            else:
                raise serializers.ValidationError({"error":country_serializer.errors})

        return city_obj


class LocationSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)

    # def validate(self, data):
    #     """
    #     Check if location exists.
    #     """
    #     if data['lat'] is None and data['long'] is None:
    #         if isCoachInCity(city=data['city'], coach_id=data['coach']):
    #             raise serializers.ValidationError("this location is already exists")
    #     else:
    #         if isLongAndLatExist(long=data['long'], lat=data['lat']):
    #             raise serializers.ValidationError("this location is already exists")
    #
    #     return data

    def create(self, validated_data):
        city_data = validated_data['city']
        lat = validated_data['lat']
        long = validated_data['long']
        formatted_address = validated_data['formatted_address']
        location = validated_data

        # search city
        city_query = CityDB.objects.filter(name=city_data["name"],country__name=city_data["country"]["name"])
        if city_query.exists():
            city_obj = list(city_query)[0]
            city_pk = list(city_query)[0].pk
        else:
            city_serializer = CitySerializer(data=city_data)
            if city_serializer.is_valid():
                city_obj = city_serializer.save(country=city_data["country"])
                city_pk = city_obj.pk

        location_result = LocationDB.objects.filter(city=city_pk, formatted_address=formatted_address, long=long, lat=lat)
        if location_result.exists():
            raise serializers.ValidationError({"error": "this location is already exists",
                                               "location_id": list(location_result)[0].pk})
        else:
            location.update({"city":city_obj})
            location = LocationDB.objects.create(**location)
            return location


    class Meta:
        model = LocationDB
        fields = "__all__"
