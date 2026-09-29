"""Unit tests for ``openbb_sec.models.insider_trading``."""

from openbb_sec.models.insider_trading import (
    SecInsiderTradingData,
    SecInsiderTradingFetcher,
)


def test_insider_trading_transform_query_default_dates():
    """insider_trading.py:189-190 -> default date range injected when absent."""
    query = SecInsiderTradingFetcher.transform_query({"symbol": "AAPL"})
    assert query.start_date is not None
    assert query.end_date is not None
    assert query.start_date < query.end_date


def test_insider_trading_validator_ownership_type_none():
    """insider_trading.py:146 -> ownership_type validator returns None on empty."""
    data = SecInsiderTradingData.model_validate(
        {"symbol": "aapl", "ownership_type": ""}
    )
    assert data.ownership_type is None
    # _to_upper validator also exercised: symbol upcased.
    assert data.symbol == "AAPL"


def test_insider_trading_validator_acq_disp_and_timeliness():
    """insider_trading.py:154 & 171 -> acquisition/disposition + timeliness maps."""
    data = SecInsiderTradingData.model_validate(
        {
            "symbol": "MSFT",
            "acquisition_or_disposition": "",
            "transaction_timeliness": "E",
            "ownership_type": "D",
        }
    )
    # acquisition_or_disposition empty -> None (line 154 branch).
    assert data.acquisition_or_disposition is None
    # transaction_timeliness "E" -> "Early" (line 171 mapped value).
    assert data.transaction_timeliness == "Early"
    # ownership_type "D" -> "Direct".
    assert data.ownership_type == "Direct"
