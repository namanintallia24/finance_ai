# finance_app/tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
from finance_app.models import UserQueryHistory
import json
import jwt
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
User = get_user_model()
import jwt
from datetime import datetime, timedelta
from django.conf import settings

def generate_jwt_for_user(user):
    payload = {
        "user_id": user.id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token

    

class ViewsSmokeTests(TestCase):
    def setUp(self):
    # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )


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
        self.client.cookies["jwt_token"] = "dummy_jwt"
        resp = self.client.get(reverse("dashboard"), follow=True)
        self.assertEqual(resp.status_code, 200)

    @patch("finance_app.views.verify_jwt")
    def test_dashboard_view_history(self, mock_verify_jwt):
        # Make verify_jwt return payload with our user id
        mock_verify_jwt.return_value = {"user_id": self.user.id}

        # Force-login sets request.user correctly
        self.client.force_login(self.user)

        # Create a history item
        history = UserQueryHistory.objects.create(
            user=self.user,
            query="test query",
            response="test response",
            tables_html=[],
            chart_data={}
        )

        # Access dashboard
        url = reverse("dashboard") + f"?history_id={history.id}"
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("history", resp.context)
        self.assertEqual(resp.context["history"].first().query, "test query")

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
