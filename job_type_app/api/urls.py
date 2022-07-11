from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from user_app.api.views import registration_view
from user_app.api.views import logout_view
from job_type_app.api.views import job_type_list_view
from job_type_app.api.views import job_type_detail_view

urlpatterns = [
    path('job_type_list/', job_type_list_view, name='job_type_list'),
    path('job_type_detail/<int:pk>/', job_type_detail_view, name='job_type_detail'),
]