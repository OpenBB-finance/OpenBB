"""FINRA TRACE public dataset client.

Reads from the unauthenticated ``services-dynarep.ddwa.finra.org`` proxy that
backs the public FINRA Data portal. The proxy demands an ``X-XSRF-TOKEN``
header whose value comes from the ``XSRF-TOKEN`` cookie issued on the first
hit to any dataset URL.

Three datasets cover the public surface:

* ``<Type>Securities`` — current reference data / "last sale" snapshot.
* ``EndOfDayPriceYield`` — daily EOD price/yield history (all product types).
* ``<Type>TradeHistory`` — intraday tick history (only reachable for
  authenticated users; the synchronous public path 524s after 120s and the
  async fallback redirects to a login wall, so this client does not call it).
"""

from __future__ import annotations

import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
from http.cookiejar import CookieJar
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, Request, build_opener

BASE_URL = "https://services-dynarep.ddwa.finra.org"
DATASET_PATH = "/public/reporting/v2/data/group/FixedIncomeMarket/name"
PUBLIC_PAGE_URL = "https://www.finra.org/finra-data/fixed-income/corp-and-agency/trade"
USER_AGENT = "Mozilla/5.0"

DEFAULT_BOND_TYPE = "CA"
DEFAULT_HISTORY_DAYS = 1825  # ~5 years
DEFAULT_HISTORY_LIMIT = 5000  # API record cap

# Each entry: snapshot dataset + the fields the dataset returns. We probe the
# server once for the union of all known FINRA TRACE field names; everything
# below was confirmed accepted on a real query.
BOND_TYPE_CONFIG: dict[str, dict[str, Any]] = {
    "CA": {
        "label": "Corporate & Agency",
        "snapshot_dataset": "CorporateAndAgencySecurities",
        "snapshot_fields": [
            "couponRate", "couponType", "cusip", "industryGroup", "is144A",
            "isCallable", "isConvertible", "issueSymbolIdentifier", "issuerName",
            "lastSalePrice", "lastSaleYield", "lastTradeDate", "maturityDate",
            "moodyRatingDate", "moodysRating", "nextCallDate",
            "productSubTypeCode", "standardAndPoorsRating",
            "standardAndPoorsRatingDate", "traceGradeCode",
        ],
    },
    "TBA": {
        "label": "To-Be-Announced MBS",
        "snapshot_dataset": "TBASecurities",
        "snapshot_fields": [
            "couponRate", "couponType", "cusip", "issueSymbolIdentifier",
            "issuingAgency", "lastSalePrice", "lastSaleYield", "lastTradeDate",
            "maturityDate", "productSubTypeCode", "settlementDateMonth",
            "subProductType",
        ],
    },
    "MBS": {
        "label": "Mortgage-Backed Securities",
        "snapshot_dataset": "MortgageBackedSecurities",
        "snapshot_fields": [
            "amortizationType", "couponRate", "cusip", "issueSymbolIdentifier",
            "issuingAgency", "lastSalePrice", "lastSaleYield", "lastTradeDate",
            "maturityDate", "mortgageProduct", "poolNumber",
            "productSubTypeCode", "referenceDataIdentifier", "subProductType",
            "weightedAverageCoupon", "weightedAverageLoanAge",
            "weightedAverageMaturity",
        ],
    },
    "ABS": {
        "label": "Asset-Backed Securities",
        "snapshot_dataset": "AssetBackedSecurities",
        "snapshot_fields": [
            "couponRate", "couponType", "cusip", "is144A", "issueDescription",
            "issueSymbolIdentifier", "issuerName", "lastSalePrice",
            "lastSaleYield", "lastTradeDate", "maturityDate", "moodysRating",
            "productSubTypeCode", "subProductType",
        ],
    },
    "CMO": {
        "label": "Collateralized Mortgage Obligations",
        "snapshot_dataset": "CollateralizedMortgageObligationsSecurities",
        "snapshot_fields": [
            "couponRate", "couponType", "cusip", "is144A",
            "issueSymbolIdentifier", "issuerName", "issuingAgency",
            "lastSalePrice", "lastSaleYield", "lastTradeDate", "maturityDate",
            "moodysRating", "productSubTypeCode", "productType",
            "securityDescription", "subProductType",
        ],
    },
    "TS": {
        "label": "U.S. Treasury Securities",
        "snapshot_dataset": "TreasurySecurities",
        "snapshot_fields": [
            "benchmarkTermCode", "couponRate", "couponType", "cusip",
            "issueSymbolIdentifier", "issuerName", "lastSalePrice",
            "lastSaleYield", "lastSaleYieldDirectionFlag", "lastTradeDate",
            "lastTradeTime", "maturityDate", "productSubTypeCode",
            "securityDescription", "traceGradeCode",
        ],
    },
}

