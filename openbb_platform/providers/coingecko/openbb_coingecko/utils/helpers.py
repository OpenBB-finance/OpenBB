"""CoinGecko helper functions."""

from datetime import date as dateType
from datetime import datetime, time, timezone
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError, UnauthorizedError

COINGECKO_BASE_URL = "https://pro-api.coingecko.com/api/v3"
INTERVAL_MAP = {"1h": "hourly", "1d": "daily"}
KNOWN_QUOTES = ("USDT", "USDC", "USD", "EUR", "GBP", "JPY", "BTC", "ETH")


def _to_milliseconds(timestamp: int | float) -> int:
    ts = int(timestamp)
    return ts * 1000 if ts < 1_000_000_000_000 else ts


def _to_unix_timestamp(value: dateType, end_of_day: bool = False) -> int:
    target_time = time.max if end_of_day else time.min
    target_datetime = datetime.combine(value, target_time, tzinfo=timezone.utc)
    return int(target_datetime.timestamp())


def _is_ohlcv_payload(payload: Any) -> bool:
    return (
        isinstance(payload, list)
        and bool(payload)
        and isinstance(payload[0], list)
        and len(payload[0]) >= 6
    )


def _is_ohlc_payload(payload: Any) -> bool:
    return (
        isinstance(payload, list)
        and bool(payload)
        and isinstance(payload[0], list)
        and len(payload[0]) >= 5
    )


def _requires_ohlc_fallback(error: OpenBBError) -> bool:
    message = str(error).lower()
    return (
        "404" in message
        or "not found" in message
        or "endpoint" in message
        or "unsupported" in message
    )


def split_crypto_symbol(symbol: str) -> tuple[str, str]:
    """Split a crypto pair string into `(base, quote)`."""
    candidate = symbol.strip().upper()

    if not candidate:
        raise ValueError("symbol cannot be empty")

    for separator in ("/", "-", "_"):
        if separator not in candidate:
            continue
        base, quote = candidate.split(separator, 1)
        if base and quote:
            return base, quote

    for quote in KNOWN_QUOTES:
        if candidate.endswith(quote) and len(candidate) > len(quote):
            return candidate[: -len(quote)], quote

    raise ValueError(
        "Unable to infer quote currency. Use formats like BTCUSD, BTC-USD, or BTC/USD."
    )


async def response_callback(response, _):
    """Handle CoinGecko responses."""
    if response.status in (401, 403):
        message = await response.text()
        raise UnauthorizedError(
            f"Unauthorized CoinGecko request -> {response.status} -> {message}",
            provider_name="CoinGecko",
        )

    if response.status >= 400:
        message = await response.text()
        raise OpenBBError(
            f"CoinGecko request failed -> {response.status} -> {message}"
        )

    payload = await response.json()

    if isinstance(payload, dict):
        if error_message := payload.get("error"):
            lowered = str(error_message).lower()
            if any(
                token in lowered
                for token in ("api key", "permission", "subscription", "quota")
            ):
                raise UnauthorizedError(
                    f"Unauthorized CoinGecko request -> {error_message}",
                    provider_name="CoinGecko",
                )
            raise OpenBBError(f"CoinGecko error -> {error_message}")

    if payload in (None, [], {}):
        raise EmptyDataError("No data returned from CoinGecko.")

    return payload


