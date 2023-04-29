# IMPORTATION STANDARD
import logging
import re

# IMPORTATION THIRDPARTY
# IMPORTATION INTERNAL
from openbb_terminal.core.config.paths import HOME_DIRECTORY
from openbb_terminal.core.log.generation.settings import AppSettings
from openbb_terminal.core.log.generation.user_logger import get_user_uuid


class FormatterWithExceptions(logging.Formatter):
    """Logging Formatter that includes formatting of Exceptions"""

    DATEFORMAT = "%Y-%m-%dT%H:%M:%S%z"
    LOGFORMAT = "%(asctime)s|%(name)s|%(funcName)s|%(lineno)s|%(message)s"
    LOGPREFIXFORMAT = (
        "%(levelname)s|%(appName)s|%(commitHash)s|%(appId)s|%(sessionId)s|%(userId)s|"
    )

    @staticmethod
    def calculate_level_name(record: logging.LogRecord) -> str:
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

        if hasattr(record, "session_id"):
            log_extra["sessionId"] = record.session_id  # type: ignore

        return log_extra

    @staticmethod
    def mock_ipv4(text: str) -> str:
        pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        replacement = " FILTERED_IP "
        text_mocked = re.sub(pattern, replacement, text)

        return text_mocked

    @staticmethod
    def mock_email(text: str) -> str:
        pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        replacement = " FILTERED_EMAIL "
        text_mocked = re.sub(pattern, replacement, text)

        return text_mocked

    @staticmethod
    def mock_password(text: str) -> str:
        pattern = r'("password": ")[^"]+'
        replacement = r"\1 FILTERED_PASSWORD "
        text_mocked = re.sub(pattern, replacement, text)
        return text_mocked

    @staticmethod
    def mock_flair(text: str) -> str:
        pattern = r'("FLAIR": "\[)(.*?)\]'
        replacement = r"\1 FILTERED_FLAIR ]"
        text_mocked = re.sub(pattern, replacement, text)

        return text_mocked

    @staticmethod
    def mock_home_directory(text: str) -> str:
        user_home_directory = str(HOME_DIRECTORY.as_posix())
        text_mocked = text.replace("\\\\", "/").replace(
            user_home_directory, "MOCKING_USER_PATH"
        )

        return text_mocked

    @classmethod
    def filter_special_tags(cls, text: str) -> str:
        text_filtered = text.replace("\n", " MOCKING_BREAKLINE ")
        text_filtered = text_filtered.replace("'Traceback", "Traceback")

        return text_filtered

    @classmethod
    def filter_piis(cls, text: str) -> str:
        text_filtered = cls.mock_ipv4(text=text)
        text_filtered = cls.mock_email(text=text_filtered)
        text_filtered = cls.mock_password(text=text_filtered)
        text_filtered = cls.mock_home_directory(text=text_filtered)
        text_filtered = cls.mock_flair(text=text_filtered)

        return text_filtered

    @classmethod
    def filter_log_line(cls, text: str):
        text_filtered = cls.filter_special_tags(text=text)
        text_filtered = cls.filter_piis(text=text_filtered)

        return text_filtered

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
        ----------
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
        ----------
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
            "userId": get_user_uuid(),
        }

        log_extra = self.extract_log_extra(record=record)
        log_prefix_content = {**log_prefix_content, **log_extra}
        log_prefix = self.LOGPREFIXFORMAT % log_prefix_content

        record.msg = record.msg.replace("|", "-MOCK_PIPE-")

        log_line = super().format(record)
        log_line = self.filter_log_line(text=log_line)
        log_line_full = log_prefix + log_line

        return log_line_full
