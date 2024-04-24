"""Settings module."""

from copy import deepcopy
from typing import Any, Type, TypeVar

from pydantic import ValidationError

from src.config.env import read_env
from src.models import Settings
from src.models.base_model import BaseModel

T = TypeVar("T", bound=BaseModel)


def load_dict_to_model(dictionary: dict, model: Type[T]) -> T:
    """Load variables to model.

    Parameters
    ----------
    dictionary : dict
        Variables dictionary.
    model : Type[T]
        Model to load.

    Returns
    -------
    T
        Model with validated data.
    """
    model_name = model.__name__.strip("Model").lower()
    try:
        return model(**dictionary)  # type: ignore
    except ValidationError as error:
        print(f"Error loading {model_name}:")  # noqa: T201
        for err in error.errors():
            loc = err.get("loc", None)
            var_name = str(loc[0]) if loc else ""
            msg = err.get("msg", "")
            var = dictionary.pop(var_name, None)
            fields: dict[str, Any] = model.get_fields()
            if var and var_name in fields:
                default = fields[var_name].default
                print(  # noqa: T201
                    f"    {var_name}: {msg}, using default -> {default}"
                )

        return model(**dictionary)  # type: ignore
    except Exception:
        print(f"Error loading {model_name}, using defaults.")  # noqa: T201
        return model()  # type: ignore


def get_current_settings() -> Settings:
    """Get current user."""
    return deepcopy(__current_settings)


def _set_current_settings(settings: Settings):
    """Set current user."""
    global __current_settings  # pylint: disable=global-statement # noqa
    __current_settings = settings


def set_settings(
    name: str,
    value: Any,
):
    """Set preference.

    Parameters
    ----------
    name : str
        Preference name
    value : Any
        Preference value
    """
    settings = get_current_settings()  # this is a copy of the settings in place
    setattr(settings, name, value)
    _set_current_settings(settings)


__env_dict = read_env()
__current_settings = load_dict_to_model(__env_dict, Settings)
