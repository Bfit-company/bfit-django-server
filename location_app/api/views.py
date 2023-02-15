import location as location
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F, Value as V
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from Utils.utils import Utils
from coach_app.models import CoachDB
from location_app.models import LocationDB, CountryDB, CityDB
from location_app.api.serializer import LocationSerializer, CitySerializer, CountrySerializer

from rest_framework.views import APIView

from geopy.distance import distance


# def checkCountry(country):
#     country_obj = CountryDB.objects.filter(name=country['name'])
#     if not country_obj.exists():
#         country_obj = CountryDB(name=country['name'])
#         country_obj.save()
#     else:
#         country_obj = country_obj.first()
#     return country_obj
#
#
# def checkCity(city):
#     if city:
#         city_serializer = CitySerializer(data=city)
#         city_obj = CityDB.objects.filter(name=city['name'],
#                                          country=city['country'])
#
#         if not city_obj.exists():
#             if city_serializer.is_valid():
#                 city_obj = city_serializer.save()
#                 print("city saved")
#         else:
#             city_obj = city_obj.first()
#         return city_obj
#     return None

def distance_location(long, lat, filtered_coach_list=None):
    '''
    create a sorted list of all the locations that close to the current user
    '''
    user_cord = (long, lat)
    distance_list = []
    serializer_dict = {}
    if filtered_coach_list is None:
        coaches = list(CoachDB.objects.filter(locations__long__isnull=False, locations__lat__isnull=False))
    else:
        coaches = list(filtered_coach_list)
    for coach in coaches:
        coach_locations = list(coach.locations.all())
        for location in coach_locations:
            coach_cord = (location.long, location.lat)
            distance_dict = {
                "distance": distance(user_cord, coach_cord).km,
                "coach": coach
            }
            distance_list.append(distance_dict)
    sorted_distance_list = sorted(distance_list, key=lambda d: d['distance'])
    for distance_item in sorted_distance_list:
        serializer_dict[distance_item["coach"].id] = distance_item["coach"]
    return list(serializer_dict.values())


def create_location(data):
    city = data.get("city")
    location_obj = data
    serializer = LocationSerializer(data=location_obj)
    if serializer.is_valid():
        try:
            response = serializer.save(city=city)
        except ObjectDoesNotExist:
            return Response("not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response(ex.args, status=status.HTTP_404_NOT_FOUND)
        if not isinstance(response, LocationDB):  # if there is some error
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LocationList(APIView):
    def get(self, request):
        location_list = LocationDB.objects.all()
        serializer = LocationSerializer(location_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        return create_location(request.data)


class LocationDetail(APIView):
    # permission_classes = [PostUserOrReadOnly, AdminOrReadOnly]
    def get(self, request, pk):
        location = get_object_or_404(LocationDB, pk=pk)
        serializer = LocationSerializer(location)
        return Response(serializer.data)

    def put(self, request, pk):
        location = get_object_or_404(LocationDB, pk=pk)
        self.check_object_permissions(request, location)
        serializer = LocationSerializer(location, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        location = get_object_or_404(LocationDB, pk=pk)
        location.delete()
        return Response("Delete Successfully", status=status.HTTP_200_OK)


class CityList(APIView):
    def get(self, request):
        city_list = CityDB.objects.all()
        serializer = CitySerializer(city_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(country=request.data["country"])
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CityDetail(APIView):
    # permission_classes = [PostUserOrReadOnly, AdminOrReadOnly]

    def get(self, request, pk):
        city = get_object_or_404(CityDB, pk=pk)
        serializer = CitySerializer(city)
        return Response(serializer.data)

    def put(self, request, pk):
        city = get_object_or_404(CityDB, pk=pk)
        self.check_object_permissions(request, city)
        serializer = CitySerializer(city, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        city = get_object_or_404(CityDB, pk=pk)
        city.delete()
        return Response("Delete Successfully", status=status.HTTP_200_OK)


class CountryList(APIView):
    def get(self, request):
        country_list = CountryDB.objects.all()
        serializer = CountrySerializer(country_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CountrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CountryDetail(APIView):
    # permission_classes = [PostUserOrReadOnly, AdminOrReadOnly]

    def get(self, request, pk):
        country = get_object_or_404(CountryDB, pk=pk)
        serializer = CountrySerializer(country)
        return Response(serializer.data)

    def put(self, request, pk):
        country = get_object_or_404(CountryDB, pk=pk)
        self.check_object_permissions(request, country)
        serializer = CountrySerializer(country, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        country = get_object_or_404(CountryDB, pk=pk)
        country.delete()
        return Response("Delete Successfully", status=status.HTTP_200_OK)


class GetLocationsDetailByLocationList(APIView):
    def post(self, request):
        locations = LocationDB.objects.filter(id__in=request.data['locations_id'])
        if locations.exists():
            serializer = LocationSerializer(locations, many=True)
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response({"error": "not found"}, status.HTTP_404_NOT_FOUND)