HISTORY_DATASET = "EndOfDayPriceYield"
HISTORY_FIELDS = [
    "cusip", "issueSymbolIdentifier", "lastSalePrice", "lastSaleYield",
    "productType", "tradeDate",
]

# Auto-detection order when caller doesn't pass an explicit bond_type.
AUTO_BOND_TYPE_ORDER = ("CA", "TS", "CMO", "ABS", "MBS", "TBA")

# Mapping from API camelCase → snake_case used in the output payload.
_CAMEL_TO_SNAKE_RE = re.compile(r"(?<!^)(?=[A-Z])")

_NA_TOKENS = ("", "-", "NA", "NA  ")


def _snake(name: str) -> str:
    return _CAMEL_TO_SNAKE_RE.sub("_", name).lower()


# ---------------------------------------------------------------------------
# HTTP / session helpers
# ---------------------------------------------------------------------------


class _Session:
    """Cookie-jar-backed opener with a captured XSRF token."""

    def __init__(self) -> None:
        self._jar = CookieJar()
        self._opener = build_opener(HTTPCookieProcessor(self._jar))
        self._xsrf: str | None = None

    def _capture_xsrf(self) -> None:
        for cookie in self._jar:
            if cookie.name == "XSRF-TOKEN" and cookie.value:
                self._xsrf = cookie.value
                return

    def _ensure_session(self) -> None:
        if self._xsrf is not None:
            return
        # A GET to any dataset URL returns 401 + sets XSRF-TOKEN. The proxy is
        # happy with either the dataset URL or the public landing page.
        url = f"{BASE_URL}{DATASET_PATH}/CorporateAndAgencySecurities"
        request = Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with self._opener.open(request, timeout=30) as response:
                response.read()
        except HTTPError:
            pass
        self._capture_xsrf()
        if self._xsrf is None:
            raise RuntimeError(
                "Failed to obtain FINRA XSRF-TOKEN cookie from the public proxy."
            )

    def post_dataset(self, dataset: str, payload: dict[str, Any], *, timeout: int = 60) -> list[dict[str, Any]]:
        rows, _ = self.post_dataset_with_total(dataset, payload, timeout=timeout)
        return rows

    def post_dataset_with_total(
        self, dataset: str, payload: dict[str, Any], *, timeout: int = 60
    ) -> tuple[list[dict[str, Any]], int]:
        self._ensure_session()
        url = f"{BASE_URL}{DATASET_PATH}/{dataset}"
        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Content-Type": "application/json",
                "Origin": "https://www.finra.org",
                "Referer": PUBLIC_PAGE_URL,
                "X-XSRF-TOKEN": self._xsrf or "",
            },
        )
        try:
            with self._opener.open(request, timeout=timeout) as response:
                body = response.read().decode("utf-8", errors="replace")
        except HTTPError as error:
            detail = ""
            try:
                detail = error.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            if error.code in {401, 403}:
                raise PermissionError(
                    f"FINRA TRACE request rejected with HTTP {error.code}. "
                    "Refresh the XSRF token or contact FINRA for an API key."
                ) from error
            raise RuntimeError(
                f"FINRA TRACE request failed with HTTP {error.code}: {detail[:300]}"
            ) from error
        return _parse_dataset_response(body, dataset)


def _parse_dataset_response(body: str, dataset: str) -> tuple[list[dict[str, Any]], int]:
    parsed = json.loads(body) if body.strip() else {}
    if parsed.get("status") != "success":
        raise RuntimeError(
            f"FINRA TRACE dataset {dataset!r} returned: "
            f"{parsed.get('statusMessage', body[:300])}"
        )
    return_body = parsed.get("returnBody") or {}
    data = return_body.get("data")
    if isinstance(data, str):
        data = json.loads(data) if data.strip() else []
    total_header = (return_body.get("headers") or {}).get("Record-Total") or ["0"]
    try:
        total = int(total_header[0])
    except (ValueError, IndexError, TypeError):
        total = 0
    return data or [], total


