from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, schema, permission_classes
import re
from rest_framework import permissions
from django.core.mail import send_mail

from rest_framework.permissions import AllowAny
from rest_framework import generics
from Utils.utils import Utils
from rest_framework.utils import json
from django.db.models import Q
from rest_framework.views import APIView
from coach_app.api.serializer import CoachSerializer
from coach_app.models import CoachDB
from person_app.api.serializer import PersonSerializer
from person_app.models import PersonDB
from rest_framework.authtoken.models import Token
from user_app.models import UserDB
from user_app.api.serializer import RegistrationSerializer, LogoutSerializer
from rest_framework.schemas import AutoSchema
import coreapi
from person_app.api.views import create_person
from coach_app.api.views import create_coach

User = get_user_model()


class LoginViewSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []
        if method.lower() in ['post', 'put']:
            extra_fields = [
                coreapi.Field('username'),
                coreapi.Field('password')
            ]
        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields


class RegistrationViewSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []
        if method.lower() in ['post', 'put']:
            extra_fields = [
                coreapi.Field('email'),
                coreapi.Field('password'),
                coreapi.Field('password2')
            ]
        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields


def login_user(request_data):
    data = {}

    if request_data["username"] == '' or request_data["password"] == '':
        data['error'] = "some fields are empty"
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = UserDB.objects.get(email=request_data["username"])  # get the user_id
    except ObjectDoesNotExist:
        data['error'] = "invalid email"
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    if not check_password(request_data['password'], user.password):
        data['error'] = "invalid password"
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    is_coach = False
    user_id = user.id
    if user.is_admin and user.is_active:
        token = user.token()
        data["token"] = token
        return JsonResponse(data)
    try:
        coach = CoachDB.objects.select_related('person').get(Q(person__user=user_id))
        if coach:  # check if the coach exists
            serializer = CoachSerializer(coach)
            data = serializer.data
            is_coach = True
            if not data["coach"]["is_confirmed"]:
                return Response({"msg":"the coach is not confirmed (cosch_id = " + data["coach"]["id"] + ")"}, status=status.HTTP_202_ACCEPTED)

    except ObjectDoesNotExist:
        is_coach = False
        print("coach not exist")

    if not is_coach:
        try:
            person = PersonDB.objects.get(user=user_id)
            if person:  # check if the trainee exists
                serializer = PersonSerializer(person)
                data = serializer.data
                is_coach = False
        except ObjectDoesNotExist:
            data['error'] = "the user do not finish the registration"
            data['user_id'] = user_id
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    token = user.token()
    data["token"] = token
    return JsonResponse(data)


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', ])
def logout_view(request):
    """
    **** importent **** add header like this: {"Authorization": Token "userToken"}
    """
    if request.method == 'POST':
        request.user.auth_token.delete()
        return Response({'success': 'logout successfully'}, status=status.HTTP_200_OK)


@api_view(['POST', ])
@schema(LoginViewSchema())
@permission_classes([AllowAny])
def login_view(request):
    if request.method == 'POST':
        return login_user(request.data)


@api_view(['POST', ])
@schema(RegistrationViewSchema())
def registration_view(request):
    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)

        data = {}

        if serializer.is_valid():
            account = serializer.save()
            data['id'] = account.id
            data['email'] = account.email
            # token = Token.objects.get(user=account).key
            token = account.token()
            data['token'] = token
            data['response'] = 'Registration Successful'

        else:
            if UserDB.objects.filter(email=serializer.data['email']).exists():
                data['error'] = 'Email is already exist !'

            elif serializer.data['email'] == '' or \
                    serializer.data['password'] == '' or \
                    serializer.data['password2'] == '':
                data['error'] = 'Some fields are blank !'
            else:
                data['error'] = 'invalid field'
            return Response(data)

        return Response(data)


