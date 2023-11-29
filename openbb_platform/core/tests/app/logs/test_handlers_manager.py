import logging
from unittest.mock import Mock, patch

from openbb_core.app.logs.handlers_manager import (
    HandlersManager,
    PathTrackingFileHandler,
    PosthogHandler,
)


class MockPosthogHandler(logging.NullHandler):
    def __init__(self, settings):
        self.settings = settings
        self.level = logging.DEBUG


class MockPathTrackingFileHandler(logging.NullHandler):
    def __init__(self, settings):
        self.settings = settings
        self.level = logging.DEBUG


class MockFormatterWithExceptions(logging.Formatter):
    def __init__(self, settings):
        self.settings = settings


def test_handlers_added_correctly():
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
                assert hdlr.formatter.settings == changed_settings
