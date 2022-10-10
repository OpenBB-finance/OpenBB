import pytest

from openbb_terminal.cryptocurrency.onchain import shroom_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("x-api-key", "MOCK_AUTHORIZATION"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_daily_transactions():
    shroom_view.display_daily_transactions()


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_dapp_stats():
    shroom_view.display_dapp_stats(platform="uniswap-v3")


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_total_value_locked():
    shroom_view.display_total_value_locked(
        user_address="0x0000000000000000000000000000000000000000", address_name=""
    )
