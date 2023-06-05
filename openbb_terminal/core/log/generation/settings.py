# IMPORTATION STANDARD
from copy import deepcopy
from pathlib import Path

# IMPORTATION THIRDPARTY
from typing import List

# IMPORTATION INTERNAL


class AWSSettings:
    @property
    def aws_access_key_id(self) -> str:
        return self.__aws_access_key_id

    @property
    def aws_secret_access_key(self) -> str:
        return self.__aws_secret_access_key

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
    ):
        self.__aws_access_key_id = aws_access_key_id
        self.__aws_secret_access_key = aws_secret_access_key


class AppSettings:
    @property
    def name(self) -> str:
        return self.__name

    @property
    def commit_hash(self) -> str:
        return self.__commit_hash

    @property
    def identifier(self) -> str:
        return self.__identifier

    @property
    def session_id(self) -> str:
        return self.__session_id

    @property
    def user_id(self) -> str:
        return self.__user_id

    @user_id.setter
    def user_id(self, value: str):
        self.__user_id = value

    def __init__(
        self,
        name: str,
        commit_hash: str,
        session_id: str,
        identifier: str,
        user_id: str,
    ):
        """
        Args:
            name (str): Source of the application.
            commit_hash (str): Commit hash of the current running code.
            identifier (str): Unique key identifying a particular installation.
            session_id (str): Key identifying a particular running session.
            user_id (str): Hash identifying a particular user.
        """

        self.__name = name
        self.__commit_hash = commit_hash
        self.__identifier = identifier
        self.__session_id = session_id
        self.__user_id = user_id


class LogSettings:
    @property
    def directory(self) -> Path:
        return self.__directory

    @property
    def frequency(self) -> str:
        return self.__frequency

    @property
    def handler_list(self) -> List[str]:
        return self.__handler_list

    @property
    def rolling_clock(self) -> bool:
        return self.__rolling_clock

    @property
    def verbosity(self) -> int:
        return self.__verbosity

    def __init__(
        self,
        directory: Path,
        frequency: str,
        handler_list: List[str],
        rolling_clock: bool,
        verbosity: int,
    ):
        """
        Args:
            directory (Path): Directory used to store log files.
            frequency (str): Frequency of the log files rotation.
            handler_list (List[str]) : list of handlers : stdout,stderr,noop,file,posthog.
            rolling_clock (bool): Whether or not to start a Thread to rotate logs even when inactive.
            verbosity (str): Verbosity level as defined in Python `logging` module.
        """

        self.__directory = directory
        self.__frequency = frequency
        self.__handler_list = handler_list
        self.__rolling_clock = rolling_clock
        self.__verbosity = verbosity


class Settings:
    @property
    def app_settings(self) -> AppSettings:
        return deepcopy(self.__app_settings)

    @property
    def log_settings(self) -> LogSettings:
        return deepcopy(self.__log_settings)

    @property
    def aws_settings(self) -> AWSSettings:
        return deepcopy(self.__aws_settings)

    def __init__(
        self,
        app_settings: AppSettings,
        aws_settings: AWSSettings,
        log_settings: LogSettings,
    ):
        """This model regroups all configurations used by these classes instance :
         - openbb_terminal.core.log.collection.log_sender.LogSender
         - openbb_terminal.core.log.generation.formatter_with_exceptions.FormatterWithExceptions
         - openbb_terminal.core.log.generation.path_tracking_file_handler.PathTrackingFileHandler

        Args:
            app_name (str): Instance of AppSettings.
            log_settings (str): Instance of LogSettings.
            aws_settings (str): Instance of AWSSettings.
        """

        self.__app_settings = app_settings
        self.__log_settings = log_settings
        self.__aws_settings = aws_settings
