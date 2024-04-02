import requests

from logs.log_handler import logger


# Function to send notification to Discord
def send_discord_notification(webhook_url: str, message: str) -> None:
    """Send a notification to Discord using a webhook URL"""
    payload = {"content": message}
    try:
        response = requests.post(webhook_url, json=payload, timeout=15)
        if response.status_code == 204:
            logger.info("Notification sent successfully.")
        else:
            logger.error("Failed to send notification.")
    except Exception as e:
        logger.error(f"Error sending Discord notification: {e}")
