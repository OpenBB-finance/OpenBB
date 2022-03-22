# IMPORTATION STANDARD
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from gamestonk_terminal.log.collection.log_sender import LogSender, LOG_SENDER


class PathTrackingFileHandler(TimedRotatingFileHandler):
    # OVERRIDE
    def __init__(
        self, filename: str, *args, log_sender: Optional[LogSender] = None, **kwargs
    ) -> None:
        super().__init__(filename, *args, **kwargs)
        self.suffix += ".log"

        self.__log_sender = log_sender or LOG_SENDER

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
