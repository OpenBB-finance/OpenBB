"""日志服务模块。"""

import json
import logging
from collections.abc import Callable
from enum import Enum
from types import TracebackType
from typing import Any

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
    """用于处理错误的带有日志的虚拟提供者。"""

    provider: str = "not_passed_to_kwargs"


class LoggingService(metaclass=SingletonMeta):
    """日志服务类负责管理日志设置和处理日志。

    Attributes
    ----------
    _user_settings : Optional[UserSettings]
        用户设置对象。
    _system_settings : Optional[SystemSettings]
        系统设置对象。
    _logging_settings : LoggingSettings
        包含当前日志设置的 LoggingSettings 对象。
    _handlers_manager : HandlersManager
        管理日志处理程序的 HandlersManager 对象。

    Methods
    -------
    __init__(system_settings, user_settings)
        日志管理器构造函数。

    log(user_settings, system_settings, route, func, kwargs, exec_info or None, custom_headers or None)
        记录命令输出和相关信息。

    logging_settings
        访问当前日志设置的属性。

    logging_settings.setter(value)
        更新日志设置的 Setter 方法。

    _setup_handlers()
        设置日志处理程序。

    _log_startup(route or None, custom_headers or None)
        记录启动信息。
    """

    _logger = logging.getLogger("openbb.logging_service")

    def __init__(
        self,
        system_settings: SystemSettings,
        user_settings: UserSettings,
    ) -> None:
        """定义日志服务构造函数。

        设置日志设置和处理程序，然后记录启动信息。

        Parameters
        ----------
        system_settings : SystemSettings
            系统设置，默认为 None
        user_settings : UserSettings
            用户设置，默认为 None
        """
        if system_settings.logging_suppress is True:
            return

        self._user_settings = user_settings
        self._system_settings = system_settings
        self._logging_settings = LoggingSettings(
            user_settings=self._user_settings,
            system_settings=self._system_settings,
        )
        self._handlers_manager = self._setup_handlers()
        self._log_startup()

        return

    @property
    def logging_settings(self) -> LoggingSettings:
        """定义当前日志设置。

        Returns
        -------
        LoggingSettings
            包含当前日志设置的 LoggingSettings 对象。
        """
        return self._logging_settings

    @logging_settings.setter
    def logging_settings(self, value: tuple[SystemSettings, UserSettings]) -> None:
        """定义用于更新日志设置的 Setter。

        Parameters
        ----------
        value : Tuple[SystemSettings, UserSettings]
            包含更新后的 SystemSettings 和 UserSettings 的元组。
        Returns
        -------
        None
        """
        system_settings, user_settings = value
        self._logging_settings = LoggingSettings(
            user_settings=user_settings,
            system_settings=system_settings,
        )

    def _setup_handlers(self) -> HandlersManager:
        """设置日志处理程序。

        Returns
        -------
        HandlersManager
            Handlers Manager 对象。
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
        route: str | None = None,
        custom_headers: dict[str, Any] | None = None,
    ) -> None:
        """
        记录启动信息。
        Parameters
        ----------
        route : Optional[str]
            命令的路由，默认为 None
        custom_headers : Optional[Dict[str, Any]]
            要包含在日志中的自定义标头，默认为 None
        Returns
        -------
        None
        """

        def check_credentials_defined(credentials: dict[str, Any]):
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
        kwargs: dict[str, Any],
        exec_info: (
            tuple[type[BaseException], BaseException, TracebackType]
            | tuple[None, None, None]
        ),
        custom_headers: dict[str, Any] | None = None,
    ) -> None:
        """记录命令输出和相关信息。

        Parameters
        ----------
        user_settings : UserSettings
            用户设置对象。
        system_settings : SystemSettings
            系统设置对象。
        route : str
            命令的路由。
        func : Callable
            表示已执行函数的可调用对象。
        kwargs : Dict[str, Any]
            传递给函数的关键字参数。
        exec_info : Union[
            Tuple[Type[BaseException], BaseException, TracebackType],
            Tuple[None, None, None],
        ]
            异常信息，默认为 None
        custom_headers : Optional[Dict[str, Any]]
            要包含在日志中的自定义标头，默认为 None
        Returns
        -------
        None
        """
        self._user_settings = user_settings
        self._system_settings = system_settings
        self._logging_settings = LoggingSettings(
            user_settings=self._user_settings,
            system_settings=self._system_settings,
        )
        self._handlers_manager.update_handlers(self._logging_settings)

        if not self._logging_settings.logging_suppress:
            if "login" in route:
                self._log_startup(route, custom_headers)
            else:
                # 移除 CommandContext（如果有）
                kwargs.pop("cc", None)

                passed_model = kwargs.get("provider_choices", DummyProvider())
                provider = (
                    passed_model.provider
                    if hasattr(passed_model, "provider")
                    else "not_passed_to_kwargs"
                )

                # 如果 kwargs 太长，则截断
                kwargs = {k: str(v)[:300] for k, v in kwargs.items()}
                # 获取执行信息
                error = None if all(i is None for i in exec_info) else str(exec_info[1])

                # 构造消息
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
