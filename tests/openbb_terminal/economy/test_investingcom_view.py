# IMPORTATION STANDARD
# import gzip

# IMPORTATION THIRDPARTY
# import pandas as pd

from typing import List, Union
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.economy import investingcom_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_yieldcurve():
    investingcom_view.display_yieldcurve(country="portugal", export="")


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_economic_calendar():
    investingcom_view.display_economic_calendar(
        country="united states",
        importance="high",
        category="Employment",
        start_date="2022-7-7",
        end_date="2022-7-8",
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "countries, maturity, change, color, raw",
    [
        (
            "EZ",
            "10Y",
            False,
            "rgb",
            True,
        ),
        (
            ["Portugal", "Spain"],
            "5Y",
            True,
            "rgb",
            True,
        ),
        (
            "PIIGS",
            "10Y",
            False,
            "binary",
            True,
        ),
        (
            "AMERICAS",
            "10Y",
            False,
            "openbb",
            True,
        ),
        (
            "G7",
            "20Y",
            True,
            "openbb",
            True,
        ),
    ],
)
def test_display_spread_matrix(
    countries: Union[str, List[str]],
    maturity: str,
    change: bool,
    color: str,
    raw: bool,
):
    investingcom_view.display_spread_matrix(
        countries=countries, maturity=maturity, change=change, color=color, raw=raw
    )
