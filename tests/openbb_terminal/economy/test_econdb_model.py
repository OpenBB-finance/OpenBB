# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.economy import econdb_model


@pytest.mark.vcr
@pytest.mark.parametrize(
    "parameter, country, start_date, end_date, convert_currency",
    [
        ["RGDP", "United States", "2005-05-05", "2006-01-01", False],
        ["EMP", "Germany", "2020-01-01", "2020-10-10", False],
        ["GDP", "France", "2015-01-01", "2020-10-10", False],
    ],
)
def test_get_macro_data(parameter, country, start_date, end_date, convert_currency):
    result_df, units = econdb_model.get_macro_data(
        parameter, country, start_date, end_date, convert_currency
    )

    assert isinstance(result_df, pd.Series)
    assert isinstance(units, str)
    assert not result_df.empty


@pytest.mark.vcr
@pytest.mark.parametrize(
    "parameters, countries, start_date, end_date, convert_currency",
    [
        [["RGDP"], ["United States", "Germany"], "2020-01-01", "2020-10-10", False],
        [["EMP", "PPI"], ["France"], "2018-01-01", "2019-01-01", False],
        [["RGDP", "GDP"], ["Italy", "Netherlands"], "2010-01-01", "2010-10-08", False],
    ],
)
def test_get_aggregated_macro_data(
    parameters, countries, start_date, end_date, convert_currency
):
    result_df, units = econdb_model.get_aggregated_macro_data(
        parameters, countries, start_date, end_date, convert_currency
    )

    assert isinstance(result_df, pd.DataFrame)
    assert isinstance(units, dict)
    assert not result_df.empty


@pytest.mark.vcr
@pytest.mark.parametrize(
    "instruments, maturities, frequency, start_date, end_date",
    [
        [["nominal", "inflation"], ["3y", "5y"], "monthly", "2020-01-01", "2020-04-05"],
        [["nominal"], ["1m", "30y"], "annually", "2015-01-04", "2015-01-28"],
        [["average", "inflation"], ["3y", "5y"], "weekly", "2018-06-05", "2018-07-06"],
    ],
)
def test_get_treasuries(
    recorder, instruments, maturities, frequency, start_date, end_date
):
    result_df = econdb_model.get_treasuries(
        instruments, maturities, frequency, start_date, end_date
    )

    recorder.capture(pd.DataFrame(result_df))


@pytest.mark.vcr
def test_obtain_treasury_maturities(recorder):
    result_df = econdb_model.obtain_treasury_maturities(econdb_model.TREASURIES)

    recorder.capture(result_df)
