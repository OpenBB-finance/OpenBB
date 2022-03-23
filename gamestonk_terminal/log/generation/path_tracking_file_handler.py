# IMPORTATION STANDARD
from copy import deepcopy
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from gamestonk_terminal.log.collection.log_sender import LogSender
from gamestonk_terminal.log.generation.settings import Settings


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

    @property
    def log_sender(self) -> str:
        return self.__log_sender

    @property
    def settings(self) -> str:
        return deepcopy(self.__settings)

    # OVERRIDE
    def __init__(
        self,
        settings: Settings,
        *args,
        **kwargs,
    ) -> None:
        filename = str(self.build_log_file_path(settings=settings))
        frequency = settings.log_settings.frequency
        super().__init__(filename, when=frequency, *args, **kwargs)
        self.suffix += ".log"

        self.__settings = settings
        self.__log_sender = LogSender(app_settings=settings.app_settings, daemon=True)
        self.__log_sender.start()

    # OVERRIDE
    def doRollover(self) -> None:
        super().doRollover()

        log_sender = self.__log_sender
        to_delete_path_list = self.getFilesToDelete()
        for path in to_delete_path_list:
            print(path)
            log_sender.send_path(path=Path(path))

    # OVERRIDE
    def close(self):
        super().close()

        log_sender = self.__log_sender
        closed_log_path = self.baseFilename
        log_sender.send_path(path=Path(closed_log_path), last=True)
        log_sender.join()
        print("Exiting", self.baseFilename)
