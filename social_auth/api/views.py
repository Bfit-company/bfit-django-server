from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from ..api.serializer import GoogleSocialAuthSerializer, AppleSocialAuthSerializer
from .register import register_social_user, login_social_user
from rest_framework.permissions import IsAuthenticated, AllowAny



class SignupAppleSocialAuthView(GenericAPIView):
    serializer_class = AppleSocialAuthSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        """

        POST with "auth_token"

        Send an idtoken as from apple to get user information

        """
        user_data = request.data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        # user_data.pop("auth_token")
        response_data = register_social_user(provider='google', email=data.get("email"), user_data=user_data)
        return response_data

class SignupGoogleSocialAuthView(GenericAPIView):
    serializer_class = GoogleSocialAuthSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        """

        POST with "auth_token"

        Send an idtoken as from google to get user information

        """
        user_data = request.data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        # user_data.pop("auth_token")
        response_data = register_social_user(provider='google', email=data.get("email"), user_data=user_data)
        return response_data


class LoginGoogleSocialAuthView(GenericAPIView):
    serializer_class = GoogleSocialAuthSerializer

    def post(self, request):
        """

        POST with "auth_token"

        Send an idtoken as from google to get user information

        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        return login_social_user(provider="google", email=data.get("email"))

# class FacebookSocialAuthView(GenericAPIView):
#
#     serializer_class = FacebookSocialAuthSerializer
#
#     def post(self, request):
#         """
#
#         POST with "auth_token"
#
#         Send an access token as from facebook to get user information
#
#         """
#
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data = ((serializer.validated_data)['auth_token'])
#         return Response(data, status=status.HTTP_200_OK)
#
#
# class TwitterSocialAuthView(GenericAPIView):
#     serializer_class = TwitterAuthSerializer
#
#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         return Response(serializer.validated_data, status=status.HTTP_200_OK)
