# mcp_server/response_formatter.py

import json


class MCPResponseFormatter:
    @staticmethod
    def format_tool_response(result: any) -> dict:
        """Convert any tool result to MCP-compliant format"""
        if isinstance(result, dict):
            content_text = json.dumps(result, indent=2)
        elif isinstance(result, list):
            content_text = json.dumps(result, indent=2)
        elif isinstance(result, str):
            content_text = result
        else:
            content_text = str(result)

        return {
            "content": [
                {
                    "type": "text",
                    "text": content_text
                }
            ]
        }

    @staticmethod
    def format_error_response(error_msg: str) -> dict:
        """Format error in MCP-compliant way"""
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error: {error_msg}"
                }
            ]
        }
