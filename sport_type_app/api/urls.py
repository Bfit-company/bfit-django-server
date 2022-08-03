from django.urls import path
from sport_type_app.api.views import sport_type_list_view, SearchSportType
from sport_type_app.api.views import sport_type_detail_view, InitSportType

urlpatterns = [
    path('sport_type_list/', sport_type_list_view, name='sport_type_list'),
    path('sport_type_detail/<int:pk>/', sport_type_detail_view, name='sport_type_detail'),
    path('search_sport_type/<str:sport_type>/', SearchSportType.as_view(), name='search_sport_type'),
    path('init_sport_type/', InitSportType.as_view(), name='init_sport_type'),
]
