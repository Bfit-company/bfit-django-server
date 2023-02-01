import json

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from Utils.aws.s3 import S3
from Utils.utils import Utils
from coach_app.models import CoachDB
from config import BUCKET, S3_KEY
from job_type_app.models import JobTypeDB
from person_app.api.permissions import PersonUserOrReadOnly
from person_app.api.serializer import PersonSerializer
from person_app.models import PersonDB
from rest_framework.response import Response
from sport_type_app.models import SportTypeDB
from trainee_app.models import TraineeDB
from rest_framework.views import APIView

from user_app.models import UserDB


class PersonList(APIView):
    def get(self, request):
        all_trainee_list = PersonDB.objects.all()
        serializer = PersonSerializer(all_trainee_list, many=True)
        return Response(serializer.data)

    def post(self, request):
        create_person(request.data)


def person_validate(data):
    res = {}
    if data["phone_number"] and phone_number_exists(data["phone_number"]):
        res = {"error": "invalid phone number"}

    if len(data["fav_sport"]) == 0:
        res = {"error": "fav_sport cannot be empty"}

    return res


def add_fav_sport(data, serializer):
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


def add_job_type(person_obj, data, serializer):
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
            person_obj = add_job_type(person_obj, data, serializer)
        except Exception as ex:
            return Response({"error": "invalid data"}, status=status.HTTP_400_BAD_REQUEST)

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


def update_person(data, pk, person, profile_img):
    data.update({"profile_image_s3_path": Utils.profile_img_s3_path(file=profile_img,
                                                                    email=person.user.email)})
    serializer = PersonSerializer(person, data=data, partial=True)
    if serializer.is_valid():
        if data.get('phone_number') and phone_number_exists(data["phone_number"], pk):
            return Response({"error": "Phone number already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # check if there is change in fav_sports
        if data.get("fav_sport"):
            serializer.save(fav_sport=data.get("fav_sport"))
        else:
            serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PersonDetail(APIView):
    permission_classes = [PersonUserOrReadOnly]

    def get(self, request, pk):
        person = get_object_or_404(PersonDB, pk=pk)
        serializer = PersonSerializer(person)
        return Response(serializer.data)

    def put(self, request, pk):
        request_data = request.data["user_data"]
        request_data = json.loads(request_data)  # str to dict
        profile_img = request.data.get("file")

        person = get_object_or_404(PersonDB, pk=pk)
        self.check_object_permissions(request, person)
        return update_person(data=request_data, pk=pk, person=person, profile_img=profile_img)

    def delete(self, request, pk):
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


class IsPhoneNumberExists(APIView):
    permission_classes = [AllowAny]

    def get(self, request, phone_number):
        if Utils.is_phone_number_valid(phone_number):
            is_exists = phone_number_exists(phone_number=phone_number)
            return Response({"result": is_exists}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "invalid phone number"}, status=status.HTTP_400_BAD_REQUEST)


class UploadProfileImage(APIView):

    def post(self, request, pk):
        person = PersonDB.objects.select_related('user').get(id=pk)
        file = request.data.get('file')

        s3 = S3()
        s3_key = S3_KEY.format(
            user=person.user.email,
            image_type="profile_image",
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

# def change_person_image(person_serializer, profile_img):
#         try:
#             # person = request_data.get("person")
#             person.update({"profile_image_s3_path": Utils.profile_img_s3_path(file=profile_img,
#                                                                               email=person.user.email)})
#         except Exception as ex:
#             raise {"error": "could not success to save profile image",
#                    "Exception": ex}
#
#         person_serializer.save()
