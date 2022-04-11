import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from math import ceil
from threading import Thread
from typing import Callable, Optional


class Precision(Enum):
    hour = 3600
    minute = 60


class LoggingClock(Thread):
    """
    Like a Talking Clock but for logs.

    Usage example :
        import logging
        from openbb_terminal.log_collection.logging_clock import LoggingClock, Precision

        logging.basicConfig()
        logger = logging.getLogger(__name__)
        logger.setLevel(level=logging.INFO)

        logging_clock = LoggingClock(
            logger=logger,
            precision=Precision.minute,
        )
        logging_clock.start()
        logging_clock.join()
    """

    @classmethod
    def calculate_next_sharp(
        cls,
        current_time: datetime,
        precision: Precision,
    ) -> datetime:
        if precision is Precision.hour:
            sharp_time = cls.calculate_next_sharp_hour(current_time=current_time)
        elif precision is Precision.minute:
            sharp_time = cls.calculate_next_sharp_minute(current_time=current_time)
        else:
            raise AttributeError(f"Unknown precision {precision}")

        return sharp_time

    @staticmethod
    def calculate_next_sharp_hour(current_time: datetime) -> datetime:
        current_truncated_time = datetime(
            current_time.year,
            current_time.month,
            current_time.day,
            current_time.hour,
        )
        next_sharp_hour = current_truncated_time + timedelta(minutes=1)

        return next_sharp_hour

    @staticmethod
    def calculate_next_sharp_minute(current_time: datetime) -> datetime:
        current_truncated_time = datetime(
            current_time.year,
            current_time.month,
            current_time.day,
            current_time.hour,
            current_time.minute,
        )
        next_sharp_minute = current_truncated_time + timedelta(minutes=1)

        return next_sharp_minute

    @classmethod
    def do_action_every_sharp(
        cls,
        action: Callable,
        precision: Precision = Precision.hour,
    ):
        next_hour = cls.calculate_next_sharp(
            current_time=datetime.now(),
            precision=precision,
        )

        while True:
            current_time = datetime.now()
            delta = current_time - next_hour
            delta_seconds = delta.total_seconds()

            if delta_seconds > 0:
                action()
                next_hour = cls.calculate_next_sharp(
                    current_time=current_time,
                    precision=precision,
                )
            else:
                sleep_duration = ceil(abs(delta_seconds))
                time.sleep(sleep_duration)

    # OVERRIDE
    def run(self):
        action = self.__action
        precision = self.__precision

        self.do_action_every_sharp(
            action=action,
            precision=precision,
        )

    # OVERRIDE
    def __init__(
        self,
        *args,
        action: Optional[Callable] = None,
        level: int = logging.INFO,
        logger: Optional[logging.Logger] = None,
        msg: str = "Logging Clock : %s",
        precision: Precision = Precision.hour,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.__action = action or self.default_action
        self.__level = level
        self.__logger = logger or logging.getLogger(self.__module__)
        self.__msg = msg
        self.__precision = precision

    def default_action(self):
        level = self.__level
        logger = self.__logger
        msg = self.__msg % datetime.now()

        logger.log(level=level, msg=msg)
