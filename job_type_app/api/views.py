from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from job_type_app.api.serializer import JobTypeSerializer
from job_type_app.models import JobTypeDB
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated, AllowAny

from user_app import models



@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def job_type_list_view(request):
    if request.method == 'GET':
        all_trainee_list = JobTypeDB.objects.all()
        serializer = JobTypeSerializer(all_trainee_list, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = JobTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({"error":serializer.errors})


@api_view(['GET', 'DELETE', 'PUT'])
def job_type_detail_view(request, pk):
    if request.method == 'GET':
        trainee = get_object_or_404(JobTypeDB, pk=pk)
        serializer = JobTypeSerializer(trainee)
        return Response(serializer.data)

    if request.method == 'PUT':
        trainee = get_object_or_404(JobTypeDB, pk=pk)
        serializer = JobTypeSerializer(trainee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        trainee = get_object_or_404(JobTypeDB, pk=pk)
        trainee.delete()
        return Response("Delete Successfully", status=status.HTTP_200_OK)
