from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from django.urls import path
from . import views

urlpatterns = [
    path("api/signup/", views.signup_api, name="signup_api"),
    path("api/login/", views.login_api, name="login_api"),
    path("api/logout/", views.logout_api, name="logout_api"),
    path("api/dashboard/", views.dashboard_api, name="dashboard_api"),
    path("api/llm-query/", views.llm_query_api, name="llm_query_api"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
