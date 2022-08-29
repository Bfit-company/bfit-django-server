from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework.response import Response
from rest_framework import status


class Google:
    """Google class to fetch the user info and return it"""

    @staticmethod
    def validate(auth_token):
        """
        validate method Queries the Google oAUTH2 api to fetch the user info
        """
        try:
            idinfo = id_token.verify_oauth2_token(
                auth_token, requests.Request())

            if 'accounts.google.com' in idinfo['iss']:
                return idinfo

        except:
            return Response("The token is either invalid or has expired", status=status.HTTP_400_BAD_REQUEST)