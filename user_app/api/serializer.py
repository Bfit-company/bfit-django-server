from django.contrib.auth import get_user_model
from rest_framework import serializers
import re
from user_app.models import UserDB
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.response import Response

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'password2', 'last_login', 'auth_provider']
        extra_kwargs = {
            'password': {'write_only': True}
        }
        error_messages = {"password": {"error": "The field is empty"},
                          "password2": {"error": "The field is empty"}}

        # overwrite the save method because the pass2 and validate the email

    def save(self):
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'error': 'passwords invalid'})

        if User.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError({'error': 'Email already exist!'})

        if self.validated_data.get("auth_provider") is None:
            self.validated_data["auth_provider"] = "email"

        account = User(
            email=self.validated_data['email'],
            auth_provider=self.validated_data["auth_provider"]
        )

        # # @#$%^&+=
        # if not re.fullmatch(r'[A-Za-z0-9]{8,}', password):
        #     raise serializers.ValidationError({'error': "The password must contain Capital letter, Number and minimum 8 characters."})

        account.set_password(password)
        account.save()
        return account


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDB
        fields = ('id', 'email')


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


# #todo: in future
# class LoginSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = User
#         fields = ['email', 'password']

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    error_messages = {
        'bad_token': "Token is expired or invalid"
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            return Response({"error":"Token is expired or invalid"})
