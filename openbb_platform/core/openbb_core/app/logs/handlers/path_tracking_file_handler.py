"""Path Tracking File Handler."""

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
    """Path Tracking File Handler."""

    @staticmethod
    def build_log_file_path(settings: LoggingSettings) -> Path:
        """Build the log file path."""
        app_name = settings.app_name
        directory = settings.user_logs_directory
        session_id = settings.session_id

        path = directory.absolute().joinpath(f"{app_name}_{session_id}")
        return path

    def clean_expired_files(self, before_timestamp: float):
        """Remove expired files from logs directory."""
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
        """Get the settings."""
        return deepcopy(self.__settings)

    @settings.setter
    def settings(self, settings: LoggingSettings) -> None:
        """Set the settings."""
        self.__settings = settings

    # OVERRIDE
    def __init__(
        self,
        settings: LoggingSettings,
        *args,
        **kwargs,
    ) -> None:
        """Initialize the PathTrackingFileHandler."""
        # SETUP PARENT CLASS
        filename = str(self.build_log_file_path(settings=settings))
        frequency = settings.frequency
        kwargs["when"] = frequency

        super().__init__(filename, *args, **kwargs)

        self.suffix += ".log"

        # SETUP CURRENT CLASS
        self.__settings = settings

        self.clean_expired_files(before_timestamp=get_timestamp_from_x_days(x=5))
