"""Decorators"""

__docformat__ = "numpy"
import logging

from openbb_terminal.core.session.current_user import (
    get_current_user,
    set_current_user,
)

logger = logging.getLogger(__name__)


def disable_check_api():
    current_user = get_current_user()
    current_user.preferences.ENABLE_CHECK_API = False
    set_current_user(current_user)
