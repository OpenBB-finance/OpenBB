# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.economy import econdb_view


@pytest.mark.vcr
@pytest.mark.parametrize(
    "parameters, countries, transform, start_date, end_date, convert_currency, raw",
    [
        [
            ["RGDP"],
            ["United States", "Germany"],
            "",
            "2020-01-01",
            "2020-10-02",
            "",
            False,
        ],
        [["EMP", "PPI"], ["France"], "TOYA", "2010-01-01", "2019-01-01", "", False],
        [
            ["GDP", "RGDP"],
            ["Italy", "Netherlands"],
            "TPOP",
            "2016-01-01",
            "2016-10-10",
            "EUR",
            False,
        ],
        [
            ["GDP", "RGDP"],
            ["Italy", "Netherlands"],
            "TUSD",
            "2016-01-01",
            "2016-10-10",
            "USD",
            True,
        ],
    ],
)
def test_show_macro_data(
    parameters, countries, transform, start_date, end_date, convert_currency, raw
):
    econdb_view.show_macro_data(
        parameters, countries, transform, start_date, end_date, convert_currency, raw
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "instruments, maturities, frequency, start_date, end_date",
    [
        [["nominal", "inflation"], ["3y", "5y"], "monthly", "2020-01-01", "2020-02-03"],
        [["nominal"], ["1m", "30y"], "annually", "2015-01-04", "2015-01-28"],
        [["average", "inflation"], ["3y", "5y"], "weekly", "2018-06-05", "2018-07-06"],
    ],
)
def test_show_treasuries(instruments, maturities, frequency, start_date, end_date):
    econdb_view.show_treasuries(
        instruments, maturities, frequency, start_date, end_date
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_show_treasury_maturities():
    econdb_view.show_treasury_maturities()
