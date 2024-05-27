import os

ROOT_DIR = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "../.")
)  # project root
HOME_PATH = os.getenv("HOME")
CONFIG_PATH = "checks.yaml"  # f"{home_path}/.config/ppi/checks.yml"
STATUS_FILE = "status.yaml"  # f"{home_path}/.config/ppi/status.yml"
SCHEMA_PATH = "src/schema/schema.yaml"
TIME_BETWEEN_INITIAL_CHECKS = 5
TIME_BETWEEN_SCHEDULED_CHECKS = os.getenv("TIME_BETWEEN_SCHEDULED_CHECKS") or 60
HEALTHCHECKS_URL = os.getenv("HEALTHCHECKS_URL_PYTHON_URLCHECKER")
