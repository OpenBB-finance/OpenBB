import os
from typing import List
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


def clean_environment(env_var_name_list: List[str]) -> None:

    # Remove keys from patched os.environ
    for env_var_name in env_var_name_list:
        if env_var_name in os.environ:
            os.environ.pop(env_var_name)

    # Remove .tmp content
    if Path(".tmp").is_file():
        open(".tmp", 'w').close()
    
    # Set new temporary .env
    keys_model.USER_ENV_FILE = Path(".tmp")


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_key"],
            False,
            True,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["test_key"],
            True,
            False,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_av_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_KEY_ALPHAVANTAGE",
     ]

    clean_environment(env_var_name_list)

    status = keys_model.set_av_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_key"],
            False,
            True,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["test_key"],
            True,
            False,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_fmp_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_KEY_FINANCIALMODELINGPREP",
     ]

    clean_environment(env_var_name_list)

    status = keys_model.set_fmp_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_key"],
            False,
            True,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["test_key"],
            True,
            False,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_quandl_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_KEY_QUANDL",
     ]

    clean_environment(env_var_name_list)

    status = keys_model.set_quandl_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_key"],
            False,
            True,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["test_key"],
            True,
            False,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_polygon_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_POLYGON_KEY",
     ]

    clean_environment(env_var_name_list)

    status = keys_model.set_polygon_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_key"],
            False,
            True,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["test_key"],
            True,
            False,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_fred_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_FRED_KEY",
     ]

    clean_environment(env_var_name_list)

    status = keys_model.set_fred_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_key"],
            False,
            True,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["test_key"],
            True,
            False,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_news_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_NEWS_TOKEN",
     ]

    clean_environment(env_var_name_list)

    status = keys_model.set_news_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_key"],
            False,
            True,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["test_key"],
            True,
            False,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_tradier_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_TRADIER_TOKEN",
     ]

    clean_environment(env_var_name_list)

    status = keys_model.set_tradier_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_key"],
            False,
            True,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["test_key"],
            True,
            False,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_cmc_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_CMC_KEY",
     ]

    clean_environment(env_var_name_list)

    status = keys_model.set_cmc_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_key"],
            False,
            True,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["test_key"],
            True,
            False,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_finnhub_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_FINNHUB_KEY",
     ]

    clean_environment(env_var_name_list)

    status = keys_model.set_finnhub_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_key"],
            False,
            True,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["test_key"],
            True,
            False,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_iex_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_IEX_KEY",
     ]

    clean_environment(env_var_name_list)

    status = keys_model.set_iex_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_id", "test_secret", "test_pass", "test_user", "test_agent"],
            False,
            True,
            -1,
        ),
        (
            ["test_id", "test_secret", "test_pass", "test_user", "test_agent"],
            False,
            False,
            -1,
        ),
        (
            ["test_id", "test_secret", "test_pass", "test_user", "test_agent"],
            True,
            False,
            -1,
        ),
        (
            ["test_id", "test_secret", "test_pass", "test_user", "test_agent"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME", "REPLACE_ME", "REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME", "REPLACE_ME", "REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_reddit_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_REDDIT_CLIENT_ID",
        "OPENBB_API_REDDIT_CLIENT_SECRET",
        "OPENBB_API_REDDIT_PASSWORD",
        "OPENBB_API_REDDIT_USERNAME",
        "OPENBB_API_REDDIT_USER_AGENT",
    ]

    for env_var_name in env_var_name_list:
        if env_var_name in os.environ:
            os.environ.pop(env_var_name)

    if Path(".tmp").is_file():
        open(".tmp", 'w').close()
    
    keys_model.USER_ENV_FILE = Path(".tmp")

    status = keys_model.set_reddit_key(
        client_id=args[0],
        client_secret=args[1],
        password=args[2],
        username=args[3],
        useragent=args[4],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_key"],
            False,
            True,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["test_key"],
            True,
            False,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_bitquery_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_BITQUERY_KEY",
     ]

    clean_environment(env_var_name_list)

    status = keys_model.set_bitquery_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected


### def test_set_twitter_key

### def test_set_rh_key

### def test_set_degiro_key

### def test_set_oanda_key

### def test_set_binance_key


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_key"],
            False,
            True,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["test_key"],
            True,
            False,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_si_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_SENTIMENTINVESTOR_TOKEN",
     ]

    clean_environment(env_var_name_list)

    status = keys_model.set_si_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected


### def test_set_coinbase_key


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_key"],
            False,
            True,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["test_key"],
            True,
            False,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_walert_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_WHALE_ALERT_KEY",
     ]

    clean_environment(env_var_name_list)

    status = keys_model.set_walert_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_key"],
            False,
            True,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["test_key"],
            True,
            False,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_glassnode_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_GLASSNODE_KEY",
     ]

    clean_environment(env_var_name_list)

    status = keys_model.set_glassnode_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_key"],
            False,
            True,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["test_key"],
            True,
            False,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_coinglass_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_COINGLASS_KEY",
     ]

    clean_environment(env_var_name_list)

    status = keys_model.set_coinglass_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_key"],
            False,
            True,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["test_key"],
            True,
            False,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_cpanic_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_CRYPTO_PANIC_KEY",
     ]

    clean_environment(env_var_name_list)

    status = keys_model.set_cpanic_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_key"],
            False,
            True,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["test_key"],
            True,
            False,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_ethplorer_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_ETHPLORER_KEY",
     ]

    clean_environment(env_var_name_list)

    status = keys_model.set_ethplorer_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected


### def test_set_smartstake_key


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_key"],
            False,
            True,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["test_key"],
            True,
            False,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_github_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_GITHUB_KEY",
     ]

    clean_environment(env_var_name_list)

    status = keys_model.set_github_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_key"],
            False,
            True,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["test_key"],
            True,
            False,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_messari_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_MESSARI_KEY",
     ]

    clean_environment(env_var_name_list)

    status = keys_model.set_messari_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_key"],
            False,
            True,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["test_key"],
            True,
            False,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_eodhd_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_EODHD_KEY",
     ]

    clean_environment(env_var_name_list)

    status = keys_model.set_eodhd_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected


@patch.dict(os.environ, {})
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, expected",
    [
        (
            ["test_key"],
            False,
            True,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["test_key"],
            True,
            False,
            -1,
        ),
        (
            ["test_key"],
            False,
            False,
            -1,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            0,
        ),
        (
            ["REPLACE_ME"],
            False,
            False,
            0,
        ),
    ],
)
def test_set_santiment_key(
    args: List[str], persist: bool, show_output: bool, expected: int
):

    env_var_name_list = [
        "OPENBB_API_SANTIMENT_KEY",
     ]

    clean_environment(env_var_name_list)

    status = keys_model.set_santiment_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )

    for i, env_var_name in enumerate(env_var_name_list):

        dotenv_var = keys_model.dotenv.get_key(
            str(keys_model.USER_ENV_FILE), key_to_get=env_var_name
        )

        os_var = os.getenv(env_var_name)

        if env_var_name.startswith("OPENBB_"):
            env_var_name = env_var_name[7:]
        cfg_var = getattr(keys_model.cfg, env_var_name)

        if persist is True:
            assert dotenv_var == os_var == cfg_var == args[i]
        else:
            assert (
                (dotenv_var is None) and (os_var is None) and (cfg_var == args[i])
            )

        assert status == expected
