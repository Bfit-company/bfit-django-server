from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

from user_app.api.serializer import RegistrationSerializer

User = get_user_model()


class TestSportType(APITestCase):

    def test_create_sport_type(self):
        body = {
            "name": "Athlestics",
            "rating": 1,
            "image": "https://www.essd.eu/wp-content/uploads/2020/07/ESSD_Hungary-12.jpg"
        }
        res = self.client.post(reverse("sport_type_list"),body)
        self.assertEqual(res.status_code,status.HTTP_200_OK)

# Create your tests here.
