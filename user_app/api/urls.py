from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from user_app.api.views import registration_view, UpdateUser
from user_app.api.views import (
    logout_view,
    full_user_create,
    login_view,
    ChangePasswordView,
    # send_mail,
)
# from user_app.api.views import login_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', registration_view, name='register'),
    path('full_user_create/', full_user_create, name='full_user_create'),
    path('logout/', logout_view, name='logout'),
    path('update-user/<int:pk>/', UpdateUser.as_view(), name='update-user'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    # path('api/password_reset/', send_mail, name='password_reset'),

]