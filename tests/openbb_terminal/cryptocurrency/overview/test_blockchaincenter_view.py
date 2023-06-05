import pytest

from openbb_terminal.cryptocurrency.overview import blockchaincenter_view


@pytest.mark.record_http
@pytest.mark.parametrize(
    "period, start_date, end_date",
    [
        (30, "2021-01-01", "2021-01-10"),
    ],
)
def test_display_altcoin_index(period, start_date, end_date):
    blockchaincenter_view.display_altcoin_index(period, start_date, end_date)
