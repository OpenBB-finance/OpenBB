import os
from pathlib import Path
from typing import List

import pandas as pd
import pytest

from openbb_terminal import keys_model
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)

# pylint: disable=R0902,R0903,W1404,C0302
TEST_PATH = Path(__file__).parent.resolve()
proc_id = os.getpid()


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("api_key", "test_key"),
        ],
    }


@pytest.fixture(autouse=True)
def revert_current_user(mocker):
    mocker.patch(
        target="openbb_terminal.keys_model.set_credential",
    )
    yield


def test_get_keys():
    df = keys_model.get_keys()
    assert isinstance(df, pd.DataFrame)


def set_naive_environment(var_name_list: List[str]) -> None:
    temp_name = "_".join(var_name_list).replace("OPENBB_", "").replace("API_", "")
    tmp_env = (TEST_PATH / f"{temp_name}{proc_id}.tmp").resolve()

    # Remove keys from patched os.environ
    for var_name in var_name_list:
        if var_name in os.environ:
            os.environ.pop(var_name)

    # Remove .tmp content
    if tmp_env.is_file():
        tmp_env.unlink(missing_ok=True)

    # Set new temporary .env
    keys_model.SETTINGS_ENV_FILE = tmp_env


# Alphavantage api is working with any key you pass, so expected is 1 with dummy keys


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_PASSED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_PASSED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_PASSED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_av_key(args: List[str], persist: bool, show_output: bool, __expected: str):
    var_name_list = [
        "OPENBB_API_KEY_ALPHAVANTAGE",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_av_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_fmp_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_KEY_FINANCIALMODELINGPREP",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_fmp_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_quandl_key(
    args: List[str],
    persist: bool,
    show_output: bool,
    __expected: str,
    mocker,
):
    preferences = PreferencesModel(
        ENABLE_EXIT_AUTO_HELP=False,
        ENABLE_CHECK_API=False,
    )
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    var_name_list = [
        "OPENBB_API_KEY_QUANDL",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_quandl_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_polygon_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_POLYGON_KEY",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_polygon_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_fred_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_FRED_KEY",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_fred_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_news_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_NEWS_TOKEN",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_news_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_tradier_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_TRADIER_TOKEN",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_tradier_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_cmc_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_CMC_KEY",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_cmc_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_finnhub_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_FINNHUB_KEY",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_finnhub_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_id", "test_secret", "test_pass", "test_user", "test_agent"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_id", "test_secret", "test_pass", "test_user", "test_agent"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_id", "test_secret", "test_pass", "test_user", "test_agent"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME", "REPLACE_ME", "REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_reddit_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_REDDIT_CLIENT_ID",
        "OPENBB_API_REDDIT_CLIENT_SECRET",
        "OPENBB_API_REDDIT_PASSWORD",
        "OPENBB_API_REDDIT_USERNAME",
        "OPENBB_API_REDDIT_USER_AGENT",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_reddit_key(
        client_id=args[0],
        client_secret=args[1],
        password=args[2],
        username=args[3],
        useragent=args[4],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_bitquery_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_BITQUERY_KEY",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_bitquery_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "access_token, persist, show_output, __expected",
    [
        (
            "test_access_token",
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            "test_access_token",
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            "test_access_token",
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            "REPLACE_ME",
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_twitter_key(
    access_token: str, persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_TWITTER_BEARER_TOKEN",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_twitter_key(
        access_token=access_token,
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_username", "test_password"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_NOT_TESTED,
        ),
        (
            ["test_username", "test_password"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_NOT_TESTED,
        ),
        (
            ["test_username", "test_password"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_NOT_TESTED,
        ),
        (
            ["REPLACE_ME", "REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_rh_key(args: List[str], persist: bool, show_output: bool, __expected: str):
    var_name_list = [
        "OPENBB_RH_USERNAME",
        "OPENBB_RH_PASSWORD",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_rh_key(
        username=args[0],
        password=args[1],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_username", "test_password", "test_secret"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_username", "test_password", "test_secret"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_username", "test_password", "test_secret"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_degiro_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_DG_USERNAME",
        "OPENBB_DG_PASSWORD",
        "OPENBB_DG_TOTP_SECRET",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_degiro_key(
        username=args[0],
        password=args[1],
        secret=args[2],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_account", "test_access_token", "account_type"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_account", "test_access_token", "account_type"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_account", "test_access_token", "account_type"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_oanda_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_OANDA_ACCOUNT",
        "OPENBB_OANDA_TOKEN",
        "OPENBB_OANDA_ACCOUNT_TYPE",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_oanda_key(
        account=args[0],
        access_token=args[1],
        account_type=args[2],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key", "test_secret"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key", "test_secret"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key", "test_secret"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME", "REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_binance_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_BINANCE_KEY",
        "OPENBB_API_BINANCE_SECRET",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_binance_key(
        key=args[0],
        secret=args[1],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key", "test_secret", "test_passphrase"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key", "test_secret", "test_passphrase"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key", "test_secret", "test_passphrase"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_coinbase_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_COINBASE_KEY",
        "OPENBB_API_COINBASE_SECRET",
        "OPENBB_API_COINBASE_PASS_PHRASE",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_coinbase_key(
        key=args[0],
        secret=args[1],
        passphrase=args[2],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_walert_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_WHALE_ALERT_KEY",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_walert_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_glassnode_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_GLASSNODE_KEY",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_glassnode_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_coinglass_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_COINGLASS_KEY",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_coinglass_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_cpanic_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_CRYPTO_PANIC_KEY",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_cpanic_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_ethplorer_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_ETHPLORER_KEY",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_ethplorer_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key", "test_access_token"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key", "test_access_token"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key", "test_access_token"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME", "REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_smartstake_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_SMARTSTAKE_KEY",
        "OPENBB_API_SMARTSTAKE_TOKEN",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_smartstake_key(
        key=args[0],
        access_token=args[1],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_NOT_TESTED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_NOT_TESTED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_NOT_TESTED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_github_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_GITHUB_KEY",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_github_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_messari_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_MESSARI_KEY",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_messari_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_eodhd_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_EODHD_KEY",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_eodhd_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_santiment_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_SANTIMENT_KEY",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_santiment_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_tokenterminal_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_TOKEN_TERMINAL_KEY",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_tokenterminal_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_shroom_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_API_SHROOM_KEY",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_shroom_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "args, persist, show_output, __expected",
    [
        (
            ["test_key"],
            False,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            False,
            False,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["test_key"],
            True,
            True,
            keys_model.KeyStatus.DEFINED_TEST_FAILED,
        ),
        (
            ["REPLACE_ME"],
            False,
            True,
            keys_model.KeyStatus.NOT_DEFINED,
        ),
    ],
)
def test_set_openbb_key(
    args: List[str], persist: bool, show_output: bool, __expected: str
):
    var_name_list = [
        "OPENBB_OPENBB_PERSONAL_ACCESS_TOKEN",
    ]

    set_naive_environment(var_name_list)

    keys_model.set_openbb_personal_access_token(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )


def delete_tmp_files():
    tmp_files = TEST_PATH.glob(f"*{proc_id}.tmp")
    for file in tmp_files:
        file.unlink(missing_ok=True)


@pytest.fixture(scope="session", autouse=True)
def delete_tmp_files_session():
    delete_tmp_files()
    yield
    delete_tmp_files()
