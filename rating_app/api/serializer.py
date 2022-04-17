from rest_framework import serializers

from sport_type_app.models import SportTypeDB
from rating_app.models import RatingDB

from django.contrib.auth import get_user_model

User = get_user_model()


class GeneralRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingDB
        fields = "__all__"
        depth = 1


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingDB
        fields = "__all__"


class RatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingDB
        fields = ("id", "person_id", "created")
