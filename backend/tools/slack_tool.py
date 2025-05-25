from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackTool:
    """
    Tool for sending messages to Slack channels using the Slack API.
    Usage: run(token: str, channel: str, message: str) -> dict
    """
    def run(self, token: str, channel: str, message: str) -> dict:
        try:
            client = WebClient(token=token)
            response = client.chat_postMessage(channel=channel, text=message)
            return {"status": "success", "ts": response["ts"]}
        except SlackApiError as e:
            return {"status": "error", "error": str(e)}
        except Exception as e:
            return {"status": "error", "error": str(e)}