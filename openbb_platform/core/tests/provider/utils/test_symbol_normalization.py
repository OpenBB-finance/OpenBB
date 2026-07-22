"""Tests for provider-aware symbol normalization."""

import pytest
from openbb_core.provider.utils.symbol_normalization import normalize_symbol_map


@pytest.mark.parametrize(
    ("symbol", "polygon_symbol", "suffix"),
    [
        ("ricoauto.ns", "XNSE:RICOAUTO", ".NS"),
        ("vod.l", "XLON:VOD", ".L"),
        ("shop.to", "XTSE:SHOP", ".TO"),
    ],
)
def test_normalize_international_equity_suffixes(symbol, polygon_symbol, suffix):
    """Normalize exchange suffixes consistently across providers."""
    result = normalize_symbol_map(symbol)

    assert result.asset_type == "equity"
    assert result.exchange_suffix == suffix
    assert result.fmp == symbol.upper()
    assert result.yfinance == symbol.upper()
    assert result.polygon == polygon_symbol


def test_normalize_otc_symbol():
    """Map OTC inputs to provider-specific conventions."""
    result = normalize_symbol_map("otc:abvc")

    assert result.asset_type == "equity"
    assert result.normalized == "ABVC.OTC"
    assert result.fmp == "ABVC"
    assert result.yfinance == "ABVC"
    assert result.polygon == "OTC:ABVC"


def test_normalize_crypto_pair():
    """Map crypto pairs to each provider's symbol format."""
    result = normalize_symbol_map("eth/usd")

    assert result.asset_type == "crypto"
    assert result.normalized == "ETH/USD"
    assert result.fmp == "ETHUSD"
    assert result.yfinance == "ETH-USD"
    assert result.polygon == "X:ETHUSD"


def test_normalize_share_class_symbol():
    """Keep class shares canonical and convert only for Yahoo format."""
    result = normalize_symbol_map("brk.b")

    assert result.asset_type == "equity"
    assert result.normalized == "BRK.B"
    assert result.fmp == "BRK.B"
    assert result.polygon == "BRK.B"
    assert result.yfinance == "BRK-B"


def test_normalize_symbol_raises_on_empty_value():
    """Reject empty symbols."""
    with pytest.raises(ValueError):
        normalize_symbol_map("   ")
