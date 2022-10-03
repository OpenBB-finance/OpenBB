import os
from unittest.mock import patch
from pathlib import Path
import pandas as pd
import pytest

from openbb_terminal import keys_model

# pylint: disable=R0902,R0903,W1404

# Test persist
@patch.dict(os.environ, {}, clear=True)
@pytest.mark.parametrize(
    "env_var_name, env_var_value, persist",
    [("OPENBB_API_TEST", "TEST_KEY", True), ("OPENBB_API_TEST", "TEST_KEY", False)],
)
def test_set_key(env_var_name: str, env_var_value: str, persist: bool):

    # Route .env file location
    keys_model.USER_ENV_FILE = Path(".tmp")

    # Test
    keys_model.set_key(env_var_name, env_var_value, persist)

    # Get key from temp .env
    dotenv_key = keys_model.dotenv.get_key(
        str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
    )

    # Remove temp .env
    if keys_model.USER_ENV_FILE.is_file():
        os.remove(keys_model.USER_ENV_FILE)

    # Get key from patched os.environ
    os_key = os.getenv(env_var_name)

    # Get key from config_terminal.py
    if env_var_name.startswith("OPENBB_"):
        env_var_name = env_var_name[7:]
        cfg_key = getattr(keys_model.cfg, env_var_name)

    if persist is True:
        assert dotenv_key == os_key == cfg_key == env_var_value
    else:
        assert (dotenv_key is None) and (os_key is None) and (cfg_key == env_var_value)


