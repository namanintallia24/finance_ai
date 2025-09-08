from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from finance_app.models import UserQueryHistory
from finance_app.utils.jwt_utils import generate_jwt
from unittest.mock import patch


User = get_user_model()


class ViewsSmokeTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.username = "testuser"
        self.password = "strong-password-123"
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def _auth_headers(self, user=None):
        user = user or self.user
        token = generate_jwt(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_signup_success(self):
        url = reverse("signup_api")
        payload = {"username": "u2", "password": "pass12345", "password2": "pass12345"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)

    def test_signup_password_mismatch(self):
        url = reverse("signup_api")
        payload = {"username": "u3", "password": "pass1", "password2": "pass2"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_invalid_credentials(self):
        url = reverse("login_api")
        payload = {"username": self.username, "password": "wrong"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_success_returns_tokens(self):
        url = reverse("login_api")
        payload = {"username": self.username, "password": self.password}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

    def test_logout_requires_authentication(self):
        url = reverse("logout_api")
        response = self.client.post(url, {}, format="json")
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_logout_authenticated(self):
        url = reverse("logout_api")
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_dashboard_get_requires_auth(self):
        url = reverse("dashboard_api")
        response = self.client.get(url)
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_dashboard_get_authenticated_with_valid_bearer(self):
        url = reverse("dashboard_api")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, **self._auth_headers())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("history", response.data)

    def test_dashboard_post_empty_query_400(self):
        url = reverse("dashboard_api")
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, {"query": ""}, format="json", **self._auth_headers())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_llm_query_requires_prompt(self):
        url = reverse("llm_query_api")
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, {"prompt": ""}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_llm_query_requires_auth(self):
        url = reverse("llm_query_api")
        response = self.client.post(url, {"prompt": "hello"}, format="json")
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    @patch("finance_app.views.run_gemini_prompt")
    def test_llm_query_valid_prompt(self, mock_gemini):
        mock_gemini.return_value = "mocked response"
        url = reverse("llm_query_api")
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, {"prompt": "test"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"response": "mocked response"})