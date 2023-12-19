# IMPORTATION STANDARD
import contextlib
from copy import deepcopy
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Callable

from openbb_terminal.core.log.collection.log_sender import LogSender
from openbb_terminal.core.log.collection.logging_clock import LoggingClock, Precision

# IMPORTATION THIRDPARTY
# IMPORTATION INTERNAL
from openbb_terminal.core.log.constants import ARCHIVES_FOLDER_NAME, TMP_FOLDER_NAME
from openbb_terminal.core.log.generation.directories import get_log_dir, get_log_sub_dir
from openbb_terminal.core.log.generation.expired_files import (
    get_expired_file_list,
    get_timestamp_from_x_days,
    remove_file_list,
)
from openbb_terminal.core.log.generation.settings import Settings


class PathTrackingFileHandler(TimedRotatingFileHandler):
    @staticmethod
    def build_log_file_path(settings: Settings) -> Path:
        app_settings = settings.app_settings
        log_settings = settings.log_settings
        app_name = app_settings.name
        directory = log_settings.directory
        session_id = app_settings.session_id

        path = directory.absolute().joinpath(f"{app_name}_{session_id}")
        return path

    @staticmethod
    def build_log_sender(settings: Settings, start: bool) -> LogSender:
        log_sender = LogSender(settings=settings, daemon=True)

        if start:
            log_sender.start()

        return log_sender

    @staticmethod
    def clean_expired_files(before_timestamp: float):
        """Deleting old files inside : archives and tmp folders.

        Only files inside the following folders are considered :
         - {LOG_FOLDER_PATH}/{ARCHIVES_FOLDER_NAME}
         - {LOG_FOLDER_PATH}/{TMP_FOLDER_NAME}

        Args:
            before_timestamp (float): Timestamp before which files are considered expired.
        """

        archives_directory = get_log_sub_dir(name=ARCHIVES_FOLDER_NAME)
        tmp_directory = get_log_sub_dir(name=TMP_FOLDER_NAME)
        expired_archives_file_list = get_expired_file_list(
            directory=archives_directory,
            before_timestamp=before_timestamp,
        )
        expired_tmp_file_list = get_expired_file_list(
            directory=tmp_directory,
            before_timestamp=before_timestamp,
        )

        remove_file_list(file_list=expired_archives_file_list)
        remove_file_list(file_list=expired_tmp_file_list)

    @staticmethod
    def build_rolling_clock(
        action: Callable,
        frequency: str,
        start: bool,
    ) -> LoggingClock:
        frequency = frequency.upper()

        if frequency == "H":
            precision = Precision.hour
        elif frequency == "M":
            precision = Precision.minute
        else:
            raise AttributeError("Unsupported `logging_clock.Precision`.")

        rolling_clock = LoggingClock(
            action=action,
            daemon=True,
            precision=precision,
        )

        if start:
            rolling_clock.start()

        return rolling_clock

    def send_expired_files(self, before_timestamp: float):
        """Try to send files older than before_timestamp days.

        Only files inside the following folder are considered :
         - {LOG_FOLDER_PATH}/

        Args:
            before_timestamp (float): Timestamp before which files are considered expired.
        """

        log_sender = self.__log_sender
        log_directory = get_log_dir()

        expired_log_file_list = get_expired_file_list(
            directory=log_directory,
            before_timestamp=before_timestamp,
        )

        for file in expired_log_file_list:
            log_sender.send_path(last=False, path=file)

    @property
    def log_sender(self) -> LogSender:
        return self.__log_sender

    @property
    def rolling_clock(self) -> LoggingClock:
        return self.__rolling_clock

    @property
    def settings(self) -> Settings:
        return deepcopy(self.__settings)

    # OVERRIDE
    def __init__(
        self,
        settings: Settings,
        *args,
        **kwargs,
    ) -> None:
        # SETUP PARENT CLASS
        filename = str(self.build_log_file_path(settings=settings))
        frequency = settings.log_settings.frequency
        kwargs["when"] = frequency

        super().__init__(filename, *args, **kwargs)

        self.suffix += ".log"

        # SETUP CURRENT CLASS
        self.__settings = settings

        self.clean_expired_files(before_timestamp=get_timestamp_from_x_days(x=5))

        self.__log_sender = self.build_log_sender(
            settings=settings,
            start=False,
        )
        self.__rolling_clock = self.build_rolling_clock(
            action=self.doRollover,
            frequency=frequency,
            start=settings.log_settings.rolling_clock,
        )

        if LogSender.start_required():
            self.__log_sender.start()
            self.send_expired_files(before_timestamp=get_timestamp_from_x_days(x=1))

    # OVERRIDE
    def doRollover(self) -> None:
        log_sender = self.__log_sender

        if self.lock:
            with self.lock:
                super().doRollover()

                log_path = Path(self.baseFilename)

                if log_sender.check_sending_conditions(file=log_path):
                    to_delete_path_list = self.getFilesToDelete()
                    for path in to_delete_path_list:
                        log_sender.send_path(path=Path(path))

    # OVERRIDE
    def close(self):
        """Do not use the file logger in this function."""

        log_sender = self.__log_sender
        closed_log_path = Path(self.baseFilename)

        if log_sender.check_sending_conditions(file=closed_log_path):
            log_sender.send_path(path=closed_log_path, last=True)
            with contextlib.suppress(Exception):
                log_sender.join(timeout=3)

        super().close()

        if log_sender.check_sending_conditions(file=closed_log_path):
            closed_log_path.unlink(missing_ok=True)
