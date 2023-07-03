from django.utils import timezone
from datetime import timedelta
import jwt
import requests

from rest_framework.response import Response
from rest_framework import status

from BfitServer import settings


class Apple:
    """apple class to fetch the user info and return it"""
    name = 'apple'
    ACCESS_TOKEN_URL = 'https://appleid.apple.com/auth/token'
    SCOPE_SEPARATOR = ','
    ID_KEY = 'uid'
    def get_key_and_secret(self):
        headers = {
            'kid': settings.SOCIAL_AUTH_APPLE_KEY_ID
        }

        payload = {
            'iss': settings.SOCIAL_AUTH_APPLE_TEAM_ID,
            'iat': timezone.now(),
            'exp': timezone.now() + timedelta(days=180),
            'aud': 'https://appleid.apple.com',
            'sub': settings.CLIENT_ID,
        }

        client_secret = jwt.encode(
            payload,
            settings.SOCIAL_AUTH_APPLE_PRIVATE_KEY,
            algorithm='ES256',
            headers=headers
        ).decode("utf-8")

        return settings.CLIENT_ID, client_secret
    def validate(self,access_token):
        """
        validate method Queries the Google oAUTH2 api to fetch the user info
        """
        try:
            client_id, client_secret = self.get_key_and_secret()

            headers = {'content-type': "application/x-www-form-urlencoded"}
            data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'code': access_token,
                'grant_type': 'authorization_code',
            }

            res = requests.post(Apple.ACCESS_TOKEN_URL, data=data, headers=headers)
            response_dict = res.json()
            id_token = response_dict.get('id_token', None)
            return id_token

        except:
            return Response("The token is either invalid or has expired", status=status.HTTP_400_BAD_REQUEST)