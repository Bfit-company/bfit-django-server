
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes

from coach_app.api.serializer import CoachSerializer
from coach_app.models import CoachDB
from person_app.api.serializer import PersonSerializer
from person_app.models import PersonDB
from rest_framework.response import Response

from sport_type_app.models import SportTypeDB
from trainee_app.models import TraineeDB
from rest_framework.views import APIView


class PersonList(APIView):
    def get(self,request):
        all_trainee_list = PersonDB.objects.all()
        serializer = PersonSerializer(all_trainee_list, many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer = PersonSerializer(data=request.data)
        if serializer.is_valid():

            if request.data["phone_number"] and phone_number_exists(request.data["phone_number"]):
                return Response({"error": "invalid phone number"}, status=status.HTTP_400_BAD_REQUEST)

            # add favorite sport to coach list
            fav_arr = []
            for fav in request.data["fav_sport"]:
                fav_obj = get_object_or_404(SportTypeDB, pk=fav)
                fav_arr.append(fav_obj)

            # create person
            person_obj = serializer.save()
            for fav in fav_arr:
                person_obj.fav_sport.add(fav)
            person_obj.save()

            serializer = PersonSerializer(person_obj)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def person_validate(data):
    res = {}
    if data["phone_number"] and phone_number_exists(data["phone_number"]):
        res = {"error": "invalid phone number"}

    if len(data["fav_sport"]) == 0:
        res = {"error": "fav_sport cannot be empty"}

    return res

def create_person(data):
    serializer = PersonSerializer(data=data)
    if serializer.is_valid():

        validation = person_validate(data)
        if validation.get("error"):
            return Response(validation, status=status.HTTP_400_BAD_REQUEST)

        # add favorite sport to coach list
        fav_arr = []
        for fav in data["fav_sport"]:
            fav_obj = get_object_or_404(SportTypeDB, pk=fav)
            fav_arr.append(fav_obj)

        # create person
        person_obj = serializer.save()
        for fav in fav_arr:
            person_obj.fav_sport.add(fav)
        person_obj.save()

        serializer = PersonSerializer(person_obj)
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def person_list(request):
    if request.method == 'GET':
        all_trainee_list = PersonDB.objects.all()
        serializer = PersonSerializer(all_trainee_list, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        return create_person(request.data)
        # serializer = PersonSerializer(data=request.data)
        # if serializer.is_valid():
        #
        #     if request.data["phone_number"] and phone_number_exists(request.data["phone_number"]):
        #         return Response({"error": "invalid phone number"}, status=status.HTTP_400_BAD_REQUEST)
        #
        #     # add favorite sport to coach list
        #     fav_arr = []
        #     for fav in request.data["fav_sport"]:
        #         fav_obj = get_object_or_404(SportTypeDB, pk=fav)
        #         fav_arr.append(fav_obj)
        #
        #     # create person
        #     person_obj = serializer.save()
        #     for fav in fav_arr:
        #         person_obj.fav_sport.add(fav)
        #     person_obj.save()
        #
        #     serializer = PersonSerializer(person_obj)
        #     return Response(serializer.data)
        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def update_person(data, pk):
    person = get_object_or_404(PersonDB, pk=pk)
    serializer = PersonSerializer(person, data=data,partial=True)
    if serializer.is_valid():
        if data.get('phone_number') and phone_number_exists(data["phone_number"], pk):
            return Response({"error": "invalid phone number"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE', 'PUT'])
def person_detail(request, pk):
    if request.method == 'GET':
        person = get_object_or_404(PersonDB, pk=pk)
        serializer = PersonSerializer(person)
        return Response(serializer.data)

    if request.method == 'PUT':
        update_person(request.data,pk)

    if request.method == 'DELETE':
        trainee = get_object_or_404(PersonDB, pk=pk)
        trainee.delete()
        return Response("Delete Successfully", status=status.HTTP_200_OK)


# this function checks if the person already used in trainee or coach
def check_if_person_used(data):
    coach_check = CoachDB.objects.filter(person=data)
    trainee_check = TraineeDB.objects.filter(person=data)

    if not trainee_check.exists() and not coach_check.exists():
        return True
    return False


def phone_number_exists(phone_number, person_id=None):
    """
    check if the phone phone number exists in different person
    :param person_id:
    :param phone_number:
    :param person:
    :return:
    """
    response = False
    cur_person = PersonDB.objects.filter(phone_number=phone_number)  # get person by phone number
    if cur_person.exists():  # check if there is a person with this phone number
        # person_serializer = PersonSerializer(cur_person)
        cur_person = cur_person.first()
        response = True
        # check if person sent to function and if it is the same person
        if person_id and cur_person.id == person_id:
            response = False
    return response
