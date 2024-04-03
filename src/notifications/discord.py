import aiohttp
from aiohttp import ClientTimeout

from logs.log_handler import logger


async def send_discord_notification(
    session: aiohttp.ClientSession, webhook_url: str, message: str
) -> None:
    """Send a notification to Discord using a webhook URL asynchronously"""
    payload = {"content": message}
    try:
        async with session.post(
            webhook_url, json=payload, timeout=ClientTimeout(total=15)
        ) as response:
            if response.status == 204:
                logger.info("Notification sent successfully.")
            else:
                logger.error("Failed to send notification.")
    except Exception as e:
        logger.error(f"Error sending Discord notification: {e}")
