# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.dark_pool_shorts import stockgrid_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_dark_pool_short_positions():
    stockgrid_view.dark_pool_short_positions(
        limit=2,
        sortby="sv_pct",
        ascend=True,
        export="",
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_short_interest_days_to_cover():
    stockgrid_view.short_interest_days_to_cover(
        limit=2,
        sortby="dtc",
        export="",
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "raw",
    [True, False],
)
def test_short_interest_volume(raw):
    stockgrid_view.short_interest_volume(
        symbol="PM",
        limit=2,
        raw=raw,
        export="",
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "raw",
    [True, False],
)
def test_net_short_position(raw):
    stockgrid_view.net_short_position(
        symbol="PM",
        limit=2,
        raw=raw,
        export="",
    )
