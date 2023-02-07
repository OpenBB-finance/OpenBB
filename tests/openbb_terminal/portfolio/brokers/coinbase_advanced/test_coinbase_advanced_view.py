import pytest

import openbb_terminal.portfolio.brokers.coinbase_advanced.coinbase_advanced_view as cbv


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            ("CB-ACCESS-SIGN", "MOCK-CB-ACCESS-SIGN"),
            ("CB-ACCESS-TIMESTAMP", "MOCK-CB-ACCESS-TIMESTAMP"),
            ("CB-ACCESS-KEY", "MOCK-CB-ACCESS-KEY"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_accounts():
    cbv.display_account()


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_orders():
    cbv.display_orders()


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_create_order():
    cbv.display_create_order()


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_cancel_order():
    cbv.display_cancel_order()