def user_registration_validate(data):
    password = data['password']
    password2 = data['password2']

    # check blank fields
    if data['email'] == '' or \
            data['password'] == '' or \
            data['password2'] == '':
        return Response({'error': 'Some fields are blank'}, status=status.HTTP_400_BAD_REQUEST)

    # check email validation
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(email_regex, data['email']):
        return Response({'error': "Email Invalid "}, status=status.HTTP_400_BAD_REQUEST)

    # check 2 passwords
    if password != password2:
        return Response({'error': 'Passwords Invalid'}, status=status.HTTP_400_BAD_REQUEST)

    # check email exists
    if User.objects.filter(email=data['email']).exists():
        return Response({'error': 'Email already exist'}, status=status.HTTP_400_BAD_REQUEST)

    # check password validation
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&`~$%^()-=+_{}><:;\|[,\].\"\'])[A-Za-z\d@$!%*#?&`~$%^()-=+_{}><:;\]|[,.\"\']{8,18}$"
    match_re = re.compile(reg)
    res = re.search(match_re, password)

    if not res:
        return Response({'error': "The password must contain Capital letter, Number, Symbol and minimum 8 characters."},
                        status=status.HTTP_400_BAD_REQUEST)

    return Response({"msg": "Validation successfully complete"}, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([AllowAny])
def register_validation(request):
    if request.method == 'POST':
        return user_registration_validate(request.data)


def register(user_data):
    response = user_registration_validate(user_data)
    if not response.status_code == status.HTTP_200_OK:
        return response

    serializer = RegistrationSerializer(data=user_data)
    data = {}

    if serializer.is_valid():
        account = serializer.save()
        data['id'] = account.id
        data['email'] = account.email
        token = account.token()
        # token = Token.objects.get(user=account).key
        data['token'] = token
        data['response'] = 'Registration Successful'
    else:
        return Response({"error": 'invalid field'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(data)


@api_view(['POST', ])
# @schema(CreateFullUserViewSchema())
@permission_classes([AllowAny])
def full_user_create(request):
    if request.method == 'POST':
        return create_full_user(request.data)


def create_full_user(data):
    '''
         create full user with all the parameters
         UI send form data because image file
     '''
    is_coach = False
    request_data = data["user_data"]
    request_data = json.loads(request_data)  # str to dict
    profile_img = data.get("file")
    response = register(request_data["user"])
    if response.status_code == status.HTTP_200_OK:
        token = response.data["token"]
        # create person
        person_obj = request_data['person']
        person_obj.update({'user': response.data["id"]})
        response = create_person(person_obj)

        if response.status_code == status.HTTP_200_OK:
            person = response.data
            data = person
        else:
            UserDB.objects.filter(id=person_obj["user"]).delete()
            return response

        # check if is coach
        job_type_name = Utils.get_job_type_name(job_list=request_data['person']['job_type'])
        if "coach" in job_type_name:
            # create coach
            if "coach" in request_data:
                coach_obj = request_data["coach"]
                coach_obj.update({'person': person["id"]})
                response = create_coach(coach_obj)
                if response.status_code == status.HTTP_200_OK:
                    data = response.data
                    is_coach = True
                else:
                    data['error'] = response.data
            else:
                data['error'] = "invalid data"

        if "error" in data.keys():
            PersonDB.objects.filter(id=person["id"]).delete()
            UserDB.objects.get(pk=person["user"]).delete()
            return JsonResponse({"error":data["error"]}, status=status.HTTP_400_BAD_REQUEST, safe=False)
        else:  # the user created successfully
            if profile_img != '' and profile_img is not None:  # save profile image if exists
                try:
                    profile_img_presign_url = Utils.save_profile_img_to_s3(file=profile_img,
                                                                           email=request_data.get("user").get("email"),
                                                                           person_id=person["id"])
                    data.update({'profile_image_url': profile_img_presign_url})
                    # return JsonResponse(data, safe=False)
                except Exception as ex:
                    UserDB.objects.get(pk=data["user"]).delete()
                    return Response({"error": "could not success to save profile image"},
                                    status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(response.data, status=status.HTTP_400_BAD_REQUEST)

    data.update({'token': token})
    if is_coach:
        send_mail(
            # title:
            "New Coach {}".format(person["full_name"]),
            # message:
            f'full_name {person["full_name"]}, '
            f'phone_number {person["phone_number"]}, '
            f'coach_id {data["coach"]["id"]}, '
            f'user_id {person["user"]},'
            f'person_id {person["id"]}',
            # from:
            "noreplay@bfitapp.net",
            # to:
            ["bfit.company1@gmail.com"]
        )
        return Response({"msg": "the coach need to be confirmed "+ "coach_id "+ str(data["coach"]["id"])}, status=status.HTTP_202_ACCEPTED)
    return Response(response.data, status=status.HTTP_201_CREATED)


# work
# @api_view(['POST', ])
# # @schema(CreateFullUserViewSchema())
# def full_user_create(request):
#     data = {}
#     BASEURL = 'http://' + get_current_site(request).domain + '/'
#     # create person
#     person_obj = request.data['person']
#     person_obj.update({'user': request.data['person']['user']})
#     headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
#     response = requests.post(BASEURL + 'person/person_list/', data=json.dumps(person_obj), headers=headers)
#     if response.status_code == status.HTTP_200_OK:
#         person = json.loads(response.content)
#     else:
#         return JsonResponse(json.loads(response.content))
#
#     # check if is coach
#     if request.data['person']['is_coach']:
#         # create coach
#         data["coach"] = {}
#         coach_obj = {}
#         # coach_obj = request.data['coach']
#         coach_obj.update({'person': person["id"]})
#         response = requests.post(BASEURL + 'coach/coach_list/', data=coach_obj)
#         if response.status_code == status.HTTP_200_OK:
#             data['coach'] = json.loads(response.content)
#         else:
#             data['error'] = json.loads(response.content)
#
#     elif not request.data['person']['is_coach']:
#         # create trainee
#         data["trainee"] = {}
#         # trainee_obj = request.data['trainee']
#         trainee_obj = {}
#         trainee_obj.update({'person': person["id"]})
#         response = requests.post(BASEURL + 'trainee/trainee_list/', data=trainee_obj)
#         if response.status_code == status.HTTP_200_OK:
#             data['trainee'] = json.loads(response.content)
#         else:
#             data['error'] = json.loads(response.content)
#     # if there is some error while create trainee or coach delete person
#     if "error" in data.keys():
#         PersonDB.objects.filter(id=person["id"]).delete()
#
#     return JsonResponse(data, safe=False)


def isValidateUserRegister(password, password2, email):
    if password != password2:
        return {'error': 'passwords invalid'}

    if User.objects.filter(email=email).exists():
        return {'error': 'Email already exist!'}

    return True


class UpdateUser(APIView):

    # def put(self, request):
    #     try:
    #         data = {}
    #         person_entity = PersonDB()  # does not must
    #         if request.data["coach"]:
    #             data = request.data["coach"]
    #             person_entity = get_object_or_404(CoachDB, pk=request.data["coach"]["id"])
    #             serializer = CoachSerializer(person_entity, data=data, partial=True)
    #
    #         elif request.data["trainee"]:
    #             data = request.data["trainee"]
    #             person_entity = get_object_or_404(CoachDB, pk=request.data["trainee"]["id"])
    #             serializer = TraineeSerializer(person_entity, data=data, pertial=True)
    #
    #         if data.get("person"):
    #             response = update_person(data["person"], person_entity.person_id)
    #             if response.status_code != 200:
    #                 return Response(response)
    #
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response(serializer.data, status=status.HTTP_200_OK)
    #         else:
    #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     except Exception as ex:
    #         return Response(ex, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = get_object_or_404(UserDB, pk=pk)
        # logout
        token = Token.objects.filter(user_id=pk)
        if token.exists():
            token.delete()
        user.delete()
        return Response("Delete Successfully", status=status.HTTP_200_OK)


from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
# from django.contrib.auth.models import User
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
                return Response({"error": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'msg': 'Password updated successfully'
            }

            return Response(response)

        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserDetails(APIView):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        person = get_object_or_404(PersonDB, user=pk)  # get the person from the user_id
        person_serializer = PersonSerializer(person)
        if "coach" in person_serializer.data["job_type"]:
            coach = get_object_or_404(CoachDB, person=person.pk)  # get the coach from the person id
            coach_serializer = CoachSerializer(coach)
            return Response(coach_serializer.data)

        else:  # the user is trainee (person)
            return Response(person_serializer.data)
