from django.db.models import Q, F, Value as V
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from post_app.models import PostDB
from post_app.api.serializer import PostSerializer
from post_app.api.permissions import PostUserOrReadOnly, AdminOrReadOnly
from rest_framework.views import APIView


@api_view(['GET', 'POST'])
def post_list(request):
    if request.method == 'GET':
        posts_list = PostDB.objects.all()
        serializer = PostSerializer(posts_list, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            if (serializer.validated_data.get('body') is None or
                serializer.validated_data.get('body') == '') and \
                    (serializer.validated_data.get('image') is None or
                     serializer.validated_data.get('image') == ''):
                return Response({"error": "invalid data"}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetPostsDetailByPostList(APIView):
    def post(self, request):
        posts = PostDB.objects.filter(id__in=request.data['posts'])
        if posts.exists():
            serializer = PostSerializer(posts, many=True)
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_404_NOT_FOUND)


class PostDetail(APIView):
    serializer_class = PostSerializer
    permission_classes = [PostUserOrReadOnly]

    def get(self, request, pk):
        post = get_object_or_404(PostDB, pk=pk)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        post = get_object_or_404(PostDB, pk=pk)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        post = get_object_or_404(PostDB, pk=pk)
        post.delete()
        return Response("Delete Successfully", status=status.HTTP_200_OK)
