"""Build the bundled security-type asset from FINRA's traded-symbol universe."""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any

QUERY_API_URL = "https://api.finra.org"
MARKET_DATA_URL = "https://finra-markets.morningstar.com"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)
ASSET_PATH = Path(__file__).resolve().parents[1] / "assets" / "security_types.json.gz"
TIERS = ("T1", "T2", "OTCE")
SUMMARY_TYPES = ("ATS_W_SMBL", "OTC_W_SMBL")
UNIVERSE_FIELDS = [
    "issueSymbolIdentifier",
    "issueName",
    "tierDescription",
    "productTypeCode",
]
PAGE_LIMIT = 5000
US_COMPOSITES = ("126", "22")
LOOKUP_BATCH = 100
LOOKUP_INTERVAL = 0.5
LOOKUP_ATTEMPTS = 4
THROTTLE_WAIT = 30
CLASS_FIELDS = [
    "security_type",
    "name",
    "security_description",
    "security_id",
    "performance_id",
    "exchange",
    "listing_market_id",
    "composite_exchange_id",
    "country",
    "domicile",
    "currency",
    "quote_symbol",
]


def latest_weeks(partitions: list[list[str]]) -> dict[str, str]:
    """Return the newest published week of each tier.

    Parameters
    ----------
    partitions : list[list[str]]
        The weekly summary partitions, each a week and a tier.

    Returns
    -------
    dict[str, str]
        The latest week start date of each tier.
    """
    weeks: dict[str, str] = {}

    for partition in partitions:
        if len(partition) > 1 and partition[1] in TIERS:
            week, tier = partition[0], partition[1]
            weeks[tier] = max(weeks.get(tier, week), week)

    return weeks


def universe_payload(week: str, tier: str, summary_type: str) -> dict:
    """Return the weekly summary request for one week, tier, and summary type.

    Parameters
    ----------
    week : str
        The week start date.
    tier : str
        The tier - T1, T2, or OTCE.
    summary_type : str
        The summary type - ATS_W_SMBL or OTC_W_SMBL.

    Returns
    -------
    dict
        The request body, without the paging keys.
    """
    return {
        "fields": UNIVERSE_FIELDS,
        "compareFilters": [
            {"compareType": "EQUAL", "fieldName": "weekStartDate", "fieldValue": week},
            {"compareType": "EQUAL", "fieldName": "tierIdentifier", "fieldValue": tier},
            {
                "compareType": "EQUAL",
                "fieldName": "summaryTypeCode",
                "fieldValue": summary_type,
            },
        ],
    }


def merge_universe(universe: dict[str, dict], rows: list[dict]) -> None:
    """Add weekly summary rows to the symbol universe, first seen wins.

    Parameters
    ----------
    universe : dict[str, dict]
        The symbols gathered so far, updated in place.
    rows : list[dict]
        The weekly summary rows.
    """
    for row in rows:
        symbol = str(row.get("issueSymbolIdentifier") or "").strip().upper()

        if symbol and symbol not in universe:
            universe[symbol] = {
                "issue_name": row.get("issueName"),
                "tier": row.get("tierDescription"),
                "product_type": row.get("productTypeCode"),
            }


def _text(value: Any) -> str | None:
    """Return a stripped string, or None for a blank value."""
    text = str(value).strip() if value is not None else ""

    return text or None


def classify(record: dict) -> list:
    """Return the compact classification of one Market Data Center lookup record.

    Parameters
    ----------
    record : dict
        The raw getids.jsp record.

    Returns
    -------
    list
        The values of CLASS_FIELDS, in order.
    """
    tenfore = record.get("TenforeInfo") or []
    quote_symbol = (
        f"{tenfore[3]}.{tenfore[2]}.{tenfore[0]}"
        if len(tenfore) > 3 and all(_text(part) for part in tenfore[:4])
        else None
    )

    return [
        _text(record.get("Type")),
        _text(record.get("OS01W")) or _text(record.get("Name")),
        _text(record.get("AC021")),
        _text(record.get("SecId")),
        _text(record.get("PID")),
        _text(record.get("Exch")),
        _text(record.get("ListingMarket")),
        _text(record.get("CompositeExchangeID")),
        _text(record.get("Region")),
        _text(record.get("DomicileCountry")),
        _text(record.get("Currency")),
        quote_symbol,
    ]


def market_prefix(tier: str | None) -> str:
    """Return the US composite market a tier's symbols are looked up on.

    Parameters
    ----------
    tier : str | None
        The FINRA tier description.

    Returns
    -------
    str
        The Market Data Center id of the OTC composite for OTC equities, or of the
        US consolidated composite for NMS stocks.
    """
    return "22" if str(tier or "").upper().startswith("OTC") else "126"


