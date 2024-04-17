"""Logging Service Module."""

import json
import logging
from enum import Enum
from types import TracebackType
from typing import Any, Callable, Dict, Optional, Tuple, Type, Union, cast

from openbb_core.app.logs.formatters.formatter_with_exceptions import (
    FormatterWithExceptions,
)
from openbb_core.app.logs.handlers_manager import HandlersManager
from openbb_core.app.logs.models.logging_settings import LoggingSettings
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.abstract.singleton import SingletonMeta
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.model.user_settings import UserSettings
from pydantic_core import to_jsonable_python


class LoggingService(metaclass=SingletonMeta):
    """Logging Manager class responsible for managing logging settings and handling logs.

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
        logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=self._logging_settings.verbosity,
            format=FormatterWithExceptions.LOGFORMAT,
            datefmt=FormatterWithExceptions.DATEFORMAT,
            handlers=[],
            force=True,
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

        logger = logging.getLogger(__name__)
        logger.info(
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
        """
        Log command output and relevant information.

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
        exec_info : Optional[Tuple[Type[BaseException], BaseException, Optional[TracebackType]]], optional
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
            logger = logging.getLogger(__name__)

            # Remove CommandContext if any
            kwargs.pop("cc", None)

            # Truncate kwargs if too long
            kwargs = {k: str(v)[:100] for k, v in kwargs.items()}

            # Get execution info
            openbb_error = cast(
                Optional[OpenBBError], exec_info[1] if exec_info else None
            )

            # Construct message
            message_label = "ERROR" if openbb_error else "CMD"
            log_message = json.dumps(
                {
                    "route": route,
                    "input": kwargs,
                    "error": str(openbb_error.original) if openbb_error else None,
                    "custom_headers": custom_headers,
                },
                default=to_jsonable_python,
            )
            log_message = f"{message_label}: {log_message}"

            log_level = logger.error if openbb_error else logger.info
            log_level(
                log_message,
                extra={"func_name_override": func.__name__},
                exc_info=exec_info,
            )
