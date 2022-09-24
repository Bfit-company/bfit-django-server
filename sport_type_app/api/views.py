from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from sport_type_app.api.serializer import SportTypeSerializer
from sport_type_app.models import SportTypeDB
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.db.models import Q
from rest_framework.permissions import AllowAny, IsAdminUser



class SportTypeListView(APIView):
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method == 'GET':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get(self,request):
        all_trainee_list = SportTypeDB.objects.all()
        serializer = SportTypeSerializer(all_trainee_list, many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer = SportTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


# @api_view(['GET', 'DELETE', 'PUT'])
# @permission_classes([AllowAny])
# def sport_type_detail_view(request, pk):
class SportTypeDetailView(APIView):
    # def get_permissions(self):
    #     """
    #     Instantiates and returns the list of permissions that this view requires.
    #     """
    #     if self.request.method == 'GET':
    #         permission_classes = [AllowAny]
    #     else:
    #         permission_classes = [IsAdminUser]
    #     return [permission() for permission in permission_classes]
    # permission_classes = [AllowAny]

    def get(self, request, pk):
        sports_type = get_object_or_404(SportTypeDB, pk=pk)
        serializer = SportTypeSerializer(sports_type)
        return Response(serializer.data)

    def put(self, request, pk):
        trainee = get_object_or_404(SportTypeDB, pk=pk)
        serializer = SportTypeSerializer(trainee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        trainee = get_object_or_404(SportTypeDB, pk=pk)
        trainee.delete()
        return Response("Delete Successfully", status=status.HTTP_200_OK)


class InitSportType(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = SportTypeSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class SearchSportType(APIView):
    def get(self, request, sport_type):
        if sport_type == '':
            sport_types = SportTypeDB.objects.all()
        else:
            sport_types = SportTypeDB.objects.filter(Q(name__icontains=sport_type))
        serializer = SportTypeSerializer(sport_types, many=True)
        return Response(serializer.data)
