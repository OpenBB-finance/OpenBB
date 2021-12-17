# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.government import quiverquant_view

pytest.skip(allow_module_level=True)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("Authorization", "MOCK_TOKEN")],
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "use_tab",
    [True, False],
)
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
            dict(ticker="AMRC", gov_type="congress"),
        ),
        (
            "display_contracts",
            dict(ticker="AMRC", past_transaction_days=2, raw=True),
        ),
        (
            "display_qtr_contracts",
            dict(analysis="upmom", num=2),
        ),
        (
            "display_qtr_contracts",
            dict(analysis="total", num=2),
        ),
        (
            "display_hist_contracts",
            dict(ticker="SSTK"),
        ),
        (
            "display_top_lobbying",
            dict(num=2, raw=True),
        ),
        (
            "display_lobbying",
            dict(ticker="HBI"),
        ),
    ],
)
def test_call_func(func, kwargs_dict, mocker, use_tab):
    mocker.patch(target="matplotlib.pyplot.show", new=mocker.Mock())
    mocker.patch.object(target=quiverquant_view.gtff, attribute="USE_ION", new=False)
    mocker.patch.object(
        target=quiverquant_view.gtff, attribute="USE_TABULATE_DF", new=use_tab
    )
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
            dict(ticker="MOCK_TEXT", gov_type="MOCK_TEXT"),
        ),
        (
            "display_contracts",
            dict(ticker="MOCK_TEXT", past_transaction_days=2, raw=True),
        ),
        (
            "display_qtr_contracts",
            dict(analysis="MOCK_TEXT", num=2),
        ),
        (
            "display_hist_contracts",
            dict(ticker="MOCK_TEXT"),
        ),
        (
            "display_top_lobbying",
            dict(num=2, raw=True),
        ),
        (
            "display_lobbying",
            dict(ticker="MOCK_TEXT", num=2),
        ),
    ],
)
def test_call_func_empty_df(func, kwargs_dict, mocker):
    model_path = "gamestonk_terminal.stocks.government.quiverquant_model."
    mocker.patch(
        target=model_path + "get_government_trading",
        return_value=pd.DataFrame(),
    )
    mocker.patch(
        target=model_path + "analyze_qtr_contracts",
        return_value=pd.DataFrame(),
    )
    getattr(quiverquant_view, func)(**kwargs_dict)
