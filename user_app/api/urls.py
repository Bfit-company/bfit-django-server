from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from user_app.api.views import registration_view, UpdateUser
from user_app.api.views import (
    login_view,
    logout_view,
    full_user_create,
    ChangePasswordView,
    register_validation,
    UserDetails,
    LogoutAPIView
    # send_mail,
)
# from user_app.api.views import login_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', registration_view, name='register'),
    path('register-validate/', register_validation, name='register_validation'),
    path('full_user_create/', full_user_create, name='full_user_create'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('update-user/', UpdateUser.as_view(), name='update-user'),
    path('update-user/<int:pk>', UpdateUser.as_view(), name='update-user'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('user-details/<int:pk>', UserDetails.as_view(), name='user-details'),
    path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # path('api/password_reset/', send_mail, name='password_reset'),

]