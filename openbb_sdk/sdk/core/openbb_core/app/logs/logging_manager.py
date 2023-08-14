# IMPORT STANDARD
import json
import logging
from enum import Enum
from typing import Any, Callable, Dict, Optional, Tuple

from openbb_core.app.logs.formatters.formatter_with_exceptions import (
    FormatterWithExceptions,
)
from openbb_core.app.logs.handlers_manager import HandlersManager
from openbb_core.app.logs.models.logging_settings import LoggingSettings
from openbb_core.app.model.abstract.singleton import SingletonMeta
from openbb_core.app.model.obbject import Obbject
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.model.user_settings import UserSettings

# IMPORT INTERNAL
from openbb_core.app.service.system_service import SystemService
from openbb_core.app.service.user_service import UserService

# IMPORT THIRD-PARTY
from pydantic.json import pydantic_encoder


class LoggingManager(metaclass=SingletonMeta):
    """
    Logging Manager class responsible for managing logging settings and handling logs.

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
        system_settings: Optional[SystemSettings] = None,
        user_settings: Optional[UserSettings] = None,
    ) -> None:
        """
        Logging Manager Constructor
        Sets up the logging settings and handlers and then logs the startup information.

        Parameters
        ----------
        system_settings : Optional[SystemSettings], optional
            System Settings, by default None
        user_settings : Optional[UserSettings], optional
            User Settings, by default None
        """
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

    @property
    def logging_settings(self) -> LoggingSettings:
        """
        Current logging settings.

        Returns
        -------
        LoggingSettings
            LoggingSettings object containing the current logging settings.
        """
        return self._logging_settings

    @logging_settings.setter
    def logging_settings(self, value: Tuple[SystemSettings, UserSettings]):
        """
        Setter for updating the logging settings.

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
        """
        Setup Logging Handlers.

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
        """
        Log startup information.
        """

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
        obbject: Obbject,
        route: str,
        func: Callable,
        kwargs: Dict[str, Any],
    ):
        """
        Log command output and relevant information.

        Parameters
        ----------
        user_settings : UserSettings
            User Settings object.
        system_settings : SystemSettings
            System Settings object.
        obbject : Obbject
            Obbject object containing command output and error information.
        route : str
            Route for the command.
        func : Callable
            Callable representing the executed function.
        kwargs : Dict[str, Any]
            Keyword arguments passed to the function.
        """
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

            log_level = logger.error if obbject.error else logger.info
            log_level(
                "ERROR: %s" if obbject.error else "CMD: %s",
                json.dumps(
                    {
                        "route": route,
                        "input": kwargs,
                        "error": obbject.error,
                    },
                    default=pydantic_encoder,
                ),
                extra={"func_name_override": func.__name__},
            )
