import requests

class MCPTool:
    """
    Tool for interacting with a Model Context Protocol (MCP) server for automation.
    Usage: run(mcp_url: str, action: str, payload: dict) -> dict
    """
    def run(self, mcp_url: str, action: str, payload: dict) -> dict:
        try:
            url = f"{mcp_url.rstrip('/')}/{action.lstrip('/')}"
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            return {"status": "success", "response": response.json() if response.headers.get('content-type') == 'application/json' else response.text}
        except Exception as e:
            return {"status": "error", "error": str(e)}