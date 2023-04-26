import pytest

from openbb_terminal.cryptocurrency.overview import withdrawalfees_view


@pytest.mark.record_http
@pytest.mark.record_verify_screen
def test_display_overall_withdrawal_fees():
    withdrawalfees_view.display_overall_withdrawal_fees(limit=5)


@pytest.mark.record_http
@pytest.mark.record_verify_screen
def test_display_overall_exchange_withdrawal_fees():
    withdrawalfees_view.display_overall_exchange_withdrawal_fees()


@pytest.mark.record_http
@pytest.mark.record_verify_screen
def test_display_crypto_withdrawal_fees():
    withdrawalfees_view.display_crypto_withdrawal_fees(symbol="BTC")
