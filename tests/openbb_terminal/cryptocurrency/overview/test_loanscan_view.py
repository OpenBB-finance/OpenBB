import pytest

from openbb_terminal.cryptocurrency.overview import loanscan_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            ("User-Agent", None),
        ],
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_crypto_rates(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(
        target="openbb_terminal.cryptocurrency.overview.loanscan_view.export_data"
    )

    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    loanscan_view.display_crypto_rates(
        cryptos="BTC,ETH,USDT,USDC",
        platforms="BlockFi,Ledn,SwissBorg,Youhodler",
        rate_type="supply",
    )