def lookup_form(symbol: str, prefix: str | None = None) -> str:
    """Return a FINRA symbol in the form the Market Data Center looks up.

    Parameters
    ----------
    symbol : str
        The FINRA symbol, with preferred series after a dollar sign.
    prefix : str | None
        The composite market to look the symbol up on. Any market when None.

    Returns
    -------
    str
        The symbol with preferred series after a lower-case p, on the market.
    """
    form = symbol.replace("$", "p")

    return f"{prefix}:{form}" if prefix else form


def read_lookup(
    records: list[dict], symbols: list[str], prefix: str | None = None
) -> dict[str, list]:
    """Return the classification of each looked-up symbol.

    Parameters
    ----------
    records : list[dict]
        The raw getids.jsp records.
    symbols : list[str]
        The FINRA symbols that were looked up.
    prefix : str | None
        The composite market the symbols were looked up on. When None, only
        records on a US composite market are kept. Records with neither a type
        nor a name are skipped.

    Returns
    -------
    dict[str, list]
        The compact classification keyed by FINRA symbol.
    """
    originals = {lookup_form(symbol, prefix).upper(): symbol for symbol in symbols}

    return {
        originals[key]: classify(record)
        for record in records
        if (key := str(record.get("QueryKey") or "").upper()) in originals
        and (record.get("Type") or record.get("OS01W") or record.get("Name"))
        and (prefix or str(record.get("CompositeExchangeID")) in US_COMPOSITES)
    }


def lookup_plan(universe: dict[str, dict], symbols: list[str]) -> dict[str, list[str]]:
    """Return the symbols grouped by the composite market they are looked up on.

    Parameters
    ----------
    universe : dict[str, dict]
        The FINRA details of each symbol, with its tier.
    symbols : list[str]
        The symbols to look up.

    Returns
    -------
    dict[str, list[str]]
        The symbols keyed by composite market id.
    """
    plan: dict[str, list[str]] = {}

    for symbol in symbols:
        tier = (universe.get(symbol) or {}).get("tier")
        plan.setdefault(market_prefix(tier), []).append(symbol)

    return plan


def batches(symbols: list[str]) -> list[list[str]]:
    """Return the symbols in lookup-sized batches.

    Parameters
    ----------
    symbols : list[str]
        The symbols to look up.

    Returns
    -------
    list[list[str]]
        Batches of at most LOOKUP_BATCH symbols.
    """
    return [
        symbols[start : start + LOOKUP_BATCH]
        for start in range(0, len(symbols), LOOKUP_BATCH)
    ]


class Client:
    """A cookie-holding HTTP client built on the standard library."""

    def __init__(self) -> None:
        """Open the cookie jar the Market Data Center session lives in."""
        from http.cookiejar import CookieJar
        from urllib.request import HTTPCookieProcessor, build_opener

        self.opener = build_opener(HTTPCookieProcessor(CookieJar()))

    def request(
        self, url: str, params: dict | None = None, payload: dict | None = None
    ) -> tuple[int, str, dict]:
        """Return the status, body, and headers of one request.

        Parameters
        ----------
        url : str
            The URL.
        params : dict | None
            The query parameters.
        payload : dict | None
            A JSON body, sent as a POST.

        Returns
        -------
        tuple[int, str, dict]
            The status code, the body, and the lower-cased headers.
        """
        from urllib.error import HTTPError
        from urllib.parse import urlencode
        from urllib.request import Request

        target = f"{url}?{urlencode(params)}" if params else url
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        data = None

        if payload is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(payload).encode("utf-8")

        request = Request(target, data=data, headers=headers)  # noqa: S310

        try:
            with self.opener.open(request, timeout=60) as response:
                return (
                    response.status,
                    response.read().decode("utf-8", errors="replace"),
                    {key.lower(): value for key, value in response.headers.items()},
                )
        except HTTPError as error:
            return error.code, error.read().decode("utf-8", errors="replace"), {}


