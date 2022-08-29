from django.contrib.auth import authenticate
# from authentication.models import User
import os
import random
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model

from user_app.api.views import create_full_user, login_user

User = get_user_model()


def generate_username(name):
    username = "".join(name.split(' ')).lower()
    if not User.objects.filter(username=username).exists():
        return username
    else:
        random_username = username + str(random.randint(0, 1000))
        return generate_username(random_username)


def register_social_user(provider, email, user_data):
    filtered_user_by_email = User.objects.filter(email=email)

    if filtered_user_by_email.exists():

        if provider == filtered_user_by_email[0].auth_provider:
            login_data = {
                "username": email,
                "password": os.environ.get('SOCIAL_SECRET')
            }
            return login_user(login_data)
            # registered_user = authenticate(
            #     email=email, password=os.environ.get('SOCIAL_SECRET'))
            #
            # return {
            #     'username': registered_user.username,
            #     'email': registered_user.email,
            #     'tokens': registered_user.tokens()}

        else:
            raise AuthenticationFailed(
                detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)

    else:
        return create_full_user(user_data)
