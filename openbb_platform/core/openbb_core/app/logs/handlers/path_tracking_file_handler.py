"""路径跟踪文件处理程序。"""

# IMPORTATION STANDARD
from copy import deepcopy
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# IMPORTATION THIRD PARTY
# IMPORTATION INTERNAL
from openbb_core.app.logs.models.logging_settings import LoggingSettings
from openbb_core.app.logs.utils.expired_files import (
    get_expired_file_list,
    get_timestamp_from_x_days,
    remove_file_list,
)

ARCHIVES_FOLDER_NAME = "archives"
TMP_FOLDER_NAME = "tmp"


class PathTrackingFileHandler(TimedRotatingFileHandler):
    """路径跟踪文件处理程序。"""

    @staticmethod
    def build_log_file_path(settings: LoggingSettings) -> Path:
        """构建日志文件路径。"""
        app_name = settings.app_name
        directory = settings.user_logs_directory
        session_id = settings.session_id

        path = directory.absolute().joinpath(f"{app_name}_{session_id}")
        return path

    def clean_expired_files(self, before_timestamp: float):
        """从日志目录中删除过期文件。"""
        logs_dir = self.settings.user_logs_directory
        archives_directory = logs_dir / ARCHIVES_FOLDER_NAME
        tmp_directory = logs_dir / TMP_FOLDER_NAME

        expired_logs_file_list = get_expired_file_list(
            directory=logs_dir,
            before_timestamp=before_timestamp,
        )
        expired_archives_file_list = get_expired_file_list(
            directory=archives_directory,
            before_timestamp=before_timestamp,
        )
        expired_tmp_file_list = get_expired_file_list(
            directory=tmp_directory,
            before_timestamp=before_timestamp,
        )
        remove_file_list(file_list=expired_logs_file_list)
        remove_file_list(file_list=expired_archives_file_list)
        remove_file_list(file_list=expired_tmp_file_list)

    @property
    def settings(self) -> LoggingSettings:
        """获取设置。"""
        return deepcopy(self.__settings)

    @settings.setter
    def settings(self, settings: LoggingSettings) -> None:
        """设置设置。"""
        self.__settings = settings

    # OVERRIDE
    def __init__(
        self,
        settings: LoggingSettings,
        *args,
        **kwargs,
    ) -> None:
        """初始化 PathTrackingFileHandler。"""
        # SETUP PARENT CLASS
        filename = str(self.build_log_file_path(settings=settings))
        frequency = settings.frequency
        kwargs["when"] = frequency

        super().__init__(filename, *args, **kwargs)

        self.suffix += ".log"

        # SETUP CURRENT CLASS
        self.__settings = settings

        self.clean_expired_files(before_timestamp=get_timestamp_from_x_days(x=5))
