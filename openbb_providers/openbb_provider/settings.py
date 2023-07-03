"""Settings for the openbb_provider package."""


import os
from typing import Optional

from pydantic import BaseSettings
from pydantic.error_wrappers import ValidationError


def create_path(*path: str) -> str:
    base_path = os.path.dirname(os.path.abspath(__file__))
    in_between = os.path.dirname(base_path)
    default_path = os.path.join(in_between, *path)
    return default_path


class Settings(BaseSettings):
    FMP_API_KEY: Optional[str] = None
    POLYGON_API_KEY: Optional[str] = None
    BENZINGA_API_KEY: Optional[str] = None
    DEBUG_MODE: bool = False


try:
    settings = Settings()  # type: ignore[call-arg]
except ValidationError:
    env_path = create_path(".env")
    settings = Settings(env_path)  # type: ignore[call-arg,misc,arg-type]
