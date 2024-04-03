import unittest
from unittest import mock

from src.config.file_handler import load_status, read_config, save_status


class TestFileHandler(unittest.TestCase):
    @mock.patch("src.config.file_handler.yaml.safe_load")
    @mock.patch("builtins.open", new_callable=mock.mock_open, read_data="config: value")
    def test_read_config(self, mock_open, mock_safe_load):
        mock_safe_load.return_value = {"config": "value"}
        result = read_config("path/to/config")
        self.assertEqual(result, {"config": "value"})

    @mock.patch("src.config.file_handler.yaml.dump")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    @mock.patch("os.makedirs")
    def test_save_status(self, mock_makedirs, mock_open, mock_dump):
        save_status({"status": "value"}, "path/to/status")
        mock_makedirs.assert_called_once_with("path/to", exist_ok=True)
        mock_open.assert_called_once_with("path/to/status", "w", encoding="utf-8")
        mock_dump.assert_called_once_with({"status": "value"}, mock.ANY)

    @mock.patch("src.config.file_handler.yaml.safe_load")
    @mock.patch("builtins.open", new_callable=mock.mock_open, read_data="status: value")
    def test_load_status(self, mock_open, mock_safe_load):
        mock_safe_load.return_value = {"status": "value"}
        result = load_status("path/to/status")
        self.assertEqual(result, {"status": "value"})

    @mock.patch("src.config.file_handler.yaml.safe_load")
    @mock.patch("builtins.open", new_callable=mock.mock_open, read_data="status: value")
    def test_load_status_file_not_found(self, mock_open, mock_safe_load):
        mock_open.side_effect = FileNotFoundError
        result = load_status("path/to/status")
        self.assertEqual(result, {})
