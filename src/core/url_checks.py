from typing import Any

import aiohttp
from aiohttp import ClientTimeout

from config.file_handler import save_status
from logs.log_handler import logger
from notifications.discord import send_discord_notification


async def check_url_status(
    session: aiohttp.ClientSession,
    check: dict[str, Any],
    webhook_url: str,
    status_file: str,
    status_dict: dict[str, dict[str, Any]],
) -> None:
    """Check the status of a URL and update the status dictionary asynchronously"""
    url = check["url"]
    status_accepted = check["status_accepted"]
    url_status = status_dict.get(url, {"status": "unknown", "retries": 0})
    retries_limit = check["retries"]

    try:
        async with session.get(url, timeout=ClientTimeout(total=15)) as response:
            print(f"URL: {url} - Status Code: {response.status}")
            if response.status in status_accepted:
                if url_status["status"] == "down":
                    await send_discord_notification(
                        session, webhook_url, f"Recovery: {url} is back up."
                    )
                status_dict[url] = {"status": "up", "retries": 0}
            else:
                logger.info(f"{url} returned status code {response.status}")
                url_status["retries"] += 1
                status_dict[url] = url_status

                if url_status["retries"] >= retries_limit:
                    if url_status["status"] != "down":
                        await send_discord_notification(
                            session,
                            webhook_url,
                            f"Alert: {url} is down after {retries_limit} retries.",
                        )
                    status_dict[url] = {"status": "down", "retries": 0}
    except Exception as e:
        logger.error(f"Error checking {url}: {e}")
        url_status["retries"] += 1
        status_dict[url] = url_status

        if url_status["retries"] >= retries_limit:
            if url_status["status"] != "down":
                await send_discord_notification(
                    session,
                    webhook_url,
                    f"Alert: {url} is down after {retries_limit} retries.",
                )
            status_dict[url] = {"status": "down", "retries": 0}

    save_status(status_dict, status_file)
