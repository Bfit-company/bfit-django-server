import json

from django.contrib.auth import authenticate
# from authentication.models import User
import os
import random
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from django.contrib.auth import get_user_model
from rest_framework.response import Response

from user_app.api.views import create_full_user, login_user

User = get_user_model()


def generate_username(name):
    username = "".join(name.split(' ')).lower()
    if not User.objects.filter(username=username).exists():
        return username
    else:
        random_username = username + str(random.randint(0, 1000))
        return generate_username(random_username)


def login_social_user(provider, email):
    filtered_user_by_email = User.objects.filter(email=email)

    if filtered_user_by_email.exists():

        if provider == filtered_user_by_email[0].auth_provider:
            login_data = {
                "username": email,
                "password": os.environ.get('SOCIAL_SECRET')
            }
            return login_user(login_data)

        else:
            raise AuthenticationFailed(
                detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)

    else:
        raise ValidationError(
            {"error": "The user does not exists. please signup"}
        )


def register_social_user(provider, email, user_data):
    filtered_user_by_email = User.objects.filter(email=email)

    if filtered_user_by_email.exists():

        if provider == filtered_user_by_email[0].auth_provider:
            login_data = {
                "username": email,
                "password": os.environ.get('SOCIAL_SECRET')
            }
            return login_user(login_data)

        else:
            raise AuthenticationFailed(
                detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)

    else:
        user = {
            "email": email,
            "password": os.environ.get('SOCIAL_SECRET'),
            "password2": os.environ.get('SOCIAL_SECRET'),
            "auth_provider": "google"
        }
        request_data = user_data.get("user_data")
        if request_data is None:
            raise ValidationError({"error": "please register"})
        request_data = json.loads(request_data)
        request_data["user"] = user
        user_data._mutable = True
        user_data["user_data"] = json.dumps(request_data)
        return create_full_user(user_data)