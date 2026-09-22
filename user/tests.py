from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, Classroom


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="TestPass123!",
            first_name="Test",
            last_name="User",
            phone_number="998901112233",
            status="starter",
        )

    def test_user_created(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.user.username, "testuser")
        self.assertTrue(self.user.check_password("TestPass123!"))
        self.assertFalse(self.user.is_staff)

    def test_superuser_created(self):
        admin = User.objects.create_superuser(
            username="admin", password="SuperSecret123", status="teacher"
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)


class UserAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="john", password="johnpassword", status="starter"
        )
        self.token_url = reverse("token_obtain_pair")
        self.register_url = reverse("register")
        self.profile_url = reverse("profile")

    def test_register_user(self):
        data = {
            "username": "newuser",
            "password": "StrongPass456!",
            "status": "advanced",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_user(self):
        response = self.client.post(
            self.token_url, {"username": "john", "password": "johnpassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_profile_authenticated(self):
        # Login first to get token
        login = self.client.post(
            self.token_url, {"username": "john", "password": "johnpassword"}
        )
        access_token = login.data["access"]
        response = self.client.get(
            self.profile_url, HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "john")

    def test_profile_unauthorized(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
