import os
from unittest.mock import patch
from pathlib import Path
import pandas as pd
import pytest

from openbb_terminal import keys_model

# pylint: disable=R0902,R0903,W1404


def test_get_keys():
    df = keys_model.get_keys()
    assert isinstance(df, pd.DataFrame)


@patch.dict(os.environ, {}, clear=True)
@pytest.mark.parametrize(
    "env_var_name, env_var_value, persist",
    [("OPENBB_API_TEST", "TEST_KEY", True), ("OPENBB_API_TEST", "TEST_KEY", False)],
)
def test_set_key(env_var_name: str, env_var_value: str, persist: bool):

    # Route env file location
    keys_model.USER_ENV_FILE = ".tmp"
    keys_model.set_key(env_var_name, env_var_value, persist)

    # Check if key was exported to .env
    dotenv_key = keys_model.dotenv.get_key(
        str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
    )

    # Remove temporary env file
    if Path(keys_model.USER_ENV_FILE).is_file():
        os.remove(keys_model.USER_ENV_FILE)

    # Check if key was exported to os
    os_key = os.getenv(env_var_name)

    # Check if key was exported to config_terminal.py
    if env_var_name.startswith("OPENBB_"):
        env_var_name = env_var_name[7:]
        cfg_key = getattr(keys_model.cfg, env_var_name)

    if persist is True:
        assert (
            (dotenv_key == env_var_value)
            and (os_key == env_var_value)
            and (cfg_key == env_var_value)
        )
    else:
        assert (dotenv_key is None) and (os_key is None) and (cfg_key == env_var_value)


# TODO: Test each set method
