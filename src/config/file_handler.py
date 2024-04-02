import os
from typing import Optional

import yaml

from logs.log_handler import logger


def read_config(config_path: str) -> Optional[dict]:
    """Read the configuration file and return the contents as a dictionary"""
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        logger.error(f"Failed to read config file: {e}")
        return None


# def save_status(status_dict: dict, status_file: str) -> None:
#     """Save the status dictionary to a file"""
#     try:
#         with open(status_file, "w", encoding="utf-8") as file:
#             yaml.dump(status_dict, file)
#     except FileNotFoundError:
#         logger.error(f"Status file not found: {status_file}")
#     except Exception as e:
#         logger.error(f"Failed to save status to file: {e}")


def save_status(status_dict: dict, status_file: str) -> None:
    """Save the status dictionary to a file, ensuring the directory exists."""
    if directory := os.path.dirname(status_file):
        logger.info(f"Creating directory: {directory}")
        os.makedirs(directory, exist_ok=True)

    try:
        with open(status_file, "w", encoding="utf-8") as file:
            logger.info(f"Saving status to file: {status_file}")
            yaml.dump(status_dict, file)
    except Exception as e:
        logger.error(f"Failed to save status to file: {e}")


def load_status(status_file: str) -> dict:
    """Load the status dictionary from a file"""
    try:
        with open(status_file, "r", encoding="utf-8") as file:
            status_dict = yaml.safe_load(file) or {}
        return status_dict
    except FileNotFoundError:
        logger.info(f"Status file not found: {status_file}")
        return {}
    #     status_dict = {}
    #     save_status(status_dict, status_file)
    #     return status_dict
    except Exception as e:
        logger.error(f"Failed to load status from file: {e}")
        return {}
