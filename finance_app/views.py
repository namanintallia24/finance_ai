import os
import json
import pandas as pd
import traceback
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from llm.prompt_builder import build_prompt
from llm.gemini_client import run_gemini_prompt
from llm.context_manager import build_context
from finance_app.services import send_mcp_tool_call
from frontend.table_create import three_statements_df, flatten_all_financials
import plotly.express as px
from django.contrib.auth import authenticate , login
from .forms import SignUpForm
from .utils.jwt_utils import generate_jwt,verify_jwt
from django.contrib.auth import login as auth_login ,logout
from django.views.decorators.csrf import csrf_protect
from django.db import IntegrityError
from finance_app.frontend.chart_data import prepare_chart_data 
from finance_app.frontend.tables import merge_tables
from django.shortcuts import render, redirect
from .models import UserQueryHistory
from llm.tool_router import get_tool_call_from_gemini
USER_DB_FILE = os.path.join(os.path.dirname(__file__), "user_db.json")



# -------- Singup --------
def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()   # hashes password automatically
                return redirect("login")
            except IntegrityError:
                form.add_error("username", "This username already exists. Please choose another.")
    else:
        form = SignUpForm()
    return render(request, "finance_app/signup.html", {"form": form})



# -------- Login --------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        user = authenticate(username=username, password=password)

        if user:
            auth_login(request, user)  # Django session login
            token = generate_jwt(username)
            response = redirect("dashboard")
            response.set_cookie(
                "jwt_token",
                token,
                httponly=True,
                secure=False  # Change to True in production
            )
            return response
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "finance_app/login.html")


# -------- Logout --------
def logout_view(request):
    if request.method == "POST":
        logout(request)
        response = redirect("login")
        response.delete_cookie("jwt_token")
        return response
    return redirect("dashboard")



# -------- Dashboard --------
# this code is working proper

def dashboard_view(request):
    token = request.COOKIES.get("jwt_token")
    payload = verify_jwt(token) if token else None

    if not payload:
        messages.error(request, "Please login first.")
        return redirect("login")

    # Load history for this user
    history = UserQueryHistory.objects.filter(user=request.user).order_by("-created_at")

    context = {
        "figs_json": [],
        "tables": [],
        "raw_tool_results": None,
        "final_response": None,
        "user_query" : None,
        "nested_json": [],
        "chart_data" : None,
        "history": history
    }

    # ---- Case 1: User clicked a history item ----
    history_id = request.GET.get("history_id")
    if history_id:
        try:
            h = UserQueryHistory.objects.get(id=history_id, user=request.user)
            context["final_response"] = h.response
            context["user_query"] = h.query
            context["tables"] = h.tables_html or []
            context["chart_data"] = h.chart_data 
        except UserQueryHistory.DoesNotExist:
            messages.error(request, "History not found or not yours.")
        return render(request, "finance_app/dashboard.html", context)

    # ---- Case 2: New Query Submission ----
    if request.method == "POST":
        
        user_query = request.POST.get("query", "").strip()
        if not user_query:
            messages.error(request, "Please enter a question.")
            return render(request, "finance_app/dashboard.html", context)

        try:
            tool_calls = get_tool_call_from_gemini(user_query)
            # initial_prompt = build_prompt(user_query_corrected)
            # tool_calls = extract_tool_call(initial_prompt)

            if not tool_calls:
                messages.warning(request, "No tool was detected for this query.")
                return render(request, "finance_app/dashboard.html", context)


            tool_result_data_list = []
            tool_result_text = ""
            saved_tables = []
            chart_data = None

            for tc in tool_calls:
                tool_name = tc.get("method")
                parameters = tc.get("params", {})
                # call_id = tc.get("id", 1)
                res = send_mcp_tool_call(tool_name, parameters)
                tool_result_data_list.append(res)

                
                if res != "Unknown tool":
                    tool_result_text += build_context(tool_name, res) + "\n"

                if tool_name == "three_statements_":
                    df_income, df_cash, df_balance = three_statements_df(tool_result_text)
                    saved_tables.append({"title": "Income Statement", "html": df_income.to_html(index=False)})
                    saved_tables.append({"title": "Cash Flow Statement", "html": df_cash.to_html(index=False)})
                    saved_tables.append({"title": "Balance Sheet", "html": df_balance.to_html(index=False)})
                    continue

                if tool_name == "sector_wise_company":
                    for sector, companies in res.get("comparison", {}).items():
                        if companies:
                            df = pd.DataFrame(companies)
                            saved_tables.append({
                                "title": f"{sector} - Market Cap Comparison",
                                "html": df.to_html(index=False, classes="table table-sm")
                            })
                    continue

                if isinstance(res, dict):
                    if "comparison" in res:
                        for company, years in res["comparison"].items():
                            for year, categories in years.items():
                                if all(isinstance(v, (int, float, str)) for v in categories.values()):
                                    df = pd.DataFrame(list(categories.items()), columns=["Field", "Value"])
                                    saved_tables.append({"title": f"{company} - {year}", "html": df.to_html(index=False)})
                                else:
                                    for category, values in categories.items():
                                        df = pd.DataFrame(list(values.items()), columns=["Field", "Value"])
                                        saved_tables.append({"title": f"{company} - {year} - {category.title()}", "html": df.to_html(index=False)})

                elif isinstance(res, list) and all(isinstance(i, dict) for i in res):
                    for idx, d in enumerate(res, start=1):
                        df = pd.DataFrame(list(d.items()), columns=["Field", "Value"])
                        saved_tables.append({
                            "title": f"{tool_name.replace('_', ' ').title()} #{idx}",
                            "html": df.to_html(index=False)
                        })
            
            saved_tables_final = merge_tables(saved_tables)
            context["tables"] = saved_tables_final


            context["raw_tool_results"] = tool_result_data_list

            final_prompt = f"{user_query}\n\nTool Output:\n{tool_result_text}"
            final_response = run_gemini_prompt(final_prompt)
            context["final_response"] = final_response
            context["user_query"]= user_query

            
            chart_data = prepare_chart_data(tool_result_data_list)
            context["chart_data"] = chart_data   # ✅ pass processed chart_data

            # Save to history
            UserQueryHistory.objects.create(
                user=request.user,
                query=user_query,
                response=final_response,
                tables_html=saved_tables_final,
                chart_data=chart_data,
            )
            

            # Refresh history
            context["history"] = UserQueryHistory.objects.filter(user=request.user).order_by("-created_at")

        except Exception as e:
            tb = traceback.format_exc()
            error_message =  "❌ Gemini API is not responding. Please try again later."
            messages.error(request, f"Error while processing: {e}")
            context["error_message"] = error_message

    return render(request, "finance_app/dashboard.html", context)

def llm_query_api(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    try:
        body = json.loads(request.body)
        prompt = body.get("prompt", "")
        if not prompt:
            return JsonResponse({"error": "Empty prompt"}, status=400)
        resp = run_gemini_prompt(prompt)
        return JsonResponse({"response": resp})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)