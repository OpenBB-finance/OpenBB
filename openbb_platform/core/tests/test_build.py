"""Tests for the build module."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from openbb_core.build import main


class TestBuild:
    """Test the build module."""

    @patch("builtins.__import__")
    @patch("openbb_core.build.subprocess.run")
    def test_main_successful_build_found(self, mock_run, mock_import):
        """Test main when import openbb produces a build."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Building openbb...\n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
        mock_import.assert_not_called()

    @patch("builtins.__import__")
    @patch("openbb_core.build.subprocess.run")
    def test_main_successful_build_required(self, mock_run, mock_import):
        """Test main when openbb needs to be built after import."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Normal import output\n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        mock_openbb = MagicMock()
        mock_openbb.build = MagicMock()
        mock_import.return_value = mock_openbb

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
        mock_openbb.build.assert_called_once()

    @patch("openbb_core.build.subprocess.run")
    def test_main_openbb_not_installed(self, mock_run):
        """Test main when openbb is not installed."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "ModuleNotFoundError: No module named 'openbb'\n"
        mock_run.return_value = mock_result

        with pytest.raises(subprocess.CalledProcessError):
            main()

    @patch("openbb_core.build.subprocess.run")
    def test_main_with_other_error(self, mock_run):
        """Test main when subprocess fails with non-ModuleNotFoundError."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "Some output"
        mock_result.stderr = "Some other error\n"
        mock_run.return_value = mock_result

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    @patch("builtins.__import__")
    @patch("openbb_core.build.subprocess.run")
    def test_main_build_failure(self, mock_run, mock_import):
        """Test main when build fails during import."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Normal output\n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        mock_import.side_effect = RuntimeError("Build failed")

        with pytest.raises(RuntimeError):
            main()

    @patch("builtins.__import__")
    @patch("openbb_core.build.subprocess.run")
    def test_main_exception_handling(self, mock_run, mock_import):
        """Test main handles exceptions during build gracefully."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Output\n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        exception = Exception("Generic error")
        mock_import.side_effect = exception

        with pytest.raises(RuntimeError):
            main()
