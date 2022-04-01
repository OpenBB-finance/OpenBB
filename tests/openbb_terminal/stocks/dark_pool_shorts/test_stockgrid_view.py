# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.dark_pool_shorts import stockgrid_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_dark_pool_short_positions():
    stockgrid_view.dark_pool_short_positions(
        num=2,
        sort_field="sv_pct",
        ascending=True,
        export="",
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_short_interest_days_to_cover():
    stockgrid_view.short_interest_days_to_cover(
        num=2,
        sort_field="dtc",
        export="",
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "raw",
    [True, False],
)
def test_short_interest_volume(mocker, raw):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    stockgrid_view.short_interest_volume(
        ticker="PM",
        num=2,
        raw=raw,
        export="",
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "raw",
    [True, False],
)
def test_net_short_position(mocker, raw):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    stockgrid_view.net_short_position(
        ticker="PM",
        num=2,
        raw=raw,
        export="",
    )
