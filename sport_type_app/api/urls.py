from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from user_app.api.views import registration_view
from user_app.api.views import logout_view
from sport_type_app.api.views import sport_type_list_view
from sport_type_app.api.views import sport_type_detail_view

urlpatterns = [
    path('sport_type_list/', sport_type_list_view, name='sport_type_list'),
    path('sport_type_detail/<int:pk>/', sport_type_detail_view, name='sport_type_detail'),
]