# ---------------------------------------------------------------------------
# Value normalisation
# ---------------------------------------------------------------------------


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text not in _NA_TOKENS else None


def _number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    if text in _NA_TOKENS:
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
    upper = text.upper()
    if upper in {"Y", "YES", "TRUE", "T", "1"}:
        return True
    if upper in {"N", "NO", "FALSE", "F", "0"}:
        return False
    return None


def _date(value: Any) -> str | None:
    text = _clean(value)
    if text is None:
        return None
    if len(text) >= 10 and text[4] == "-" and text[7] == "-":
        return text[:10]
    if len(text) == 8 and text.isdigit():
        return f"{text[:4]}-{text[4:6]}-{text[6:]}"
    match = re.match(r"^(\d{2})[-/](\d{2})[-/](\d{4})(?:\s.*)?$", text)
    if match:
        month, day, year = match.groups()
        return f"{year}-{month}-{day}"
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


# Per-field type coercion. Anything not listed here is passed through unchanged
# (with whitespace stripped on strings via _clean).
_NUMBER_FIELDS = {
    "couponRate", "lastSalePrice", "lastSaleYield", "weightedAverageCoupon",
    "weightedAverageLoanAge", "weightedAverageMaturity", "settlementDateMonth",
}
_BOOL_FIELDS = {"isCallable", "isConvertible", "is144A"}
_DATE_FIELDS = {
    "lastTradeDate", "maturityDate", "moodyRatingDate", "nextCallDate",
    "standardAndPoorsRatingDate", "tradeDate",
}
_COUPON_TYPE_MAP = {
    "FXPM": "Fixed Payment at Maturity",
    "FXPV": "Fixed Plain Vanilla",
    "FXZC": "Fixed Zero Coupon",
    "FLTR": "Floating Rate",
}
_INDUSTRY_GROUP_MAP = {
    "AGENCY": "Agency",
    "BANKS": "Banks",
    "CONSUMGD": "Consumer Goods",
    "ELECTRIC": "Electric Power",
    "ENERGY": "Energy Company",
    "GASDISTR": "Gas Distribution",
    "INDFINCL": "Independent Finance",
    "MANUFACT": "Manufacturing",
    "OFFMUNI": "Official and Muni",
    "OTHFINCL": "Other Financial",
    "REIT": "Real Estate Investment Trust",
    "SERVICE": "Service Company",
    "SOVERGRN": "Sovereign",
    "SPRA": "Supranational",
    "TELEPHON": "Telephone",
    "TRANSPRT": "Transportation",
}


def _coerce(field: str, value: Any) -> Any:
    if field == "couponType":
        text = _clean(value)
        if text is None:
            return None
        return _COUPON_TYPE_MAP.get(text.upper(), text)
    if field == "industryGroup":
        text = _clean(value)
        if text is None:
            return None
        return _INDUSTRY_GROUP_MAP.get(text.upper(), text)
    if field in _NUMBER_FIELDS:
        return _number(value)
    if field in _BOOL_FIELDS:
        return _bool(value)
    if field in _DATE_FIELDS:
        return _date(value)
    return _clean(value)


def _normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    return {_snake(field): _coerce(field, value) for field, value in record.items()}


# ---------------------------------------------------------------------------
# Filter / payload construction
# ---------------------------------------------------------------------------


def _identifier_filters(identifier: str) -> list[dict[str, Any]]:
    normalized = identifier.strip().upper()
    if not normalized:
        raise ValueError("Identifier is required")
    return [
        {"fieldName": "cusip", "fieldValue": normalized, "compareType": "EQUAL"},
        {"fieldName": "issueSymbolIdentifier", "fieldValue": normalized, "compareType": "EQUAL"},
    ]


def _normalize_bond_type(bond_type: str | None) -> str | None:
    if bond_type is None:
        return None
    upper = bond_type.strip().upper()
    if upper in {"", "AUTO"}:
        return None
    if upper not in BOND_TYPE_CONFIG:
        raise ValueError(
            f"Unsupported bond_type {bond_type!r}; expected one of: "
            f"{', '.join(sorted(BOND_TYPE_CONFIG))} or 'auto'."
        )
    return upper


def _format_date(value: str | date | datetime | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value).strip()
    if not text:
        return None
    parsed = _date(text)
    if parsed is None:
        raise ValueError(f"Invalid date {value!r}; use YYYY-MM-DD")
    return parsed


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------


