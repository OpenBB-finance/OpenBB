# IMPORTS STANDARD
from typing import Any, Dict, Optional, Type, TypeVar

# IMPORTS THIRDPARTY
from dotenv import dotenv_values, set_key
from pydantic import ValidationError

# IMPORTS INTERNAL
from openbb_terminal.core.config.paths import (
    PACKAGE_ENV_FILE,
    REPOSITORY_ENV_FILE,
    SETTINGS_ENV_FILE,
)
from openbb_terminal.core.models import BaseModel

T = TypeVar("T", bound=BaseModel)


def reading_env() -> Dict[str, Any]:
    __env_dict: Dict[str, Optional[str]] = {}

    if REPOSITORY_ENV_FILE.exists():
        __env_dict.update(**dotenv_values(REPOSITORY_ENV_FILE))

    if PACKAGE_ENV_FILE.exists():
        __env_dict.update(**dotenv_values(PACKAGE_ENV_FILE))

    if SETTINGS_ENV_FILE.exists():
        __env_dict.update(**dotenv_values(SETTINGS_ENV_FILE))

    __env_dict_filtered = {
        k[len("OPENBBB_") - 1 :]: v
        for k, v in __env_dict.items()
        if k.startswith("OPENBB_")
    }

    return __env_dict_filtered


def load_env_to_model(env_dict: dict, model: Type[T]) -> T:
    """Load environment variables to model.

    Parameters
    ----------
    env_dict : dict
        Environment variables dictionary.
    model : Type[T]
        Type of the model to validate (can be any type that is a subclass of `BaseModel`).

    Returns
    -------
    T
        Model with environment variables.
    """
    model_name = model.__name__.strip("Model").lower()
    try:
        return model(**env_dict)  # type: ignore
    except ValidationError as error:
        print(f"Error loading {model_name}:")
        for err in error.errors():
            loc = err.get("loc", None)
            var_name = str(loc[0]) if loc else ""
            msg = err.get("msg", "")
            var = env_dict.pop(var_name, None)
            fields: dict[str, Any] = model.get_fields()
            if var and var_name in fields:
                default = fields[var_name].default
                print(f"    {var_name}: {msg}, using default -> {default}")

        return model(**env_dict)  # type: ignore
    except Exception:
        print(f"Error loading {model_name}, using defaults.")
        return model()  # type: ignore


def write_to_dotenv(name: str, value: str) -> None:
    """Write to .env file.

    Parameters
    ----------
    name : str
        Name of the variable.
    value : str
        Value of the variable.
    """
    set_key(str(SETTINGS_ENV_FILE), name, str(value))
