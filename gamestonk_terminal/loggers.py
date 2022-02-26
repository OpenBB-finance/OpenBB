"""Logging Configuration"""
__docformat__ = "numpy"
import logging
import os
from pathlib import Path
import sys
import time
import uuid
from math import floor, ceil

import git

import gamestonk_terminal.config_terminal as cfg

logger = logging.getLogger(__name__)
LOGFORMAT = "%(asctime)s|%(name)s|%(funcName)s|%(lineno)s|%(message)s"
LOGPREFIXFORMAT = "%(levelname)s|%(version)s|%(loggingId)s|%(sessionId)s|"
DATEFORMAT = "%Y-%m-%dT%H:%M:%S%z"


def library_loggers(verbosity: int = 0) -> None:
    """Setup library logging

    Parameters
    ----------
    verbosity : int, optional
        Log level verbosity, by default 0
    """

    logging.getLogger("requests").setLevel(verbosity)
    logging.getLogger("urllib3").setLevel(verbosity)


def setup_file_logger(session_id: str) -> None:
    """Setup File Logger"""
    file_path = Path(__file__)
    logger.debug("Parent dir: %s", file_path.parent.parent.absolute())
    log_dir = file_path.parent.parent.absolute().joinpath("logs")
    logger.debug("Future logdir: %s", log_dir)

    if not os.path.isdir(log_dir.absolute()):
        logger.debug("Logdir does not exist. Creating.")
        os.mkdir(log_dir.absolute())

    log_id = log_dir.absolute().joinpath(".logid")

    if not os.path.isfile(log_id.absolute()):
        logger.debug("Log ID does not exist: %s", log_id.absolute())
        cfg.LOGGING_ID = f"{uuid.uuid4()}"
        with open(log_id.absolute(), "a") as a_file:
            a_file.write(f"{cfg.LOGGING_ID}\n")
    else:
        logger.debug("Log ID exists: %s", log_id.absolute())
        with open(log_id.absolute()) as a_file:
            cfg.LOGGING_ID = a_file.readline().rstrip()

    logger.debug("Log id: %s", cfg.LOGGING_ID)

    uuid_log_dir = log_dir.absolute().joinpath(cfg.LOGGING_ID)

    logger.debug("Current log dir: %s", uuid_log_dir)

    if not os.path.isdir(uuid_log_dir.absolute()):
        logger.debug(
            "UUID log dir does not exist: %s. Creating.", uuid_log_dir.absolute()
        )
        os.mkdir(uuid_log_dir.absolute())

    start_time = int(time.time())
    cfg.LOGGING_FILE = uuid_log_dir.absolute().joinpath(f"{start_time}.log")  # type: ignore

    logger.debug("Current log file: %s", cfg.LOGGING_FILE)

    handler = logging.FileHandler(cfg.LOGGING_FILE)
    formatter = CustomFormatterWithExceptions(
        cfg.LOGGING_ID, session_id, fmt=LOGFORMAT, datefmt=DATEFORMAT
    )
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)


class CustomFormatterWithExceptions(logging.Formatter):
    """Custom Logging Formatter that includes formatting of Exceptions"""

    def __init__(
        self,
        logging_id: str,
        session_id: str,
        fmt=None,
        datefmt=None,
        style="%",
        validate=True,
    ) -> None:
        super().__init__(fmt=fmt, datefmt=datefmt, style=style, validate=validate)
        self.logPrefixDict = {
            "loggingId": logging_id,
            "sessionId": session_id,
            "version": cfg.LOGGING_VERSION,
        }

    def formatException(self, ei) -> str:
        """Exception formatting handler

        Parameters
        ----------
        ei : logging._SysExcInfoType
            Exception to be logged

        Returns
        -------
        str
            Formatted exception
        """
        result = super().formatException(ei)
        return repr(result)

    def format(self, record: logging.LogRecord) -> str:
        """Log formatter

        Parameters
        ----------
        record : logging.LogRecord
            Logging record

        Returns
        -------
        str
            Formatted log message
        """
        if hasattr(record, "func_name_override"):
            record.funcName = record.func_name_override  # type: ignore
            record.lineno = 0
        s = super().format(record)
        if record.levelname:
            self.logPrefixDict["levelname"] = record.levelname[0]
        else:
            self.logPrefixDict["levelname"] = "U"

        if record.exc_text:
            self.logPrefixDict["levelname"] = "X"
            logPrefix = LOGPREFIXFORMAT % self.logPrefixDict
            s = (
                s.replace("\n", " - ")
                .replace("\t", " ")
                .replace("\r", "")
                .replace("'", "`")
                .replace('"', "`")
            )

        else:
            logPrefix = LOGPREFIXFORMAT % self.logPrefixDict
        return f"{logPrefix}{s}"


def get_commit_hash() -> None:
    """Get Commit Short Hash"""

    file_path = Path(__file__)
    git_dir = file_path.parent.parent.absolute().joinpath(".git")

    if os.path.isdir(git_dir.absolute()):
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha
        short_sha = repo.git.rev_parse(sha, short=8)
        cfg.LOGGING_VERSION = f"sha:{short_sha}"


def setup_logging() -> None:
    """Setup Logging"""

    START_TIME = int(time.time())
    LOGGING_ID = cfg.LOGGING_ID if cfg.LOGGING_ID else ""

    verbosity_terminal = floor(cfg.LOGGING_VERBOSITY / 10) * 10
    verbosity_libraries = ceil(cfg.LOGGING_VERBOSITY / 10) * 10
    logging.basicConfig(
        level=verbosity_terminal, format=LOGFORMAT, datefmt=DATEFORMAT, handlers=[]
    )

    get_commit_hash()

    for a_handler in cfg.LOGGING_HANDLERS.split(","):
        if a_handler == "stdout":
            handler = logging.StreamHandler(sys.stdout)
            formatter = CustomFormatterWithExceptions(
                LOGGING_ID, str(START_TIME), fmt=LOGFORMAT, datefmt=DATEFORMAT
            )
            handler.setFormatter(formatter)
            logging.getLogger().addHandler(handler)
        elif a_handler == "stderr":
            handler = logging.StreamHandler(sys.stderr)
            formatter = CustomFormatterWithExceptions(
                LOGGING_ID, str(START_TIME), fmt=LOGFORMAT, datefmt=DATEFORMAT
            )
            handler.setFormatter(formatter)
            logging.getLogger().addHandler(handler)
        elif a_handler == "noop":
            handler = logging.NullHandler()  # type: ignore
            formatter = CustomFormatterWithExceptions(
                LOGGING_ID, str(START_TIME), fmt=LOGFORMAT, datefmt=DATEFORMAT
            )
            handler.setFormatter(formatter)
            logging.getLogger().addHandler(handler)
        elif a_handler == "file":
            setup_file_logger(str(START_TIME))
        else:
            logger.debug("Unknown loghandler")

    library_loggers(verbosity_libraries)

    logger.info("Logging configuration finished")
    logger.info("Logging set to %s", cfg.LOGGING_HANDLERS)
    logger.info("Verbosity set to %s", verbosity_libraries)
    logger.info(
        "FORMAT: %s%s", LOGPREFIXFORMAT.replace("|", "-"), LOGFORMAT.replace("|", "-")
    )
