# finance_app/tests/test_views.py
import json
import jwt
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from finance_app.models import UserQueryHistory
from django.conf import settings
from datetime import datetime, timedelta
from finance_app.utils import jwt_utils
from django.contrib.auth import get_user_model
User = get_user_model()
    



class ViewsSmokeTests(TestCase):
    def setUp(self):
    # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.client.login(username="testuser", password="password123")


    def test_signup_view(self):
        resp = self.client.get(reverse("signup"))
        self.assertEqual(resp.status_code, 200)

    def test_login_view(self):
        resp = self.client.get(reverse("login"))
        self.assertEqual(resp.status_code, 200)

    def test_logout_view(self):
        resp = self.client.get(reverse("logout"))
        self.assertEqual(resp.status_code, 302)

    def test_dashboard_view_with_login(self):
        resp = self.client.get(reverse("dashboard"), follow=True)
        self.assertEqual(resp.status_code, 200)

    @patch("finance_app.views.verify_jwt")
    def test_dashboard_view_with_jwt(self, mock_verify_jwt):
        mock_verify_jwt.return_value = {"username": self.user.username}
        self.client.cookies["jwt_token"] = "adummy_jwt"
        resp = self.client.get(reverse("dashboard"), follow=True)
        self.assertEqual(resp.status_code, 200)


    @patch("finance_app.views.verify_jwt")
    def test_dashboard_view_with_jwt_mocked(self, mock_verify_jwt):
        # Mock verify_jwt to always return a user payload
        mock_verify_jwt.return_value = {"user_id": self.user.id}

        self.client.cookies["jwt_token"] = "dummy_jwt"

        resp = self.client.get(reverse("dashboard") , follow= True)

        self.assertEqual(resp.status_code, 200)


    @patch("finance_app.views.verify_jwt")
    def test_dashboard_view_history(self, mock_verify_jwt):
        mock_verify_jwt.return_value = {"user_id": self.user.id}

        # Create a history item linked to the user
        history = UserQueryHistory.objects.create(
            user=self.user,
            query="test query",
            response="test response",
            tables_html=[],
            chart_data={}
        )
        # Access dashboard with history_id
        url = reverse("dashboard") + f"?history_id={history.id}"
        resp = self.client.get(url, follow=True) 

        # Now the client is authenticated, and the request should be successful
        self.assertEqual(resp.status_code, 200)


    def test_dashboard_redirect_if_no_login(self):
        self.client.logout()
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.status_code, 302)

    def test_llm_query_api_empty_prompt(self):
        resp = self.client.post(
            reverse("llm_query_api"),
            data=json.dumps({"prompt": ""}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)

    def test_llm_query_api_invalid_method(self):
        resp = self.client.get(reverse("llm_query_api"))
        self.assertIn(resp.status_code, (400, 405))  # accept either

    @patch("finance_app.views.run_gemini_prompt")
    def test_llm_query_api_valid_prompt(self, mock_gemini):
        mock_gemini.return_value = "mocked response"
        resp = self.client.post(
            reverse("llm_query_api"),
            data=json.dumps({"prompt": "test prompt"}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(resp.content, {"response": "mocked response"})