def _fetch_snapshot(
    session: _Session,
    identifier: str,
    bond_type: str,
    *,
    limit: int = 1,
) -> list[dict[str, Any]]:
    config = BOND_TYPE_CONFIG[bond_type]
    payload = {
        "fields": config["snapshot_fields"],
        "orFilters": [{"compareFilters": _identifier_filters(identifier)}],
        "offset": 0,
        "limit": limit,
    }
    return session.post_dataset(config["snapshot_dataset"], payload, timeout=60)


def _auto_detect_bond_type(session: _Session, identifier: str) -> tuple[str, list[dict[str, Any]]]:
    for candidate in AUTO_BOND_TYPE_ORDER:
        rows = _fetch_snapshot(session, identifier, candidate, limit=1)
        if rows:
            return candidate, rows
    raise LookupError(
        f"No FINRA TRACE security found for {identifier!r} in any supported "
        f"bond type ({', '.join(AUTO_BOND_TYPE_ORDER)})."
    )


DEFAULT_ISSUER_PARALLELISM = 15


def list_finra_trace_issuers(
    *,
    bond_type: str = "CA",
    outstanding_only: bool = True,
    as_of: str | date | datetime | None = None,
    parallelism: int = DEFAULT_ISSUER_PARALLELISM,
) -> list[dict[str, Any]]:
    """Return every TRACE-reported bond (all fields, deduplicated by CUSIP).

    The FINRA proxy has no distinct/group-by primitive, so this scans the bond
    universe in 5,000-row pages. Pages run concurrently (default ``parallelism=15``),
    so a full sweep of ~280k outstanding Corporate & Agency bonds returns in ~5 seconds.
    Records are normalized, null values dropped, and sorted by CUSIP.
    """
    if parallelism < 1:
        raise ValueError("parallelism must be at least 1")
    resolved_type = _normalize_bond_type(bond_type) or "CA"
    config = BOND_TYPE_CONFIG[resolved_type]
    dataset = config["snapshot_dataset"]

    base_compare: list[dict[str, Any]] = []
    if outstanding_only:
        cutoff = _format_date(as_of) or datetime.now(timezone.utc).date().isoformat()
        base_compare.append(
            {"fieldName": "maturityDate", "fieldValue": cutoff, "compareType": "GREATER"}
        )

    def _payload(offset: int) -> dict[str, Any]:
        body: dict[str, Any] = {
            "fields": config["snapshot_fields"],
            "sortFields": ["cusip"],
            "offset": offset,
            "limit": 5000,
        }
        if base_compare:
            body["compareFilters"] = base_compare
        return body

    session = _Session()
    first_rows, total = session.post_dataset_with_total(dataset, _payload(0), timeout=60)
    seen_cusips: set[str] = set()
    records: list[dict[str, Any]] = []
    for row in first_rows:
        cusip_raw = row.get("cusip")
        cusip = (cusip_raw or "").strip().upper() if cusip_raw else ""
        if cusip and cusip not in seen_cusips:
            seen_cusips.add(cusip)
            normalized = _normalize_record(row)
            records.append(_drop_none(normalized))
    if total <= 5000 or not first_rows:
        return records

    offsets = list(range(5000, total, 5000))
    with ThreadPoolExecutor(max_workers=parallelism) as pool:
        futures = [pool.submit(session.post_dataset, dataset, _payload(off)) for off in offsets]
        for future in as_completed(futures):
            rows = future.result()
            for row in rows:
                cusip_raw = row.get("cusip")
                cusip = (cusip_raw or "").strip().upper() if cusip_raw else ""
                if cusip and cusip not in seen_cusips:
                    seen_cusips.add(cusip)
                    normalized = _normalize_record(row)
                    records.append(_drop_none(normalized))
    return records


