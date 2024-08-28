from typing import Any

import aiohttp
from aiohttp import ClientTimeout
from prometheus_client import Counter, Gauge

from config.file_handler import save_status
from logs.log_handler import logger
from notifications.send_notification import send_notification_async

uptime_gauge = None
check_counter = None


async def check_url_status(
    session: aiohttp.ClientSession,
    check: dict[str, Any],
    status_file: str,
    status_dict: dict[str, dict[str, Any]],
    uptime_gauge: Gauge,
    check_counter: Counter,
) -> None:
    """Check status of each URL and send Apprise notification if down."""
    name = check["name"]
    url = check["url"]
    status_accepted = check["status_accepted"]
    url_status = status_dict.get(url, {"status": "unknown", "retries": 0})
    retries_limit = check["retries"]

    check_counter.labels(url=url, name=name).inc()

    try:
        async with session.get(url, timeout=ClientTimeout(total=15)) as response:
            logger.info(f"Result for: {name} - {url} -- {response.status}")
            if response.status in status_accepted:
                if url_status["status"] == "down":
                    await send_notification_async(f"Recovery: {url} is back up.")
                status_dict[url] = {"status": "up", "retries": 0}
                uptime_gauge.labels(url=url, name=name).set(1)  # URL is up
            else:
                logger.error(f"{url} returned status code {response.status}")
                url_status["retries"] += 1
                status_dict[url] = url_status

                if url_status["retries"] >= retries_limit:
                    if url_status["status"] != "down":
                        await send_notification_async(
                            f"Alert: {url} is down after {retries_limit} retries."
                        )
                    status_dict[url] = {"status": "down", "retries": 0}
                    uptime_gauge.labels(url=url, name=name).set(0)  # URL is down
    except Exception as e:
        logger.error(f"Error checking {url}: {e}")
        url_status["retries"] += 1
        status_dict[url] = url_status

        if url_status["retries"] >= retries_limit:
            if url_status["status"] != "down":
                await send_notification_async(
                    f"Alert: {url} is down after {retries_limit} retries."
                )
            status_dict[url] = {"status": "down", "retries": 0}
            uptime_gauge.labels(url=url, name=name).set(0)  # URL is down

    save_status(status_dict, status_file)
