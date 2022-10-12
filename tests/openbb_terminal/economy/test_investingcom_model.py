# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
from typing import List, Union
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.economy import investingcom_model


@pytest.mark.vcr
@pytest.mark.parametrize(
    "country",
    [
        "united states",
        "portugal",
        "spain",
        "germany",
    ],
)
def test_get_yieldcurve(country):
    result_df = investingcom_model.get_yieldcurve(country)

    assert isinstance(result_df, pd.DataFrame)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "country, importance, category, start_date, end_date",
    [
        [
            "united states",
            "high",
            "Employment",
            "2022-7-7",
            "2022-7-8",
        ],
    ],
)
def test_get_economic_calendar(country, importance, category, start_date, end_date):
    result_df, _ = investingcom_model.get_economic_calendar(
        country, importance, category, start_date, end_date
    )

    assert isinstance(result_df, pd.DataFrame)


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "countries, maturity, change, color",
    [
        (
            "G7",
            "10Y",
            False,
            "rgb",
            False,
        ),
        (
            ["Portugal", "Spain"],
            "5Y",
            True,
            "rgb",
            False,
        ),
        (
            "PIIGS",
            "10Y",
            False,
            "binary",
            True,
        ),
        (
            "PIIGS",
            "10Y",
            False,
            "openbb",
            False,
        ),
    ],
)
def test_display_spread_matrix(
    countries: Union[str, List[str]] = "G7",
    maturity: str = "10Y",
    change: bool = False,
    color: str = "rgb",
    raw: bool = False,
):
    df = investingcom_model.get_spread_matrix(
        countries=countries, maturity=maturity, change=change, color=color, raw=raw
    )

    assert isinstance(df, pd.DataFrame)
