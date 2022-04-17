from django.urls import path, re_path
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from user_app.api.views import registration_view
from user_app.api.views import logout_view
from coach_app.api.views import (
    coach_list,
    coach_detail,
    find_coach_by_name,
    coach_list_by_sport_type,
    coach_list_sorted_by_rating,
    coach_list_sorted_by_date_joined,
    coach_list_search_by_parameters,
    coach_list_by_parameters_sorted,
    ChangeCoachRating,
    SearchCoach
)

urlpatterns = [
    path('coach_list/', coach_list, name='coach_list'),
    path('coach_list_sorted_by_rating/', coach_list_sorted_by_rating, name='coach_list_sorted_by_rating'),
    path('coach_list_sorted_by_date_joined/', coach_list_sorted_by_date_joined,
         name='coach_list_sorted_by_date_joined'),
    path('coach_detail/<int:pk>/', coach_detail, name='coach_detail'),
    path('coach_list_by_sport_type/<int:pk>/', coach_list_by_sport_type, name='coach_list_by_sport_type'),
    path('find_coach_by_name/<str:name>/', find_coach_by_name, name='find_coach_by_name'),
    path('coach_list_search_by_parameters/',
            coach_list_search_by_parameters,name='coach_list_search_by_parameters'),
    path('coach_list_by_parameters_sorted/',
         coach_list_by_parameters_sorted, name='coach_list_by_parameters_sorted'),
    path('change_coach_rating/<int:pk>/',
         ChangeCoachRating.as_view(),
         name='change_coach_rating'),
    path('search_coach/',
         SearchCoach.as_view(),
         name='search_coach'),
]
