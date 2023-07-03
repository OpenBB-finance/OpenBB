# IMPORT STANDARD
import json
import logging
from enum import Enum
from typing import Any, Callable, Dict, Optional

# IMPORT THIRD-PARTY
from pydantic.json import pydantic_encoder

from openbb_sdk_core.app.model.command_output import CommandOutput
from openbb_sdk_core.app.model.system_settings import SystemSettings
from openbb_sdk_core.app.model.user_settings import UserSettings

# IMPORT INTERNAL
from openbb_sdk_core.app.service.system_service import SystemService
from openbb_sdk_core.app.service.user_service import UserService
from openbb_sdk_core.logs.formatters.formatter_with_exceptions import (
    FormatterWithExceptions,
)
from openbb_sdk_core.logs.handlers_manager import HandlersManager
from openbb_sdk_core.logs.models.logging_settings import LoggingSettings


class LoggingManager:
    def __init__(
        self,
        system_settings: Optional[SystemSettings] = None,
        user_settings: Optional[UserSettings] = None,
    ) -> None:
        self._user_settings = (
            user_settings or UserService().read_default_user_settings()
        )
        self._system_settings = (
            system_settings or SystemService().read_default_system_settings()
        )
        self._logging_settings = LoggingSettings(
            user_settings=self._user_settings,
            system_settings=self._system_settings,
        )
        self._handlers_manager = self._setup_handlers()
        self._log_startup()

    def _setup_handlers(self) -> HandlersManager:
        """Setup Logging"""
        logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=self._logging_settings.verbosity,
            format=FormatterWithExceptions.LOGFORMAT,
            datefmt=FormatterWithExceptions.DATEFORMAT,
            handlers=[],
        )
        handlers_manager = HandlersManager(settings=self._logging_settings)

        logger.info("Logging configuration finished")
        logger.info("Logging set to %s", self._logging_settings.handler_list)
        logger.info("Verbosity set to %s", self._logging_settings.verbosity)
        logger.info(
            "LOGFORMAT: %s%s",
            FormatterWithExceptions.LOGPREFIXFORMAT.replace("|", "-"),
            FormatterWithExceptions.LOGFORMAT.replace("|", "-"),
        )

        return handlers_manager

    def _log_startup(self) -> None:
        def check_credentials_defined(credentials: Dict[str, Any]):
            class CredentialsDefinition(Enum):
                defined = "defined"
                undefined = "undefined"

            return {
                c: CredentialsDefinition.defined.value
                if credentials[c]
                else CredentialsDefinition.undefined.value
                for c in credentials
            }

        logger = logging.getLogger(__name__)
        logger.info(
            "STARTUP: %s ",
            json.dumps(
                {
                    "PREFERENCES": self._user_settings.preferences,
                    "KEYS": check_credentials_defined(
                        self._user_settings.credentials.dict()
                        if self._user_settings.credentials
                        else {}
                    ),
                    "SYSTEM": self._system_settings,
                },
                default=pydantic_encoder,
            ),
        )

    def log(
        self,
        user_settings: UserSettings,
        system_settings: SystemSettings,
        command_output: CommandOutput,
        route: str,
        func: Callable,
        kwargs: Dict[str, Any],
    ):
        self._user_settings = user_settings
        self._system_settings = system_settings
        self._logging_settings = LoggingSettings(
            user_settings=self._user_settings,
            system_settings=self._system_settings,
        )
        self._handlers_manager.update_handlers(self._logging_settings)

        if "login" in route:
            self._log_startup()
        else:
            logger = logging.getLogger(__name__)

            # Remove CommandContext if any
            if "cc" in kwargs:
                kwargs.pop("cc")

            # Truncate kwargs if too long
            kwargs = {k: str(v)[:100] for k, v in kwargs.items()}

            log_level = logger.error if command_output.error else logger.info
            log_level(
                "ERROR: %s" if command_output.error else "CMD: %s",
                json.dumps(
                    {
                        "route": route,
                        "input": kwargs,
                        "error": command_output.error,
                    },
                    default=pydantic_encoder,
                ),
                extra={"func_name_override": func.__name__},
            )
