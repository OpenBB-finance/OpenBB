# IMPORTATION THIRDPARTY
import pytest

from openbb_terminal import rich_config

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options import tradier_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("Authorization", "MOCK_TOKEN")],
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_historical(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.stocks.options.tradier_view.export_data")

    # MOCK USE_COLOR
    mocker.patch.object(target=rich_config, attribute="USE_COLOR", new=True)

    tradier_view.display_historical(
        symbol="AAPL",
        expiry="2025-01-17",
        strike=180.0,
        put=True,
        export="csv",
        sheet_name=None,
        raw=True,
        chain_id="",
    )
