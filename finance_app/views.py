import os
import json
import pandas as pd
import traceback
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from llm.prompt_builder import build_prompt
from llm.gemini_client import run_gemini_prompt
from llm.tool_router import extract_tool_call
from llm.context_manager import build_context
from finance_app.services import call_tool_http
from frontend.table_create import three_statements_df, flatten_all_financials
import plotly.express as px
USER_DB_FILE = os.path.join(os.path.dirname(__file__), "user_db.json")
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate , login
from .forms import SignUpForm
from .utils.jwt_utils import generate_jwt,verify_jwt
from django.contrib.auth import login as auth_login ,logout
from django.views.decorators.csrf import csrf_protect
from .models import UserQueryHistory
from django.db import IntegrityError



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


# def signup_view(request):
#     if request.method == "POST":
#         form = SignUpForm(request.POST)
#         breakpoint()
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Signup successful. Please login.")
#             return redirect("login")
#         else:
#             # Show detailed form errors
#             for field, errors in form.errors.items():
#                 for error in errors:
#                     messages.error(request, f"{field}: {error}")
#     else:
#         form = SignUpForm()
#     return render(request, "finance_app/signup.html", {"form": form})


# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.contrib.auth import get_user_model

# User = get_user_model()  # This will point to your CustomUser


# from django.db import IntegrityError

# def signup_view(request):
#     if request.method == "POST":
#         breakpoint()
#         username = request.POST.get("username", "").strip()
#         password = request.POST.get("password", "").strip()

#         if not username or not password:
#             messages.error(request, "⚠️ Username and Password are required.")
#             return redirect("signup")

#         # soft check
#         if User.objects.filter(username=username).exists():
#             messages.error(request, "❌ This username already exists. Please choose another.")
#             return redirect("signup")

#         try:
#             user = User.objects.create_user(username=username, password=password)
#         except IntegrityError:
#             # hard check (safety net if DB rejects duplicate)
#             messages.error(request, "❌ This username already exists. Please choose another.")
#             return redirect("signup")

#         messages.success(request, "✅ Account created successfully. Please login.")
#         return redirect("login_call")

#     return render(request, "finance_app/signup.html")


# def login_view(request):
#     if request.method == "POST":
#         username = request.POST.get("username", "").strip()
#         password = request.POST.get("password", "").strip()
#         user = authenticate(username=username, password=password)

#         if user:
#             auth_login(request, user)  # Django session login (optional)
#             token = generate_jwt(username)
#             response = redirect("dashboard")
#             response.set_cookie(
#                 "jwt_token",
#                 token,
#                 httponly=True,
#                 secure=False  # change to True in production with HTTPS
#             )
#             return response
#         else:
#             messages.error(request, "Invalid username or password.")
#     return render(request, "finance_app/login.html")


# @csrf_protect
# def logout_view(request):
#     if request.method == "POST":
#         # Clear Django session
#         logout(request)
#         # Remove JWT cookie
#         response = redirect("login")
#         response.delete_cookie("jwt_token")
#         return response
#     return redirect("dashboard")



# def dashboard_view(request):
#     token = request.COOKIES.get("jwt_token")
#     payload = verify_jwt(token) if token else None

#     if not payload:
#         messages.error(request, "Please login first.")
#         return redirect("login")

#     context = {
#         "username": request.session.get("current_user"),
#         "figs_json": [],
#         "tables": [],
#         "raw_tool_results": None,
#         "final_response": None,
#         "nested_json": []
#     }

#     if request.method == "POST":
#         user_query = request.POST.get("query", "").strip()
#         if not user_query:
#             messages.error(request, "Please enter a question.")
#             return render(request, "finance_app/dashboard.html", context)

#         try:
#             # 1️⃣ Spell check
#             user_query_corrected = run_gemini_prompt(
#                 f"Correct only spelling mistakes in this sentence (no extra text): {user_query}"
#             )

