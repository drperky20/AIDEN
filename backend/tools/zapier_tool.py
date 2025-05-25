import requests

class ZapierTool:
    """
    Tool for triggering Zapier webhooks for automation workflows.
    Usage: run(zap_url: str, payload: dict) -> dict
    """
    def run(self, zap_url: str, payload: dict) -> dict:
        try:
            response = requests.post(zap_url, json=payload, timeout=10)
            response.raise_for_status()
            return {"status": "success", "response": response.json() if response.headers.get('content-type') == 'application/json' else response.text}
        except Exception as e:
            return {"status": "error", "error": str(e)}