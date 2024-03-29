from rest_framework import serializers

from person_app.api.serializer import PersonSerializer
from rating_app.models import RatingDB

from django.contrib.auth import get_user_model

User = get_user_model()


class GeneralRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingDB
        fields = "__all__"
        # depth = 1


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingDB
        fields = "__all__"
        extra_kwargs = {'person_id': {'required': False}}


class AllCoachRatingSerializer(serializers.ModelSerializer):
    person_id = PersonSerializer(read_only=True)

    class Meta:
        model = RatingDB
        fields = ("id","person_id","rating","review")
        extra_kwargs = {'person_id': {'required': False}}


class RatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingDB
        fields = ("id", "person_id", "created")
