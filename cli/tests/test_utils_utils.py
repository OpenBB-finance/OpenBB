"""Test the utils/utils module."""

import json


class TestChangeLoggingSubApp:
    def test_sets_cli_sub_app(self, tmp_path):
        """Test that change_logging_sub_app sets logging_sub_app to 'cli'."""
        settings_file = tmp_path / "system_settings.json"
        settings_file.write_text(json.dumps({"logging_sub_app": ""}))

        from unittest.mock import patch

        with patch("openbb_cli.utils.utils.SYSTEM_SETTINGS_PATH", settings_file):
            from openbb_cli.utils.utils import change_logging_sub_app

            initial = change_logging_sub_app()

        assert initial == ""
        data = json.loads(settings_file.read_text())
        assert data["logging_sub_app"] == "cli"

    def test_returns_previous_value(self, tmp_path):
        """Test it returns the previous logging_sub_app value."""
        settings_file = tmp_path / "system_settings.json"
        settings_file.write_text(json.dumps({"logging_sub_app": "sdk"}))

        from unittest.mock import patch

        with patch("openbb_cli.utils.utils.SYSTEM_SETTINGS_PATH", settings_file):
            from openbb_cli.utils.utils import change_logging_sub_app

            initial = change_logging_sub_app()

        assert initial == "sdk"

    def test_creates_key_if_missing(self, tmp_path):
        """Test it handles missing logging_sub_app key."""
        settings_file = tmp_path / "system_settings.json"
        settings_file.write_text(json.dumps({}))

        from unittest.mock import patch

        with patch("openbb_cli.utils.utils.SYSTEM_SETTINGS_PATH", settings_file):
            from openbb_cli.utils.utils import change_logging_sub_app

            initial = change_logging_sub_app()

        assert initial == ""
        data = json.loads(settings_file.read_text())
        assert data["logging_sub_app"] == "cli"


class TestResetLoggingSubApp:
    def test_resets_to_original(self, tmp_path):
        """Test that reset_logging_sub_app restores the original value."""
        settings_file = tmp_path / "system_settings.json"
        settings_file.write_text(json.dumps({"logging_sub_app": "cli"}))

        from unittest.mock import patch

        with patch("openbb_cli.utils.utils.SYSTEM_SETTINGS_PATH", settings_file):
            from openbb_cli.utils.utils import reset_logging_sub_app

            reset_logging_sub_app("sdk")

        data = json.loads(settings_file.read_text())
        assert data["logging_sub_app"] == "sdk"

    def test_resets_to_empty(self, tmp_path):
        """Test resetting to empty string."""
        settings_file = tmp_path / "system_settings.json"
        settings_file.write_text(json.dumps({"logging_sub_app": "cli"}))

        from unittest.mock import patch

        with patch("openbb_cli.utils.utils.SYSTEM_SETTINGS_PATH", settings_file):
            from openbb_cli.utils.utils import reset_logging_sub_app

            reset_logging_sub_app("")

        data = json.loads(settings_file.read_text())
        assert data["logging_sub_app"] == ""
