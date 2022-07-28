
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes

from Utils.aws.s3 import S3
from Utils.utils import Utils
from coach_app.api.serializer import CoachSerializer
from coach_app.models import CoachDB
from config import BUCKET,S3_KEY
from job_type_app.models import JobTypeDB
from person_app.api.serializer import PersonSerializer
from person_app.models import PersonDB
from rest_framework.response import Response

from sport_type_app.models import SportTypeDB
from trainee_app.models import TraineeDB
from rest_framework.views import APIView

from user_app.models import UserDB


class PersonList(APIView):
    def get(self,request):
        all_trainee_list = PersonDB.objects.all()
        serializer = PersonSerializer(all_trainee_list, many=True)
        return Response(serializer.data)

    def post(self,request):
        create_person(request.data)

def person_validate(data):
    res = {}
    if data["phone_number"] and phone_number_exists(data["phone_number"]):
        res = {"error": "invalid phone number"}

    if len(data["fav_sport"]) == 0:
        res = {"error": "fav_sport cannot be empty"}

    return res


def add_fav_sport(data,serializer):
    # add favorite sport to coach list
    fav_arr = []
    for fav in data["fav_sport"]:
        fav_obj = SportTypeDB.objects.get(pk=fav)
        fav_arr.append(fav_obj)

    # create person
    person_obj = serializer.save()
    for fav in fav_arr:
        person_obj.fav_sport.add(fav)
    person_obj.save()
    return person_obj

def add_job_type(person_obj,data,serializer):
    job_arr = []
    for fav in data["job_type"]:
        job_obj = JobTypeDB.objects.get(pk=fav)
        job_arr.append(job_obj)

    # create person
    for fav in job_arr:
        person_obj.job_type.add(fav)
    person_obj.save()
    return person_obj

def create_person(data):
    serializer = PersonSerializer(data=data)
    if serializer.is_valid():

        validation = person_validate(data)
        if validation.get("error"):
            return Response(validation, status=status.HTTP_400_BAD_REQUEST)
        try:
            person_obj = add_fav_sport(data, serializer)
            person_obj = add_job_type(person_obj,  data, serializer)
        except Exception as ex:
            return Response({"error": "invalid data"},status=status.HTTP_400_BAD_REQUEST)

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


class UploadProfileImage(APIView):

    def post(self, request, pk):
        person = PersonDB.objects.select_related('user').get(id=pk)
        image_type = request.data.get('image_type')
        file = request.data.get('file')

        s3 = S3()
        s3_key = S3_KEY.format(
            user=person.user.email,
            image_type=image_type,
            ts_day=Utils.get_ts_today(),
            filename=file.name
        )
        s3.upload_file_obj(file=file, bucket=BUCKET, s3_key=s3_key)

        payload = {"profile_image_s3_path": f's3://{BUCKET}/{s3_key}'}
        person = get_object_or_404(PersonDB, pk=pk)
        serializer = PersonSerializer(person, data=payload, partial=True)  # set partial=True to update a data partially
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data="wrong parameters")