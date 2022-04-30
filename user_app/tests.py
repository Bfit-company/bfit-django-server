import username as username
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from sport_type_app.models import SportTypeDB

User = get_user_model()


class TestRegister(APITestCase):

    def set_up(self):
        user = {
            'email': "Hello@gmail.com",
            "password": "123",
            "password2": "123"}
        self.user = User.objects.create_user(user["email"], user["password"])
        self.user.save()
        # self.user = User.objects.create_user("liad@gmail.com", "123")

        body = {
            "name": "Athlestics",
            "rating": 1,
            "image": "https://www.essd.eu/wp-content/uploads/2020/07/ESSD_Hungary-12.jpg"
        }
        self.sportType = SportTypeDB.objects.create(**body)

    def createUser(self):
        self.set_up()
        full_user = {
            "person": {
                "full_name": "Bfit B",
                "birth_date": "2001-09-30",
                "gender": "F",
                "is_coach": False,
                "phone_number": "",
                "business_email": "bfit.company1@gmail.com",
                "instagram_url": "",
                "fav_sport": [self.sportType.id],
                "user": self.user.id
            }
        }
        return self.client.post(reverse("full_user_create"), full_user, format='json')

        # serializer = RegistrationSerializer(data=user)
        # if serializer.is_valid():
        #     account = serializer.save()


    def test_register(self):
        body = {
            'email': "Hello@gmail.com",
            "password": "123",
            "password2": "123"}
        response = self.client.post(reverse('register'), body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    def test_register_incorrect_pass2(self):
        body = {
            'email': "Hello@gmail.com",
            "password": "123",
            "password2": "12"}
        response = self.client.post(reverse('register'), body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)




    def test_full_user_create_coach(self):
        # self.user1 = User.objects.create_user("Hello@gmail.com", "123")
        # body = {
        #     "name": "Athlestics",
        #     "rating": 1,
        #     "image": "https://www.essd.eu/wp-content/uploads/2020/07/ESSD_Hungary-12.jpg"
        # }
        # sportType = SportTypeDB.objects.create(**body)
        self.set_up()
        full_user = {
            "person": {
                "full_name": "Bfit B",
                "birth_date": "2001-09-30",
                "gender": "F",
                "is_coach": True,
                "phone_number": "",
                "business_email": "bfit.company1@gmail.com",
                "instagram_url": "",
                "fav_sport": [self.sportType.id],
                "user": self.user.id
            }
        }
        res = self.client.post(reverse("full_user_create"), full_user, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)



    def test_full_user_create_trainee(self):

        self.set_up()
        full_user = {
            "person": {
                "full_name": "Bfit B",
                "birth_date": "2001-09-30",
                "gender": "F",
                "is_coach": False,
                "phone_number": "",
                "business_email": "bfit.company1@gmail.com",
                "instagram_url": "",
                "fav_sport": [self.sportType.id],
                "user": self.user.id
            }
        }
        res = self.client.post(reverse("full_user_create"), full_user, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)


    def test_login(self):
        response = self.createUser()
        body = {
            "username": "Hello@gmail.com",
            "password": "123"
        }
        response = self.client.post(reverse('login'), body, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)