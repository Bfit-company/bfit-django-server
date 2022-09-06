from django.urls import path

from .views import LoginGoogleSocialAuthView,SignupGoogleSocialAuthView

urlpatterns = [
    path('login_google/', LoginGoogleSocialAuthView.as_view()),
    path('signup_google/', SignupGoogleSocialAuthView.as_view())
]