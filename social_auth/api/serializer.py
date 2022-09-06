from django.contrib.auth import get_user_model
from rest_framework import serializers
# from user_app.models import UserDB
#
# User = get_user_model()

from rest_framework import serializers
from . import google
import os
from rest_framework.exceptions import AuthenticationFailed

from .register import login_social_user


class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = google.Google.validate(auth_token)
        try:
            user_data['sub']
        except:
            raise serializers.ValidationError(
                'The token is invalid or expired. Please login again.'
            )

        if user_data['aud'] != os.environ.get('GOOGLE_CLIENT_ID'):

            raise AuthenticationFailed('oops, who are you?')

        user_id = user_data['sub']
        email = user_data['email']
        name = user_data['name']
        provider = 'google'
        return user_data

