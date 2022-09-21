from rest_framework import serializers

from Utils.aws.presign_url import PresignUrl
from post_app.models import PostDB


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = PostDB
        fields = "__all__"

    # def save(self, image_s3_path):
    #     if image_s3_path is not None:
    #         post = PostDB(**self.validated_data, image_s3_path=image_s3_path)
    #     else:
    #         post = PostDB(**self.validated_data)
    #     post.save()
    #     return post

    def create(self, validated_data):
        return PostDB.objects.create(**validated_data)

    def update(self, instance, validated_data):
        try:
            image_s3_path = validated_data.pop('image_s3_path')
            if image_s3_path:
                instance.image_s3_path = image_s3_path

        except KeyError as ke:
            print(ke)

        super(self.__class__, self).update(instance, validated_data)
        instance.save()
        return instance


    def to_representation(self, instance):
        data = super().to_representation(instance)
        image_s3_path = data.pop('image_s3_path')
        if image_s3_path != None and image_s3_path != '':
            data["image_url"] = PresignUrl().create_presigned_url(image_s3_path)
        return data
