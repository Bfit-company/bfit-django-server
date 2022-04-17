from rest_framework import serializers
from sport_type_app.models import SportTypeDB


class SportTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = SportTypeDB
        fields = '__all__'
