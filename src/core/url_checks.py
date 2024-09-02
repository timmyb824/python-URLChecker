import time
from typing import Any

import aiohttp
from aiohttp import ClientTimeout
from prometheus_client import Counter, Gauge, Histogram

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
    response_time: Histogram,
) -> None:
    """Check status of each URL and send Apprise notification if down."""
    name = check["name"]
    url = check["url"]
    status_accepted = check["status_accepted"]
    url_status = status_dict.get(url, {"status": "unknown", "retries": 0})
    retries_limit = check["retries"]

    check_counter.labels(url=url, name=name).inc()

    try:
        start_time = time.perf_counter()
        async with session.get(url, timeout=ClientTimeout(total=15)) as response:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            response_time.labels(url=url, name=name).observe(duration_ms)

            logger.info(
                f"Result for: {name} - {url} -- {response.status} (Response time: {duration_ms:.2f}ms)"
            )
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
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        response_time.labels(url=url, name=name).observe(duration_ms)

        logger.error(f"Error checking {url}: {e} (Response time: {duration_ms:.2f}ms)")
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