#             # 2️⃣ Extract tools
#             initial_prompt = build_prompt(user_query_corrected)
#             tool_calls = extract_tool_call(initial_prompt)

#             if not tool_calls:
#                 messages.warning(request, "No tool was detected for this query.")
#                 return render(request, "finance_app/dashboard.html", context)

#             tool_result_data_list = []
#             tool_result_text = ""

#             for tc in tool_calls:
#                 tool_name = tc.get("tool_name")
#                 parameters = tc.get("parameters", {})

#                 res = call_tool_http(tool_name, parameters)
#                 tool_result_data_list.append(res)

#                 if res != "Unknown tool":
#                     tool_result_text += build_context(tool_name, res) + "\n"

#                 # ---------- Handle Three Statements ----------
#                 if tool_name == "three_statements_":
#                     df_income, df_cash, df_balance = three_statements_df(tool_result_text)
#                     context["tables"].append({"title": "Income Statement", "html": df_income.to_html(index=False)})
#                     context["tables"].append({"title": "Cash Flow Statement", "html": df_cash.to_html(index=False)})
#                     context["tables"].append({"title": "Balance Sheet", "html": df_balance.to_html(index=False)})
#                     continue

#                 # ---------- Handle Sector Wise ----------
#                 if tool_name == "sector_wise_company":
#                     for sector, companies in res.get("comparison", {}).items():
#                         if companies:
#                             df = pd.DataFrame(companies)
#                             context["tables"].append({
#                                 "title": f"{sector} - Market Cap Comparison",
#                                 "html": df.to_html(index=False, classes="table table-sm")
#                             })
#                     continue
#                 breakpoint()
#                 # ---------- Universal Handling ----------
#                 if isinstance(res, dict):
#                     if "comparison" in res:  # Nested JSON for one company/year
#                         context["nested_json"] = [res]
#                         for company, years in res["comparison"].items():
#                             for year, categories in years.items():
#                                 # Case A: Direct metrics under year
#                                 if all(isinstance(v, (int, float, str)) for v in categories.values()):
#                                     df = pd.DataFrame(list(categories.items()), columns=["Field", "Value"])
#                                     context["tables"].append({
#                                         "title": f"{company} - {year}",
#                                         "html": df.to_html(index=False, classes="table table-bordered")
#                                     })
#                                 # Case B: category -> metrics
#                                 else:
#                                     for category, values in categories.items():
#                                         df = pd.DataFrame(list(values.items()), columns=["Field", "Value"])
#                                         context["tables"].append({
#                                             "title": f"{company} - {year} - {category.title()}",
#                                             "html": df.to_html(index=False, classes="table table-bordered")
#                                         })


#                 elif isinstance(res, list) and all(isinstance(i, dict) for i in res):
#                     # List of dicts
#                     if all("comparison" in i for i in res):  # List of nested JSON
#                         context["nested_json"] = res
#                         for item in res:
#                             for company, years in item["comparison"].items():
#                                 for year, categories in years.items():
#                                     for category, values in categories.items():
#                                         df = pd.DataFrame(list(values.items()), columns=["Field", "Value"])
#                                         context["tables"].append({
#                                             "title": f"{company} - {year} - {category.title()}",
#                                             "html": df.to_html(index=False, classes="table table-bordered")
#                                         })
#                     else:  # List of flat dicts
#                         for idx, d in enumerate(res, start=1):
#                             df = pd.DataFrame(list(d.items()), columns=["Field", "Value"])
#                             context["tables"].append({
#                                 "title": f"{tool_name.replace('_', ' ').title()} #{idx}",
#                                 "html": df.to_html(index=False, classes="table table-bordered")
#                             })

