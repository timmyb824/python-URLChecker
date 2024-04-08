import os
from unittest.mock import MagicMock, patch

import pytest

from src.notifications.send_notification import send_notification_async


@pytest.mark.asyncio
async def test_send_notification_async():
    # Mock environment variables
    test_env = {
        "APPRISE_URL1": "mock://testurl1",
        "APPRISE_URL2": "mock://testurl2",
        "NOT_APPRISE": "should_not_be_used",
    }

    # Use a context manager to mock os.environ
    with patch.dict(os.environ, test_env, clear=True):
        # Mock the apprise.Apprise object and its methods
        with patch("apprise.Apprise") as mock_apprise:
            mock_apprise_obj = MagicMock()
            mock_apprise.return_value = mock_apprise_obj

            # Run the coroutine
            await send_notification_async("Test message")

            # Ensure the Apprise object was created and used correctly
            mock_apprise.assert_called_once()
            mock_apprise_obj.add.assert_any_call(test_env["APPRISE_URL1"])
            mock_apprise_obj.add.assert_any_call(test_env["APPRISE_URL2"])
            mock_apprise_obj.notify.assert_called_once_with(
                body="Test message", title="URL Checker Notification"
            )


###########################################
# WORKS LOCALLY BUT NOT IN GITHUB ACTIONS #
###########################################

# import os
# from unittest.mock import MagicMock, patch

# import pytest

# from src.notifications.send_notification import send_notification_async


# @pytest.mark.asyncio
# @pytest.mark.parametrize(
#     "env_vars, message, expected_calls, test_id",
#     [
#         # Happy path tests
#         (
#             {
#                 "APPRISE_URL1": "discord://webhook_id/webhook_token",
#                 "APPRISE_URL2": "telegram://bot_token/",
#             },
#             "Test message",
#             4,
#             "happy_path_multiple_services",
#         ),
#         (
#             {"APPRISE_URL1": "pover://user_key/device_key"},
#             "Another test message",
#             3,
#             "happy_path_single_service",
#         ),
#         # Edge case: No environment variables set
#         ({}, "No services configured", 2, "edge_case_no_services"),
#         # Edge case: Environment variables set but not starting with APPRISE_
#         (
#             {"NOT_APPRISE_URL": "discord://webhook_id/webhook_token"},
#             "Message with no valid services",
#             2,
#             "edge_case_invalid_env_var",
#         ),
#     ],
# )
# async def test_send_notification_async(env_vars, message, expected_calls, test_id):
#     with patch.dict(os.environ, env_vars), patch(
#         "notifications.send_notification.apprise.Apprise"
#     ) as mocked_apprise:
#         # Arrange
#         apobj_mock = MagicMock()
#         mocked_apprise.return_value = apobj_mock

#         # Act
#         await send_notification_async(message)

#         # Assert
#         assert apobj_mock.add.call_count == expected_calls
#         if expected_calls > 0:
#             apobj_mock.notify.assert_called_with(
#                 body=message, title="URL Checker Notification"
#             )
#         else:
#             apobj_mock.notify.assert_not_called()
