import requests

class WebhookTool:
    """
    Tool for sending generic HTTP POST requests to any webhook URL for automation.
    Usage: run(url: str, payload: dict) -> dict
    """
    def run(self, url: str, payload: dict) -> dict:
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return {"status": "success", "response": response.json() if response.headers.get('content-type') == 'application/json' else response.text}
        except Exception as e:
            return {"status": "error", "error": str(e)}