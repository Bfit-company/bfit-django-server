from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from sport_type_app.api.serializer import SportTypeSerializer
from sport_type_app.models import SportTypeDB
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


from user_app import models



@api_view(['GET', 'POST'])
def sport_type_list_view(request):
    if request.method == 'GET':
        all_trainee_list = SportTypeDB.objects.all()
        serializer = SportTypeSerializer(all_trainee_list, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = SportTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


@api_view(['GET', 'DELETE', 'PUT'])
def sport_type_detail_view(request, pk):
    if request.method == 'GET':
        trainee = get_object_or_404(SportTypeDB, pk=pk)
        serializer = SportTypeSerializer(trainee)
        return Response(serializer.data)

    if request.method == 'PUT':
        trainee = get_object_or_404(SportTypeDB, pk=pk)
        serializer = SportTypeSerializer(trainee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    if request.method == 'DELETE':
        trainee = get_object_or_404(SportTypeDB, pk=pk)
        trainee.delete()
        return Response("Delete Successfully", status=status.HTTP_200_OK)
