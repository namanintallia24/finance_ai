import requests

BASE_URL = "http://127.0.0.1:8000"

def test_tool_list():
    print("\n=== GET /tools/list ===")
    resp = requests.get(f"{BASE_URL}/tools/list")
    print(resp.json())

def test_resource_list():
    print("\n=== GET /resources/list ===")
    resp = requests.get(f"{BASE_URL}/resources/list")
    print(resp.json())

def test_call_compare_net_income():
    print("\n=== POST /tools/call - compare_net_income ===")
    data = {
        "tool_name": "compare_net_income",
        "parameters": {
            "company_names": ["HDFC", "ICICI"]
        }
    }
    resp = requests.post(f"{BASE_URL}/tools/call", json=data)
    print(resp.status_code)
    print(resp.text)

def test_call_summarize_balance_sheet():
    print("\n=== POST /tools/call - summarize_balance_sheet ===")
    data = {
        "tool_name": "summarize_balance_sheet",
        "parameters": {
            "company_name": "HDFC",
            "year": "2023"
        }
    }
    resp = requests.post(f"{BASE_URL}/tools/call", json=data)
    print(resp.json())

if __name__ == "__main__":
    test_tool_list()
    test_resource_list()
    test_call_compare_net_income()
    test_call_summarize_balance_sheet()
