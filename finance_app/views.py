import json
import pandas as pd
import traceback
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from .serializers import RegisterSerializer, UserQueryHistorySerializer
from .utils.jwt_utils import generate_jwt, verify_jwt
from .models import UserQueryHistory
from llm.tool_router import get_tool_call_from_gemini
from llm.gemini_client import run_gemini_prompt
from llm.context_manager import build_context
from finance_app.services import send_mcp_tool_call
from frontend.table_create import three_statements_df
from finance_app.frontend.chart_data import prepare_chart_data, sanitize_for_json
from finance_app.frontend.tables import merge_tables
from rest_framework_simplejwt.tokens import RefreshToken





# -------- Signup API --------
@api_view(["POST"])
@permission_classes([AllowAny])
def signup_api(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------- Login API --------
@api_view(["POST"])
@permission_classes([AllowAny])
def login_api(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"error": "Username and password required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "username": user.username,
                },
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {"error": "Invalid username or password"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


# -------- Logout API --------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_api(request):
    logout(request)
    return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)



# -------- Dashboard API --------
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def dashboard_api(request):
    try:
        # JWT validation
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = verify_jwt(token) if token else None
        if not payload:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)

        # User history
        history_qs = UserQueryHistory.objects.filter(user=request.user).order_by("-created_at")
        history = UserQueryHistorySerializer(history_qs, many=True).data

        # ---- Case 1: History fetch ----
        history_id = request.query_params.get("history_id")
        if history_id:
            try:
                h = UserQueryHistory.objects.get(id=history_id, user=request.user)
                return Response(
                    {
                        "final_response": h.response,
                        "user_query": h.query,
                        "tables": h.tables_html or [],  # ✅ return JSON instead of HTML
                        "chart_data": h.chart_data,
                        "history": history,
                    },
                    status=status.HTTP_200_OK,
                )
            except UserQueryHistory.DoesNotExist:
                return Response({"error": "History not found"}, status=status.HTTP_404_NOT_FOUND)

        # ---- Case 2: New query ----
        if request.method == "POST":
            user_query = request.data.get("query", "").strip()
            if not user_query:
                return Response({"error": "Please enter a question."}, status=status.HTTP_400_BAD_REQUEST)

            tool_calls = get_tool_call_from_gemini(user_query)
            
            if not tool_calls:
                return Response({"warning": "No tool detected"}, status=status.HTTP_200_OK)

            tool_result_data_list = []
            tool_result_text = ""
            saved_tables = []

            for tc in tool_calls:
                tool_name = tc.get("method")
                parameters = tc.get("params", {})
                res = send_mcp_tool_call(tool_name, parameters)
                # breakpoint()
                print("response from tool call------------------>>>>>>>", res)
                tool_result_data_list.append(res)

                
                
                if res != "Unknown tool":
                    tool_result_text += build_context(tool_name, res) + "\n"

                # ✅ Income / Cash / Balance as JSON
                # if tool_name == "three_statements_":
                #     df_income, df_cash, df_balance = three_statements_df(tool_result_text)
                #     saved_tables.extend([
                #         {"title": "Income Statement", "data": df_income.to_dict(orient="records")},
                #         {"title": "Cash Flow Statement", "data": df_cash.to_dict(orient="records")},
                #         {"title": "Balance Sheet", "data": df_balance.to_dict(orient="records")},
                #     ])
                #     continue

                if tool_name == "sector_wise_company":
                    for sector, companies in res.get("comparison", {}).items():
                        if companies:
                            df = pd.DataFrame(companies)
                            saved_tables.append({
                                "title": f"{sector} - Market Cap Comparison",
                                "data": df.to_dict(orient="records")
                            })
                    continue

                # ✅ Dict comparison result
                # if isinstance(res, dict):
                #     if "comparison" in res:
                #         for company, years in res["comparison"].items():
                #             for year, categories in years.items():
                #                 df = pd.DataFrame(list(categories.items()), columns=["Field", "Value"])
                #                 saved_tables.append({
                #                     "title": f"{company} - {year}",
                #                     "data": df.to_dict(orient="records")
                #                 })
                if isinstance(res, dict):
                    if "comparison" in res:
                        for company, years in res["comparison"].items():
                            for year, categories in years.items():
                                if all(isinstance(v, (int, float, str)) for v in categories.values()):
                                    df = pd.DataFrame(list(categories.items()), columns=["Field", "Value"])
                                    saved_tables.append({"title": f"{company} - {year}",  "data": df.to_dict(orient="records")})
                                else:
                                    for category, values in categories.items():
                                        df = pd.DataFrame(list(values.items()), columns=["Field", "Value"])
                                        saved_tables.append({"title": f"{company} - {year} - {category.title()}",  "data": df.to_dict(orient="records")})


                # ✅ List[dict] case
                elif isinstance(res, list) and all(isinstance(i, dict) for i in res):
                    for idx, d in enumerate(res, start=1):
                        df = pd.DataFrame(list(d.items()), columns=["Field", "Value"])
                        saved_tables.append({
                            "title": f"{tool_name.replace('_', ' ').title()} #{idx}",
                            "data": df.to_dict(orient="records")
                        })

            # ✅ No HTML merge, just JSON
            saved_tables_final_data = saved_tables
            saved_tables_final = sanitize_for_json(saved_tables_final_data)  

            final_prompt = f"{user_query}\n\nTool Output:\n{tool_result_text}"
            final_response = run_gemini_prompt(final_prompt)

            chart_data_final = prepare_chart_data(tool_result_data_list)
            chart_data = sanitize_for_json(chart_data_final) 

            # Save history (store JSON instead of HTML)
            UserQueryHistory.objects.create(
                user=request.user,
                query=user_query,
                response=final_response,
                tables_html=saved_tables_final,  # ✅ make sure your model has JSONField
                chart_data=chart_data,
            )

            return Response(
                {
                    "final_response": final_response,
                    "user_query": user_query,
                    "tables": saved_tables_final,  # ✅ return JSON
                    "chart_data": chart_data,
                    # "history": history,
                },
                status=status.HTTP_200_OK,
            )

        # Default (GET request)
        return Response({"history": history}, status=status.HTTP_200_OK)

    except Exception as e:
        tb = traceback.format_exc()
        return Response({"error": str(e), "traceback": tb}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#----this dashboard code is working fine -----
# # -------- Dashboard API --------
# @api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated])
# def dashboard_api(request):
#     try:
#         # JWT validation
#         token = request.headers.get("Authorization", "").replace("Bearer ", "")
#         payload = verify_jwt(token) if token else None
#         if not payload:
#             return Response({"error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)

#         # User history
#         history_qs = UserQueryHistory.objects.filter(user=request.user).order_by("-created_at")
#         history = UserQueryHistorySerializer(history_qs, many=True).data

#         # ---- Case 1: History fetch ----
#         history_id = request.query_params.get("history_id")
#         if history_id:
#             try:
#                 h = UserQueryHistory.objects.get(id=history_id, user=request.user)
#                 return Response(
#                     {
#                         "final_response": h.response,
#                         "user_query": h.query,
#                         "tables": h.tables_html or [],
#                         "chart_data": h.chart_data,
#                         "history": history,
#                     },
#                     status=status.HTTP_200_OK,
#                 )
#             except UserQueryHistory.DoesNotExist:
#                 return Response({"error": "History not found"}, status=status.HTTP_404_NOT_FOUND)

#         # ---- Case 2: New query ----
#         if request.method == "POST":
#             user_query = request.data.get("query", "").strip()
#             if not user_query:
#                 return Response({"error": "Please enter a question."}, status=status.HTTP_400_BAD_REQUEST)

#             tool_calls = get_tool_call_from_gemini(user_query)
#             if not tool_calls:
#                 return Response({"warning": "No tool detected"}, status=status.HTTP_200_OK)

#             tool_result_data_list = []
#             tool_result_text = ""
#             saved_tables = []

#             for tc in tool_calls:
#                 tool_name = tc.get("method")
#                 parameters = tc.get("params", {})
#                 res = send_mcp_tool_call(tool_name, parameters)
#                 tool_result_data_list.append(res)

#                 if res != "Unknown tool":
#                     tool_result_text += build_context(tool_name, res) + "\n"

#                 if tool_name == "three_statements_":
#                     df_income, df_cash, df_balance = three_statements_df(tool_result_text)
#                     saved_tables.extend([
#                         {"title": "Income Statement", "html": df_income.to_html(index=False)},
#                         {"title": "Cash Flow Statement", "html": df_cash.to_html(index=False)},
#                         {"title": "Balance Sheet", "html": df_balance.to_html(index=False)},
#                     ])
#                     continue

#                 if isinstance(res, dict):
#                     if "comparison" in res:
#                         for company, years in res["comparison"].items():
#                             for year, categories in years.items():
#                                 df = pd.DataFrame(list(categories.items()), columns=["Field", "Value"])
#                                 saved_tables.append({"title": f"{company} - {year}", "html": df.to_html(index=False)})

#                 elif isinstance(res, list) and all(isinstance(i, dict) for i in res):
#                     for idx, d in enumerate(res, start=1):
#                         df = pd.DataFrame(list(d.items()), columns=["Field", "Value"])
#                         saved_tables.append({
#                             "title": f"{tool_name.replace('_', ' ').title()} #{idx}",
#                             "html": df.to_html(index=False)
#                         })
#             
#             saved_tables_final = merge_tables(saved_tables)

#             final_prompt = f"{user_query}\n\nTool Output:\n{tool_result_text}"
#             final_response = run_gemini_prompt(final_prompt)

#             chart_data = prepare_chart_data(tool_result_data_list)

#             # Save history
#             UserQueryHistory.objects.create(
#                 user=request.user,
#                 query=user_query,
#                 response=final_response,
#                 tables_html=saved_tables_final,
#                 chart_data=chart_data,
#             )

#             return Response(
#                 {
#                     "final_response": final_response,
#                     "user_query": user_query,
#                     "tables": saved_tables_final,
#                     "chart_data": chart_data,
#                     "history": history,
#                 },
#                 status=status.HTTP_200_OK,
#             )

#         # Default (GET request)
#         return Response({"history": history}, status=status.HTTP_200_OK)

#     except Exception as e:
#         tb = traceback.format_exc()
#         return Response({"error": str(e), "traceback": tb}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -------- LLM Query API --------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def llm_query_api(request):
    try:
        prompt = request.data.get("prompt", "")
        if not prompt:
            return Response({"error": "Empty prompt"}, status=status.HTTP_400_BAD_REQUEST)

        resp = run_gemini_prompt(prompt)
        return Response({"response": resp}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
