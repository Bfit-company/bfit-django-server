from django.db.models import Q, F, Value as V
from django.db.models.functions import Concat
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView

from coach_app.api.serializer import CoachSerializer
from coach_app.models import CoachDB
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from random import shuffle

from person_app.api.serializer import PersonSerializer
from person_app.models import PersonDB
from sport_type_app.models import SportTypeDB
from user_app import models


@api_view(['GET', 'POST'])
def coach_list(request):
    if request.method == 'GET':
        all_trainee_list = CoachDB.objects.all()
        serializer = CoachSerializer(all_trainee_list, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = CoachSerializer(data=request.data)
        if serializer.is_valid():
            person_id = request.data.get("person")
            person_check = CoachDB.objects.filter(person=person_id)
            person_coach = PersonDB.objects.get(pk=person_id)
            # check if the person is not coach
            if not person_coach.is_coach:
                return Response({"error": "the user is not coach"})
            if not person_check.exists():
                serializer.save(person=PersonDB.objects.get(pk=person_id))
                return Response(serializer.data)
            else:
                return Response({"error": "the coach already exist"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE', 'PUT'])
def coach_detail(request, pk):
    if request.method == 'GET':
        coach = get_object_or_404(CoachDB, pk=pk)
        serializer = CoachSerializer(coach)
        return Response(serializer.data)

    if request.method == 'PUT':
        coach = get_object_or_404(CoachDB, pk=pk)
        serializer = CoachSerializer(coach, data=request.data)
        if serializer.is_valid():
            coach.person = get_object_or_404(PersonDB, pk=request.data["person"])
            coach.description = request.data["description"]
            coach.rating = request.data["rating"]
            coach.save()

            serializer = CoachSerializer(coach)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

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


class SearchCoach(APIView):
    def post(self, request):

        name = request.data["name"]
        rating = request.data["rating"]
        number_of_rating = request.data["number_of_rating"]
        start_price = request.data["start_price"]
        end_price = request.data["end_price"]
        fav_sports = request.data["fav_sport"]
        city = request.data["city"]
        is_train_at_home = request.data["is_train_at_home"]
        limit = request.data["limit"]

        name = name.strip()
        query = Q()
        if name != '':
            query = query & Q(person__full_name__icontains=name)  #
        if limit == '':
            limit = MAX_LIMIT  # max limit
        if fav_sports != '':  # fav_sport can be more than one
            sport_type_list = [fav_sport for fav_sport in fav_sports]
            query = query & Q(person__fav_sport__in=sport_type_list)
        if rating != '':
            query = query & Q(rating__gte=rating)
        if city != '':  # to do
            query = query & Q(location_coach__city__name__contains=city)
        if number_of_rating != '':
            query = query & Q(number_of_rating__gte=number_of_rating)
        if is_train_at_home != '':
            query = query & Q(is_train_at_home=is_train_at_home)
        if start_price != '' and end_price != '':
            query = query & Q(price__range=(start_price, end_price))

        coaches = list(CoachDB.objects.select_related('person').filter(query)[:int(limit)])

        shuffle(coaches)
        serializer = CoachSerializer(coaches, many=True)
        return Response(serializer.data)


class SearchCoach(APIView):
    # def post(self, request):
    #
    #     name = request.data["name"]
    #     rating = request.data["rating"]
    #     number_of_rating = request.data["number_of_rating"]
    #     start_price = request.data["start_price"]
    #     end_price = request.data["end_price"]
    #     fav_sports = request.data["fav_sport"]
    #     city = request.data["city"]
    #     is_train_at_home = request.data["is_train_at_home"]
    #     limit = request.data["limit"]
    #
    #     name = name.strip()
    #     query = Q()
    #     if name != '':
    #         query = query & Q(person__full_name__icontains=name)  #
    #     if limit == '':
    #         limit = MAX_LIMIT  # max limit
    #     if fav_sports != '':  # fav_sport can be more than one
    #         sport_type_list = [fav_sport for fav_sport in fav_sports]
    #         query = query & Q(person__fav_sport__in=sport_type_list)
    #     if rating != '':
    #         query = query & Q(rating__gte=rating)
    #     if city != '':  # to do
    #         query = query & Q(location_coach__city__name__contains=city)
    #     if number_of_rating != '':
    #         query = query & Q(number_of_rating__gte=number_of_rating)
    #     if is_train_at_home != '':
    #         query = query & Q(is_train_at_home=is_train_at_home)
    #     if start_price != '' and end_price != '':
    #         query = query & Q(price__range=(start_price, end_price))
    #
    #     coaches = list(CoachDB.objects.select_related('person').filter(query)[:int(limit)])
    #
    #     shuffle(coaches)
    #     serializer = CoachSerializer(coaches, many=True)
    #     return Response(serializer.data)

    def get(self, request):
        name = request.query_params.get("name")
        rating = request.query_params.get("rating")
        number_of_rating = request.query_params.get("number_of_rating")
        start_price = request.query_params.get("start_price")
        end_price = request.query_params.get("end_price")
        fav_sports = request.query_params.get("fav_sport")
        country = request.query_params.get("country")
        city = request.query_params.get("city")
        is_train_at_home = request.query_params.get("is_train_at_home")
        limit = request.query_params.get("limit")

        name = name.strip()
        query = Q()
        if name != '':
            query = query & Q(person__full_name__icontains=name)  #
        if limit == '':
            limit = MAX_LIMIT  # max limit
        if fav_sports != '':  # fav_sport can be more than one
            sport_type_list = [int(x) for x in fav_sports.split(',')]
            query = query & Q(person__fav_sport__in=sport_type_list)
        if rating != '':
            query = query & Q(rating__gte=rating)
        if country != '':
            query = query & Q(location_coach__city__country__name__contains=country)
        if city != '':
            query = query & Q(location_coach__city__name__contains=city)
        if number_of_rating != '':
            query = query & Q(number_of_rating__gte=number_of_rating)
        if is_train_at_home != '':
            query = query & Q(is_train_at_home=is_train_at_home)
        if start_price != '' and end_price != '':
            query = query & Q(price__range=(start_price, end_price))

        coaches = list(CoachDB.objects.select_related('person').filter(query)[:int(limit)])

        shuffle(coaches)
        serializer = CoachSerializer(coaches, many=True)
        return Response(serializer.data)
