# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import datetime
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
    "countries, importances, categories, from_date, to_date",
    [
        [
            ["united states"],
            ["high"],
            ["Employment"],
            datetime.date(2022, 7, 7),
            datetime.date(2022, 7, 8),
        ],
    ],
)
def test_get_economic_calendar(countries, importances, categories, from_date, to_date):
    result_df, _ = investingcom_model.get_economic_calendar(
        countries, importances, categories, from_date, to_date
    )

    assert isinstance(result_df, pd.DataFrame)
