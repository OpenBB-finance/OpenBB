# IMPORTATION STANDARD
import logging

from openbb_terminal.base_helpers import remove_log_handlers
from openbb_terminal.core.log.generation import settings_logger
from openbb_terminal.core.log.generation.common import do_rollover

# IMPORTATION THIRDPARTY
# IMPORTATION INTERNAL
from openbb_terminal.loggers import setup_logging

logger = logging.getLogger(__name__)


def log_terminal(test_mode: bool):
    """Logs for the terminal"""

    do_rollover()
    remove_log_handlers()

    if not test_mode:
        setup_logging()

    logger.info("START")
    settings_logger.log_all_settings(with_rollover=False)
    do_rollover()
