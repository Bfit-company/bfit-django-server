from django.core.exceptions import ObjectDoesNotExist
from requests import Response
from rest_framework import serializers, status
from person_app.models import PersonDB
from datetime import date

from post_app.api.serializer import PostSerializer
from rating_app.api.serializer import RatingSerializer
from sport_type_app.api.serializer import SportTypeSerializer


class PersonRelatedField(serializers.StringRelatedField):
    def to_representation(self, value):
        return PersonSerializer(value, many=False).data

    def to_internal_value(self, data):
        return data


class PersonSerializer(serializers.ModelSerializer):
    fav_sport = SportTypeSerializer(many=True, read_only=True)
    post = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    rating_coach = serializers.SerializerMethodField()

    class Meta:
        model = PersonDB
        fields = "__all__"

    # def save(self):
    #     phone_number = self.validated_data['phone_number']
    #
    #     if PersonDB.objects.filter(phone_number=phone_number).exists():
    #         raise serializers.ValidationError({'error': 'invalid phone number'})
    #
    #     account = User(
    #         email=self.validated_data['email'],
    #     )
    #     account.set_password(password)
    #     account.save()
    #     return account

    def get_rating_coach(self, obj):
        return RatingSerializer(obj.rating.all(), many=True).data

    def validate_birth_date(self, value):
        if self.calculate_age(born=value) <= 13:
            raise serializers.ValidationError("Age must be 13 and above")
        return value

    # calculate the age
    def calculate_age(self, born):
        today = date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
