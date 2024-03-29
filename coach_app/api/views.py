import json

from django.db.models import Q
from rest_framework import status, permissions, authentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.db.models import QuerySet
from Utils.pagination import CustomPageNumberPagination
from Utils.utils import Utils
from coach_app.api.permissions import CoachUserOrReadOnly
from coach_app.api.serializer import CoachSerializer
from coach_app.models import CoachDB
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from random import shuffle
from location_app.api.views import create_location, distance_location
from person_app.api.serializer import PersonSerializer
from person_app.models import PersonDB
from rest_framework import generics

MAX_LIMIT = 100


def add_locations(locations, coach_obj):
    location_pk_arr = []
    for location in locations:
        response = create_location(location)
        location_pk_arr.append(response.data["id"])

    for location_pk in location_pk_arr:
        coach_obj.locations.add(location_pk)
    coach_obj.save()
    return coach_obj


def create_coach(data):
    serializer = CoachSerializer(data=data)
    if serializer.is_valid():
        try:
            person_id = data.get("person")
            person_check = CoachDB.objects.filter(person=person_id)
            person_coach = PersonDB.objects.get(pk=person_id)
            person_serializer = PersonSerializer(person_coach)
            # check if the person is not coach
            if "coach" not in person_serializer.data["job_type"]:
                return Response({"error": "the user is not coach"})
            if not person_check.exists():
                if person_serializer.data["phone_number"] == "" or person_serializer.data["phone_number"] == None:
                    return Response({"error": "Phone number is required"})
                coach_obj = serializer.save(person=PersonDB.objects.get(pk=person_id))
                coach_obj = add_locations(data["locations"], coach_obj)
                coach_serializer = CoachSerializer(coach_obj)
                return Response(coach_serializer.data)
            else:
                return Response({"error": "the coach already exist"})
        except Exception as ex:
            return Response({"error": ex})
    else:
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAdminUser])
def coach_list(request):
    if request.method == 'GET':
        all_trainee_list = CoachDB.objects.all()
        serializer = CoachSerializer(all_trainee_list, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        return create_coach(request.data)


# @api_view(['GET', 'DELETE', 'PUT'])
# def coach_detail(request, pk):
class CoachDetail(APIView):
    permission_classes = [CoachUserOrReadOnly, permissions.IsAuthenticated]

    def get(self, request, pk):
        coach = get_object_or_404(CoachDB, pk=pk)
        serializer = CoachSerializer(coach)
        return Response(serializer.data)

    def put(self, request, pk):
        request_data = request.data["user_data"]
        request_data = json.loads(request_data)  # str to dict
        profile_img = request.data.get("file")

        coach = get_object_or_404(CoachDB, pk=pk)
        self.check_object_permissions(request, coach)
        serializer = CoachSerializer(coach, data=request_data, partial=True)

        if serializer.is_valid():
            if profile_img != '' and profile_img is not None:  # save profile image if exists
                try:
                    person = request_data.get("person")
                    person.update({"profile_image_s3_path": Utils.profile_img_s3_path(file=profile_img,
                                                                                      email=coach.person.user.email)})
                except Exception as ex:
                    raise {"error": "could not success to save profile image",
                           "Exception": ex}

            serializer.save(person=request_data.get("person"), locations=request_data.get("locations"), )

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        trainee = get_object_or_404(CoachDB, pk=pk)
        trainee.delete()
        return Response("Delete Successfully", status=status.HTTP_200_OK)


# find trainee by full name (first 10 matches)
@api_view(['GET'])
def find_coach_by_name(request, name):
    if request.method == 'GET':
        if name is None:
            return Response("name is empty")

        name = name.strip()
        coaches = CoachDB.objects.select_related('person').filter(
            Q(person__full_name__icontains=name))[:10]

        serializer = CoachSerializer(coaches, many=True)
        return Response(serializer.data)


# get coach list by sport type
@api_view(['GET'])
def coach_list_by_sport_type(request, pk):
    if request.method == 'GET':
        if pk is None:
            return Response("pk is empty")

        # get coach list by sport type
        coaches = list(CoachDB.objects.select_related('person').filter(
            Q(person__fav_sport=pk))[:10])
        shuffle(coaches)  # shuffle the query

        serializer = CoachSerializer(coaches, many=True)
        return Response(serializer.data)


# get coach list by rating
@api_view(['GET'])
def coach_list_sorted_by_rating(request):
    if request.method == 'GET':
        # get coach list by sport type
        coaches = list(CoachDB.objects.order_by("-rating")[:10])
        shuffle(coaches)  # shuffle the query
        serializer = CoachSerializer(coaches, many=True)
        return Response(serializer.data)


# get coach list by rating
@api_view(['GET'])
def coach_list_sorted_by_date_joined(request):
    if request.method == 'GET':
        # get coach list by sport type
        coaches = list(CoachDB.objects.order_by("-date_joined")[:10])
        shuffle(coaches)  # shuffle the query

        serializer = CoachSerializer(coaches, many=True)
        return Response(serializer.data)


# get coach list search by parameters
@api_view(['GET'])
def coach_list_search_by_parameters(request):
    if request.method == 'GET':

        name = request.query_params.get("name")
        rating = request.query_params.get("rating")
        date_joined = request.query_params.get("date_joined")
        limit = request.query_params.get("limit")
        fav_sport = request.query_params.get("fav_sport")

        if date_joined == '':
            date_joined = '1900-01-01'
        if rating == '':
            rating = '1'
        if limit == '':
            limit = MAX_LIMIT  # max limit
        if fav_sport == '':  # if empty get all sport_type
            fav_sport = ~Q(person__fav_sport=None)  # not equal to None
        else:
            fav_sport = Q(person__fav_sport=fav_sport)

        name = name.strip()
        coaches = list(CoachDB.objects.select_related('person').filter(
            Q(person__full_name__icontains=name) |
            Q(date_joined__gte=date_joined),
            Q(rating__gte=rating),
            fav_sport)[:int(limit)])
    shuffle(coaches)
    serializer = CoachSerializer(coaches, many=True)
    return Response(serializer.data)


# get coach list search by parameters sorted
@api_view(['GET'])
def coach_list_by_parameters_sorted(request):
    if request.method == 'GET':

        name = request.query_params.get("name")
        is_rating_sort = request.query_params.get("rating")
        is_date_joined_sort = request.query_params.get("date_joined")
        limit = request.query_params.get("limit")
        fav_sport = request.query_params.get("fav_sport")

        name = name.strip()
        if limit == '':
            limit = MAX_LIMIT  # max limit
        if fav_sport == '':  # if empty get all sport_type
            fav_sport = ~Q(person__fav_sport=None)  # not equal to None
        else:  # fav_sport can be more than one
            sport_type_list = [int(x) for x in fav_sport.split(',')]
            fav_sport = Q(person__fav_sport__in=sport_type_list)

        if is_date_joined_sort != '':
            coaches = list(CoachDB.objects.select_related('person').filter(
                Q(person__full_name__icontains=name), fav_sport)
                           .order_by("-date_joined")[:int(limit)])
        elif is_rating_sort != '':
            coaches = list(CoachDB.objects.select_related('person').filter(
                Q(person__full_name__icontains=name), fav_sport).order_by('-rating')[:int(limit)])
        else:
            coaches = list(CoachDB.objects.select_related('person').filter(
                Q(person__full_name__icontains=name), fav_sport)[:int(limit)])

    shuffle(coaches)
    serializer = CoachSerializer(coaches, many=True)
    return Response(serializer.data)


class ChangeCoachRating(APIView):
    def change_coach_rating(self, coach_id, user_rating, request_method, preview_rating=None):
        coach = get_object_or_404(CoachDB, pk=coach_id)
        if user_rating and coach.number_of_rating is not None:
            new_number_of_rating = coach.number_of_rating  # first initial
            coach_rating = coach.rating

            if request_method == 'POST':
                new_number_of_rating = coach.number_of_rating + 1
            elif request_method == 'DELETE':
                new_number_of_rating = coach.number_of_rating - 1
                user_rating = (-1) * user_rating
            elif request_method == 'PUT':
                if preview_rating is None:
                    return Response({"error": "invalid data"}, status=status.HTTP_400_BAD_REQUEST)
                # reverse the average
                user_rating = user_rating - preview_rating
                new_number_of_rating = coach.number_of_rating

            new_rating = self.calc_new_avg(
                number_of_rating=coach.number_of_rating,
                rating_avg=coach_rating,
                new_rating=user_rating,
                new_number_of_rating=new_number_of_rating)

            new_rating = round(new_rating, 1)  # get one digit after dot

            data = {"number_of_rating": new_number_of_rating,
                    "rating": new_rating}
            serializer = CoachSerializer(coach, data=data, partial=True)
            if serializer.is_valid():
                return serializer, Response(serializer.validated_data, status=status.HTTP_200_OK)
            else:
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "invalid data"}, status=status.HTTP_400_BAD_REQUEST)

    def calc_new_avg(self, number_of_rating, rating_avg, new_rating, new_number_of_rating):
        return ((number_of_rating * rating_avg) + new_rating) / new_number_of_rating

    def put(self, request, pk):
        coach = get_object_or_404(CoachDB, pk=pk)
        if request.data["new_rating"] and coach.number_of_rating is not None:
            new_rating = self.calc_new_avg(
                coach.number_of_rating,
                coach.rating,
                request.data["new_rating"])

            new_number_of_rating = coach.number_of_rating + 1
            data = {"number_of_rating": new_number_of_rating,
                    "rating": new_rating}
            serializer = CoachSerializer(coach, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "invalid data"}, status=status.HTTP_400_BAD_REQUEST)


