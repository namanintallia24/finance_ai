from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from mcp_server.tools import list_tools, call_tool
from mcp_server.resources import list_resources
import uvicorn

app = FastAPI(title="MCP-Compliant Server for Financial Assistant")

@app.get("/tools/list")
def tools_list():
    return JSONResponse(content=list_tools())

@app.post("/tools/call")
async def tools_call(request: Request):
    body = await request.json()
    tool_name = body.get("tool_name")
    parameters = body.get("parameters")
    return JSONResponse(content=call_tool(tool_name, parameters))

@app.get("/resources/list")
def resources_list():
    return JSONResponse(content=list_resources())

if __name__ == "__main__":
    uvicorn.run("mcp_server.main:app", host="0.0.0.0", port=8000, reload=True)
