"""Settings model"""

from typing import Any

from dotenv import set_key
from pydantic import BaseModel, ConfigDict

from src.config.constants import ENV_FILE_SETTINGS


class Settings(BaseModel):
    """Settings model."""

    # Platform CLI version
    VERSION: str = "1.0.0"

    # DEVELOPMENT FLAGS
    TEST_MODE: bool = False
    DEBUG_MODE: bool = False
    DEV_BACKEND: bool = False

    # FEATURE FLAGS
    FILE_OVERWRITE: bool = False
    SHOW_VERSION: bool = True
    USE_INTERACTIVE_DF: bool = True
    USE_CLEAR_AFTER_CMD: bool = False
    USE_DATETIME: bool = True
    USE_PROMPT_TOOLKIT: bool = True
    ENABLE_QUICK_EXIT: bool = False
    ENABLE_EXIT_AUTO_HELP: bool = True
    REMEMBER_CONTEXTS: bool = True
    ENABLE_RICH_PANEL: bool = True
    TOOLBAR_HINT: bool = True

    # GENERAL
    TIMEZONE: str = "America/New_York"
    FLAIR: str = ":openbb"
    USE_LANGUAGE: str = "en"
    PREVIOUS_USE: bool = False

    # STYLE
    RICH_STYLE: str = "dark"

    # OUTPUT
    ALLOWED_NUMBER_OF_ROWS: int = 366
    ALLOWED_NUMBER_OF_COLUMNS: int = 15

    # OPENBB
    HUB_URL: str = "https://my.openbb.co"
    BASE_URL: str = "https://payments.openbb.co"

    model_config = ConfigDict(validate_assignment=True)

    def __repr__(self) -> str:
        """Return a string representation of the model."""
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.model_dump().items()
        )

    def set_item(self, key: str, value: Any) -> None:
        """Set an item in the model and save to .env."""
        setattr(self, key, value)
        set_key(str(ENV_FILE_SETTINGS), "OPENBB_" + key, str(value))


# from src.config.constants import (
#     ENV_FILE_PROJECT,
#     ENV_FILE_REPOSITORY,
#     ENV_FILE_SETTINGS,
# )

# DEFAULT_ORDER = [ENV_FILE_SETTINGS, ENV_FILE_PROJECT, ENV_FILE_REPOSITORY]


# def load_env_files():
#     """Load .env files.

#     Loads the dotenv files in the following order:
#     1. Repository .env file
#     2. Package .env file
#     3. User .env file

#     This allows the user to override the package settings with their own
#     settings, and the package to override the repository settings.

#     openbb_terminal modules are reloaded to refresh config files with new env,
#     otherwise they will use cache with old variables.
#     """
#     load_dotenv(ENV_FILE_REPOSITORY, override=True)
#     load_dotenv(ENV_FILE_PROJECT, override=True)
#     load_dotenv(ENV_FILE_SETTINGS, override=True)


# def get_reading_order() -> list:
#     """Get order of .env files.

#     If we are on frozen app, we reverse the order to read the ENV_FILE_SETTINGS last.

#     Returns
#     -------
#     list
#         List of .env files.
#     """
#     local_order = DEFAULT_ORDER.copy()
#     if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
#         local_order.reverse()
#     return local_order


# def read_env() -> Dict[str, Any]:
#     """Read .env files."""
#     __env_dict: Dict[str, Optional[str]] = {}

#     for env_file in get_reading_order():
#         if env_file.exists():
#             __env_dict.update(**dotenv_values(env_file))

#     __env_dict_filtered = {
#         k[len("OPENBBB_") - 1 :]: v
#         for k, v in __env_dict.items()
#         if k.startswith("OPENBB_")
#     }

#     return __env_dict_filtered
