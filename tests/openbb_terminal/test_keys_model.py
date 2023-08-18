import os
from pathlib import Path
from typing import List

import pandas as pd
import pytest

from openbb_terminal import keys_model

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
def mock(mocker):
    mocker.patch(
        target="openbb_terminal.keys_model.set_credential",
    )
    mocker.patch(
        target="openbb_terminal.keys_model.write_to_dotenv",
    )


def test_get_keys():
    df = keys_model.get_keys()
    assert isinstance(df, pd.DataFrame)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key"],
            False,
            True,
        ),
        (
            ["test_key"],
            False,
            False,
        ),
    ],
)
def test_set_av_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_av_key")
    keys_model.set_av_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key"],
            False,
            True,
        ),
        (
            ["test_key"],
            False,
            False,
        ),
    ],
)
def test_set_fmp_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_fmp_key")
    keys_model.set_fmp_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key"],
            False,
            True,
        ),
        (
            ["test_key"],
            False,
            False,
        ),
    ],
)
def test_set_quandl_key(
    args: List[str],
    persist: bool,
    show_output: bool,
    mocker,
):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_quandl_key")
    keys_model.set_quandl_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key"],
            False,
            True,
        ),
        (
            ["test_key"],
            False,
            False,
        ),
    ],
)
def test_set_polygon_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_polygon_key")
    keys_model.set_polygon_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key"],
            False,
            True,
        ),
        (
            ["test_key"],
            False,
            False,
        ),
    ],
)
def test_set_fred_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_fred_key")
    keys_model.set_fred_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key"],
            False,
            True,
        ),
        (
            ["test_key"],
            False,
            False,
        ),
    ],
)
def test_set_news_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_news_key")
    keys_model.set_news_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key"],
            False,
            True,
        ),
        (
            ["test_key"],
            False,
            False,
        ),
    ],
)
def test_set_biztoc_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_biztoc_key")
    keys_model.set_biztoc_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key"],
            False,
            True,
        ),
        (
            ["test_key"],
            False,
            False,
        ),
    ],
)
def test_set_tradier_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_tradier_key")
    keys_model.set_tradier_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key"],
            False,
            True,
        ),
        (
            ["test_key"],
            False,
            False,
        ),
    ],
)
def test_set_cmc_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_cmc_key")
    keys_model.set_cmc_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key"],
            False,
            True,
        ),
        (
            ["test_key"],
            False,
            False,
        ),
    ],
)
def test_set_finnhub_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_finnhub_key")
    keys_model.set_finnhub_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_id", "test_secret", "test_pass", "test_user", "test_agent"],
            False,
            True,
        ),
        (
            ["test_id", "test_secret", "test_pass", "test_user", "test_agent"],
            False,
            False,
        ),
        (
            ["test_id", "test_secret", "test_pass", "test_user", "test_agent"],
            True,
            True,
        ),
        (
            ["REPLACE_ME", "REPLACE_ME", "REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
            False,
            True,
        ),
    ],
)
def test_set_reddit_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_reddit_key")
    keys_model.set_reddit_key(
        client_id=args[0],
        client_secret=args[1],
        password=args[2],
        username=args[3],
        useragent=args[4],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key"],
            False,
            True,
        ),
        (
            ["test_key"],
            False,
            False,
        ),
    ],
)
def test_set_bitquery_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_bitquery_key")
    keys_model.set_bitquery_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_username", "test_password"],
            False,
            True,
        ),
        (
            ["test_username", "test_password"],
            False,
            False,
        ),
    ],
)
def test_set_rh_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_rh_key")
    keys_model.set_rh_key(
        username=args[0],
        password=args[1],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_username", "test_password", "test_secret"],
            False,
            True,
        ),
        (
            ["test_username", "test_password", "test_secret"],
            False,
            False,
        ),
    ],
)
def test_set_degiro_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_degiro_key")
    keys_model.set_degiro_key(
        username=args[0],
        password=args[1],
        secret=args[2],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_account", "test_access_token", "account_type"],
            False,
            True,
        ),
        (
            ["test_account", "test_access_token", "account_type"],
            False,
            False,
        ),
    ],
)
def test_set_oanda_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_oanda_key")
    keys_model.set_oanda_key(
        account=args[0],
        access_token=args[1],
        account_type=args[2],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key", "test_secret"],
            False,
            True,
        ),
        (
            ["test_key", "test_secret"],
            False,
            False,
        ),
    ],
)
def test_set_binance_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_binance_key")
    keys_model.set_binance_key(
        key=args[0],
        secret=args[1],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key", "test_secret", "test_passphrase"],
            False,
            True,
        ),
        (
            ["test_key", "test_secret", "test_passphrase"],
            False,
            False,
        ),
    ],
)
def test_set_coinbase_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_coinbase_key")
    keys_model.set_coinbase_key(
        key=args[0],
        secret=args[1],
        passphrase=args[2],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key"],
            False,
            True,
        ),
        (
            ["test_key"],
            False,
            False,
        ),
    ],
)
def test_set_walert_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_walert_key")
    keys_model.set_walert_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key"],
            False,
            True,
        ),
        (
            ["test_key"],
            False,
            False,
        ),
    ],
)
def test_set_glassnode_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_glassnode_key")
    keys_model.set_glassnode_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key"],
            False,
            True,
        ),
        (
            ["test_key"],
            False,
            False,
        ),
    ],
)
def test_set_coinglass_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_coinglass_key")
    keys_model.set_coinglass_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key"],
            False,
            True,
        ),
        (
            ["test_key"],
            False,
            False,
        ),
    ],
)
def test_set_cpanic_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_cpanic_key")
    keys_model.set_cpanic_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key"],
            False,
            True,
        ),
        (
            ["test_key"],
            False,
            False,
        ),
    ],
)
def test_set_ethplorer_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_ethplorer_key")
    keys_model.set_ethplorer_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key", "test_access_token"],
            False,
            True,
        ),
        (
            ["test_key", "test_access_token"],
            False,
            False,
        ),
    ],
)
def test_set_smartstake_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_smartstake_key")
    keys_model.set_smartstake_key(
        key=args[0],
        access_token=args[1],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key"],
            False,
            True,
        ),
        (
            ["test_key"],
            False,
            False,
        ),
    ],
)
def test_set_github_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_github_key")
    keys_model.set_github_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key"],
            False,
            True,
        ),
        (
            ["test_key"],
            False,
            False,
        ),
    ],
)
def test_set_messari_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_messari_key")
    keys_model.set_messari_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key"],
            False,
            True,
        ),
        (
            ["test_key"],
            False,
            False,
        ),
    ],
)
def test_set_eodhd_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_eodhd_key")
    keys_model.set_eodhd_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key"],
            False,
            True,
        ),
        (
            ["test_key"],
            False,
            False,
        ),
    ],
)
def test_set_santiment_key(args: List[str], persist: bool, show_output: bool, mocker):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_santiment_key")
    keys_model.set_santiment_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "args, persist, show_output",
    [
        (
            ["test_key"],
            False,
            True,
        ),
        (
            ["test_key"],
            False,
            False,
        ),
    ],
)
def test_set_tokenterminal_key(
    args: List[str], persist: bool, show_output: bool, mocker
):
    mock_check = mocker.patch("openbb_terminal.keys_model.check_tokenterminal_key")
    keys_model.set_tokenterminal_key(
        key=args[0],
        persist=persist,
        show_output=show_output,
    )
    mock_check.assert_called_once_with(show_output)
