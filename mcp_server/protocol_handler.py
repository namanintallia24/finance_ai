# mcp_server/protocol_handler.py

import json
from mcp_server.tools import call_tool, list_tools
from mcp_server.response_formatter import MCPResponseFormatter


class MCPProtocolHandler:
    def __init__(self, tools_manager=None, resources_manager=None):
        """
        tools_manager: Optional external manager for listing tools
        resources_manager: Optional external manager for listing resources
        """
        self.tools_manager = tools_manager
        self.resources_manager = resources_manager
        self.initialized = False

    def handle_message(self, message: dict) -> dict:
        """Main entrypoint: Handle incoming MCP JSON-RPC message"""
        method = message.get("method")
        message_id = message.get("id")
        
        # print("for tool callin purpose----------")
        try:
            if method == "initialize":
                return self.handle_initialize(message)

            elif method == "tools/list":
                return self.handle_tools_list(message)

            elif method == "tools/call":
                return self.handle_tools_call(message)

            elif method == "resources/list":
                return self.handle_resources_list(message)

            else:
                return self.create_error_response(
                    message_id, -32601, f"Method not found: {method}"
                )

        except Exception as e:
            return self.create_error_response(message_id, -32603, str(e))

    # -------------------------
    # MCP Standard Handlers
    # -------------------------

    def handle_initialize(self, message: dict) -> dict:
        """Handle MCP initialize request"""
        self.initialized = True
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": True,
                    "resources": True
                }
            }
        }

    def handle_tools_list(self, message: dict) -> dict:
        """Return list of available tools in MCP format"""
        if self.tools_manager:
            tools = self.tools_manager.list_tools()
        else:
            tools = list_tools()

        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": tools
        }

    def handle_tools_call(self, message: dict) -> dict:
        """Execute a tool and return MCP-compliant response"""
        params = message.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        result = call_tool(tool_name, arguments)

        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": result  # Already formatted by MCPResponseFormatter
        }

    def handle_resources_list(self, message: dict) -> dict:
        """Return list of available resources (if implemented)"""
        resources = []
        if self.resources_manager:
            resources = self.resources_manager.list_resources()

        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {"resources": resources}
        }

    # -------------------------
    # Error Handling
    # -------------------------

    def create_error_response(self, message_id, code, msg) -> dict:
        """Return standardized JSON-RPC error response"""
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "error": {
                "code": code,
                "message": msg
            }
        }
