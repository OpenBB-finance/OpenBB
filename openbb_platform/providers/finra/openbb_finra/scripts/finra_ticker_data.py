from __future__ import annotations

from collections import deque
import json
import re
import sys
from http.cookiejar import CookieJar
from typing import Any
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, Request, build_opener

BASE_URL = "https://finra-markets.morningstar.com"
SDK_VERSION = "2.63.2"
USER_AGENT = "Mozilla/5.0"
DEFAULT_SEARCH_CONDITION = "ST,FE,FC,FO,2,1"
DEFAULT_SEARCH_PAGE_LIMIT = 35
DEFAULT_SEARCH_ROOT_PREFIXES = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
DEFAULT_SEARCH_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def _request(opener: Any, url: str, params: dict[str, Any] | None = None) -> str:
    if params:
        url = f"{url}?{urlencode(params)}"
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json, text/javascript, */*; q=0.01",
        },
    )
    with opener.open(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def _build_opener() -> Any:
    return build_opener(HTTPCookieProcessor(CookieJar()))


def _seed_session(opener: Any, query: str) -> None:
    redirect_query = query.strip().upper() or "AAPL"
    _request(
        opener,
        f"{BASE_URL}/finralogin.jsp",
        {
            "redirectPage": f"/MarketData/EquityOptions/detail.jsp?query={redirect_query}&sdkVersion={SDK_VERSION}"
        },
    )


def _parse_jsonp(payload: str) -> dict[str, Any]:
    text = payload.strip()
    if text.startswith("{"):
        return json.loads(text)
    match = re.match(r"^[^(]+\((.*)\)\s*;?\s*$", text, re.S)
    if not match:
        raise ValueError("Unexpected payload format")
    return json.loads(match.group(1))


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text not in ("", "-", "NA", "NA  ") else None


def _number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    if text in ("", "-", "NA", "NA  "):
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    text = _clean(value)
    if text is None:
        return None
    text = text.upper()
    if text == "TRUE":
        return True
    if text == "FALSE":
        return False
    return None


def _date(value: Any) -> str | None:
    text = _clean(value)
    if not isinstance(text, str):
        return None
    text_value = str(text)
    if len(text_value) == 10 and text_value[4] == "-" and text_value[7] == "-":
        return text_value
    if len(text_value) == 8 and text_value.isdigit():
        return f"{text_value[:4]}-{text_value[4:6]}-{text_value[6:]}"
    match = re.match(r"^(\d{2})[-/](\d{2})[-/](\d{4})(?:\s.*)?$", text_value)
    if match:
        month, day, year = match.groups()
        return f"{year}-{month}-{day}"
    return None


def _first(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and value.strip() in ("", "-", "NA", "NA  "):
            continue
        return value
    return None


def _drop_none(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _drop_none(item)
            for key, item in value.items()
            if item is not None and item != {} and item != []
        }
    if isinstance(value, list):
        return [_drop_none(item) for item in value if item is not None]
    return value


def _select_record(records: list[dict[str, Any]], ticker: str) -> dict[str, Any] | None:
    if not records:
        return None
    target = ticker.upper()
    preferred_exchanges = {"XNAS", "XNYS", "XASE", "ARCX"}

    def score(record: dict[str, Any]) -> tuple[int, int, int, int, int, int]:
        query_key = str(record.get("QueryKey", "")).upper()
        symbol = str(record.get("Symbol", "")).upper()
        record_ticker = str(record.get("Ticker", "")).upper()
        exchange = str(record.get("Exch", "")).upper()
        region = str(record.get("Region", "")).upper()
        record_type = str(record.get("Type", "")).upper()
        return (
            int(query_key == target),
            int(record_ticker == target),
            int(symbol == target),
            int(region == "USA"),
            int(record_type == "ST"),
            int(exchange in preferred_exchanges),
        )

    return max(records, key=score)


def _search_records(opener: Any, query: str, condition: str) -> list[dict[str, Any]]:
    normalized_query = query.strip().upper()
    if not normalized_query:
        raise ValueError("Search query is required")

    payload = json.loads(
        _request(
            opener,
            f"{BASE_URL}/acb.jsp",
            {"condition": condition, "kw": normalized_query, "id": "1"},
        )
    )

    error_message = _clean(payload.get("errorMessage"))
    if error_message and not payload.get("result"):
        raise LookupError(
            f"FINRA search failed for {normalized_query!r}: {error_message}"
        )

    return payload.get("result") or []


def _normalize_search_record(
    record: dict[str, Any], include_raw: bool
) -> dict[str, Any]:
    symbol = _clean(_first(record.get("OS001"), record.get("AC001")))
    sec_id = _clean(_first(record.get("SecId"), record.get("OS06Y")))
    listing_market_id = _clean(record.get("AC018"))
    composite_exchange_id = _clean(
        _first(record.get("CompositeExchangeID"), record.get("AC005"))
    )
    exchange_id = _clean(_first(composite_exchange_id, listing_market_id))
    detail_query = f"{exchange_id}:{sec_id}" if exchange_id and sec_id else None
    data = {
        "symbol": symbol,
        "name": _clean(
            _first(record.get("OS01W"), record.get("Name"), record.get("AC020"))
        ),
        "display_name": _clean(_first(record.get("Name"), record.get("AC020"))),
        "description": _clean(record.get("AC021")),
        "type": _clean(record.get("OS010")),
        "country": _clean(_first(record.get("OS01V"), record.get("XI018"))),
        "currency": _clean(_first(record.get("Currency"), record.get("AC019"))),
        "isin": _clean(_first(record.get("ISIN"), record.get("OS05J"))),
        "sec_id": sec_id,
        "exchange_id": exchange_id,
        "listing_market_id": listing_market_id,
        "composite_exchange_id": composite_exchange_id,
        "search_ticker": _clean(record.get("Ticker")),
        "detail_query": detail_query,
        "detail_url": (
            f"{BASE_URL}/MarketData/EquityOptions/detail.jsp?query={detail_query}"
            if detail_query
            else None
        ),
    }
    if include_raw:
        data["raw"] = record
    return _drop_none(data)


def _search_record_key(record: dict[str, Any]) -> str:
    key = _clean(_first(record.get("Ticker"), record.get("SecId"), record.get("OS06Y")))
    if key:
        return key
    symbol = _clean(_first(record.get("OS001"), record.get("AC001"))) or "UNKNOWN"
    exchange_id = (
        _clean(
            _first(
                record.get("AC018"),
                record.get("CompositeExchangeID"),
                record.get("AC005"),
            )
        )
        or "UNKNOWN"
    )
    record_type = _clean(record.get("OS010")) or "UNKNOWN"
    return f"{symbol}|{exchange_id}|{record_type}"


def _normalize(
    ticker: str, record: dict[str, Any], static_row: dict[str, Any], include_raw: bool
) -> dict[str, Any]:
    tenfore_info = record.get("TenforeInfo") or []
    tenfore_ticker = _clean(tenfore_info[0] if len(tenfore_info) > 0 else None)
    tenfore_market = _clean(tenfore_info[1] if len(tenfore_info) > 1 else None)
    tenfore_type = _clean(tenfore_info[2] if len(tenfore_info) > 2 else None)
    tenfore_code = _clean(tenfore_info[3] if len(tenfore_info) > 3 else None)
    tf_ticker = _clean(static_row.get("tfTicker"))
    if not tf_ticker and tenfore_code and tenfore_type and tenfore_ticker:
        tf_ticker = f"{tenfore_code}.{tenfore_type}.{tenfore_ticker}"

    market_data_exchange_id = _clean(
        _first(record.get("MarketDataExchangeID"), record.get("CompositeExchangeID"))
    )
    pid = _clean(_first(record.get("PID"), record.get("SecId"), record.get("SID")))
    detail_query = (
        f"{market_data_exchange_id}:{pid}"
        if market_data_exchange_id and pid
        else _clean(record.get("QueryKey"))
    )

    data = {
        "source": "finra_markets_morningstar",
        "input": {"ticker": ticker},
        "security": {
            "ticker": _clean(_first(record.get("Ticker"), record.get("Symbol")))
            or ticker,
            "name": _clean(
                _first(
                    record.get("OS01W"),
                    static_row.get("MstarStandardName"),
                    static_row.get("IssuerName"),
                    record.get("Name"),
                )
            ),
            "pid": _clean(record.get("PID")),
            "sec_id": _clean(_first(record.get("SecId"), record.get("SID"))),
            "query_key": _clean(record.get("QueryKey")),
            "detail_query": detail_query,
            "detail_url": (
                f"{BASE_URL}/MarketData/EquityOptions/detail.jsp?query={detail_query}"
                if detail_query
                else None
            ),
            "exchange": _clean(_first(record.get("Exch"), static_row.get("MicCode"))),
            "listing_market": _clean(record.get("ListingMarket")),
            "market_data_exchange_id": _clean(record.get("MarketDataExchangeID")),
            "composite_exchange_id": _clean(record.get("CompositeExchangeID")),
            "region": _clean(record.get("Region")),
            "domicile_country": _clean(record.get("DomicileCountry")),
            "currency": _clean(_first(static_row.get("S9"), record.get("Currency"))),
            "type": _clean(_first(static_row.get("secType"), record.get("Type"))),
            "security_type": _clean(record.get("SecurityType")),
            "cusip": _clean(_first(static_row.get("S1012"), record.get("OS05K"))),
            "ipo_date": _date(_first(record.get("IPODate"), record.get("ST467"))),
            "cfid": _clean(record.get("CFID")),
            "tenfore": {
                "ticker": tenfore_ticker,
                "market": tenfore_market,
                "type": tenfore_type,
                "code": tenfore_code,
                "tf_ticker": tf_ticker,
            },
        },
        "price": {
            "last": _number(_first(static_row.get("D20"), static_row.get("os065"))),
            "last_trade_date": _date(
                _first(static_row.get("priceLastTradeDate"), static_row.get("pd001"))
            ),
            "one_week_ago": _number(static_row.get("Price1Week")),
            "same_day": _bool(static_row.get("SameDay")),
            "fifty_two_week_high": _number(static_row.get("st168")),
            "fifty_two_week_low": _number(static_row.get("st169")),
            "fifty_two_week_high_date": _date(static_row.get("st109")),
            "fifty_two_week_low_date": _date(static_row.get("st106")),
        },
        "dividends": {
            "net_dividend": _number(static_row.get("NetDividend")),
            "annual_dividend": _number(static_row.get("ar112")),
            "yield_pct": _number(
                _first(static_row.get("pm032"), static_row.get("st299"))
            ),
            "frequency": _clean(static_row.get("DividendFrequency")),
            "ex_date": _date(_first(static_row.get("EXDate"), static_row.get("os088"))),
            "payment_date": _date(
                _first(static_row.get("PaymentDateOfDividend"), static_row.get("st469"))
            ),
        },
        "valuation": {
            "pe_ratio": _number(
                _first(static_row.get("st198"), static_row.get("S1077"))
            ),
            "price_to_cash_flow_ratio": _number(static_row.get("PC_RATIO")),
            "price_to_free_cash_flow_ratio": _number(static_row.get("P_FCF_RATIO")),
            "rating": _number(static_row.get("st200")),
            "valuation_status": _clean(static_row.get("qv004")),
        },
        "classification": {
            "sector": _clean(_first(static_row.get("st152"), record.get("ST152"))),
            "industry": _clean(_first(static_row.get("st153"), record.get("ST153"))),
            "industry_group": _clean(static_row.get("sta4h")),
            "industry_group_alt": _clean(static_row.get("sta4j")),
            "super_sector": _clean(static_row.get("sta4n")),
        },
        "risk": {
            "standard_deviation_1y": _number(static_row.get("STANDARDDEVIATION1YR")),
            "standard_deviation_3y": _number(static_row.get("STANDARDDEVIATION3YR")),
        },
    }
    if include_raw:
        data["raw"] = {"lookup": record, "static": static_row}
    return _drop_none(data)


def search_finra_tickers(
    query: str,
    *,
    condition: str = DEFAULT_SEARCH_CONDITION,
    include_raw: bool = False,
) -> list[dict[str, Any]]:
    normalized_query = query.strip().upper()
    if not normalized_query:
        raise ValueError("Search query is required")

    opener = _build_opener()
    _seed_session(opener, normalized_query)

    return [
        _normalize_search_record(record, include_raw)
        for record in _search_records(opener, normalized_query, condition)
    ]


def get_finra_search_master_list(
    *,
    condition: str = DEFAULT_SEARCH_CONDITION,
    include_raw: bool = False,
    root_prefixes: list[str] | tuple[str, ...] | None = None,
    alphabet: str = DEFAULT_SEARCH_ALPHABET,
    page_limit: int = DEFAULT_SEARCH_PAGE_LIMIT,
    max_prefix_length: int = 6,
) -> list[dict[str, Any]]:
    if page_limit < 1:
        raise ValueError("page_limit must be at least 1")
    if max_prefix_length < 1:
        raise ValueError("max_prefix_length must be at least 1")

    prefixes = root_prefixes or DEFAULT_SEARCH_ROOT_PREFIXES
    normalized_prefixes = [
        prefix.strip().upper() for prefix in prefixes if prefix and prefix.strip()
    ]
    normalized_alphabet = "".join(
        dict.fromkeys(character.upper() for character in alphabet if character.strip())
    )
    if not normalized_prefixes:
        raise ValueError("At least one root prefix is required")
    if not normalized_alphabet:
        raise ValueError("alphabet must contain at least one character")

    opener = _build_opener()
    _seed_session(opener, normalized_prefixes[0])

    pending = deque(normalized_prefixes)
    visited: set[str] = set()
    results_by_key: dict[str, dict[str, Any]] = {}

    while pending:
        prefix = pending.popleft()
        if prefix in visited:
            continue
        visited.add(prefix)

        records = _search_records(opener, prefix, condition)
        for record in records:
            results_by_key.setdefault(
                _search_record_key(record),
                _normalize_search_record(record, include_raw),
            )

        if len(records) >= page_limit and len(prefix) < max_prefix_length:
            for character in normalized_alphabet:
                pending.append(f"{prefix}{character}")

    return list(results_by_key.values())


def get_finra_ticker_data(ticker: str, include_raw: bool = False) -> dict[str, Any]:
    normalized_ticker = ticker.strip().upper()
    if not normalized_ticker:
        raise ValueError("Ticker symbol is required")

    opener = _build_opener()
    _seed_session(opener, normalized_ticker)

    lookup_payload = _parse_jsonp(
        _request(
            opener,
            f"{BASE_URL}/getids.jsp",
            {"symbol": normalized_ticker, "cb": "finraLookup"},
        )
    )

    if lookup_payload.get("status", {}).get("errorMsg") == "Invalid session":
        raise RuntimeError("FINRA session was rejected by the upstream service")

    record = _select_record(lookup_payload.get("Records") or [], normalized_ticker)
    if not record:
        raise LookupError(f"Ticker {normalized_ticker!r} was not found")

    sec_id = _clean(_first(record.get("SecId"), record.get("SID"), record.get("PID")))
    if not sec_id:
        raise LookupError(
            f"Ticker {normalized_ticker!r} did not resolve to a security id"
        )

    static_payload = json.loads(
        _request(opener, f"{BASE_URL}/getStaticData.jsp", {"secId": sec_id})
    )
    rows = static_payload.get("data") or []
    if not rows:
        raise LookupError(f"No static data returned for {normalized_ticker!r}")

    return _normalize(normalized_ticker, record, rows[0], include_raw)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "data"
    if mode == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else "AAPL"
        print(
            json.dumps(
                search_finra_tickers(query),
                indent=2,
            )
        )
    else:
        ticker = mode if mode != "data" else (sys.argv[2] if len(sys.argv) > 2 else "AAPL")
        print(
            json.dumps(
                get_finra_ticker_data(ticker, include_raw="--raw" in sys.argv),
                indent=2,
                sort_keys=True,
            )
        )
