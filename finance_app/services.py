import requests
from django.conf import settings

def call_tool_http(tool_name: str, parameters: dict):
    """
    Calls your FastAPI MCP endpoint that you used in streamlit:
    POST /tools/call body: {"tool_name":..., "parameters":...}
    """
    url = f"{settings.FASTAPI_URL.rstrip('/')}/tools/call"
    resp = requests.post(url, json={"tool_name": tool_name, "parameters": parameters}, timeout=60)
    resp.raise_for_status()
    return resp.json()
