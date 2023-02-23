# IMPORTATION STANDARD
import logging

# IMPORTATION THIRDPARTY
# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import is_local, get_current_user

logger = logging.getLogger(__name__)

NO_USER_PLACEHOLDER = "NA"


def get_user_uuid() -> str:
    """Get user UUID"""
    if not is_local():
        return get_current_user().profile.get_uuid()

    return NO_USER_PLACEHOLDER
