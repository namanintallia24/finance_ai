# FINANCE_AI – MCP-Compliant Financial Assistant

This project implements a local AI-powered financial assistant using the Model Context Protocol (MCP). It allows structured interaction between large language models and CSV-based financial data.

## Features

- Follows MCP standard for tool execution and data access
- Streamlit frontend with Gemini integration
- Secure, offline-only processing
- Tools for analyzing income, balance sheets, etc.
- Robust tool routing based on LLM interpretation

## Project Structure

```text
finance_ai/
├── client/
│   └── test_tool_router.py
├── config/
├── data/
│   ├── hdfc_income.csv
│   ├── icici_income.csv
│   └── ...
├── frontend/
│   └── app.py
├── llm/
│   ├── gemini_client.py
│   ├── prompt_builder.py
│   └── tool_router.py
├── mcp_server/
│   ├── main.py
│   ├── schemas.py
│   └── tools.py
├── requirements.txt
└── README.md
```

## Instructions to Set Up and Run

1. Clone the repository:

```bash
git clone <your-repo-url>
cd finance_ai
```

2. Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the MCP server:

```bash
uvicorn mcp_server.main:app --reload

or 

cd mcp_server
uvicorn main:app --reload
```

5. In a new terminal, run the Streamlit app:

```bash
cd frontend
streamlit run app.py
```

6. Open your browser and go to:

```
http://localhost:8501
```

You can now ask financial questions like:

- Compare net income trend of HDFC and ICICI
- Show me balance sheet for ICICI in 2023
- Summarize assets for HDFC
