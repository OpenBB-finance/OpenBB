"""Settings for the openbb_provider package."""


import os

from pydantic import BaseSettings
from pydantic.error_wrappers import ValidationError


def create_path(*path: str) -> str:
    """Create a path from the root of the project."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    in_between = os.path.dirname(base_path)
    default_path = os.path.join(in_between, *path)
    return default_path


class Settings(BaseSettings):
    """Settings for the managing the openbb_provider package.

    They are dynamically populated inside the ./registry.py file with the
    adequate provider API key placeholders.
    """

    DEBUG_MODE: bool = False


try:
    settings = Settings()  # type: ignore[call-arg,misc,arg-type]
except ValidationError:
    env_path = create_path(".env")
    settings = Settings(env_path)  # type: ignore[call-arg,misc,arg-type]
