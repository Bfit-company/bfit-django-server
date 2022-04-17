from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from user_app.api.views import registration_view
from user_app.api.views import logout_view
from trainee_app.api.views import trainee_detail,find_trainee_by_name,trainee_list
from rest_framework.routers import DefaultRouter
# from .views import traineeVS
#
# router = DefaultRouter()
# router.register("trainee",traineeVS,basename='trainee')


urlpatterns = [
    path('trainee_list/', trainee_list, name='trainee_list'),
    path('trainee_detail/<int:pk>/', trainee_detail, name='trainee_detail'),
    path('find_trainee_by_name/<str:name>/', find_trainee_by_name, name='find_trainee_by_name'),

    # url('', include(router.urls))
]