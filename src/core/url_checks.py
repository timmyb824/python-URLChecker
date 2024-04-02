from typing import Any

import requests

from config.file_handler import save_status
from logs.log_handler import logger
from notifications.discord import send_discord_notification


def check_url_status(
    check: dict[str, Any],
    webhook_url: str,
    status_file: str,
    status_dict: dict[str, dict[str, Any]],
) -> None:
    """Check the status of a URL and update the status dictionary"""
    url = check["url"]
    status_accepted = check["status_accepted"]
    url_status = status_dict.get(url, {"status": "unknown", "retries": 0})
    retries_limit = check["retries"]

    try:
        response = requests.get(url, timeout=15)
        print(f"URL: {url} - Status Code: {response.status_code}")
        if response.status_code in status_accepted:
            if url_status["status"] == "down":
                # URL recovered from downtime, send notification only once
                send_discord_notification(webhook_url, f"Recovery: {url} is back up.")
            # Update or reset status to up and retries
            status_dict[url] = {"status": "up", "retries": 0}
        else:
            # If the response code is not accepted, increment the retry count
            logger.info(f"{url} returned status code {response.status_code}")
            url_status["retries"] += 1
            status_dict[url] = url_status

            if url_status["retries"] >= retries_limit:
                if url_status["status"] != "down":
                    # URL is down, send notification only once
                    send_discord_notification(
                        webhook_url,
                        f"Alert: {url} is down after {retries_limit} retries.",
                    )
                # Update status to down and reset retries
                status_dict[url] = {"status": "down", "retries": 0}
    except Exception as e:
        logger.error(f"Error checking {url}: {e}")
        url_status["retries"] += 1
        status_dict[url] = url_status

        if url_status["retries"] >= retries_limit:
            if url_status["status"] != "down":
                # URL is down, send notification only once
                send_discord_notification(
                    webhook_url, f"Alert: {url} is down after {retries_limit} retries."
                )
            # Update status to down and reset retries
            status_dict[url] = {"status": "down", "retries": 0}

    # Save the updated status to the status file after each check
    save_status(status_dict, status_file)