async def get_data(url: str, **kwargs: Any) -> list | dict:
    """Fetch data from CoinGecko."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import amake_request

    return await amake_request(url, response_callback=response_callback, **kwargs)


def _api_headers(api_key: str) -> dict[str, str]:
    return {"x-cg-pro-api-key": api_key} if api_key else {}


async def resolve_coin_ids(
    symbols: list[str],
    vs_currency: str,
    api_key: str,
    **kwargs: Any,
) -> dict[str, str]:
    """Resolve coin ids from symbol tickers using `/coins/markets`."""
    requested_symbols = sorted({symbol.upper() for symbol in symbols})
    if not requested_symbols:
        raise EmptyDataError("No symbols were provided.")

    symbols_csv = ",".join(symbol.lower() for symbol in requested_symbols)
    url = (
        f"{COINGECKO_BASE_URL}/coins/markets?"
        f"vs_currency={vs_currency.lower()}&symbols={symbols_csv}&order=market_cap_desc"
        "&per_page=250&page=1&sparkline=false"
    )

    payload = await get_data(url, headers=_api_headers(api_key), **kwargs)
    if not isinstance(payload, list):
        raise OpenBBError("Unexpected CoinGecko `/coins/markets` response format.")

    symbol_to_id: dict[str, str] = {}
    for row in payload:
        symbol = str(row.get("symbol", "")).upper()
        coin_id = row.get("id")
        if symbol and coin_id and symbol not in symbol_to_id:
            symbol_to_id[symbol] = str(coin_id)

    missing = [symbol for symbol in requested_symbols if symbol not in symbol_to_id]
    if missing:
        missing_text = ", ".join(missing)
        raise EmptyDataError(f"CoinGecko could not resolve symbol(s): {missing_text}")

    return {symbol: symbol_to_id[symbol] for symbol in requested_symbols}


def _merge_ohlc_with_volume(
    ohlc_rows: list[list[Any]],
    volume_rows: list[list[Any]],
) -> list[list[Any]]:
    """Attach nearest volume values to OHLC rows."""
    if not ohlc_rows:
        return []

    normalized_volumes = [
        (_to_milliseconds(volume_row[0]), volume_row[1])
        for volume_row in volume_rows
        if isinstance(volume_row, list) and len(volume_row) >= 2
    ]

    if not normalized_volumes:
        return [ohlc_row + [None] for ohlc_row in ohlc_rows]

    exact_volume_lookup = {
        volume_timestamp: volume_value
        for volume_timestamp, volume_value in normalized_volumes
    }

    results: list[list[Any]] = []
    for ohlc_row in ohlc_rows:
        if not isinstance(ohlc_row, list) or len(ohlc_row) < 5:
            continue

        candle_timestamp = _to_milliseconds(ohlc_row[0])
        volume = exact_volume_lookup.get(candle_timestamp)

        if volume is None:
            closest = min(
                normalized_volumes,
                key=lambda item: abs(item[0] - candle_timestamp),
            )
            volume = closest[1]

        normalized_row = [
            candle_timestamp,
            ohlc_row[1],
            ohlc_row[2],
            ohlc_row[3],
            ohlc_row[4],
            volume,
        ]
        results.append(normalized_row)

    return results


async def get_ohlcv_series(
    coin_id: str,
    vs_currency: str,
    start_date: dateType,
    end_date: dateType,
    interval: str,
    api_key: str,
    **kwargs: Any,
) -> list[list[Any]]:
    """Fetch OHLCV series from CoinGecko with graceful fallback behavior."""
    interval_value = INTERVAL_MAP.get(interval, "daily")
    from_ts = _to_unix_timestamp(start_date)
    to_ts = _to_unix_timestamp(end_date, end_of_day=True)
    headers = _api_headers(api_key)

    ohlcv_url = (
        f"{COINGECKO_BASE_URL}/coins/{coin_id}/ohlcv/range?"
        f"vs_currency={vs_currency.lower()}&from={from_ts}&to={to_ts}"
        f"&interval={interval_value}"
    )

    try:
        payload = await get_data(ohlcv_url, headers=headers, **kwargs)
        if _is_ohlcv_payload(payload):
            return payload
    except OpenBBError as error:
        if not _requires_ohlc_fallback(error):
            raise

    ohlc_url = (
        f"{COINGECKO_BASE_URL}/coins/{coin_id}/ohlc/range?"
        f"vs_currency={vs_currency.lower()}&from={from_ts}&to={to_ts}"
        f"&interval={interval_value}"
    )
    ohlc_payload = await get_data(ohlc_url, headers=headers, **kwargs)
    if not _is_ohlc_payload(ohlc_payload):
        raise OpenBBError("Unexpected CoinGecko `/coins/{id}/ohlc/range` response.")

    market_chart_url = (
        f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart/range?"
        f"vs_currency={vs_currency.lower()}&from={from_ts}&to={to_ts}"
        f"&interval={interval_value}"
    )
    market_chart_payload = await get_data(market_chart_url, headers=headers, **kwargs)
    volume_rows = (
        market_chart_payload.get("total_volumes", [])
        if isinstance(market_chart_payload, dict)
        else []
    )

    return _merge_ohlc_with_volume(ohlc_payload, volume_rows)
