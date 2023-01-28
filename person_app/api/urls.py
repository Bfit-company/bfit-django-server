from django.urls import path
from person_app.api.views import person_list, IsPhoneNumberExists
from person_app.api.views import PersonDetail
from person_app.api.views import UploadProfileImage


urlpatterns = [
    path('person_list/', person_list, name='person_list'),
    path('person_detail/<int:pk>/', PersonDetail.as_view(), name='person_detail'),
    path('upload_profile_image/<int:pk>', UploadProfileImage.as_view(), name='upload_profile_image'),
    path('is_phone_number_exists/<str:phone_number>', IsPhoneNumberExists.as_view(), name='is_phone_number_exists'),
    # path('person_detail/<string:pk>/', person_detail_by_string, name='person_detail'),
]