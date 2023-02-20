# IMPORTATION STANDARD
import logging

# IMPORTATION THIRDPARTY
# IMPORTATION INTERNAL
from openbb_terminal.session.user import User

logger = logging.getLogger(__name__)

NO_USER_PLACEHOLDER = "NA"


def get_user_uuid() -> str:
    """Get user UUID"""

    if not User.is_guest():
        return User.get_uuid()

    return NO_USER_PLACEHOLDER
