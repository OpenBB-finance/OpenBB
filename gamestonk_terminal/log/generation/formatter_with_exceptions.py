# IMPORTATION STANDARD
import logging

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from gamestonk_terminal.log.generation.settings import AppSettings


class FormatterWithExceptions(logging.Formatter):
    """Logging Formatter that includes formatting of Exceptions"""

    DATEFORMAT = "%Y-%m-%dT%H:%M:%S%z"
    LOGFORMAT = "%(asctime)s|%(name)s|%(funcName)s|%(lineno)s|%(message)s"
    LOGPREFIXFORMAT = (
        "%(levelname)s|%(appName)s|%(commitHash)s|%(appId)s|%(sessionId)s|"
    )

    @staticmethod
    def calculate_level_name(record: logging.LogRecord):
        if record.exc_text:
            level_name = "X"
        elif record.levelname:
            level_name = record.levelname[0]
        else:
            level_name = "U"

        return level_name

    @staticmethod
    def extract_log_extra(record: logging.LogRecord):
        log_extra = dict()

        if hasattr(record, "func_name_override"):
            record.funcName = record.func_name_override  # type: ignore
            record.lineno = 0

        if hasattr(record, "user_id"):
            log_extra["loggingId"] = record.user_id  # type: ignore

        if hasattr(record, "session_id"):
            log_extra["sessionId"] = record.session_id  # type: ignore

        return log_extra

    @staticmethod
    def filter_special_characters(text: str):
        filtered_text = (
            text.replace("\n", " - ")
            .replace("\t", " ")
            .replace("\r", "")
            .replace("'", "`")
            .replace('"', "`")
        )

        return filtered_text

    # OVERRIDE
    def __init__(
        self,
        app_settings: AppSettings,
        style="%",
        validate=True,
    ) -> None:
        super().__init__(
            fmt=self.LOGFORMAT,
            datefmt=self.DATEFORMAT,
            style=style,
            validate=validate,
        )
        self.__log_settings = app_settings

    # OVERRIDE
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

    # OVERRIDE
    def format(self, record: logging.LogRecord) -> str:
        """Log formatter
        Parameters
        ----------
        record : logging.LogRecord
            Logging record
        Returns
        -------
        str
            Formatted_log message
        """

        app_settings = self.__log_settings

        level_name = self.calculate_level_name(record=record)
        log_prefix_content = {
            "appName": app_settings.name,
            "levelname": level_name,
            "appId": app_settings.identifier,
            "sessionId": app_settings.session_id,
            "commitHash": app_settings.commit_hash,
        }
        log_extra = self.extract_log_extra(record=record)
        log_prefix_content = {**log_prefix_content, **log_extra}
        log_prefix = self.LOGPREFIXFORMAT % log_prefix_content

        log_line = super().format(record)
        log_line = self.filter_special_characters(text=log_line)
        log_line_full = log_prefix + log_line

        return log_line_full
