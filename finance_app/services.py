# # finance_app/services.py

# import os
# import sys
# import json
# import uuid
# import subprocess
# from typing import Dict, Any, List, Optional

# # from mcp_server.tool_selector import ToolSelector


# def _default_mcp_command() -> List[str]:
#     """
#     Command to launch the MCP server (stdio).
#     Override via env var MCP_SERVER_CMD (JSON array or space-separated).
#     """
#     env_cmd = os.getenv("MCP_SERVER_CMD")
#     if env_cmd:
#         try:
#             # Try JSON array first
#             return json.loads(env_cmd)
#         except Exception:
#             # Fallback: split by spaces
#             return env_cmd.split()

#     # Default: run the module directly with current Python
#     return [sys.executable, "-m", "mcp_server.main"]


# def send_mcp_request(request_obj: Dict[str, Any], cmd: Optional[List[str]] = None) -> Dict[str, Any]:
#     """
#     Fire-and-forget request to the MCP server over stdio by spawning the process once.
#     NOTE: For production, consider keeping the server as a long-running process
#     and reusing the same pipes instead of spawning per request.
#     """
#     command = cmd or _default_mcp_command()
#     proc = subprocess.Popen(
#         command,
#         stdin=subprocess.PIPE,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True,
#     )
#     # 
#     # Send one JSON line and read a single JSON line response
#     req_line = json.dumps(request_obj) + "\n"
#     out, err = proc.communicate(req_line, timeout=30)

#     if err and err.strip():
#         # Not fatal; but you may want to log this
#         pass

#     # The server can emit multiple lines; pick the last non-empty JSON line
#     response_line = ""
#     for ln in out.splitlines():
#         ln = ln.strip()
#         if ln:
#             response_line = ln

#     if not response_line:
#         return {"error": {"code": -32603, "message": "Empty response from MCP server"}}

#     try:
#         return json.loads(response_line)
#     except Exception as e:
#         return {"error": {"code": -32700, "message": f"Invalid JSON from MCP server: {e}"}}


# def generate_request_id() -> str:
#     return str(uuid.uuid4())


# def fetch_tools_from_server() -> List[Dict[str, Any]]:
#     # 
#     """Get full tool catalog from MCP server."""
#     req = {
#         "jsonrpc": "2.0",
#         "id": generate_request_id(),
#         "method": "tools/list",
#         "params": {}
#     }
#     resp = send_mcp_request(req)
#     if "result" in resp and "tools" in resp["result"]:
#         return resp["result"]["tools"]
#     return []


# def filter_tools(tools_catalog: List[Dict[str, Any]], allowed_names: List[str]) -> List[Dict[str, Any]]:
#     allowed = set(allowed_names)
#     return [t for t in tools_catalog if t.get("name") in allowed]


# def call_llm_with_tools(query: str, tools_subset: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     """
#     STUB: Replace with your OpenAI/Gemini function-calling integration.
#     Return a list of tool calls in the form:
#     [
#       {"tool_name": "company_info_", "parameters": {"company_names": ["TCS"], "year": "2024"}},
#       ...
#     ]
#     For now, we do a tiny heuristic so things work end-to-end.
#     """
#     import re

#     ql = query.lower()
#     calls: List[Dict[str, Any]] = []
#     subset_names = [t["name"] for t in tools_subset]

#     # Simple regex to extract company name and year from query
#     company_match = re.search(r"net income ([\w\s\.\-&]+) for (\d{4})", ql)
#     if company_match:
#         company = company_match.group(1).strip()
#         year = company_match.group(2)
#     else:
#         company = ""
#         year = ""

#     if "compare" in ql and "compare_net_income" in subset_names:
#         calls.append({"tool_name": "compare_net_income", "parameters": {"company_names": [company] if company else [], "year": year}})
#     elif any(k in ql for k in ["quarter", "q1", "q2", "q3", "q4"]) and "compare_quarterly_income" in subset_names:
#         calls.append({"tool_name": "compare_quarterly_income", "parameters": {"company_names": [company] if company else [], "year": year}})
#     elif "three" in ql and "three_statements_" in subset_names:
#         calls.append({"tool_name": "three_statements_", "parameters": {"company_names": [company] if company else [], "year": year}})
#     elif "screen" in ql and "screen_companies" in subset_names:
#         calls.append({"tool_name": "screen_companies", "parameters": {"filters": {}, "limit": 50}})
#     elif "sector" in ql and "sector_wise_company" in subset_names:
#         calls.append({"tool_name": "sector_wise_company", "parameters": {"sector": ""}})
#     elif "company_info_" in subset_names:
#         # Always send company_names (list) and year (string)
#         calls.append({"tool_name": "company_info_", "parameters": {"company_names": [company] if company else [], "year": year}})

#     return calls

# # def call_llm_with_tools(query: str, tools_subset: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
# #     """
# #     STUB: Replace with your OpenAI/Gemini function-calling integration.
# #     Return a list of tool calls in the form:
# #     [
# #       {"tool_name": "company_info_", "parameters": {"company": "TCS", "year": 2024}},
# #       ...
# #     ]
# #     For now, we do a tiny heuristic so things work end-to-end.
# #     """
# #     ql = query.lower()
# #     calls: List[Dict[str, Any]] = []

