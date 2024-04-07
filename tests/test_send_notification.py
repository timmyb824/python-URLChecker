import os
from unittest.mock import MagicMock, patch

import pytest

from src.notifications.send_notification import send_notification_async


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "env_vars, message, expected_calls, test_id",
    [
        # Happy path tests
        (
            {
                "APPRISE_URL1": "discord://webhook_id/webhook_token",
                "APPRISE_URL2": "telegram://bot_token/",
            },
            "Test message",
            4,
            "happy_path_multiple_services",
        ),
        (
            {"APPRISE_URL1": "pover://user_key/device_key"},
            "Another test message",
            3,
            "happy_path_single_service",
        ),
        # Edge case: No environment variables set
        ({}, "No services configured", 2, "edge_case_no_services"),
        # Edge case: Environment variables set but not starting with APPRISE_
        (
            {"NOT_APPRISE_URL": "discord://webhook_id/webhook_token"},
            "Message with no valid services",
            2,
            "edge_case_invalid_env_var",
        ),
    ],
)
async def test_send_notification_async(env_vars, message, expected_calls, test_id):
    with patch.dict(os.environ, env_vars), patch(
        "notifications.send_notification.apprise.Apprise"
    ) as mocked_apprise:
        # Arrange
        apobj_mock = MagicMock()
        mocked_apprise.return_value = apobj_mock

        # Act
        await send_notification_async(message)

        # Assert
        assert apobj_mock.add.call_count == expected_calls
        if expected_calls > 0:
            apobj_mock.notify.assert_called_with(
                body=message, title="URL Checker Notification"
            )
        else:
            apobj_mock.notify.assert_not_called()
