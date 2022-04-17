from rest_framework import serializers
from post_app.models import PostDB


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = PostDB
        fields = "__all__"

