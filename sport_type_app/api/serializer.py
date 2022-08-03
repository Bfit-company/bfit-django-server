from rest_framework import serializers

from Utils.aws.presign_url import PresignUrl
from sport_type_app.models import SportTypeDB


class SportTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = SportTypeDB
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        image_s3_path = data.pop('image_s3_path')
        if image_s3_path != None and image_s3_path != '':
            data["image_url"] = PresignUrl().create_presigned_url(image_s3_path)
        return data
