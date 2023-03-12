# IMPORTS STANDARD
from typing import Any, Dict, Optional, Type, Union

# IMPORTS THIRDPARTY
from dotenv import dotenv_values
from pydantic import ValidationError

# IMPORTS INTERNAL
from openbb_terminal.core.config.paths import (
    PACKAGE_ENV_FILE,
    REPOSITORY_ENV_FILE,
    SETTINGS_ENV_FILE,
)
from openbb_terminal.core.models.credentials_model import CredentialsModel
from openbb_terminal.core.models.preferences_model import PreferencesModel


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


def load_env_to_model(
    env_dict: dict, model: Union[Type[CredentialsModel], Type[PreferencesModel]]
) -> Union[Type[CredentialsModel], Type[PreferencesModel]]:
    """Load environment variables to model.

    Parameters
    ----------
    env_dict : dict
        Environment variables dictionary.
    model : Union[Type[CredentialsModel], Type[PreferencesModel]]
        Model to validate.

    Returns
    -------
    Union[Type[CredentialsModel], Type[PreferencesModel]]
        Model with environment variables.
    """
    try:
        return model(**env_dict)  # type: ignore
    except ValidationError as error:
        model_name = model.__name__.strip("Model").lower()
        print(f"Error loading {model_name}:")
        for err in error.errors():
            loc = err.get("loc", None)
            var_name = str(loc[0]) if loc else ""
            msg = err.get("msg", "")
            var = env_dict.pop(var_name, None)
            fields = model.__dataclass_fields__  # type: ignore
            if var and var_name in fields:
                default = fields[var_name].default
                print(f"    {var_name}: {msg}, using default -> {default}")

        return model(**env_dict)  # type: ignore
