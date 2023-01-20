# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options import tradier_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("Authorization", "MOCK_TOKEN")],
    }


@pytest.mark.vcr(record_mode="none")
def test_check_valid_option_chains_headers(recorder):
    result = tradier_view.check_valid_option_chains_headers(headers="gamma,delta")
    recorder.capture(result)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_historical(mocker):
    # MOCK CHARTS
    mocker.patch(
        target="openbb_terminal.stocks.options.tradier_view.theme.visualize_output"
    )

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.stocks.options.tradier_view.export_data")

    # MOCK USE_COLOR
    mocker.patch.object(
        target=tradier_view.rich_config, attribute="USE_COLOR", new=True
    )

    tradier_view.display_historical(
        symbol="AAPL",
        expiry="2025-01-17",
        strike=180.0,
        put=True,
        export="csv",
        raw=True,
        chain_id="",
    )
