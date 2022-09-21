from django.urls import path, re_path
from sport_type_app.api.views import SportTypeListView, SearchSportType
from sport_type_app.api.views import SportTypeDetailView, InitSportType

urlpatterns = [
    path('sport_type_list/', SportTypeListView.as_view(), name='sport_type_list'),
    path('sport_type_detail/<int:pk>/', SportTypeDetailView.as_view(), name='sport_type_detail'),
    # path('search_sport_type/<str:sport_type>/', SearchSportType.as_view(), name='search_sport_type'),
    re_path(r'^search_sport_type/(?P<sport_type>\w*)/$', SearchSportType.as_view(), name='search_sport_type'),
    path('init_sport_type/', InitSportType.as_view(), name='init_sport_type'),
]
