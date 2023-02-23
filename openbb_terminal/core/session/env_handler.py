# IMPORTS STANDARD
from typing import Any, Dict

# IMPORTS THIRDPARTY
from dotenv import dotenv_values

# IMPORTS INTERNAL
from openbb_terminal.core.config.paths import (
    PACKAGE_ENV_FILE,
    REPOSITORY_ENV_FILE,
    USER_ENV_FILE,
)


def reading_env() -> Dict[str, Any]:
    __env_dict = {
        **dotenv_values(REPOSITORY_ENV_FILE),
        **dotenv_values(PACKAGE_ENV_FILE),
        **dotenv_values(USER_ENV_FILE),
    }
    __env_dict_filtered = {
        k[len("OPENBBB_") - 1 :]: v
        for k, v in __env_dict.items()
        if k.startswith("OPENBB_")
    }

    return __env_dict_filtered
