# IMPORTATION STANDARD
import json
import logging

from openbb_terminal.core.log.generation.common import do_rollover

# IMPORTATION THIRDPARTY
# IMPORTATION INTERNAL
from openbb_terminal.session.user import User

logger = logging.getLogger(__name__)


def log_user(with_rollover: bool = True):
    """Log user"""
    if not User.is_guest():
        _log_user_info()

    if with_rollover:
        do_rollover()


def _log_user_info():
    """Log user info"""
    user_info = {"user_uuid": User.get_uuid()}
    logger.info("USER: %s ", json.dumps(user_info))
