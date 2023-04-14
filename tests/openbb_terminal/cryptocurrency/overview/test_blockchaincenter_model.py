import pytest
from pandas import DataFrame

from openbb_terminal.cryptocurrency.overview import blockchaincenter_model


@pytest.mark.record_http
@pytest.mark.parametrize(
    "period, start_date, end_date",
    [
        (30, "2021-01-01", "2021-01-10"),
    ],
)
def test_get_altcoin_index(period, start_date, end_date):
    df = blockchaincenter_model.get_altcoin_index(
        period=period, start_date=start_date, end_date=end_date
    )

    assert isinstance(df, DataFrame)