def test_get_keys():
    df = keys_model.get_keys()
    assert isinstance(df, pd.DataFrame)


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "key, persist, show_output, expected",
    [
        ("test_key", False, True, -1),
        ("test_key", False, False, -1),
        ("test_key", True, False, -1),
        ("test_key", False, False, -1),
        ("REPLACE_ME", False, True, 0),
        ("REPLACE_ME", False, False, 0),
    ],
)
def test_set_av_key(key, persist, show_output, expected):

    env_var_name = "OPENBB_API_KEY_ALPHAVANTAGE"

    # Route .env file location
    # Just for safety, persist=False should not change it
    keys_model.USER_ENV_FILE = Path(".tmp")

    # Test
    status = keys_model.set_av_key(key=key, persist=persist, show_output=show_output)

    # Get key from temp .env
    dotenv_key = keys_model.dotenv.get_key(
        str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
    )

    # Get key from patched os.environ
    os_key = os.getenv(env_var_name)

    # Get key from config_terminal.py
    if env_var_name.startswith("OPENBB_"):
        env_var_name = env_var_name[7:]
        cfg_key = getattr(keys_model.cfg, env_var_name)

    # Remove temp .env
    if keys_model.USER_ENV_FILE.is_file():
        os.remove(keys_model.USER_ENV_FILE)

    if persist is True:
        assert dotenv_key == os_key == cfg_key == key
    else:
        assert (dotenv_key is None) and (os_key is None) and (cfg_key == key)

    assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "key, persist, show_output, expected",
    [
        ("test_key", False, True, -1),
        ("test_key", False, False, -1),
        ("test_key", True, False, -1),
        ("test_key", False, False, -1),
        ("REPLACE_ME", False, True, 0),
        ("REPLACE_ME", False, False, 0),
    ],
)
def test_set_fmp_key(key, persist, show_output, expected):

    env_var_name = "OPENBB_API_KEY_FINANCIALMODELINGPREP"

    keys_model.USER_ENV_FILE = Path(".tmp")

    status = keys_model.set_fmp_key(key=key, persist=persist, show_output=show_output)

    dotenv_key = keys_model.dotenv.get_key(
        str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
    )

    os_key = os.getenv(env_var_name)

    if env_var_name.startswith("OPENBB_"):
        env_var_name = env_var_name[7:]
        cfg_key = getattr(keys_model.cfg, env_var_name)

    if keys_model.USER_ENV_FILE.is_file():
        os.remove(keys_model.USER_ENV_FILE)

    if persist is True:
        assert dotenv_key == os_key == cfg_key == key
    else:
        assert (dotenv_key is None) and (os_key is None) and (cfg_key == key)

    assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "key, persist, show_output, expected",
    [
        ("test_key", False, True, -1),
        ("test_key", False, False, -1),
        ("test_key", True, False, -1),
        ("test_key", False, False, -1),
        ("REPLACE_ME", False, True, 0),
        ("REPLACE_ME", False, False, 0),
    ],
)
def test_set_quandl_key(key, persist, show_output, expected):

    env_var_name = "OPENBB_API_KEY_QUANDL"

    keys_model.USER_ENV_FILE = Path(".tmp")

    status = keys_model.set_quandl_key(key=key, persist=persist, show_output=show_output)

    dotenv_key = keys_model.dotenv.get_key(
        str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
    )

    os_key = os.getenv(env_var_name)

    if env_var_name.startswith("OPENBB_"):
        env_var_name = env_var_name[7:]
        cfg_key = getattr(keys_model.cfg, env_var_name)

    if keys_model.USER_ENV_FILE.is_file():
        os.remove(keys_model.USER_ENV_FILE)

    if persist is True:
        assert dotenv_key == os_key == cfg_key == key
    else:
        assert (dotenv_key is None) and (os_key is None) and (cfg_key == key)

    assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "key, persist, show_output, expected",
    [
        ("test_key", False, True, -1),
        ("test_key", False, False, -1),
        ("test_key", True, False, -1),
        ("test_key", False, False, -1),
        ("REPLACE_ME", False, True, 0),
        ("REPLACE_ME", False, False, 0),
    ],
)
def test_set_polygon_key(key, persist, show_output, expected):

    env_var_name = "OPENBB_API_POLYGON_KEY"

    keys_model.USER_ENV_FILE = Path(".tmp")

    status = keys_model.set_polygon_key(key=key, persist=persist, show_output=show_output)

    dotenv_key = keys_model.dotenv.get_key(
        str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
    )

    os_key = os.getenv(env_var_name)

    if env_var_name.startswith("OPENBB_"):
        env_var_name = env_var_name[7:]
        cfg_key = getattr(keys_model.cfg, env_var_name)

    if keys_model.USER_ENV_FILE.is_file():
        os.remove(keys_model.USER_ENV_FILE)

    if persist is True:
        assert dotenv_key == os_key == cfg_key == key
    else:
        assert (dotenv_key is None) and (os_key is None) and (cfg_key == key)

    assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "key, persist, show_output, expected",
    [
        ("test_key", False, True, -1),
        ("test_key", False, False, -1),
        ("test_key", True, False, -1),
        ("test_key", False, False, -1),
        ("REPLACE_ME", False, True, 0),
        ("REPLACE_ME", False, False, 0),
    ],
)
def test_set_fred_key(key, persist, show_output, expected):

    env_var_name = "OPENBB_API_FRED_KEY"

    # Route .env file location
    # Just for safety, persist=False should not change it
    keys_model.USER_ENV_FILE = Path(".tmp")

    # Test
    status = keys_model.set_fred_key(key=key, persist=persist, show_output=show_output)

    # Get key from temp .env
    dotenv_key = keys_model.dotenv.get_key(
        str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
    )

    # Get key from patched os.environ
    os_key = os.getenv(env_var_name)

    # Get key from config_terminal.py
    if env_var_name.startswith("OPENBB_"):
        env_var_name = env_var_name[7:]
        cfg_key = getattr(keys_model.cfg, env_var_name)

    # Remove temp .env
    if keys_model.USER_ENV_FILE.is_file():
        os.remove(keys_model.USER_ENV_FILE)

    if persist is True:
        assert dotenv_key == os_key == cfg_key == key
    else:
        assert (dotenv_key is None) and (os_key is None) and (cfg_key == key)

    assert status == expected