# #     subset_names = [t["name"] for t in tools_subset]
# #     if "compare" in ql and "compare_net_income" in subset_names:
# #         calls.append({"tool_name": "compare_net_income", "parameters": {"companies": [], "year": 2024}})
# #     elif any(k in ql for k in ["quarter", "q1", "q2", "q3", "q4"]) and "compare_quarterly_income" in subset_names:
# #         calls.append({"tool_name": "compare_quarterly_income", "parameters": {"company": "", "year": 2024}})
# #     elif "three" in ql and "three_statements_" in subset_names:
# #         calls.append({"tool_name": "three_statements_", "parameters": {"company": "", "year": 2024}})
# #     elif "screen" in ql and "screen_companies" in subset_names:
# #         calls.append({"tool_name": "screen_companies", "parameters": {"filters": {}, "limit": 50}})
# #     elif "sector" in ql and "sector_wise_company" in subset_names:
# #         calls.append({"tool_name": "sector_wise_company", "parameters": {"sector": ""}})
# #     elif "company_info_" in subset_names:
# #         calls.append({"tool_name": "company_info_", "parameters": {"company": ""}})

# #     return calls


# def send_mcp_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
#     """Send a single tools/call request to the MCP server."""
#     req = {
#         "jsonrpc": "2.0",
#         "id": generate_request_id(),
#         "method": "tools/call",
#         "params": {
#             "name": name,
#             "arguments": arguments or {}
#         }
#     }
#     return send_mcp_request(req)


# def call_mcp_tools(user_query: str) -> List[Dict[str, Any]]:
#     # 
#     """
#     High-level entry: pick tools, ask LLM to craft calls, execute via MCP.
#     Returns the raw MCP responses (each should contain a 'result' with 'content').
#     """
#     # 1) Select candidate tools
#     selector = ToolSelector()
#     selected_names = selector.select_tools(user_query)

#     # 2) Get full catalog and filter to selected
#     catalog = fetch_tools_from_server()
#     tools_subset = filter_tools(catalog, selected_names)
#     
#     # 3) Ask LLM to decide concrete calls (stubbed)
#     llm_tool_calls = call_llm_with_tools(user_query, tools_subset)

#     # 4) Execute each tool via MCP
#     results = []
#     for tc in llm_tool_calls:
#         name = tc.get("tool_name")
#         args = tc.get("parameters", {})
#         resp = send_mcp_tool_call(name, args)
#         results.append(resp.get("result") or resp)  # prefer 'result' (MCP success), else whole resp (error)
#     return results




# import requests
# from django.conf import settings

# def send_mcp_tool_call(tool_call: dict):
#     """
#     Accepts JSON-RPC tool_call and routes it to FastAPI MCP backend.
#     Converts JSON-RPC format <-> HTTP format.
#     """
#     call_id = tool_call.get("id", 1)
#     method = tool_call.get("method")
#     params = tool_call.get("params", {})
#     

#     # Convert JSON-RPC → FastAPI format
#     url = f"{settings.FASTAPI_URL.rstrip('/')}/tools/call"
#     try:
#         resp = requests.post(url, json={
#             "tool_name": method,
#             "parameters": params
#         }, timeout=60)
#         resp.raise_for_status()
#         backend_result = resp.json()
#     except Exception as e:
#         return {
#             "jsonrpc": "2.0",
#             "id": call_id,
#             "error": {"code": -32000, "message": str(e)}
#         }

#     # Wrap back into JSON-RPC response
#     return {
#         "jsonrpc": "2.0",
#         "id": call_id,
#         "result": backend_result
#     }


import os
import requests

try:
    from django.conf import settings
    FASTAPI_URL = getattr(settings, "FASTAPI_URL", None)
except Exception:
    FASTAPI_URL = None


def send_mcp_tool_call(tool_name: str, parameters: dict) -> dict:
    """
    Accepts JSON-RPC tool_call and routes it to FastAPI MCP backend.
    Converts JSON-RPC format <-> HTTP format.
    
    Example input:
    {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "compare_quarterly_income",
        "params": {"company_name": "TCS", "year": "2022"}
    }
    """
    # call_id = tool_call.get("id", 1)
    # method = tool_call.get("method")
    # params = tool_call.get("params", {})
    

    # Select FastAPI URL (settings > env > default)
    base_url = FASTAPI_URL or os.getenv("FASTAPI_URL", "http://fastapi:8001")
    url = f"{base_url.rstrip('/')}/tools/call"

    try:
        resp = requests.post(
            url,
            json={"tool_name": tool_name, "parameters": parameters},
            timeout=60
        )
        print("resp_________new1------------------>>>>>>>", resp)
        resp.raise_for_status()
        backend_result = resp.json()
        return backend_result
    except Exception as e:
        return {"error": {"code": -32000, "message": str(e)}}

    # # Wrap into JSON-RPC success response
    # return {
    #     "jsonrpc": "2.0",
    #     "id": call_id,
    #     "result": backend_result
    # }

