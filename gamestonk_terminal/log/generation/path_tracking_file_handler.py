# IMPORTATION STANDARD
from copy import deepcopy
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from gamestonk_terminal.log.collection.log_sender import LogSender
from gamestonk_terminal.log.collection.logging_clock import LoggingClock, Precision
from gamestonk_terminal.log.generation.settings import Settings

# DO NOT USE THE FILE LOGGER IN THIS MODULE


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
        log_sender = LogSender(app_settings=settings.app_settings, daemon=True)

        if start:
            log_sender.start()

        return log_sender

    def build_rolling_clock(self, frequency: str, start: bool) -> LoggingClock:
        frequency = frequency.upper()

        if frequency == "H":
            precision = Precision.hour
        elif frequency == "M":
            precision = Precision.minute
        else:
            raise AttributeError("Unsupported `logging_clock.Precision`.")

        rolling_clock = LoggingClock(
            action_func=self.doRollover,
            daemon=True,
            precision=precision,
        )

        if start:
            rolling_clock.start()

        return rolling_clock

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
        rolling_clock: bool = False,
        **kwargs,
    ) -> None:
        filename = str(self.build_log_file_path(settings=settings))
        frequency = settings.log_settings.frequency
        kwargs["when"] = frequency
        super().__init__(filename, *args, **kwargs)
        self.suffix += ".log"

        self.__settings = settings
        self.__log_sender = self.build_log_sender(settings=settings, start=True)
        self.__rolling_clock = self.build_rolling_clock(
            frequency=frequency, start=rolling_clock
        )

    # OVERRIDE
    def doRollover(self) -> None:
        super().doRollover()

        # print("I am rolling.")
        log_sender = self.__log_sender
        to_delete_path_list = self.getFilesToDelete()
        for path in to_delete_path_list:
            # print(path)
            log_sender.send_path(path=Path(path))

    # OVERRIDE
    def close(self):
        super().close()

        log_sender = self.__log_sender
        closed_log_path = self.baseFilename
        log_sender.send_path(path=Path(closed_log_path), last=True)
        log_sender.join()
        # print("Exiting", self.baseFilename)
