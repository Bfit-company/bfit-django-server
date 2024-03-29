from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView

from coach_app.api.views import ChangeCoachRating
from coach_app.models import CoachDB
from person_app.models import PersonDB
from rating_app.api.serializer import GeneralRatingSerializer, RatingSerializer, AllCoachRatingSerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import coreapi
from user_app import models
from rating_app.models import RatingDB
from rest_framework.schemas import AutoSchema


class RatingViewSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []
        if method.lower() in ['post', 'put']:
            extra_fields = [
                coreapi.Field('desc')
            ]
        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields


def rating_handler(data, rating_obj=None, preview_rating=None, method=None):
    serializer = GeneralRatingSerializer(rating_obj, data=data)

    if serializer.is_valid():
        change_coach_rating_serializer, response = ChangeCoachRating().change_coach_rating(
            coach_id=data["rating_coach_id"],
            user_rating=data["rating"],
            request_method=method,
            preview_rating=preview_rating
        )

        if response.status_code == status.HTTP_200_OK:  # save, change or delete
            try:
                if method == "DELETE":
                    rating_obj.delete()
                    return Response("Delete Successfully", status=status.HTTP_200_OK)

                else:
                    serializer.save(person_id=PersonDB.objects.get(pk=data["person_id"]),
                                    rating_coach_id=CoachDB.objects.get(pk=data["rating_coach_id"]))
                    change_coach_rating_serializer.save()
                    return Response(change_coach_rating_serializer.data, status=status.HTTP_200_OK)
            except:
                return Response({"error": "user can not rating the same coach more than once"},
                                status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"error": change_coach_rating_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class RatingList(GenericAPIView):
    serializer_class = RatingSerializer

    def get(self, request):
        # permission_classes = (IsAuthenticatedOrReadOnly,)
        rating_list = RatingDB.objects.all()
        serializer = GeneralRatingSerializer(rating_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        return rating_handler(request)
        # serializer = GeneralRatingSerializer(data=request.data)
        # if serializer.is_valid():
        #     change_coach_rating_serializer, response = ChangeCoachRating().change_coach_rating(
        #         coach_id=request.data["rating_coach_id"],
        #         user_rating=request.data["rating"],
        #         request_method=request.method)  # 'POST'
        #     if response.status_code == status.HTTP_200_OK:
        #         try:
        #             serializer.save(person_id=PersonDB.objects.get(pk=request.data["person_id"]),
        #                             rating_coach_id=CoachDB.objects.get(pk=request.data["rating_coach_id"]))
        #             change_coach_rating_serializer.save()
        #             return Response(change_coach_rating_serializer.data, status=status.HTTP_201_CREATED)
        #         except:
        #             return Response({"error": "user can not rating the same coach more than once"},
        #                             status=status.HTTP_400_BAD_REQUEST)
        #
        #     else:
        #         return Response(change_coach_rating_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RatingDetail(GenericAPIView):
    serializer_class = RatingSerializer

    def put(self, request, pk):
        rating = get_object_or_404(RatingDB, pk=pk)
        serializer = RatingSerializer(rating, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({"error":serializer.errors})

    def delete(self, request, pk):
        rating = get_object_or_404(RatingDB, pk=pk)
        rating.delete()
        return Response("Delete Successfully", status=status.HTTP_200_OK)


class RatingDetailDelete(GenericAPIView):
    serializer_class = RatingSerializer

    def post(self, request):
        rating_obj = get_object_or_404(RatingDB,
                                       person_id=request.data["person_id"],
                                       rating_coach_id=request.data["rating_coach_id"])
        rating_obj.delete()
        return Response("Delete Successfully", status=status.HTTP_200_OK)


class RatingDetailUpdate(GenericAPIView):
    serializer_class = RatingSerializer

    def post(self, request):
        """
        check if rating already exists
        yes -> update rating
        no -> create rating
        """
        person_id = get_object_or_404(PersonDB, user_id=request.user).pk
        rating_obj = RatingDB.objects.filter(person_id=person_id,
                                             rating_coach_id=request.data["rating_coach_id"])
        data = request.data
        data.update({"person_id": person_id})
        if rating_obj.exists():
            rating_obj = rating_obj.first()
            return rating_handler(data, rating_obj, rating_obj.rating, method="PUT")

        else:
            return rating_handler(data, method="POST")


class GetAllCoachRating(GenericAPIView):
    '''
    getting all the rating with review for specific coach
    '''
    serializer_class = AllCoachRatingSerializer

    def get(self, request, coach_id):
        rating_coach_list = RatingDB.objects.filter(rating_coach_id=coach_id, review__isnull=False).exclude(review='')
        serializer = AllCoachRatingSerializer(rating_coach_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
