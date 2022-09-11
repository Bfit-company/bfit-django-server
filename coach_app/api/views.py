import json
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from Utils.utils import Utils
from coach_app.api.serializer import CoachSerializer
from coach_app.models import CoachDB
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from random import shuffle
from location_app.api.views import create_location
from person_app.api.serializer import PersonSerializer
from person_app.models import PersonDB
from user_app.models import UserDB


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
                coach_obj = serializer.save(person=PersonDB.objects.get(pk=person_id))
                coach_obj = add_locations(data["locations"], coach_obj)
                coach_serializer = CoachSerializer(coach_obj)
                return Response(coach_serializer.data)
            else:
                return Response({"error": "the coach already exist"})
        except Exception as ex:
            return Response({"error": ex})
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def coach_list(request):
    if request.method == 'GET':
        all_trainee_list = CoachDB.objects.all()
        serializer = CoachSerializer(all_trainee_list, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        return create_coach(request.data)


@api_view(['GET', 'DELETE', 'PUT'])
def coach_detail(request, pk):
    if request.method == 'GET':
        coach = get_object_or_404(CoachDB, pk=pk)
        serializer = CoachSerializer(coach)
        return Response(serializer.data)

    if request.method == 'PUT':
        request_data = request.data["user_data"]
        request_data = json.loads(request_data)  # str to dict
        profile_img = request.data.get("file")
        presign_url = None

        coach = get_object_or_404(CoachDB, pk=pk)
        serializer = CoachSerializer(coach, data=request_data, partial=True)

        # if request.data.get("person"):
        #     response = update_person(request.data["person"], coach.person_id)
        #     if response.status_code != 200:
        #         return Response(response)

        if serializer.is_valid():
            if profile_img != '' and profile_img is not None:  # save profile image if exists
                try:
                    presign_url = Utils.save_profile_img_to_s3(file=profile_img,
                                                               email=coach.person.user.email,
                                                               person_id=coach.person.id)
                except Exception as ex:
                    raise {"error": "could not success to save profile image",
                           "Exception": ex}

            serializer.save(person=request_data.get("person"), locations=request.data.get("locations"))
            if presign_url:
                serializer.data.update({"profile_image_url": presign_url})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
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


MAX_LIMIT = 100


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
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "invalid data"}, status=status.HTTP_400_BAD_REQUEST)


class CoachesForMap(APIView):

    def get(self, request):
        coaches_with_long_and_lat = CoachDB.objects.filter(locations__long__isnull=False,
                                                           locations__lat__isnull=False).distinct()
        serializer = CoachSerializer(coaches_with_long_and_lat, many=True)
        return Response(serializer.data)


class SearchCoach(APIView):

    def get(self, request):
        name = request.query_params.get("name")
        rating = request.query_params.get("rating")
        number_of_rating = request.query_params.get("number_of_rating")
        price = request.query_params.get("price")
        fav_sports = request.query_params.get("fav_sport")
        country = request.query_params.get("country")
        gender_coach_type = request.query_params.get("gender_coach_type")
        city = request.query_params.get("city")
        is_train_at_home = request.query_params.get("is_train_at_home") == 'true'
        limit = request.query_params.get("limit")

        name = name.strip()
        query = Q()
        if name != '' and name is not None:
            query = query & Q(person__full_name__icontains=name)  #
        if limit == '' and limit is not None:
            limit = MAX_LIMIT  # max limit
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

        coaches = list(CoachDB.objects.select_related('person').filter(query)[:int(limit)])

        shuffle(coaches)
        serializer = CoachSerializer(coaches, many=True)
        return Response(serializer.data)
