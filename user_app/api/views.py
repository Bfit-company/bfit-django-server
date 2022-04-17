import boto3
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
import requests
from rest_framework.utils import json
from django.db.models import Q, F, Value as V
from rest_framework.views import APIView

from coach_app.api.serializer import CoachSerializer
from coach_app.models import CoachDB
from person_app.models import PersonDB
from trainee_app.api.serializer import TraineeSerializer
from trainee_app.models import TraineeDB
from rest_framework.authtoken.models import Token
from user_app.models import UserDB
from user_app.api.serializer import RegistrationSerializer

User = get_user_model()


@api_view(['POST', ])
def logout_view(request):
    if request.method == 'POST':
        request.user.auth_token.delete()
        return Response({'success': 'logout successfully'}, status=status.HTTP_200_OK)


@api_view(['POST', ])
def login_view(request):
    if request.method == 'POST':
        data = {}

        if request.data["username"] == '' or request.data["password"] == '':
            data['error'] = "some fields are empty"
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserDB.objects.get(email=request.data["username"])  # get the user_id
        except ObjectDoesNotExist:
            data['error'] = "invalid email"
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if not check_password(request.data['password'], user.password):
            data['error'] = "invalid password"
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        user_id = user.id
        is_coach = False
        try:
            coach = CoachDB.objects.select_related('person').get(Q(person__user=user_id))
            if coach:  # check if the coach exists
                serializer = CoachSerializer(coach)
                data['coach'] = serializer.data
                is_coach = True
        except ObjectDoesNotExist:
            is_coach = False
            print("coach not exist")

        if not is_coach:
            try:
                trainee = TraineeDB.objects.select_related('person').get(Q(person__user=user_id))
                if trainee:  # check if the trainee exists
                    serializer = TraineeSerializer(trainee)
                    data['trainee'] = serializer.data
                    is_coach = False
            except ObjectDoesNotExist:
                data['error'] = "the user do not finish the registration"
                data['user_id'] = user_id
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

        token, created = Token.objects.get_or_create(user=user)
        data["token"] = token.key
        return JsonResponse(data)


@api_view(['POST', ])
def registration_view(request):
    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)

        data = {}

        if serializer.is_valid():
            account = serializer.save()
            data['id'] = account.id
            data['email'] = account.email
            token = Token.objects.get(user=account).key
            data['token'] = token
            data['response'] = 'Registration Successful'

        else:
            if UserDB.objects.filter(email=serializer.data['email']).exists():
                data['error'] = 'Email is already exist !'

            elif serializer.data['email'] == '' or \
                    serializer.data['password'] == '' or \
                    serializer.data['password2'] == '':
                data['error'] = 'Some field is blank !'
            else:
                data['error'] = 'invalid field'
            return Response(data)

        return Response(data)


#
@api_view(['POST', ])
def full_user_create(request):
    data = {}
    BASEURL = 'http://' + get_current_site(request).domain + '/'
    # create person
    person_obj = request.data['person']
    person_obj.update({'user': request.data['person']['user']})
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.post(BASEURL + 'person/person_list/', data=json.dumps(person_obj), headers=headers)
    if response.status_code == status.HTTP_200_OK:
        person = json.loads(response.content)
    else:
        return JsonResponse(json.loads(response.content))

    # check if is coach
    if request.data['person']['is_coach']:
        # create coach
        data["coach"] = {}
        coach_obj = {}
        # coach_obj = request.data['coach']
        coach_obj.update({'person': person["id"]})
        response = requests.post(BASEURL + 'coach/coach_list/', data=coach_obj)
        if response.status_code == status.HTTP_200_OK:
            data['coach'] = json.loads(response.content)
        else:
            data['error'] = json.loads(response.content)

    elif not request.data['person']['is_coach']:
        # create trainee
        data["trainee"] = {}
        # trainee_obj = request.data['trainee']
        trainee_obj = {}
        trainee_obj.update({'person': person["id"]})
        response = requests.post(BASEURL + 'trainee/trainee_list/', data=trainee_obj)
        if response.status_code == status.HTTP_200_OK:
            data['trainee'] = json.loads(response.content)
        else:
            data['error'] = json.loads(response.content)
    # if there is some error while create trainee or coach delete person
    if "error" in data.keys():
        PersonDB.objects.filter(id=person["id"]).delete()

    return JsonResponse(data, safe=False)


def isValidateUserRegister(password, password2, email):
    if password != password2:
        return {'error': 'passwords invalid'}

    if User.objects.filter(email=email).exists():
        return {'error': 'Email already exist!'}

    return True


class UpdateUser(APIView):

    def put(self, request, pk):
        coach = get_object_or_404(CoachDB, pk=pk)
        serializer = CoachSerializer(coach, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(person=request.data["person"])
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth.models import User
from user_app.api.serializer import ChangePasswordSerializer
from rest_framework.permissions import IsAuthenticated


class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# from django.shortcuts import render, HttpResponse
# from django.core.mail import send_mail as sm
#
#
# @api_view(['POST', ])
# def send_mail(request):
#     if request.method == 'POST':
#         ses_client = boto3.client("ses", region_name="eu-central-1")
#         CHARSET = "UTF-8"
#
#         response = ses_client.send_email(
#             Destination={
#                 "ToAddresses": [
#                     "abhishek@learnaws.org",
#                 ],
#             },
#             Message={
#                 "Body": {
#                     "Text": {
#                         "Charset": CHARSET,
#                         "Data": "Hello, world!",
#                     }
#                 },
#                 "Subject": {
#                     "Charset": CHARSET,
#                     "Data": "Amazing Email Tutorial",
#                 },
#             },
#             Source="abhishek@learnaws.org",
#         )

        # res = sm(
        #     subject='Subject here',
        #     message='Here is thedjango message.',
        #     from_email='bfit.company1@gmail.com',
        #     recipient_list=['liadhazoot5@gmail.com'],
        #     fail_silently=False,
        # )
        #
        # return HttpResponse(f"Email sent to {res} members")