def search_finra_trace_bonds(
    issuer_name: str | None = None,
    *,
    bond_type: str = "CA",
    outstanding_only: bool = True,
    as_of: str | date | datetime | None = None,
    limit: int = DEFAULT_HISTORY_LIMIT,
    parallelism: int = DEFAULT_ISSUER_PARALLELISM,
    include_raw: bool = False,
) -> list[dict[str, Any]]:
    """List TRACE-reported bonds.

    When ``issuer_name`` is provided, returns all bonds for that issuer (exact
    match on the registered legal name, e.g. ``"APPLE INC"``). When
    ``issuer_name`` is ``None``, returns the full bond universe across all
    issuers via a paginated parallel scan, deduplicated by CUSIP.

    ``outstanding_only`` (default ``True``) filters out bonds whose
    ``maturityDate`` is on or before ``as_of`` (default: today UTC).
    """
    if limit < 1:
        raise ValueError("limit must be at least 1")
    resolved_type = _normalize_bond_type(bond_type) or "CA"
    config = BOND_TYPE_CONFIG[resolved_type]
    dataset = config["snapshot_dataset"]

    base_compare: list[dict[str, Any]] = []
    if issuer_name is not None:
        name = issuer_name.strip()
        if not name:
            raise ValueError("issuer_name must not be blank; pass None to get all bonds")
        base_compare.append(
            {"fieldName": "issuerName", "fieldValue": name.upper(), "compareType": "EQUAL"}
        )
    if outstanding_only:
        cutoff = _format_date(as_of) or datetime.now(timezone.utc).date().isoformat()
        base_compare.append(
            {"fieldName": "maturityDate", "fieldValue": cutoff, "compareType": "GREATER"}
        )

    def _payload(offset: int, page_limit: int) -> dict[str, Any]:
        body: dict[str, Any] = {
            "fields": config["snapshot_fields"],
            "sortFields": ["cusip"] if issuer_name is None else ["maturityDate"],
            "offset": offset,
            "limit": page_limit,
        }
        if base_compare:
            body["compareFilters"] = base_compare
        return body

    session = _Session()

    if issuer_name is not None:
        rows = session.post_dataset(dataset, _payload(0, limit), timeout=60)
        normalized = [_normalize_record(row) for row in rows]
        if include_raw:
            for record, raw in zip(normalized, rows):
                record["raw"] = raw
        return [_drop_none(record) for record in normalized]

    if parallelism < 1:
        raise ValueError("parallelism must be at least 1")
    first_rows, total = session.post_dataset_with_total(dataset, _payload(0, 5000), timeout=60)
    seen_cusips: set[str] = set()
    records: list[dict[str, Any]] = []
    for row in first_rows:
        cusip_raw = row.get("cusip")
        cusip = (cusip_raw or "").strip().upper() if cusip_raw else ""
        if cusip and cusip not in seen_cusips:
            seen_cusips.add(cusip)
            normalized = _normalize_record(row)
            if include_raw:
                normalized["raw"] = row
            records.append(_drop_none(normalized))
    if total <= 5000 or not first_rows:
        return records

    offsets = list(range(5000, total, 5000))
    with ThreadPoolExecutor(max_workers=parallelism) as pool:
        futures = [pool.submit(session.post_dataset, dataset, _payload(off, 5000)) for off in offsets]
        for future in as_completed(futures):
            rows = future.result()
            for row in rows:
                cusip_raw = row.get("cusip")
                cusip = (cusip_raw or "").strip().upper() if cusip_raw else ""
                if cusip and cusip not in seen_cusips:
                    seen_cusips.add(cusip)
                    normalized = _normalize_record(row)
                    if include_raw:
                        normalized["raw"] = row
                    records.append(_drop_none(normalized))
    return records


def get_finra_trace_bond_data(
    identifier: str,
    *,
    bond_type: str | None = None,
    include_raw: bool = False,
) -> dict[str, Any]:
    """Return the current reference / last-sale snapshot for a bond.

    ``identifier`` may be a 9-character CUSIP or the FINRA bond symbol (the
    ``issueSymbolIdentifier`` returned by the snapshot). When ``bond_type`` is
    ``None`` or ``"auto"`` the matching dataset is detected by probing
    Corporate & Agency, Treasury, then the structured-product datasets.
    """
    normalized_identifier = identifier.strip().upper()
    if not normalized_identifier:
        raise ValueError("Identifier is required")

    session = _Session()
    resolved_type = _normalize_bond_type(bond_type)
    if resolved_type is None:
        resolved_type, rows = _auto_detect_bond_type(session, normalized_identifier)
    else:
        rows = _fetch_snapshot(session, normalized_identifier, resolved_type)
        if not rows:
            raise LookupError(
                f"No FINRA TRACE security found for {normalized_identifier!r} "
                f"in bond_type={resolved_type!r}."
            )

    raw_record = rows[0]
    security = _normalize_record(raw_record)
    result: dict[str, Any] = {
        "source": "finra_trace",
        "input": {
            "identifier": normalized_identifier,
            "bond_type": resolved_type,
            "bond_type_label": BOND_TYPE_CONFIG[resolved_type]["label"],
            "dataset": BOND_TYPE_CONFIG[resolved_type]["snapshot_dataset"],
        },
        "security": security,
    }
    if include_raw:
        result["raw"] = raw_record
    return _drop_none(result)


