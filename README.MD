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
finance_ai-main/
├── client/
│   ├── __init__.py
│   └── mcp_client.py          # Client for MCP communication
│
├── data1/
│   ├── __init__.py
│   ├── db.py                  # Database connection logic
│   └── table_create.py        # Table creation scripts
│
├── finance_app/               # Django app (contains models, views, APIs)
│
├── finance_project/           # Django project (settings, urls, wsgi/asgi)
│
├── frontend/
│   ├── __init__.py
│   └── table_create.py        # Utility for table creation (frontend specific)
│
├── llm/                       # LLM integration
│   ├── gemini_client.py
│   ├── prompt_builder.py
│   └── tool_router.py
│
├── mcp_server/
│   ├── main.py                # MCP FastAPI server
│   ├── schemas.py
│   └── tools.py
│
├── venv/                      # Python virtual environment
├── venv2/                     # (Optional) second venv
│
├── .env                       # Environment variables
├── db.sqlite3                 # Default SQLite database
├── docker-compose.yml         # Docker services config
├── Dockerfile                 # Docker build config
├── manage.py                  # Django management commands
├── requirements.txt           # Python dependencies
└── README.md
```

## Instructions to Set Up and Run

1. Clone the repository:

```bash
git clone <your-repo-url>
cd finance_ai-main
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


4. Set up environment variables

```bash
SECRET_KEY=your_django_secret_key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

5. Run database migrations

```bash
python manage.py migrate
```


6. Run the MCP server:

```bash
uvicorn mcp_server.main:app --reload --port 8001
```

7. Run the Django server:

```bash
python manage.py runserver
```

You can now ask financial questions like:

- Compare net income trend of HDFC and ICICI
- Show me balance sheet for ICICI in 2023
- Summarize assets for HDFC
