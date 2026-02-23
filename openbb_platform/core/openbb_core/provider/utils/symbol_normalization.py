"""Provider-aware symbol normalization helpers."""

from dataclasses import dataclass
from typing import Literal

_CRYPTO_QUOTES: tuple[str, ...] = (
    "USDT",
    "USDC",
    "USD",
    "EUR",
    "GBP",
    "JPY",
    "BTC",
    "ETH",
)
_INTERNATIONAL_SUFFIX_TO_POLYGON_MIC = {
    ".NS": "XNSE",
    ".L": "XLON",
    ".TO": "XTSE",
}


@dataclass(frozen=True)
class SymbolMap:
    """Normalized symbols for different provider conventions."""

    original: str
    normalized: str
    fmp: str
    polygon: str
    yfinance: str
    asset_type: Literal["equity", "crypto"]
    exchange_suffix: str | None = None


def _parse_crypto_pair(symbol: str) -> tuple[str, str] | None:
    candidate = symbol.replace("X:", "")

    for separator in ("/", "-", "_"):
        if separator not in candidate:
            continue

        base, quote = candidate.split(separator, 1)
        if base and quote in _CRYPTO_QUOTES:
            return base, quote

    for quote in _CRYPTO_QUOTES:
        if candidate.endswith(quote) and len(candidate) > len(quote):
            return candidate[: -len(quote)], quote

    return None


def _is_equity_share_class(symbol: str) -> bool:
    if symbol.count(".") != 1:
        return False

    ticker, share_class = symbol.split(".", 1)
    return bool(ticker) and len(share_class) == 1 and share_class.isalpha()


def normalize_symbol_map(symbol: str) -> SymbolMap:
    """Normalize ticker inputs across FMP, Polygon, and Yahoo Finance."""
    normalized_input = symbol.strip().upper()

    if not normalized_input:
        raise ValueError("symbol cannot be empty")

    parsed_crypto_pair = _parse_crypto_pair(normalized_input)
    if parsed_crypto_pair:
        base, quote = parsed_crypto_pair
        canonical = f"{base}/{quote}"
        compact = f"{base}{quote}"

        return SymbolMap(
            original=symbol,
            normalized=canonical,
            fmp=compact,
            polygon=f"X:{compact}",
            yfinance=f"{base}-{quote}",
            asset_type="crypto",
        )

    if normalized_input.startswith("OTC:"):
        ticker = normalized_input.split(":", 1)[1]
        if not ticker:
            raise ValueError("invalid OTC symbol")
        canonical = f"{ticker}.OTC"
        return SymbolMap(
            original=symbol,
            normalized=canonical,
            fmp=ticker,
            polygon=f"OTC:{ticker}",
            yfinance=ticker,
            asset_type="equity",
            exchange_suffix=".OTC",
        )

    if normalized_input.endswith(".OTC"):
        ticker = normalized_input[:-4]
        if not ticker:
            raise ValueError("invalid OTC symbol")
        return SymbolMap(
            original=symbol,
            normalized=f"{ticker}.OTC",
            fmp=ticker,
            polygon=f"OTC:{ticker}",
            yfinance=ticker,
            asset_type="equity",
            exchange_suffix=".OTC",
        )

    for suffix, polygon_mic in _INTERNATIONAL_SUFFIX_TO_POLYGON_MIC.items():
        if normalized_input.endswith(suffix):
            ticker = normalized_input[: -len(suffix)]
            if not ticker:
                raise ValueError("invalid international symbol")
            return SymbolMap(
                original=symbol,
                normalized=f"{ticker}{suffix}",
                fmp=f"{ticker}{suffix}",
                polygon=f"{polygon_mic}:{ticker}",
                yfinance=f"{ticker}{suffix}",
                asset_type="equity",
                exchange_suffix=suffix,
            )

    canonical_equity = normalized_input

    # Convert Yahoo class-share notation to a provider-agnostic canonical form.
    if "-" in normalized_input and "." not in normalized_input:
        ticker, share_class = normalized_input.split("-", 1)
        if ticker and len(share_class) == 1 and share_class.isalpha():
            canonical_equity = f"{ticker}.{share_class}"

    yfinance_symbol = (
        canonical_equity.replace(".", "-")
        if _is_equity_share_class(canonical_equity)
        else canonical_equity
    )

    return SymbolMap(
        original=symbol,
        normalized=canonical_equity,
        fmp=canonical_equity,
        polygon=canonical_equity,
        yfinance=yfinance_symbol,
        asset_type="equity",
    )
