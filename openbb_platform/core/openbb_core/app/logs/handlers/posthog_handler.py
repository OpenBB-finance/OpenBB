"""Posthog Handler."""

import json
import logging
from enum import Enum
from typing import Any, Dict

import posthog
from openbb_core.app.logs.formatters.formatter_with_exceptions import (
    FormatterWithExceptions,
)
from openbb_core.app.logs.models.logging_settings import LoggingSettings
from openbb_core.env import Env


class PosthogHandler(logging.Handler):
    """Posthog Handler."""

    class AllowedEvents(Enum):
        """Allowed Posthog Events."""

        log_startup = "log_startup"
        log_cmd = "log_cmd"
        log_error = "log_error"
        log_warning = "log_warning"

    def __init__(self, settings: LoggingSettings):
        """Initialize Posthog Handler."""

        super().__init__()
        self._settings = settings
        self.logged_in = False
        posthog.api_key = "phc_6FXLqu4uW9yxfyN8DpPdgzCdlYXOmIWdMGh6GnBgJLX"  # pragma: allowlist secret  # noqa
        posthog.host = "https://app.posthog.com"  # noqa

    @property
    def settings(self) -> LoggingSettings:
        """Get logging settings."""
        # pylint: disable=import-outside-toplevel
        from copy import deepcopy

        return deepcopy(self._settings)

    @settings.setter
    def settings(self, settings: LoggingSettings) -> None:
        """Set logging settings."""
        self._settings = settings

    def emit(self, record: logging.LogRecord):
        """Emit log record."""
        try:
            self.send(record=record)
        except Exception as e:
            self.handleError(record)
            if Env().DEBUG_MODE:
                raise e

    def distinct_id(self) -> str:
        """Get distinct id."""
        return self._settings.user_id or self._settings.app_id

    def identify(self) -> None:
        """Identify user."""
        if self.logged_in or not self._settings.user_id:
            return

        posthog.identify(
            self._settings.user_id,
            {
                "email": self._settings.user_email,
                "primaryUsage": self._settings.user_primary_usage,
            },
        )

        if self._settings.sub_app_name == "pro":
            return

        self.logged_in = True
        posthog.alias(self._settings.user_id, self._settings.app_id)

    def log_to_dict(self, log_info: str) -> dict:
        """Log to dict."""
        # pylint: disable=import-outside-toplevel
        import re

        log_regex = r"(STARTUP|CMD|ERROR): (.*)"
        log_dict: Dict[str, Any] = {}

        for log in re.findall(log_regex, log_info):
            log_dict[log[0]] = json.loads(log[1])

        return log_dict

    def send(self, record: logging.LogRecord):
        """Send log record to Posthog."""
        # pylint: disable=import-outside-toplevel
        import re

        level_name = logging.getLevelName(record.levelno)
        log_line = FormatterWithExceptions.filter_log_line(text=record.getMessage())

        log_extra = self.extract_log_extra(record=record)
        log_extra.update(dict(level=level_name, message=log_line))
        event_name = f"log_{level_name.lower()}"

        if log_dict := self.log_to_dict(log_info=log_line):
            event_name = f"log_{list(log_dict.keys())[0].lower()}"
            log_dict = log_dict.get("STARTUP", log_dict)

            log_extra = {**log_extra, **log_dict}
            log_extra.pop("message", None)

        if re.match(r"^(QUEUE|START|END|INPUT:)", log_line) and not log_dict:
            return

        if event_name not in [e.value for e in self.AllowedEvents]:
            return

        self.identify()
        posthog.capture(self.distinct_id(), event_name, properties=log_extra)

    def extract_log_extra(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Extract log extra from record."""
        log_extra: Dict[str, Any] = {
            "appName": self._settings.app_name,
            "subAppName": self._settings.sub_app_name,
            "appId": self._settings.app_id,
            "sessionId": self._settings.session_id,
            "platform": self._settings.platform,
            "pythonVersion": self._settings.python_version,
            "obbPlatformVersion": self._settings.platform_version,
        }

        if self._settings.user_id:
            log_extra["userId"] = self._settings.user_id

        if hasattr(record, "extra"):
            log_extra = {**log_extra, **record.extra}  # type: ignore

        if record.exc_info:
            log_extra["exception"] = {
                "type": str(record.exc_info[0]),
                "value": str(record.exc_info[1]),
            }

        return log_extra
