"""处理程序管理器。"""

import logging
import sys

from openbb_core.app.logs.formatters.formatter_with_exceptions import (
    FormatterWithExceptions,
)
from openbb_core.app.logs.handlers.path_tracking_file_handler import (
    PathTrackingFileHandler,
)
from openbb_core.app.logs.models.logging_settings import LoggingSettings


class HandlersManager:
    """处理程序管理器。"""

    def __init__(self, logger: logging.Logger, settings: LoggingSettings):
        """初始化处理程序管理器。"""
        self._logger = logger
        self._handlers = settings.handler_list
        self._settings = settings

    def setup(self):
        """设置记录器处理程序和设置。"""
        # 禁用传播到根记录器以避免重复日志
        self._logger.propagate = False
        self._logger.setLevel(self._settings.verbosity)

        for handler_type in self._handlers:
            if handler_type == "stdout":
                self._add_stdout_handler()
            elif handler_type == "stderr":
                self._add_stderr_handler()
            elif handler_type == "noop":
                self._add_noop_handler()
            elif handler_type == "file" and not self._settings.logging_suppress:
                self._add_file_handler()
            else:
                self._logger.debug("未知的日志处理程序。")

    def _add_stdout_handler(self):
        """添加 stdout 处理程序。"""
        handler = logging.StreamHandler(sys.stdout)
        formatter = FormatterWithExceptions(settings=self._settings)
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def _add_stderr_handler(self):
        """添加 stderr 处理程序。"""
        handler = logging.StreamHandler(sys.stderr)
        formatter = FormatterWithExceptions(settings=self._settings)
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def _add_noop_handler(self):
        """添加空处理程序。"""
        handler = logging.NullHandler()
        formatter = FormatterWithExceptions(settings=self._settings)
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def _add_file_handler(self):
        """添加文件处理程序。"""
        handler = PathTrackingFileHandler(settings=self._settings)
        formatter = FormatterWithExceptions(settings=self._settings)
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def update_handlers(self, settings: LoggingSettings):
        """使用新设置更新处理程序。"""
        logger = self._logger
        for hdlr in logger.handlers:
            if (
                isinstance(hdlr, PathTrackingFileHandler)
                and not settings.logging_suppress
            ):
                hdlr.settings = settings
                hdlr.formatter.settings = settings  # type: ignore
