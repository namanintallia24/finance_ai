from django.urls import path
from . import views

urlpatterns = [
    path("", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    # path("history/", views.history_list, name="history_list"),
    # path("history/<int:pk>/", views.history_detail, name="history_detail"),
    # path("get-history/<int:history_id>/", views.get_history, name="get_history"),
    # path("api/llm-query/", views.llm_query_api, name="llm_query_api"),  # <-- important



]
