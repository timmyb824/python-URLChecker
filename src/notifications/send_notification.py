import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

import apprise


async def send_notification_async(message: str) -> None:
    """Send notification asynchronously using Apprise with environment variables."""

    def notify_sync():
        apobj = apprise.Apprise()
        # Add all services from environment variables
        for key, value in os.environ.items():
            if key.startswith("APPRISE_"):
                apobj.add(value)
        apobj.notify(body=message, title="URL Checker Notification")

    loop = asyncio.get_running_loop()
    # Run the synchronous notification function in a separate thread
    await loop.run_in_executor(ThreadPoolExecutor(), notify_sync)
