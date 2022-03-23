# IMPORTATION STANDARD
from copy import deepcopy
from pathlib import Path

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL


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

    def __init__(
        self,
        name: str,
        commit_hash: str,
        session_id: str,
        identifier: str,
    ):
        """
        Args:
            name (str): Name of the application.
            commit_hash (str): Commit hash of the current running code.
            identifier (str): Unique key identifying a particular installation.
            session_id (str): Key identifying a particular running session.
        """

        self.__name = name
        self.__commit_hash = commit_hash
        self.__identifier = identifier
        self.__session_id = session_id


class LogSettings:
    @property
    def directory(self) -> Path:
        return self.__directory

    @property
    def frequency(self) -> str:
        return self.__frequency

    @property
    def handler_list(self) -> str:
        return self.__handler_list

    @property
    def verbosity(self) -> int:
        return self.__verbosity

    def __init__(
        self,
        directory: Path,
        frequency: str,
        handler_list: str,
        verbosity: int,
    ):
        """
        Args:
            directory (Path): Directory used to store log files.
            frequency (str): Frequency of the log files rotation.
            handler_list (str) : Comma separated list of handlers : stdout,stderr,noop,file.
            verbosity (str): Verbosity level as defined in Python `logging` module.
        """

        self.__directory = directory
        self.__frequency = frequency
        self.__handler_list = handler_list
        self.__verbosity = verbosity


class Settings:
    @property
    def app_settings(self) -> AppSettings:
        return deepcopy(self.__app_settings)

    @property
    def log_settings(self) -> LogSettings:
        return deepcopy(self.__log_settings)

    def __init__(
        self,
        app_settings: AppSettings,
        log_settings: LogSettings,
    ):
        """This model regroups all configurations used by these classes instance :
         - gamestonk_terminal.log.collection.log_sender.LogSender
         - gamestonk_terminal.log.generation.formatter_with_exceptions.FormatterWithExceptions
         - gamestonk_terminal.log.generation.path_tracking_file_handler.PathTrackingFileHandler

        Args:
            app_name (str): Instance of AppSettings.
            log_settings (str): Instance of LogSettings.
        """

        self.__app_settings = app_settings
        self.__log_settings = log_settings
