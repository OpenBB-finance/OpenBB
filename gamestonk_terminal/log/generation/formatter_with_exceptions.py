# IMPORTATION STANDARD
import logging
import os
import re

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from gamestonk_terminal.log.generation.settings import AppSettings


class FormatterWithExceptions(logging.Formatter):
    """Logging Formatter that includes formatting of Exceptions"""

    DATEFORMAT = "%Y-%m-%dT%H:%M:%S%z"
    LOGFORMAT = "%(asctime)s|%(name)s|%(funcName)s|%(lineno)s|%(message)s"
    LOGPREFIXFORMAT = (
        "%(levelname)s|%(appName)s|%(commitHash)s|%(appId)s|%(sessionId)s|%(userId)s|"
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

        log_extra["userId"] = record.user_id if hasattr(record, "user_id") else "NA"  # type: ignore

        if hasattr(record, "session_id"):
            log_extra["sessionId"] = record.session_id  # type: ignore

        return log_extra

    @staticmethod
    def filter_piis(text: str) -> str:
        ip_regex = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        s_list = []
        ip_reg = re.compile(ip_regex)
        for word in text.split():
            if (
                ip_reg.search(word)
                # and int(max(word.split(""))) < 256
                # and int(min(word.split(""))) >= 0
            ):
                s_list.append("suspected_ip")
            elif "@" in word and "." in word:
                s_list.append("suspected_email")
            elif os.sep in word and "GamestonkTerminal/" in word:
                s_list.append(word.split("GamestonkTerminal/")[1])
            elif os.sep in word:
                s_list.append("cut/file/path/" + word.split(os.sep)[-1])
            else:
                s_list.append(word)

            text = " ".join(s_list)

        return text

    @staticmethod
    def filter_special_characters(text: str):
        filtered_text = text.replace("\n", " - ").replace("\t", " ").replace("\r", "")

        return filtered_text

    @classmethod
    def filter_log_line(cls, text: str):
        text = cls.filter_special_characters(text=text)
        text = (
            text
            if "CMD: {" in text or "QUEUE: {" in text
            else cls.filter_piis(text=text)  # change this
        )

        return text

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
        log_line = self.filter_log_line(text=log_line)
        log_line_full = log_prefix + log_line

        return log_line_full
