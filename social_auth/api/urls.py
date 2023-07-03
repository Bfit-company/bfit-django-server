from django.urls import path

from .views import LoginGoogleSocialAuthView, SignupGoogleSocialAuthView, SignupAppleSocialAuthView

urlpatterns = [
    path('login_google/', LoginGoogleSocialAuthView.as_view()),
    path('signup_google/', SignupGoogleSocialAuthView.as_view()),
    path('signup_apple/', SignupAppleSocialAuthView.as_view())
]
