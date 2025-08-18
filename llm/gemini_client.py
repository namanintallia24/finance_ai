import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Load API key from environment
api_key = os.getenv("API_KEY")

# Validate API key
if not api_key:
    raise ValueError("API_KEY not found in .env file")

# Configure Gemini
genai.configure(api_key=api_key)

# Create Gemini model instance
model = genai.GenerativeModel("models/gemini-1.5-flash")

def run_gemini_prompt(prompt: str) -> str:
    """Send prompt to Gemini and return response text."""
    response = model.generate_content(prompt)
    return response.text.strip()