class ConfirmCoach(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk):
        coach = get_object_or_404(CoachDB, pk=pk)
        # serializer = CoachSerializer(coach)

        if coach:
            if not coach.is_confirmed:
                coach.is_confirmed = True
                coach.save()
                return Response({"msg": "confirmed"}, status=status.HTTP_200_OK)
            else:
                return Response({"msg": "the coach has already confirmed"}, status=status.HTTP_200_OK)
        return Response({"error": "coach does not exist"}, status=status.HTTP_400_BAD_REQUEST)


class CoachesForMap(APIView):

    def get(self, request):
        coaches_with_long_and_lat = CoachDB.objects.filter(locations__long__isnull=False,
                                                           locations__lat__isnull=False).distinct()
        serializer = CoachSerializer(coaches_with_long_and_lat, many=True)
        return Response(serializer.data)


class SearchCoach(generics.ListAPIView):
    serializer_class = CoachSerializer
    pagination_class = CustomPageNumberPagination

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not isinstance(queryset, list) and not isinstance(queryset, QuerySet) and queryset["error"]:
            return Response(queryset, status=400)
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        try:
            name = self.request.query_params.get("name")
            rating = self.request.query_params.get("rating")
            number_of_rating = self.request.query_params.get("number_of_rating")
            price = self.request.query_params.get("price")
            fav_sports = self.request.query_params.get("fav_sport")
            country = self.request.query_params.get("country")
            gender_coach_type = self.request.query_params.get("gender_coach_type")
            city = self.request.query_params.get("city")
            is_train_at_home = self.request.query_params.get("is_train_at_home") == 'true'
            sort_by = self.request.query_params.get("sort_by")
            long = self.request.query_params.get("long")
            lat = self.request.query_params.get("lat")
            # limit = self.request.query_params.get("limit")

            name = name.strip()
            query = Q()
            query = query & Q(is_confirmed=True)  # query just the confirmed coaches
            if name != '' and name is not None:
                query = query & Q(person__full_name__icontains=name)  #
            if fav_sports != '' and fav_sports is not None:  # fav_sport can be more than one
                sport_type_list = [int(x) for x in fav_sports.split(',')]
                query = query & Q(person__fav_sport__in=sport_type_list)
            if rating != '' and rating is not None:
                query = query & Q(rating__gte=rating)
            if country != '' and country is not None:
                query = query & Q(locations__city__country__name__contains=country)
            if city != '' and city is not None:
                query = query & Q(locations__city__name__contains=city)
            if number_of_rating != '' and number_of_rating is not None:
                query = query & Q(number_of_rating__gte=number_of_rating)
            if is_train_at_home != '' and is_train_at_home is not None:
                query = query & Q(is_train_at_home=is_train_at_home)
            if price != '' and price is not None:
                query = query & Q(price__lte=price)
            if gender_coach_type != '' and gender_coach_type is not None:
                query = query & Q(gender_coach_type=gender_coach_type)

            if sort_by != '' and sort_by is not None:
                if sort_by == "location":
                    query = query & Q(locations__long__isnull=False, locations__lat__isnull=False)

                    if long != '' and long is not None and \
                            lat != '' and lat is not None:
                        try:
                            long, lat = check_long_lat(long, lat)
                        except Exception as ex:
                            return {"error": "invalid long and lat"}

                        filtered_coach_list = CoachDB.objects.select_related('person').filter(query)
                        filtered_coach_list = distance_location(long, lat, filtered_coach_list)
                    else:
                        filtered_coach_list = CoachDB.objects.select_related('person').filter(query).order_by("locations__city")
                else:
                    try:
                        filtered_coach_list = CoachDB.objects.select_related('person')\
                            .filter(query)\
                            .order_by(sort_by)\
                            .distinct()
                    except Exception as ex:
                        return {"error": "invalid parameter"}

            else:
                filtered_coach_list = CoachDB.objects.select_related('person')\
                    .filter(query)\
                    .distinct()
        except Exception as ex:
            return {"error": "invalid parameter"}
        return filtered_coach_list

def check_long_lat(long, lat):
    long = float(long)
    lat = float(lat)
    if not (-90 < long < 90) or not (-90 < lat < 90):
        raise
    return long, lat
