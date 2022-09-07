# IMPORTATION STANDARD
import pandas as pd
import numpy as np

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.sector_industry_analysis import stockanalysis_model


@pytest.mark.vcr
@pytest.mark.parametrize(
    "symbols, finance_key, period, statement",
    [
        (["AAPL"], "re", "annual", "IS"),
        (["AAPL"], "rec", "quarterly", "BS"),
        (
            ["FB", "TSLA", "MSFT"],
            "ncf",
            "annual",
            "CF",
        ),
        (
            ["FB", "TSLA", "MSFT"],
            "ni",
            "quarterly",
            "IS",
        ),
        (
            ["FB", "TSLA", "MSFT"],
            "tle",
            "trailing",
            "BS",
        ),
    ],
)
def test_get_stocks_data(recorder, symbols, finance_key, period, statement):
    result = stockanalysis_model.get_stocks_data(
        symbols=symbols,
        finance_key=finance_key,
        stocks_data=dict(),
        period=period,
    )

    recorder.capture_list(result[statement].values())


@pytest.mark.vcr
def test_match_length_dataframes(recorder):
    result = stockanalysis_model.match_length_dataframes(
        dataframes={
            "TSLA": pd.DataFrame(
                np.nan, index=["Item 1", "Item 2"], columns=["2010", "2011", "2012"]
            ),
            "AAPL": pd.DataFrame(np.nan, index=["Item 1", "Item 2"], columns=["2011"]),
        }
    )

    recorder.capture_list(result.values())


@pytest.mark.vcr
def test_change_type_dataframes(recorder):
    result = stockanalysis_model.change_type_dataframes(
        data=pd.DataFrame(
            [["1,0", "1.0", "1,0"], ["2,0", "2,000", 2]],
            index=["Item 1", "Item 2"],
            columns=["2010", "2011", "2012"],
        )
    )

    recorder.capture(result)
