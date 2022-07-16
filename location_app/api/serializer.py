from rest_framework import serializers

# from coach_app.api.serializer import CoachSerializer
from location_app.models import LocationDB, CountryDB, CityDB
from django.db.models import Q


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
    class Meta:
        model = CityDB
        fields = "__all__"


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
        city_obj = checkCity(city_data)
        city_pk = int(city_obj.pk)
        lat = validated_data['lat']
        long = validated_data['long']
        formatted_address = validated_data['formatted_address']

        if LocationDB.objects.filter(city=city_pk,formatted_address=formatted_address,long=long,lat=lat).exists():
            raise serializers.ValidationError({"error":"this location is already exists"})
        else:
            location = LocationDB.objects.create(**validated_data)
            return location


    class Meta:
        model = LocationDB
        fields = "__all__"