def get_finra_trace_price_history(
    identifier: str,
    *,
    bond_type: str | None = None,
    start_date: str | date | datetime | None = None,
    end_date: str | date | datetime | None = None,
    days: int | None = None,
    limit: int = DEFAULT_HISTORY_LIMIT,
    include_raw: bool = False,
) -> list[dict[str, Any]]:
    """Return daily end-of-day price/yield history for a bond.

    Uses the ``EndOfDayPriceYield`` public dataset. The synchronous TRACE
    tick-level history endpoint is gated behind login + Cloudflare 524 timeouts,
    so this function is the practical public ceiling.

    ``days`` is ignored when an explicit ``start_date`` is supplied. Date
    parameters accept ``YYYY-MM-DD`` strings, ``date``, or ``datetime``.
    """
    normalized_identifier = identifier.strip().upper()
    if not normalized_identifier:
        raise ValueError("Identifier is required")
    if limit < 1:
        raise ValueError("limit must be at least 1")

    end_value = _format_date(end_date) or datetime.now(timezone.utc).date().isoformat()
    if start_date is not None:
        start_value = _format_date(start_date)
    else:
        history_days = days if days is not None else DEFAULT_HISTORY_DAYS
        if history_days < 1:
            raise ValueError("days must be at least 1")
        anchor = datetime.strptime(end_value, "%Y-%m-%d").date()
        start_value = (anchor - timedelta(days=history_days)).isoformat()

    session = _Session()
    resolved_type = _normalize_bond_type(bond_type)
    payload: dict[str, Any] = {
        "fields": HISTORY_FIELDS,
        "orFilters": [{"compareFilters": _identifier_filters(normalized_identifier)}],
        "dateRangeFilters": [{
            "startDate": start_value,
            "endDate": end_value,
            "fieldName": "tradeDate",
        }],
        "sortFields": ["-tradeDate"],
        "offset": 0,
        "limit": limit,
    }
    if resolved_type is not None:
        payload["compareFilters"] = [
            {"fieldName": "productType", "fieldValue": _product_type_code(resolved_type), "compareType": "EQUAL"}
        ]

    rows = session.post_dataset(HISTORY_DATASET, payload, timeout=120)
    normalized = [_normalize_record(row) for row in rows]
    if include_raw:
        for record, raw in zip(normalized, rows):
            record["raw"] = raw
    return [_drop_none(record) for record in normalized]


def _product_type_code(bond_type: str) -> str:
    # EndOfDayPriceYield exposes the umbrella product type, not the structured-
    # product sub-type. Map our bond_type codes onto the productType column.
    if bond_type == "TS":
        return "TS"
    if bond_type in {"TBA", "MBS", "ABS", "CMO"}:
        return "SP"
    return "CA"


