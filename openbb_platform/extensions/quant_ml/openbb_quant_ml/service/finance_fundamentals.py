import json
import logging
import os
import re
import urllib.request
from typing import Any

from openbb import obb

LOGGER = logging.getLogger(__name__)


def _extract_timestamp(result: Any) -> Any:
    extra = getattr(result, "extra", None)
    metadata = getattr(extra, "metadata", None)
    if isinstance(metadata, dict):
        return metadata.get("timestamp")
    return None


def _build_payload(result: Any, provider: str) -> dict[str, Any]:
    rows = [r.model_dump() for r in (result.results or [])]
    return {
        "results": rows,
        "provider": getattr(result, "provider", provider),
        "extra": {"metadata": {"timestamp": _extract_timestamp(result)}},
    }


def _forecast_rows_are_usable(rows: list[dict[str, Any]]) -> bool:
    signal_keys = (
        "target_high",
        "target_low",
        "target_consensus",
        "target_median",
        "recommendation_mean",
        "recommendation",
        "consensus_action",
        "current_price",
    )
    analyst_keys = (
        "number_of_analysts",
        "total_analysts",
        "buy_ratings",
        "hold_ratings",
        "sell_ratings",
    )
    for row in rows:
        if any(row.get(key) not in (None, "", 0) for key in signal_keys):
            return True
        if any((row.get(key) or 0) > 0 for key in analyst_keys):
            return True
    return False

def get_api_keys() -> dict[str, str]:
    """Read API keys from OpenBB user settings."""
    settings_path = os.path.expanduser("~/.openbb_platform/user_settings.json")
    try:
        if os.path.exists(settings_path):
            with open(settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("credentials", {})
    except Exception as exc:
        LOGGER.warning("Failed to read user_settings.json: %s", exc)
    return {}

def camel_to_snake(name: str) -> str:
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

def _fetch_av_statement(kind: str, symbol: str, apikey: str, limit: int = 4) -> dict[str, Any] | None:
    fn_map = {
        "income": "INCOME_STATEMENT",
        "balance": "BALANCE_SHEET",
        "cash": "CASH_FLOW"
    }
    if kind not in fn_map:
        return None
        
    url = f"https://www.alphavantage.co/query?function={fn_map[kind]}&symbol={symbol}&apikey={apikey}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            
        reports = data.get("annualReports", [])
        if not reports and "Information" in data:
            LOGGER.warning("AlphaVantage rate limit: %s", data)
            return None
            
        results = []
        for r in reports[:limit]:
            row = {"period_ending": r.get("fiscalDateEnding", "")}
            for k, v in r.items():
                if k in ("fiscalDateEnding", "reportedCurrency"):
                    continue
                try:
                    row[camel_to_snake(k)] = float(v) if v != "None" else None
                except ValueError:
                    row[camel_to_snake(k)] = v
            results.append(row)
            
        return {
            "results": results,
            "provider": "alphavantage",
            "extra": {"metadata": {"timestamp": None}}
        }
    except Exception as exc:
        LOGGER.exception("AlphaVantage fallback failed: %s", exc)
        return None

def get_statement(
    kind: str,
    symbol: str,
    period: str = "annual",
    limit: int = 4
) -> dict[str, Any]:
    """Fetch income, balance, or cash flow statements via FMP, fallback to AlphaVantage."""
    symbol = symbol.upper().strip()
    try:
        # FMP is more reliable but requires premium for some tickers
        res = obb.equity.fundamental.income(symbol, provider="fmp", period=period, limit=limit) if kind == "income" else \
              obb.equity.fundamental.balance(symbol, provider="fmp", period=period, limit=limit) if kind == "balance" else \
              obb.equity.fundamental.cash(symbol, provider="fmp", period=period, limit=limit) if kind == "cash" else None
              
        if res is None:
            return {"detail": f"Unknown statement kind: {kind}"}
            
        rows = [r.model_dump() for r in (res.results or [])]
        return {
            "results": rows,
            "provider": getattr(res, "provider", "fmp"),
            "extra": {"metadata": {"timestamp": getattr(res.extra, "metadata", {}).get("timestamp") if hasattr(res, "extra") else None}}
        }
    except Exception as exc:  # noqa: BLE001
        err_msg = str(exc)
        LOGGER.warning("FMP fetch failed for %s %s: %s", kind, symbol, err_msg)
        
        # Fallback to Alpha Vantage
        keys = get_api_keys()
        av_key = keys.get("alpha_vantage_api_key")
        if av_key and period == "annual":
            av_res = _fetch_av_statement(kind, symbol, av_key, limit)
            if av_res and av_res["results"]:
                return av_res

        detail = "Provider requires a premium subscription for this symbol." if "402" in err_msg or "Premium" in err_msg else err_msg
        return {"detail": detail}

def get_forecast(symbol: str) -> dict[str, Any]:
    """Fetch analyst consensus and price targets via obb SDK."""
    symbol = symbol.upper().strip()
    first_error: str | None = None
    provider_attempts = ("fmp", "yfinance", "tmx")

    for provider in provider_attempts:
        try:
            if provider == "yfinance":
                from openbb_quant_ml.service.data_loader import _ensure_ssl_bundle_path  # noqa: PLC0415

                _ensure_ssl_bundle_path()

            res = obb.equity.estimates.consensus(symbol, provider=provider)
            payload = _build_payload(res, provider)
            if _forecast_rows_are_usable(payload["results"]):
                return payload

            LOGGER.warning(
                "Forecast fallback %s returned no usable targets for %s.",
                provider,
                symbol,
            )
        except Exception as exc:  # noqa: BLE001
            err_msg = str(exc)
            LOGGER.warning("Forecast provider %s failed for %s: %s", provider, symbol, err_msg)
            if first_error is None:
                first_error = err_msg

    detail = (
        "Forecast data is not available from the configured providers for this symbol."
        if first_error is None
        else "Forecast data is not available on your current provider tier."
        if "402" in first_error or "Premium" in first_error
        else first_error
    )
    return {"detail": detail}
