# IMPORTATION STANDARD
import json
import logging
from typing import Optional

# IMPORTATION THIRDPARTY
# IMPORTATION INTERNAL
from openbb_terminal.core.log.generation.common import do_rollover
from openbb_terminal.session.user import User

logger = logging.getLogger(__name__)

NO_USER_PLACEHOLDER = "NA"


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


def get_user_uuid() -> Optional[str]:
    """Get user UUID"""

    if not User.is_guest():
        return User.get_uuid()

    return None
