from copy import deepcopy

from openbb import obb
from openbb_core.app.model.user_settings import UserSettings


def get_platform_user() -> UserSettings:
    """Get platform user."""
    if hasattr(obb, "user"):
        return deepcopy(obb.user)
    raise AttributeError("The 'obb' object has no attribute 'user'")


def is_local() -> bool:
    """Check if user is guest.

    Returns
    -------
    bool
        True if user is guest, False otherwise.
    """
    if hasattr(obb, "user") and hasattr(obb.user, "profile"):
        return not bool(obb.user.profile.hub_session)
    return True
