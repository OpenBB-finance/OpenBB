# IMPORTATION STANDARD
import logging

# IMPORTATION THIRDPARTY


# IMPORTATION INTERNAL
from openbb_terminal.loggers import setup_logging
from openbb_terminal.core.log.generation import settings_logger
from openbb_terminal.core.log.generation import user_logger
from openbb_terminal.core.log.generation.common import do_rollover

logger = logging.getLogger(__name__)


def log_terminal(test_mode: bool):
    """Logs for the terminal"""

    if not test_mode:
        setup_logging()

    logger.info("START")
    settings_logger.log_all_settings(with_rollover=False)
    user_logger.log_user(with_rollover=False)
    do_rollover()
