import os

HOME_PATH = os.getenv("HOME")
CONFIG_PATH = "checks.yaml"  # f"{home_path}/.config/ppi/checks.yml"
STATUS_FILE = "status.yaml"  # f"{home_path}/.config/ppi/status.yml"
SCHEMA_PATH = "src/schema/schema.yaml"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
TIME_BETWEEN_INITIAL_CHECKS = 5
TIME_BETWEEN_SCHEDULED_CHECKS = 15