#                 else:
#                     # ---------- Fallback: Use your flatten_all_financials ----------
#                     df = flatten_all_financials([res])
#                     if not df.empty:
#                         for (company, period), group_df in df.groupby(["Company", "Period"]):
#                             clean_df = group_df[["Field", "Value"]].sort_values(by="Value", ascending=False)
#                             context["tables"].append({
#                                 "company": company,
#                                 "period": period,
#                                 "html": clean_df.to_html(classes="table table-striped", index=False)
#                             })
#                             # Chart
#                             fig = px.bar(clean_df, x="Field", y="Value", text="Value",
#                                          title=f"{company} - {period} Financial Metrics")
#                             fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
#                             fig.update_layout(xaxis_tickangle=-30, height=400, margin=dict(t=60, b=100))
#                             context["figs_json"].append(fig.to_json())

#             # Raw tool results
#             context["raw_tool_results"] = tool_result_data_list

#             # 3️⃣ Final Summary from LLM
#             final_prompt = f"{initial_prompt}\n\nTool Output:\n{tool_result_text}"
#             context["final_response"] = run_gemini_prompt(final_prompt)

#         except Exception as e:
#             tb = traceback.format_exc()
#             messages.error(request, f"Error while processing: {e}")
#             context["error_trace"] = tb

#     return render(request, "finance_app/dashboard.html", context)


# def dashboard_view(request):
#     token = request.COOKIES.get("jwt_token")
#     payload = verify_jwt(token) if token else None

#     if not payload:
#         messages.error(request, "Please login first.")
#         return redirect("login")

#     username = request.session.get("current_user")

#     # Load history for this user
#     history = UserQueryHistory.objects.filter(user=request.user).order_by("-created_at")

#     context = {
#         "username": username,
#         "figs_json": [],
#         "tables": [],
#         "raw_tool_results": None,
#         "final_response": None,
#         "nested_json": [],
#         "history": history
#     }

#     if request.method == "POST":
#         user_query = request.POST.get("query", "").strip()
#         if not user_query:
#             messages.error(request, "Please enter a question.")
#             return render(request, "finance_app/dashboard.html", context)

#         try:
#             user_query_corrected = run_gemini_prompt(
#                 f"Correct only spelling mistakes in this sentence (no extra text): {user_query}"
#             )

#             initial_prompt = build_prompt(user_query_corrected)
#             tool_calls = extract_tool_call(initial_prompt)

#             if not tool_calls:
#                 messages.warning(request, "No tool was detected for this query.")
#                 return render(request, "finance_app/dashboard.html", context)

#             tool_result_data_list = []
#             tool_result_text = ""
#             saved_tables = []

#             for tc in tool_calls:
#                 tool_name = tc.get("tool_name")
#                 parameters = tc.get("parameters", {})
#                 res = call_tool_http(tool_name, parameters)
#                 tool_result_data_list.append(res)

#                 if res != "Unknown tool":
#                     tool_result_text += build_context(tool_name, res) + "\n"

#                 if tool_name == "three_statements_":
#                     df_income, df_cash, df_balance = three_statements_df(tool_result_text)
#                     saved_tables.append({"title": "Income Statement", "html": df_income.to_html(index=False)})
#                     saved_tables.append({"title": "Cash Flow Statement", "html": df_cash.to_html(index=False)})
#                     saved_tables.append({"title": "Balance Sheet", "html": df_balance.to_html(index=False)})
#                     continue

#                 if tool_name == "sector_wise_company":
#                     for sector, companies in res.get("comparison", {}).items():
#                         if companies:
#                             df = pd.DataFrame(companies)
#                             saved_tables.append({
#                                 "title": f"{sector} - Market Cap Comparison",
#                                 "html": df.to_html(index=False, classes="table table-sm")
#                             })
#                     continue

#                 if isinstance(res, dict):
#                     if "comparison" in res:
#                         for company, years in res["comparison"].items():
#                             for year, categories in years.items():
#                                 if all(isinstance(v, (int, float, str)) for v in categories.values()):
#                                     df = pd.DataFrame(list(categories.items()), columns=["Field", "Value"])
#                                     saved_tables.append({"title": f"{company} - {year}", "html": df.to_html(index=False)})
#                                 else:
#                                     for category, values in categories.items():
#                                         df = pd.DataFrame(list(values.items()), columns=["Field", "Value"])
#                                         saved_tables.append({"title": f"{company} - {year} - {category.title()}", "html": df.to_html(index=False)})