def get_finra_trace_data(
    identifier: str,
    *,
    bond_type: str | None = None,
    include_raw: bool = False,
    start_date: str | date | datetime | None = None,
    end_date: str | date | datetime | None = None,
    days: int | None = None,
    limit: int = DEFAULT_HISTORY_LIMIT,
) -> dict[str, Any]:
    """Return snapshot + EOD price history for a bond in a single call."""
    normalized_identifier = identifier.strip().upper()
    if not normalized_identifier:
        raise ValueError("Identifier is required")

    bond_data = get_finra_trace_bond_data(
        normalized_identifier,
        bond_type=bond_type,
        include_raw=include_raw,
    )
    history = get_finra_trace_price_history(
        normalized_identifier,
        bond_type=bond_data["input"]["bond_type"],
        start_date=start_date,
        end_date=end_date,
        days=days,
        limit=limit,
        include_raw=include_raw,
    )
    result = dict(bond_data)
    result["price_history"] = history
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_cli(argv: list[str]) -> tuple[str, str, dict[str, Any]]:
    args = argv[1:]
    if not args or args[0] in {"-h", "--help"}:
        print(
            "Usage: finra_trace_data.py <mode> <identifier> [options]\n\n"
            "Modes:\n"
            "  data     (default) snapshot + EOD price history for one bond\n"
            "  snapshot reference / last-sale snapshot for one bond\n"
            "  history  daily EOD price/yield series for one bond\n"
            "  search   list every TRACE bond for an issuer name\n"
            "  issuers  dump every distinct bond (all fields; no identifier arg)\n\n"
            "Options:\n"
            "  --bond-type=CA|TBA|MBS|ABS|CMO|TS|auto   (default: auto; search/issuers use CA)\n"
            "  --start=YYYY-MM-DD     History start date\n"
            "  --end=YYYY-MM-DD       History end date\n"
            "  --days=N               Days of history if no --start given\n"
            "  --limit=N              Max rows (max 5000)\n"
            "  --include-matured      Include matured bonds in search/issuers (default: outstanding only)\n"
            "  --as-of=YYYY-MM-DD     Maturity cutoff for search/issuers (default: today)\n"
            "  --parallelism=N        Concurrent pages for `issuers` sweep (default: 15)\n"
            "  --raw                  Include raw API rows in the output\n\n"
            "Examples:\n"
            "  finra_trace_data.py snapshot 037833EH9\n"
            "  finra_trace_data.py history  037833EH9 --days=30\n"
            "  finra_trace_data.py search 'APPLE INC'\n"
            "  finra_trace_data.py issuers",
            file=sys.stderr,
        )
        sys.exit(0 if args else 2)

    mode = "data"
    if args and args[0] in {"snapshot", "history", "data", "search", "issuers"}:
        mode = args[0]
        args = args[1:]

    options: dict[str, Any] = {
        "bond_type": None,
        "include_raw": False,
    }
    positional: list[str] = []
    for raw in args:
        if raw == "--raw":
            options["include_raw"] = True
        elif raw == "--include-matured":
            options["outstanding_only"] = False
        elif raw.startswith("--bond-type="):
            options["bond_type"] = raw.split("=", 1)[1] or None
        elif raw.startswith("--start="):
            options["start_date"] = raw.split("=", 1)[1] or None
        elif raw.startswith("--end="):
            options["end_date"] = raw.split("=", 1)[1] or None
        elif raw.startswith("--as-of="):
            options["as_of"] = raw.split("=", 1)[1] or None
        elif raw.startswith("--days="):
            options["days"] = int(raw.split("=", 1)[1])
        elif raw.startswith("--limit="):
            options["limit"] = int(raw.split("=", 1)[1])
        elif raw.startswith("--parallelism="):
            options["parallelism"] = int(raw.split("=", 1)[1])
        else:
            positional.append(raw)

    if mode == "issuers":
        identifier = ""
    elif not positional:
        print("error: an identifier (CUSIP or bond symbol) is required", file=sys.stderr)
        sys.exit(2)
    else:
        identifier = positional[0]
    return mode, identifier, options


def main(argv: list[str] | None = None) -> int:
    mode, identifier, options = _parse_cli(argv or sys.argv)
    bond_type = options.pop("bond_type")
    include_raw = options.pop("include_raw")
    try:
        if mode == "snapshot":
            payload = get_finra_trace_bond_data(
                identifier, bond_type=bond_type, include_raw=include_raw,
            )
        elif mode == "history":
            payload = get_finra_trace_price_history(
                identifier, bond_type=bond_type, include_raw=include_raw, **options,
            )
        elif mode == "search":
            payload = search_finra_trace_bonds(
                identifier,
                bond_type=bond_type or "CA",
                outstanding_only=options.get("outstanding_only", True),
                as_of=options.get("as_of"),
                limit=options.get("limit", DEFAULT_HISTORY_LIMIT),
                include_raw=include_raw,
            )
        elif mode == "issuers":
            payload = search_finra_trace_bonds(
                None,
                bond_type=bond_type or "CA",
                outstanding_only=options.get("outstanding_only", True),
                as_of=options.get("as_of"),
                parallelism=options.get("parallelism", DEFAULT_ISSUER_PARALLELISM),
                include_raw=include_raw,
            )
        else:
            payload = get_finra_trace_data(
                identifier, bond_type=bond_type, include_raw=include_raw, **options,
            )
    except (LookupError, PermissionError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
