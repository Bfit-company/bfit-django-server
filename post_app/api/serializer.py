from rest_framework import serializers

from Utils.aws.presign_url import PresignUrl
from post_app.models import PostDB


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = PostDB
        fields = "__all__"

    def save(self, image_s3_path):
        post = PostDB(**self.validated_data,image_s3_path=image_s3_path)
        post.save()
        return post


    def to_representation(self, instance):
        data = super().to_representation(instance)
        image_s3_path = data.pop('image_s3_path')
        if image_s3_path != None and image_s3_path != '':
            data["image_url"] = PresignUrl().create_presigned_url(image_s3_path)
        return data
