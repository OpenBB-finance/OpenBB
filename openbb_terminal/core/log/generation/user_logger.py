# IMPORTATION STANDARD
import json
import logging

# IMPORTATION THIRDPARTY


# IMPORTATION INTERNAL
from openbb_terminal.account.user import User
from openbb_terminal.core.log.generation.common import do_rollover

logger = logging.getLogger(__name__)


def log_user(with_rollover: bool = True):
    """Log user"""
    if User.is_logged_in():
        log_user_info()

    if with_rollover:
        do_rollover()


def log_user_info():
    """Log user info"""
    user_info = {"user_uuid": User.UUID, "user_email": User.EMAIL}
    logger.info("USER: %s ", json.dumps(user_info))
