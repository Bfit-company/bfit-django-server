from rest_framework import serializers

from Utils.aws.presign_url import PresignUrl
from post_app.models import PostDB


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = PostDB
        fields = "__all__"

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     profile_image_s3_path = data.pop('profile_image_s3_path')
    #     if profile_image_s3_path is not None and profile_image_s3_path is not '':
    #         data["profile_image_url"] = PresignUrl().create_presigned_url(profile_image_s3_path)
    #     return data