#                 elif isinstance(res, list) and all(isinstance(i, dict) for i in res):
#                     for idx, d in enumerate(res, start=1):
#                         df = pd.DataFrame(list(d.items()), columns=["Field", "Value"])
#                         saved_tables.append({
#                             "title": f"{tool_name.replace('_', ' ').title()} #{idx}",
#                             "html": df.to_html(index=False)
#                         })

#             context["tables"] = saved_tables
#             context["raw_tool_results"] = tool_result_data_list

#             final_prompt = f"{initial_prompt}\n\nTool Output:\n{tool_result_text}"
#             final_response = run_gemini_prompt(final_prompt)
#             context["final_response"] = final_response

#             # Save to history
#             UserQueryHistory.objects.create(
#                 user=request.user,
#                 query=user_query,
#                 response=final_response,
#                 tables_html=saved_tables
#             )

#             # Refresh history after saving
#             context["history"] = UserQueryHistory.objects.filter(user=request.user).order_by("-created_at")

#         except Exception as e:
#             tb = traceback.format_exc()
#             messages.error(request, f"Error while processing: {e}")
#             context["error_trace"] = tb

#     return render(request, "finance_app/dashboard.html", context)

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
        except UserQueryHistory.DoesNotExist:
            messages.error(request, "History not found or not yours.")
        return render(request, "finance_app/dashboard.html", context)

    # ---- Case 2: New Query Submission ----
    if request.method == "POST":
        breakpoint()
        user_query = request.POST.get("query", "").strip()
        if not user_query:
            messages.error(request, "Please enter a question.")
            return render(request, "finance_app/dashboard.html", context)

        try:
            user_query_corrected = run_gemini_prompt(
                f"Correct only spelling mistakes in this sentence (no extra text): {user_query}"
            )

            initial_prompt = build_prompt(user_query_corrected)
            tool_calls = extract_tool_call(initial_prompt)

            if not tool_calls:
                messages.warning(request, "No tool was detected for this query.")
                return render(request, "finance_app/dashboard.html", context)

            tool_result_data_list = []
            tool_result_text = ""
            saved_tables = []
            chart_data = None

            for tc in tool_calls:
                tool_name = tc.get("tool_name")
                parameters = tc.get("parameters", {})
                res = call_tool_http(tool_name, parameters)
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

            context["tables"] = saved_tables
            context["raw_tool_results"] = tool_result_data_list

            final_prompt = f"{initial_prompt}\n\nTool Output:\n{tool_result_text}"
            final_response = run_gemini_prompt(final_prompt)
            context["final_response"] = final_response
            context["user_query"]= user_query
            context["chart_data"]= tool_result_data_list

            breakpoint()

            # Save to history
            UserQueryHistory.objects.create(
                user=request.user,
                query=user_query,
                response=final_response,
                tables_html=saved_tables
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
    


# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required


# # @login_required
# # def history_list(request):
# #     histories = UserQueryHistory.objects.filter(user=request.user).order_by("-created_at")
# #     return render(request, "finance_app/history_list.html", {"histories": histories})

# # @login_required
# # def history_detail(request, pk):
# #     history = get_object_or_404(UserQueryHistory, pk=pk, user=request.user)
# #     return render(request, "finance_app/history_detail.html", {"history": history})

# @login_required
# def get_history(request, history_id):
#     h = get_object_or_404(UserQueryHistory, id=history_id, user=request.user)

#     # tables_html is stored as JSON → ensure safe
#     tables_data = h.tables_html if h.tables_html else []

#     return JsonResponse({
#         "query": h.query,
#         "response": h.response,
#         "tables": tables_data,
#         "created_at": h.created_at.strftime("%Y-%m-%d %H:%M"),
#     })