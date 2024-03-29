"""bfit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from Utils.aws.presign_url import PresignUrl

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('user_app.api.urls')),
    path('sport_type/', include('sport_type_app.api.urls')),
    path('trainee/', include('trainee_app.api.urls')),
    path('person/', include('person_app.api.urls')),
    path('coach/', include('coach_app.api.urls')),
    path('post/', include('post_app.api.urls')),
    path('location/', include('location_app.api.urls')),
    path('rating/', include('rating_app.api.urls')),
    path('job_type/', include('job_type_app.api.urls')),
    path('social_auth/', include('social_auth.api.urls')),
    path('presign-url/', PresignUrl.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('rest-auth/', include('rest_framework.urls', namespace='rest_framework'))


]
