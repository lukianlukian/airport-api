from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class UserAPITests(APITestCase):
    def test_registration_jwt_and_profile(self):
        credentials = {"email": "passenger@example.com", "password": "Secret123!"}
        response = self.client.post("/api/user/register/", {**credentials, "is_staff": True})
        self.assertEqual(response.status_code, 201, response.data)
        self.assertNotIn("password", response.data)
        self.assertFalse(response.data["is_staff"])
        user = get_user_model().objects.get(email=credentials["email"])
        self.assertTrue(user.check_password(credentials["password"]))
        response = self.client.post("/api/user/token/", credentials)
        self.assertEqual(response.status_code, 200, response.data)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        self.assertEqual(self.client.get("/api/user/me/").data["email"], credentials["email"])
        self.assertEqual(self.client.post("/api/user/token/refresh/", {"refresh": response.data["refresh"]}).status_code, 200)

    def test_email_superuser(self):
        user = get_user_model().objects.create_superuser("admin@example.com", "Secret123!")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser("bad@example.com", "Secret123!", is_staff=False)
