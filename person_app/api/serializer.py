
from rest_framework import serializers, status

from Utils.aws.presign_url import PresignUrl
from person_app.models import PersonDB
from datetime import date
from rating_app.api.serializer import RatingSerializer
from sport_type_app.api.serializer import SportTypeSerializer


class PersonRelatedField(serializers.StringRelatedField):
    def to_representation(self, value):
        return PersonSerializer(value, many=False).data

    def to_internal_value(self, data):
        return data


class PersonSerializer(serializers.ModelSerializer):
    fav_sport = SportTypeSerializer(many=True, read_only=True)
    job_type = serializers.StringRelatedField(many=True, read_only=True)
    post = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    rating_coach = serializers.SerializerMethodField()

    class Meta:
        model = PersonDB
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        profile_image_s3_path = data.pop('profile_image_s3_path')
        if profile_image_s3_path is not None and profile_image_s3_path is not '':
            data["profile_image_url"] = PresignUrl().create_presigned_url(profile_image_s3_path)
        return data
    # def create(self, validated_data):
    #     pass

    # def save(self, validated_data):
    #     fav_sports = validated_data.get("fav_sport")
    #     instance = super(PersonSerializer, self).create(validated_data)
    #     # for item in fav_sports:
    #     #     instance.fav_sport.add(item)
    #     phone_number = self.validated_data.get('phone_number')
    #
    #     if phone_number is not None and \
    #             PersonDB.objects.filter(phone_number=phone_number).exists():
    #         raise serializers.ValidationError({'error': 'invalid phone number'})
    #
    #     instance.save()
    #     return instance

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
