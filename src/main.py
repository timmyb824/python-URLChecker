import asyncio
import sys

import aiohttp

from config.file_handler import load_status, read_config
from config.validate import validate_yaml_file
from constants import (
    CONFIG_PATH,
    HEALTHCHECKS_URL,
    SCHEMA_PATH,
    STATUS_FILE,
    TIME_BETWEEN_INITIAL_CHECKS,
    TIME_BETWEEN_SCHEDULED_CHECKS,
)
from core.url_checks import check_url_status
from logs.log_handler import logger


async def send_health_check(session: aiohttp.ClientSession, url: str) -> None:
    """Send a health check signal to the healthchecks.io endpoint."""
    try:
        async with session.get(url, timeout=10) as response:
            if response.status != 200:
                logger.error(
                    f"Failed to send health check signal. Status code: {response.status}"
                )
            logger.info(f"Health check signal sent to {url}")
    except aiohttp.ClientError as e:
        logger.error(f"Failed to send health check signal. Exception: {e}")


async def main() -> None:
    """Main function to run the URL status checks"""
    status_file = STATUS_FILE
    config_path = CONFIG_PATH
    schema_path = SCHEMA_PATH

    if not validate_yaml_file(schema_path, config_path):
        logger.error("Invalid configuration. Exiting...")
        sys.exit(1)

    config = read_config(config_path)

    if not config:
        logger.error("No configuration found. Exiting...")
        sys.exit(1)

    status_dict = load_status(status_file)

    async with aiohttp.ClientSession() as session:
        # Initial status check for each URL
        for check in config:
            url = check["url"]
            if url not in status_dict:
                await check_url_status(session, check, status_file, status_dict)

        await asyncio.sleep(float(TIME_BETWEEN_INITIAL_CHECKS))

        while True:
            for check in config:
                await check_url_status(session, check, status_file, status_dict)

            if HEALTHCHECKS_URL:
                await send_health_check(session, HEALTHCHECKS_URL)

            await asyncio.sleep(float(TIME_BETWEEN_SCHEDULED_CHECKS))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
