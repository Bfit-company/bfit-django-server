from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from user_app.api.views import registration_view
from user_app.api.views import logout_view
from person_app.api.views import person_list
from person_app.api.views import person_detail
from person_app.api.views import UploadProfileImage


urlpatterns = [
    path('person_list/', person_list, name='person_list'),
    path('person_detail/<int:pk>/', person_detail, name='person_detail'),
    path('upload_profile_image/<int:pk>', UploadProfileImage.as_view(), name='upload_profile_image'),
    # path('person_detail/<string:pk>/', person_detail_by_string, name='person_detail'),
]