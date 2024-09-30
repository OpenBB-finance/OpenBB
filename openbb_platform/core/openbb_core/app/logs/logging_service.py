"""Logging Service Module."""

import json
import logging
from enum import Enum
from types import TracebackType
from typing import Any, Callable, Dict, Optional, Tuple, Type, Union

from openbb_core.app.logs.formatters.formatter_with_exceptions import (
    FormatterWithExceptions,
)
from openbb_core.app.logs.handlers_manager import HandlersManager
from openbb_core.app.logs.models.logging_settings import LoggingSettings
from openbb_core.app.model.abstract.singleton import SingletonMeta
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.model.user_settings import UserSettings
from pydantic import BaseModel
from pydantic_core import to_jsonable_python


class DummyProvider(BaseModel):
    """Dummy Provider for error handling with logs."""

    provider: str = "not_passed_to_kwargs"


class LoggingService(metaclass=SingletonMeta):
    """Logging Service class responsible for managing logging settings and handling logs.

    Attributes
    ----------
    _user_settings : Optional[UserSettings]
        User Settings object.
    _system_settings : Optional[SystemSettings]
        System Settings object.
    _logging_settings : LoggingSettings
        LoggingSettings object containing the current logging settings.
    _handlers_manager : HandlersManager
        HandlersManager object managing logging handlers.

    Methods
    -------
    __init__(system_settings, user_settings)
        Logging Manager Constructor.

    log(user_settings, system_settings, obbject, route, func, kwargs)
        Log command output and relevant information.

    logging_settings
        Property to access the current logging settings.

    logging_settings.setter
        Setter method to update the logging settings.

    _setup_handlers()
        Setup Logging Handlers.

    _log_startup()
        Log startup information.
    """

    _logger = logging.getLogger("openbb.logging_service")

    def __init__(
        self,
        system_settings: SystemSettings,
        user_settings: UserSettings,
    ) -> None:
        """Define the Logging Service Constructor.

        Sets up the logging settings and handlers and then logs the startup information.

        Parameters
        ----------
        system_settings : SystemSettings
            System Settings, by default None
        user_settings : UserSettings
            User Settings, by default None
        """
        self._user_settings = user_settings
        self._system_settings = system_settings
        self._logging_settings = LoggingSettings(
            user_settings=self._user_settings,
            system_settings=self._system_settings,
        )
        self._handlers_manager = self._setup_handlers()
        self._log_startup()

    @property
    def logging_settings(self) -> LoggingSettings:
        """Define the Current logging settings.

        Returns
        -------
        LoggingSettings
            LoggingSettings object containing the current logging settings.
        """
        return self._logging_settings

    @logging_settings.setter
    def logging_settings(self, value: Tuple[SystemSettings, UserSettings]):
        """Define the Setter for updating the logging settings.

        Parameters
        ----------
        value : Tuple[SystemSettings, UserSettings]
            Tuple containing updated SystemSettings and UserSettings.
        """
        system_settings, user_settings = value
        self._logging_settings = LoggingSettings(
            user_settings=user_settings,
            system_settings=system_settings,
        )

    def _setup_handlers(self) -> HandlersManager:
        """Set up Logging Handlers.

        Returns
        -------
        HandlersManager
            Handlers Manager object.
        """
        handlers_manager = HandlersManager(
            self._logger, settings=self._logging_settings
        )
        handlers_manager.setup()

        self._logger.info("Logging configuration finished")
        self._logger.info("Logging set to %s", self._logging_settings.handler_list)
        self._logger.info("Verbosity set to %s", self._logging_settings.verbosity)
        self._logger.info(
            "LOGFORMAT: %s%s",
            FormatterWithExceptions.LOGPREFIXFORMAT.replace("|", "-"),
            FormatterWithExceptions.LOGFORMAT.replace("|", "-"),
        )

        return handlers_manager

    def _log_startup(
        self,
        route: Optional[str] = None,
        custom_headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log startup information."""

        def check_credentials_defined(credentials: Dict[str, Any]):
            class CredentialsDefinition(Enum):
                defined = "defined"
                undefined = "undefined"

            return {
                c: (
                    CredentialsDefinition.defined.value
                    if credentials[c]
                    else CredentialsDefinition.undefined.value
                )
                for c in credentials
            }

        self._logger.info(
            "STARTUP: %s ",
            json.dumps(
                {
                    "route": route,
                    "PREFERENCES": self._user_settings.preferences,
                    "KEYS": check_credentials_defined(
                        self._user_settings.credentials.model_dump()
                        if self._user_settings.credentials
                        else {}
                    ),
                    "SYSTEM": self._system_settings,
                    "custom_headers": custom_headers,
                },
                default=to_jsonable_python,
            ),
        )

    # pylint: disable=R0917
    def log(
        self,
        user_settings: UserSettings,
        system_settings: SystemSettings,
        route: str,
        func: Callable,
        kwargs: Dict[str, Any],
        exec_info: Union[
            Tuple[Type[BaseException], BaseException, TracebackType],
            Tuple[None, None, None],
        ],
        custom_headers: Optional[Dict[str, Any]] = None,
    ):
        """Log command output and relevant information.

        Parameters
        ----------
        user_settings : UserSettings
            User Settings object.
        system_settings : SystemSettings
            System Settings object.
        route : str
            Route for the command.
        func : Callable
            Callable representing the executed function.
        kwargs : Dict[str, Any]
            Keyword arguments passed to the function.
        exec_info : Union[
            Tuple[Type[BaseException], BaseException, TracebackType],
            Tuple[None, None, None],
        ]
            Exception information, by default None
        """
        self._user_settings = user_settings
        self._system_settings = system_settings
        self._logging_settings = LoggingSettings(
            user_settings=self._user_settings,
            system_settings=self._system_settings,
        )
        self._handlers_manager.update_handlers(self._logging_settings)

        if "login" in route:
            self._log_startup(route, custom_headers)
        else:

            # Remove CommandContext if any
            kwargs.pop("cc", None)

            # Get provider for posthog logs
            passed_model = kwargs.get("provider_choices", DummyProvider())
            provider = (
                passed_model.provider
                if hasattr(passed_model, "provider")
                else "not_passed_to_kwargs"
            )

            # Truncate kwargs if too long
            kwargs = {k: str(v)[:100] for k, v in kwargs.items()}
            # Get execution info
            error = None if all(i is None for i in exec_info) else str(exec_info[1])

            # Construct message
            message_label = "ERROR" if error else "CMD"
            log_message = json.dumps(
                {
                    "route": route,
                    "input": kwargs,
                    "error": error,
                    "provider": provider,
                    "custom_headers": custom_headers,
                },
                default=to_jsonable_python,
            )
            log_message = f"{message_label}: {log_message}"
            log_level = self._logger.error if error else self._logger.info
            log_level(
                log_message,
                extra={"func_name_override": func.__name__},
                exc_info=exec_info,
            )