def fetch_universe(client: Client) -> tuple[dict[str, str], dict[str, dict]]:
    """Return the latest weeks and every symbol FINRA published volume for.

    Parameters
    ----------
    client : Client
        The HTTP client.

    Returns
    -------
    tuple[dict[str, str], dict[str, dict]]
        The latest week of each tier, and the symbols with their tier and name.

    Raises
    ------
    RuntimeError
        If the FINRA Query API refuses a request.
    """
    status, body, _ = client.request(
        f"{QUERY_API_URL}/partitions/group/otcMarket/name/weeklySummary"
    )

    if status != 200:
        raise RuntimeError(f"FINRA answered the weekly partitions with HTTP {status}.")

    weeks = latest_weeks(
        [
            list(item.get("partitions") or [])
            for item in json.loads(body).get("availablePartitions") or []
        ]
    )
    universe: dict[str, dict] = {}

    for tier, week in sorted(weeks.items()):
        for summary_type in SUMMARY_TYPES:
            offset = 0

            while True:
                status, body, headers = client.request(
                    f"{QUERY_API_URL}/data/group/otcMarket/name/weeklySummary",
                    payload={
                        **universe_payload(week, tier, summary_type),
                        "offset": offset,
                        "limit": PAGE_LIMIT,
                    },
                )

                if status == 204:
                    break

                if status != 200:
                    raise RuntimeError(
                        f"FINRA answered the {tier} weekly summary with HTTP {status}."
                    )

                rows = json.loads(body)
                merge_universe(universe, rows)
                offset += len(rows)

                if not rows or offset >= int(headers.get("record-total") or 0):
                    break

    return weeks, universe


def lookup_batch(
    client: Client, symbols: list[str], prefix: str | None = None
) -> dict[str, list]:
    """Return the classification of one batch, isolating symbols the service rejects.

    Parameters
    ----------
    client : Client
        The HTTP client.
    symbols : list[str]
        The FINRA symbols to look up.
    prefix : str | None
        The composite market to look the symbols up on. Any US market when None.

    Returns
    -------
    dict[str, list]
        The compact classification keyed by FINRA symbol.

    Raises
    ------
    RuntimeError
        If the Market Data Center keeps throttling the lookups.
    """
    import time

    for attempt in range(1, LOOKUP_ATTEMPTS + 1):
        status, body, _ = client.request(
            f"{MARKET_DATA_URL}/getids.jsp",
            {"symbol": ",".join(lookup_form(symbol, prefix) for symbol in symbols)},
        )
        time.sleep(LOOKUP_INTERVAL)

        if status == 200:
            return read_lookup(json.loads(body).get("Records") or [], symbols, prefix)

        if status != 429:
            if len(symbols) == 1:
                return {}

            middle = len(symbols) // 2

            return {
                **lookup_batch(client, symbols[:middle], prefix),
                **lookup_batch(client, symbols[middle:], prefix),
            }

        time.sleep(THROTTLE_WAIT * attempt)
        client.request(f"{MARKET_DATA_URL}/finralogin.jsp")

    raise RuntimeError("The FINRA Market Data Center kept throttling the lookups.")


def fetch_classes(client: Client, universe: dict[str, dict]) -> dict[str, list]:
    """Return the Market Data Center classification of each symbol it resolves.

    Parameters
    ----------
    client : Client
        The HTTP client.
    universe : dict[str, dict]
        The FINRA symbols to classify, with their tiers.

    Returns
    -------
    dict[str, list]
        The compact classification keyed by FINRA symbol.
    """
    client.request(f"{MARKET_DATA_URL}/finralogin.jsp")
    symbols = sorted(universe)
    classes: dict[str, list] = {}

    for prefix, group in lookup_plan(universe, symbols).items():
        for batch in batches(group):
            classes.update(lookup_batch(client, batch, prefix))

    for batch in batches([symbol for symbol in symbols if symbol not in classes]):
        classes.update(lookup_batch(client, batch))

    return classes


def build(client: Client) -> dict:
    """Return the security-type asset.

    Parameters
    ----------
    client : Client
        The HTTP client.

    Returns
    -------
    dict
        The latest weeks, the classification of every resolved symbol, and the
        symbols the Market Data Center could not resolve.
    """
    weeks, universe = fetch_universe(client)
    symbols = sorted(universe)
    classes = fetch_classes(client, universe)

    return {
        "weeks": weeks,
        "fields": CLASS_FIELDS,
        "securities": dict(sorted(classes.items())),
        "unresolved": [symbol for symbol in symbols if symbol not in classes],
    }


def main() -> int:
    """Write the security-type asset.

    Returns
    -------
    int
        The process exit code.
    """
    import sys

    asset = build(Client())
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    ASSET_PATH.write_bytes(
        gzip.compress(json.dumps(asset, separators=(",", ":")).encode("utf-8"), mtime=0)
    )
    sys.stderr.write(
        f"security-types: {len(asset['securities'])} classified, "
        f"{len(asset['unresolved'])} unresolved, weeks {asset['weeks']}\n"
    )

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
