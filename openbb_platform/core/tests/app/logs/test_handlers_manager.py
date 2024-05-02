"""Tests for the handlers manager."""

import logging
from unittest.mock import Mock, patch

from openbb_core.app.logs.handlers_manager import (
    HandlersManager,
    PathTrackingFileHandler,
    PosthogHandler,
)

# pylint: disable=W0231


class MockPosthogHandler(logging.NullHandler):
    """Mock posthog handler."""

    def __init__(self, settings):
        """Initialize the handler."""
        self.settings = settings
        self.level = logging.DEBUG


class MockPathTrackingFileHandler(logging.NullHandler):
    """Mock path tracking file handler."""

    def __init__(self, settings):
        """Initialize the handler."""
        self.settings = settings
        self.level = logging.DEBUG


class MockFormatterWithExceptions(logging.Formatter):
    """Mock formatter with exceptions."""

    def __init__(self, settings):
        """Initialize the formatter."""
        self.settings = settings


def test_handlers_added_correctly():
    """Test if the handlers are added correctly."""
    with patch(
        "openbb_core.app.logs.handlers_manager.PosthogHandler",
        MockPosthogHandler,
    ), patch(
        "openbb_core.app.logs.handlers_manager.PathTrackingFileHandler",
        MockPathTrackingFileHandler,
    ), patch(
        "openbb_core.app.logs.handlers_manager.FormatterWithExceptions",
        MockFormatterWithExceptions,
    ):
        settings = Mock()
        settings.handler_list = ["stdout", "stderr", "noop", "file", "posthog"]
        _ = HandlersManager(settings=settings)

        handlers = logging.getLogger().handlers

        assert len(handlers) >= 5

        for handler in handlers:
            assert isinstance(
                handler,
                (
                    logging.NullHandler,
                    logging.StreamHandler,
                    PathTrackingFileHandler,
                    PosthogHandler,
                ),
            )

        for mock in [MockPosthogHandler, MockPathTrackingFileHandler]:
            assert any(isinstance(handler, mock) for handler in handlers)


def test_update_handlers():
    """Test if the handlers are updated correctly."""
    with patch(
        "openbb_core.app.logs.handlers_manager.PosthogHandler",
        MockPosthogHandler,
    ), patch(
        "openbb_core.app.logs.handlers_manager.PathTrackingFileHandler",
        MockPathTrackingFileHandler,
    ), patch(
        "openbb_core.app.logs.handlers_manager.FormatterWithExceptions",
        MockFormatterWithExceptions,
    ):
        settings = Mock()
        settings.handler_list = ["file", "posthog"]
        settings.any_other_attr = "mock_settings"
        handlers_manager = HandlersManager(settings=settings)

        changed_settings = Mock()
        changed_settings.any_other_attr = "changed_settings"

        handlers_manager.update_handlers(settings=changed_settings)

        handlers = logging.getLogger().handlers

        for hdlr in handlers:
            if isinstance(hdlr, (MockPosthogHandler, MockPathTrackingFileHandler)):
                assert hdlr.settings == changed_settings
                assert hdlr.formatter.settings == changed_settings  # type: ignore[union-attr]
