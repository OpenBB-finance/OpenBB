"""Bootstrap extension."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

from openbb_core.app.model.profile import Profile
from openbb_core.app.model.user_settings import UserSettings

from openbb_userauth.auth.hook import get_userdb_service


def run_async(func: Callable):
    try:
        asyncio.get_running_loop()
        # we need to create a separate thread so we can block before returning
        with ThreadPoolExecutor(1) as pool:
            result = pool.submit(lambda: asyncio.run(func())).result()
    except RuntimeError:
        # no event loop running
        result = asyncio.run(func())

    return result


def setup_default_users():
    """Setup default users."""
    userdb_service = run_async(get_userdb_service)
    user_settings_repository = userdb_service.user_settings_repository
    default_user_settings = userdb_service.default_user_settings
    default_profile_list = [
        Profile(
            active=True,
            username="openbb",
            # HASH OF 'openbb'
            # cSpell:disable-next-line
            password_hash="$2b$12$c8x3TOBCbSMyhNE8FqVCz.FVydrgVtA8wH8e/CQ3V43IfU2O5fZoq",  # nosec  # noqa: S106
        ),
        Profile(
            active=True,
            username="finance",
            # HASH OF 'finance'
            # cSpell:disable-next-line
            password_hash="$2b$12$/EdKMJ3C5plpqDS/dqpdvO0wL9v/XRttg65kkIgp8XTJWWmCu7L8y",  # nosec # noqa: S106
        ),
    ]

    for default_profile in default_profile_list:
        user_settings = user_settings_repository.read_by_profile(
            filter_list=[("username", default_profile.username)]
        )
        if user_settings:
            user_settings.profile = default_profile
            user_settings.credentials = default_user_settings.credentials
            user_settings_repository.update(model=user_settings)
        else:
            default_user_settings = UserSettings(
                profile=default_profile,
                credentials=default_user_settings.credentials,
                preferences=default_user_settings.preferences,
                defaults=default_user_settings.defaults,
            )
            user_settings_repository.create(model=default_user_settings)
