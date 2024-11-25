"""Tests for the PosthogHandler class."""

import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from openbb_core.app.logs.handlers.posthog_handler import (
    PosthogHandler,
)


# pylint: disable=W0621, R0913
class MockLoggingSettings:
    """Mock logging settings."""

    def __init__(
        self,
        app_name,
        sub_app_name,
        user_logs_directory,
        session_id,
        frequency,
        appid,
        platform,
        python_version,
        platform_version,
        userid,
    ):
        """Initialize the mock logging settings."""
        self.app_name = app_name
        self.sub_app_name = sub_app_name
        self.user_logs_directory = Path(user_logs_directory)
        self.session_id = session_id
        self.frequency = frequency
        self.app_id = appid
        self.platform = platform
        self.python_version = python_version
        self.platform_version = platform_version
        self.user_id = userid


logging_settings = MagicMock(spec=MockLoggingSettings)
logging_settings.app_name = "TestApp"
logging_settings.sub_app_name = "TestSubApp"
logging_settings.user_logs_directory = MagicMock()
logging_settings.user_logs_directory.absolute.return_value = Path(
    "/mocked/logs/directory"
)
logging_settings.session_id = "session123"
logging_settings.frequency = "H"
logging_settings.app_id = "test123"
logging_settings.platform = "Windows"
logging_settings.python_version = "3.9"
logging_settings.platform_version = "1.2.3"
logging_settings.user_id = "user123"
logging_settings.logging_suppress = False
logging_settings.log_collect = True


@pytest.fixture
def handler():
    """Fixture to create a PosthogHandler instance."""
    return PosthogHandler(logging_settings)


def test_emit_calls_send(handler):
    """Test the emit method."""
    # Arrange
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=42,
        msg="Test message",
        args=None,
        exc_info=None,
    )

    # Mock the send method
    handler.send = MagicMock()

    # Act
    handler.emit(record)

    # Assert
    handler.send.assert_called_once_with(record=record)


def test_emit_calls_handleError_when_send_raises_exception(handler):
    """Test the emit method."""
    # Arrange
    record = logging.LogRecord(
        name="test_logger",
        level=logging.ERROR,
        pathname="test.py",
        lineno=42,
        msg="Test error message",
        args=None,
        exc_info=None,
    )

    # Mock the send method to raise an exception
    handler.send = MagicMock(side_effect=Exception)

    # Mock the handleError method
    handler.handleError = MagicMock()

    # Act
    try:
        handler.emit(record)
    except Exception as e:
        assert isinstance(e, Exception)

    # Assert
    handler.send.assert_called_once_with(record=record)
    handler.handleError.assert_called_once_with(record)


def test_emit_calls_handleError_when_send_raises_exception_of_specific_type(handler):
    """Test the emit method."""
    # Arrange
    record = logging.LogRecord(
        name="test_logger",
        level=logging.ERROR,
        pathname="test.py",
        lineno=42,
        msg="Test error message",
        args=None,
        exc_info=None,
    )

    # Mock the send method to raise an exception of a specific type
    handler.send = MagicMock(side_effect=ValueError)

    # Mock the handleError method
    handler.handleError = MagicMock()

    # Act
    try:
        handler.emit(record)
    except Exception as e:
        assert isinstance(e, ValueError)

    # Assert
    handler.send.assert_called_once_with(record=record)
    handler.handleError.assert_called_once_with(record)


def test_emit_calls_handleError_when_send_raises_exception_of_another_type(handler):
    """Test the emit method."""
    # Arrange
    record = logging.LogRecord(
        name="test_logger",
        level=logging.ERROR,
        pathname="test.py",
        lineno=42,
        msg="Test error message",
        args=None,
        exc_info=None,
    )

    # Mock the send method to raise an exception of another type
    handler.send = MagicMock(side_effect=TypeError)

    # Mock the handleError method
    handler.handleError = MagicMock()

    # Act
    try:
        handler.emit(record)
    except Exception as e:
        assert isinstance(e, TypeError)

    # Assert
    handler.send.assert_called_once_with(record=record)
    handler.handleError.assert_called_once_with(record)


@pytest.mark.parametrize(
    "log_info, expected_dict",
    [
        (
            'STARTUP: {"status": "success"}',
            {"STARTUP": {"status": "success"}},
        ),
        (
            'CMD: {"path": "/stocks/", "known_cmd": "load", "other_args": "aapl", "input": "load aapl"}',
            {
                "CMD": {
                    "path": "/stocks/",
                    "known_cmd": "load",
                    "other_args": "aapl",
                    "input": "load aapl",
                }
            },
        ),
    ],
)
def test_log_to_dict(handler, log_info, expected_dict):
    """Test the log_to_dict method."""
    # Act
    result = handler.log_to_dict(log_info)

    # Assert
    assert result == expected_dict


@pytest.mark.parametrize(
    "record, expected_extra",
    [
        (
            logging.LogRecord(
                "name", logging.INFO, "pathname", 42, "message", (), None, None
            ),
            {
                "appName": "TestApp",
                "subAppName": "TestSubApp",
                "appId": "test123",
                "sessionId": "session123",
                "platform": "Windows",
                "pythonVersion": "3.9",
                "obbPlatformVersion": "1.2.3",
                "userId": "user123",
            },
        ),
    ],
)
def test_extract_log_extra(handler, record, expected_extra):
    """Test the extract_log_extra method."""
    # Act
    result = handler.extract_log_extra(record)

    # Assert
    assert result == expected_extra
