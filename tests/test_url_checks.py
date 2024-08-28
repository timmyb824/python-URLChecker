from unittest.mock import AsyncMock, patch

import pytest
from aiohttp import ClientSession, ClientTimeout
from prometheus_client import CollectorRegistry, Counter, Gauge

from src.core.url_checks import check_url_status


@pytest.fixture(scope="function")
def prometheus_metrics():
    registry = CollectorRegistry()
    uptime_gauge = Gauge("url_uptime", "URL uptime status", ["url"], registry=registry)
    check_counter = Counter(
        "url_checks_total", "Total number of URL checks", ["url"], registry=registry
    )
    return uptime_gauge, check_counter


# Sample data for tests
test_data = [
    # Happy path tests
    (
        {
            "name": "Google",
            "url": "https://www.google.com",
            "status_accepted": [200],
            "retries": 3,
        },
        {"https://www.google.com": {"status": "unknown", "retries": 0}},
        "status_file.json",
        200,
        None,
        "happy_path_google_up",
    ),
    # Edge case: Accepted status not 200
    (
        {
            "name": "Custom API",
            "url": "https://api.example.com",
            "status_accepted": [202],
            "retries": 2,
        },
        {"https://api.example.com": {"status": "unknown", "retries": 0}},
        "status_file.json",
        202,
        None,
        "edge_case_custom_api_accepted_status",
    ),
    # Error case: URL down after retries
    (
        {
            "name": "Down Site",
            "url": "https://down.example.com",
            "status_accepted": [200],
            "retries": 1,
        },
        {"https://down.example.com": {"status": "unknown", "retries": 1}},
        "status_file.json",
        500,
        None,
        "error_case_site_down_after_retries",
    ),
    # Error case: Exception raised
    (
        {
            "name": "Exception Site",
            "url": "https://exception.example.com",
            "status_accepted": [200],
            "retries": 1,
        },
        {"https://exception.example.com": {"status": "unknown", "retries": 0}},
        "status_file.json",
        None,
        Exception("Connection failed"),
        "error_case_exception_raised",
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "check,status_dict,status_file,response_status,exception,case_id",
    test_data,
    ids=[td[-1] for td in test_data],
)
@patch("src.core.url_checks.save_status")
@patch("src.core.url_checks.send_notification_async")
@patch("src.core.url_checks.logger")
async def test_check_url_status(
    mock_logger,
    mock_send_notification_async,
    mock_save_status,
    prometheus_metrics,
    check,
    status_dict,
    status_file,
    response_status,
    exception,
    case_id,
):
    # Arrange
    session = AsyncMock(spec=ClientSession)
    uptime_gauge, check_counter = prometheus_metrics
    mock_response = AsyncMock()
    session.get.return_value.__aenter__.return_value = mock_response
    mock_response.status = response_status
    if exception:
        session.get.side_effect = exception

    # Act
    await check_url_status(
        session, check, status_file, status_dict, uptime_gauge, check_counter
    )

    # Assert
    mock_save_status.assert_called_once_with(status_dict, status_file)
    if response_status in check["status_accepted"]:
        assert status_dict[check["url"]]["status"] == "up"
    else:
        assert status_dict[check["url"]]["status"] == "down"
    if exception or (
        status_dict[check["url"]]["retries"] >= check["retries"]
        and status_dict[check["url"]]["status"] != "down"
    ):
        mock_send_notification_async.assert_called()
