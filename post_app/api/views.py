import json

from django.db.models import Q, F, Value as V
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from Utils.aws.s3 import S3
from Utils.utils import Utils
from config import BUCKET, S3_KEY
from person_app.models import PersonDB
from post_app.models import PostDB
from post_app.api.serializer import PostSerializer, PostDescriptionSerializer
from post_app.api.permissions import PostUserOrReadOnly
from rest_framework.views import APIView

s3 = S3()


@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def post_list(request):
    if request.method == 'GET':
        posts_list = PostDB.objects.all()
        serializer = PostSerializer(posts_list, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        post_data = request.data.get("post_data")
        post_image = request.data.get("post_image")
        post_data = json.loads(post_data)
        person_id = get_object_or_404(PersonDB, user_id=request.user.pk).pk
        post_data.update({"person": person_id})

        serializer = PostSerializer(data=post_data)
        if serializer.is_valid():
            if (serializer.validated_data.get('body') is None or
                serializer.validated_data.get('body') == '') and \
                    (post_image is None or
                     post_image == ''):
                return Response({"error": "invalid data"}, status=status.HTTP_400_BAD_REQUEST)
            user_email = request.user.email
            s3_key = S3_KEY.format(
                user=user_email,
                image_type="post_image",
                ts_day=Utils.get_ts_today(),
                filename=post_image.name
            )
            s3.upload_file_obj(bucket=BUCKET, s3_key=s3_key, file=post_image)
            serializer = serializer.save(image_s3_path=f's3://{BUCKET}/{s3_key}')
            serializer = PostSerializer(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class GetPostsDetailByPostList(APIView):
    def post(self, request):
        posts = PostDB.objects.filter(id__in=request.data['posts'])
        if posts.exists():
            serializer = PostSerializer(posts, many=True)
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_404_NOT_FOUND)


class ChangePostDescription(APIView):
    serializer_class = PostDescriptionSerializer
    permission_classes = [PostUserOrReadOnly]

    def put(self, request, pk):
        post = get_object_or_404(PostDB, pk=pk)
        self.check_object_permissions(request, post)
        serializer = PostDescriptionSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({"error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)



class PostDetail(APIView):
    serializer_class = PostSerializer
    permission_classes = [PostUserOrReadOnly]

    def get(self, request, pk):
        post = get_object_or_404(PostDB, pk=pk)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        post = get_object_or_404(PostDB, pk=pk)
        self.check_object_permissions(request, post)
        image_s3_path = post.image_s3_path
        bucket = s3.get_bucket_name_from_s3_path(image_s3_path)
        s3_key = s3.get_s3_key_from_s3_path(image_s3_path)
        s3.delete_object(bucket=bucket, s3_key=s3_key)
        post.delete()

        return Response("Delete Successfully", status=status.HTTP_200_OK)
'''

    def put(self, request, pk):
        post = get_object_or_404(PostDB, pk=pk)
        self.check_object_permissions(request, post)
        post_data = request.data.get("post_data")
        post_image = request.data.get("post_image")
        post_data = json.loads(post_data)
        serializer = PostSerializer(post, data=post_data, partial=True)
        image_s3_path = None

        if serializer.is_valid():
            if post_image is not None:
                user_email = request.user.email
                s3_key = S3_KEY.format(
                    user=user_email,
                    image_type="post_image",
                    ts_day=Utils.get_ts_today(),
                    filename=post_image.name
                )
                s3.upload_file_obj(bucket=BUCKET, s3_key=s3_key, file=post_image)
                image_s3_path = f's3://{BUCKET}/{s3_key}'
            serializer = serializer.save(image_s3_path=image_s3_path)
            serializer = PostSerializer(serializer)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
'''


