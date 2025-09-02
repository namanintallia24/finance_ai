import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from llm.tool_selectors import TOOLS

# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")

if not api_key:
    raise ValueError("API_KEY not found in .env file")

# Configure Gemini
genai.configure(api_key=api_key)

# Create Gemini model instance (yahi tumhara `model` hai)
model = genai.GenerativeModel("models/gemini-1.5-flash")
# tools.py


def get_tool_call_from_gemini(query: str):
    """Send user query to Gemini and parse multiple JSON-RPC tool calls."""

    tools_description = json.dumps(TOOLS, indent=2)

    prompt = f"""
You are a tool selection engine.
We have these tools:
{tools_description}

User query: "{query}"

Return ALL required tool calls as a JSON array of JSON-RPC objects.
Each object must have "jsonrpc", "id", "method", and "params".
No explanation, no text, only valid JSON array.
"""

    response = model.generate_content(prompt)
    text = response.text.strip()

    # Remove markdown or ```json ``` wrappers
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()

    # Parse JSON
    try:
        tool_calls = json.loads(text)
    except Exception as e:
        raise ValueError(f"Gemini output invalid JSON after cleanup: {text}") from e

    # Ensure output is always a list
    if isinstance(tool_calls, dict):
        tool_calls = [tool_calls]
    elif not isinstance(tool_calls, list):
        raise ValueError(f"Unexpected Gemini output type: {type(tool_calls)}")

    return tool_calls