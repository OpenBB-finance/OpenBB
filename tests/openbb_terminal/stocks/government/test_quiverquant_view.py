# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.government import quiverquant_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("Authorization", "MOCK_TOKEN")],
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func, kwargs_dict",
    [
        (
            "display_last_government",
            dict(gov_type="congress"),
        ),
        (
            "display_government_buys",
            dict(gov_type="congress"),
        ),
        (
            "display_government_sells",
            dict(gov_type="congress"),
        ),
        (
            "display_last_contracts",
            dict(),
        ),
        (
            "display_government_trading",
            dict(symbol="AMRC", gov_type="congress"),
        ),
        (
            "display_contracts",
            dict(symbol="AMRC", past_transaction_days=2, raw=True),
        ),
        (
            "display_qtr_contracts",
            dict(analysis="upmom", limit=2),
        ),
        (
            "display_qtr_contracts",
            dict(analysis="total", limit=2),
        ),
        (
            "display_hist_contracts",
            dict(symbol="SSTK"),
        ),
        (
            "display_top_lobbying",
            dict(limit=2, raw=True),
        ),
        (
            "display_lobbying",
            dict(symbol="HBI"),
        ),
    ],
)
def test_call_func(func, kwargs_dict):
    getattr(quiverquant_view, func)(**kwargs_dict)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func, kwargs_dict",
    [
        (
            "display_last_government",
            dict(gov_type="MOCK_TEXT"),
        ),
        (
            "display_government_buys",
            dict(gov_type="MOCK_TEXT"),
        ),
        (
            "display_government_sells",
            dict(gov_type="MOCK_TEXT"),
        ),
        (
            "display_last_contracts",
            dict(),
        ),
        (
            "display_government_trading",
            dict(symbol="MOCK_TEXT", gov_type="MOCK_TEXT"),
        ),
        (
            "display_contracts",
            dict(symbol="MOCK_TEXT", past_transaction_days=2, raw=True),
        ),
        (
            "display_qtr_contracts",
            dict(analysis="MOCK_TEXT", limit=2),
        ),
        (
            "display_hist_contracts",
            dict(symbol="MOCK_TEXT"),
        ),
        (
            "display_top_lobbying",
            dict(limit=2, raw=True),
        ),
        (
            "display_lobbying",
            dict(symbol="MOCK_TEXT", limit=2),
        ),
    ],
)
def test_call_func_empty_df(func, kwargs_dict, mocker):
    model_path = "openbb_terminal.stocks.government.quiverquant_model."
    mocker.patch(
        target=model_path + "get_government_trading",
        return_value=pd.DataFrame(),
    )
    mocker.patch(
        target=model_path + "get_qtr_contracts",
        return_value=pd.DataFrame(),
    )
    getattr(quiverquant_view, func)(**kwargs_dict)
