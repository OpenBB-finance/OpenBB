# IMPORTATION STANDARD
import logging

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL


class Application:
    @property
    def commit_hash(self) -> str:
        return self.__commit_hash

    @property
    def identifier(self) -> str:
        return self.__identifier

    @property
    def name(self) -> str:
        return self.__name

    @property
    def session_id(self) -> str:
        return self.__session_id

    def __init__(
        self,
        commit_hash: str,
        identifier: str,
        name: str,
        session_id: str,
    ):
        self.__commit_hash = commit_hash
        self.__identifier = identifier
        self.__name = name
        self.__session_id = session_id


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
        app: Application,
        style="%",
        validate=True,
    ) -> None:
        super().__init__(
            fmt=self.LOGFORMAT,
            datefmt=self.DATEFORMAT,
            style=style,
            validate=validate,
        )
        self.__app = app

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

        app = self.__app

        level_name = self.calculate_level_name(record=record)
        log_prefix_content = {
            "appName": app.name,
            "levelname": level_name,
            "appId": app.identifier,
            "sessionId": app.session_id,
            "commitHash": app.commit_hash,
        }
        log_extra = self.extract_log_extra(record=record)
        log_prefix_content = {**log_prefix_content, **log_extra}
        log_prefix = self.LOGPREFIXFORMAT % log_prefix_content

        log_line = super().format(record)
        log_line = self.filter_special_characters(text=log_line)
        log_line_full = log_prefix + log_line

        return log_line_full
