"""Fallback for per-share facts reported only with stock-class dimensions."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from io import BytesIO
from typing import Any
from warnings import warn

_PER_SHARE_RULES: dict[str, dict[str, Any]] = {
    "0000317540": {
        "default_member": "CommonClassUndefinedMember",
        "members": {"COKE": "CommonClassUndefinedMember"},
        "facts": {
            "EarningsPerShareBasic": {
                "source_tags": ("us-gaap_EarningsPerShareBasic",),
                "strategy": "member",
                "unit": "USD/shares",
            },
            "EarningsPerShareDiluted": {
                "source_tags": ("us-gaap_EarningsPerShareDiluted",),
                "strategy": "member",
                "unit": "USD/shares",
            },
            "WeightedAverageNumberOfSharesOutstandingBasic": {
                "source_tags": (
                    "us-gaap_WeightedAverageNumberOfSharesOutstandingBasic",
                ),
                "strategy": "sum_members",
                "unit": "shares",
            },
            # The senior class's diluted count is already an as-converted
            # figure that includes the junior class, so it must not be summed.
            "WeightedAverageNumberOfDilutedSharesOutstanding": {
                "source_tags": (
                    "us-gaap_WeightedAverageNumberOfDilutedSharesOutstanding",
                ),
                "strategy": "member",
                "unit": "shares",
            },
        },
    },
    "0001067983": {
        "default_member": "EquivalentClassAMember",
        "members": {
            "BRK-A": "EquivalentClassAMember",
            "BRK-B": "EquivalentClassBMember",
        },
        "facts": {
            "EarningsPerShareBasic": {
                "source_tags": ("us-gaap_EarningsPerShareBasic",),
                "strategy": "member",
                "unit": "USD/shares",
            },
            "WeightedAverageNumberOfSharesOutstandingBasic": {
                "source_tags": (
                    "us-gaap_WeightedAverageNumberOfSharesOutstandingBasic",
                ),
                "strategy": "member",
                "unit": "shares",
            },
        },
    },
    "0000004457": {
        "default_member": "CommonClassAMember",
        "members": {
            "UHAL": "CommonClassAMember",
            "UHAL-B": "NonvotingCommonStockMember",
        },
        "facts": {
            "EarningsPerShareBasic": {
                "source_tags": (
                    "us-gaap_EarningsPerShareBasicUndistributed",
                    "us-gaap_EarningsPerShareBasicDistributed",
                ),
                "strategy": "sum_components",
                "unit": "USD/shares",
            },
            # U-Haul files diluted EPS as IncomeLossFromContinuingOperations*,
            # not EarningsPerShareDiluted; companyfacts carries neither target
            # tag, so there is nothing to conflict with.
            "EarningsPerShareDiluted": {
                "source_tags": (
                    "us-gaap_IncomeLossFromContinuingOperationsPerDilutedShare",
                ),
                "strategy": "member",
                "unit": "USD/shares",
            },
            "WeightedAverageNumberOfSharesOutstandingBasic": {
                "source_tags": (
                    "us-gaap_WeightedAverageNumberOfSharesOutstandingBasic",
                ),
                "strategy": "sum_members",
                "unit": "shares",
            },
            # U-Haul's classes are not convertible into one another, so the
            # company-wide diluted count is the sum, mirroring the basic count.
            "WeightedAverageNumberOfDilutedSharesOutstanding": {
                "source_tags": (
                    "us-gaap_WeightedAverageNumberOfDilutedSharesOutstanding",
                ),
                "strategy": "sum_members",
                "unit": "shares",
            },
        },
    },
}


def _normalize_cik(cik: str | int) -> str:
    """Return a ten-digit SEC CIK."""
    return str(cik).lstrip("0").zfill(10)


def _normalize_symbol(symbol: str | None) -> str:
    """Normalize common separators used for share-class tickers."""
    return (symbol or "").upper().replace(".", "-").replace("/", "-")


def _local_name(name: Any) -> str:
    """Return the local part of an XBRL QName."""
    return str(name or "").rsplit(":", maxsplit=1)[-1]


def discover_equity_classes(
    instance_facts: dict[str, list[dict[str, Any]]],
) -> set[str]:
    """Enumerate common-stock class members from the filing cover page.

    ``dei:EntityCommonStockSharesOutstanding`` is tagged once per class of
    common stock and never for preferred stock or listed debt, so it is a
    reliable, issuer-agnostic enumeration of the equity classes.
    """
    classes: set[str] = set()
    for fact in instance_facts.get("dei_EntityCommonStockSharesOutstanding", []):
        for value in (fact.get("dimensions") or {}).values():
            member = _local_name(value.get("member"))
            if member:
                classes.add(member)
    return classes


_CLASS_TOKEN_NOISE = ("EQUIVALENT", "COMMON", "STOCK", "CLASS", "MEMBER", "CAPITAL")


def _class_token(member: str) -> str:
    """Reduce a class member name to its distinguishing token (A, B, C, ...)."""
    token = _local_name(member).upper()
    for word in _CLASS_TOKEN_NOISE:
        token = token.replace(word, "")
    return token or _local_name(member).upper()


def _align_member(member: str, equity_classes: set[str]) -> str | None:
    """Match a statement member to a cover-page class by its class token.

    Berkshire tags the cover page with ``CommonClassAMember`` but the income
    statement with ``brka:EquivalentClassAMember``; both reduce to "A".
    """
    token = _class_token(member)
    matches = [cls for cls in equity_classes if _class_token(cls) == token]
    return matches[0] if len(matches) == 1 else None


def discover_ticker_members(
    instance_facts: dict[str, list[dict[str, Any]]],
    equity_classes: set[str],
) -> dict[str, str]:
    """Map each listed ticker to its class member using the filing cover page.

    ``dei:TradingSymbol`` is tagged per class on the same axis the issuer uses
    for that filing, so this self-corrects when an issuer moves a member
    between axes or renames it between filings (U-Haul tags the voting class
    as ``CommonStockMember`` in its 10-Qs and ``CommonClassAMember`` in its
    10-K). Tickers for listed debt are excluded because their members never
    appear on ``dei:EntityCommonStockSharesOutstanding``.
    """
    mapping: dict[str, str] = {}
    for fact in instance_facts.get("dei_TradingSymbol", []):
        symbol = _normalize_symbol(str(fact.get("value") or "").strip())
        dimensions = fact.get("dimensions") or {}
        members = [
            _local_name(value.get("member"))
            for value in dimensions.values()
            if _local_name(value.get("member")) in equity_classes
        ]
        if symbol and len(dimensions) == 1 and len(members) == 1:
            mapping[symbol] = members[0]
    return mapping


def _sole_member(fact: dict[str, Any]) -> str | None:
    """Return the member of a fact carrying exactly one dimension.

    A fact with two or more dimensions is an aggregate (U-Haul tags its
    company-wide total on the class axis AND the equity-components axis) or a
    segment breakdown, and is never class-scoped.
    """
    dimensions = fact.get("dimensions") or {}
    if len(dimensions) != 1:
        return None
    member = _local_name(next(iter(dimensions.values())).get("member"))
    return member or None


def _member_alias(
    instance_facts: dict[str, list[dict[str, Any]]],
    tag: str,
    equity_classes: set[str],
) -> dict[str, str]:
    """Map the members this concept uses onto the cover-page equity classes.

    Matching is on the MEMBER, not the axis, because issuers move the same
    member between ``StatementClassOfStockAxis`` and
    ``StatementEquityComponentsAxis`` between filings (U-Haul does this every
    year). When a concept uses an entirely separate vocabulary -- Berkshire
    reports ``brka:EquivalentClassAMember`` while its cover page says
    ``us-gaap:CommonClassAMember`` -- the members are aligned by class token,
    but only if that alignment is unambiguous and total.
    """
    used = {
        member for fact in instance_facts.get(tag, []) if (member := _sole_member(fact))
    }
    direct = {member: member for member in used if member in equity_classes}
    if direct:
        return direct
    aligned: dict[str, str] = {}
    for member in used:
        match = _align_member(member, equity_classes)
        if match:
            aligned[member] = match
    # Only trust an alias that covers the whole class set one-to-one.
    if len(aligned) == len(set(aligned.values())) == len(equity_classes):
        return aligned
    return {}


def _decimal_value(value: Any) -> Decimal | None:
    """Parse a finite numeric XBRL value."""
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return parsed if parsed.is_finite() else None


def _period_member_values(
    instance_facts: dict[str, list[dict[str, Any]]],
    tag: str,
    equity_classes: set[str],
) -> dict[tuple[str, str], dict[str, Decimal]]:
    """Group one XBRL tag by duration period and class member."""
    output: dict[tuple[str, str], dict[str, Decimal]] = {}
    alias = _member_alias(instance_facts, tag, equity_classes)
    for fact in instance_facts.get(tag, []):
        start = fact.get("start")
        end = fact.get("end")
        member = alias.get(_sole_member(fact) or "")
        value = _decimal_value(fact.get("value"))
        if not start or not end or member is None or value is None:
            continue
        output.setdefault((start, end), {}).setdefault(member, value)
    return output


def _metadata_index(
    facts_json: dict[str, Any],
) -> dict[tuple[str, str, str, str], dict]:
    """Index fiscal metadata already present in companyfacts."""
    output: dict[tuple[str, str, str, str], dict] = {}
    for namespace in facts_json.get("facts", {}).values():
        for tag_data in namespace.values():
            for entries in tag_data.get("units", {}).values():
                for entry in entries:
                    key = (
                        entry.get("accn", ""),
                        entry.get("start", ""),
                        entry.get("end", ""),
                        entry.get("form", ""),
                    )
                    if all(key):
                        output.setdefault(
                            key,
                            {
                                field: entry[field]
                                for field in ("fy", "fp", "frame")
                                if field in entry
                            },
                        )
    return output


def _has_company_fact(
    facts_json: dict[str, Any],
    tag: str,
    start: str,
    end: str,
    *,
    accession: str,
    filed: str,
) -> bool:
    """Check whether an equal-or-newer reported value already covers the period.

    Keyed on the accession number, which is the identity of a filing vintage.
    Keying on ``form`` instead would (a) miss when companyfacts carries the
    original 10-Q and the fallback parses the 10-Q/A, and (b) let the first
    vintage processed suppress every later restatement of the same period.
    Every vintage is appended, exactly as companyfacts itself does, and
    ``compute_ref_filings`` arbitrates by filing date. The ``filed`` clause
    keeps the documented invariant that a reported value from an equal-or-later
    filing always outranks a synthesized one.
    """
    tag_data = facts_json.get("facts", {}).get("us-gaap", {}).get(tag, {})
    return any(
        entry.get("start") == start
        and entry.get("end") == end
        and (entry.get("accn") == accession or str(entry.get("filed", "")) >= filed)
        for entries in tag_data.get("units", {}).values()
        for entry in entries
    )


def merge_dimensional_per_share_facts(
    facts_json: dict[str, Any],
    instance_facts: dict[str, list[dict[str, Any]]],
    filing: dict[str, Any],
    symbol: str | None = None,
    *,
    metadata_index: dict[tuple[str, str, str, str], dict] | None = None,
) -> int:
    """Merge class-dimensioned instance facts into companyfacts shape.

    Reported facts from an equal-or-later filing always win. The return value
    is the number of synthesized companyfact entries added.
    """
    cik = _normalize_cik(facts_json.get("cik", ""))
    rule = _PER_SHARE_RULES.get(cik)
    if rule is None:
        return 0

    equity_classes = discover_equity_classes(instance_facts)
    if not equity_classes:
        return 0

    normalized_symbol = _normalize_symbol(symbol)
    # Prefer the member this filing itself associates with the ticker; fall back
    # to the configured map only when the cover page is not class-dimensioned.
    filing_members = discover_ticker_members(instance_facts, equity_classes)
    member = filing_members.get(normalized_symbol) or rule["members"].get(
        normalized_symbol, rule["default_member"]
    )
    if member not in equity_classes:
        member = _align_member(member, equity_classes) or member

    metadata = (
        metadata_index if metadata_index is not None else _metadata_index(facts_json)
    )
    accession = filing.get("accessionNumber", "")
    form = filing.get("form", "")
    filed = filing.get("filingDate", "")
    added = 0

    for target_tag, spec in rule["facts"].items():
        grouped = {
            tag: _period_member_values(instance_facts, tag, equity_classes)
            for tag in spec["source_tags"]
        }
        periods = {period for values in grouped.values() for period in values}

        for start, end in sorted(periods):
            if _has_company_fact(
                facts_json,
                target_tag,
                start,
                end,
                accession=accession,
                filed=filed,
            ):
                continue

            value: Decimal | None = None
            if spec["strategy"] == "sum_members":
                member_values = grouped[spec["source_tags"][0]].get((start, end), {})
                # Never emit a partial sum: a class missing for this period
                # would silently understate a company-wide total.
                if member_values and set(member_values) == equity_classes:
                    value = sum(member_values.values(), Decimal(0))
            elif spec["strategy"] == "sum_components":
                components = [
                    values[(start, end)][member]
                    for values in grouped.values()
                    if member in values.get((start, end), {})
                ]
                if components:
                    value = sum(components, Decimal(0))
            else:
                value = (
                    grouped[spec["source_tags"][0]].get((start, end), {}).get(member)
                )

            if value is None:
                continue

            numeric_value: int | float = (
                int(value) if spec["unit"] == "shares" else float(value)
            )
            entry = {
                "start": start,
                "end": end,
                "val": numeric_value,
                "accn": accession,
                "form": form,
                "filed": filed,
            }
            entry.update(metadata.get((accession, start, end, form), {}))

            us_gaap = facts_json.setdefault("facts", {}).setdefault("us-gaap", {})
            target = us_gaap.setdefault(target_tag, {"units": {}})
            target.setdefault("units", {}).setdefault(spec["unit"], []).append(entry)
            added += 1

    return added


def _select_filings(
    submissions: dict[str, Any],
    period: str,
    fiscal_years: list[int] | None,
) -> list[dict[str, Any]]:
    """Select the smallest useful set of recent inline-XBRL filings."""
    recent = submissions.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    records = [
        {key: values[index] for key, values in recent.items() if index < len(values)}
        for index in range(len(forms))
    ]
    records = [
        record
        for record in records
        if record.get("form") in {"10-K", "10-K/A", "10-Q", "10-Q/A"}
        and str(record.get("isInlineXBRL", "0")) == "1"
        and record.get("primaryDocument")
    ]

    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for record in records:
        form_type = record["form"].split("/")[0]
        key = (form_type, record.get("reportDate", ""))
        if key not in seen:
            deduped.append(record)
            seen.add(key)

    annual = [record for record in deduped if record["form"].startswith("10-K")]
    quarterly = [record for record in deduped if record["form"].startswith("10-Q")]
    annual_mode = period in {"annual", "yoy"}

    def report_year(record: dict[str, Any]) -> int | None:
        """Return the calendar year of a filing's report date."""
        try:
            return int(str(record.get("reportDate", ""))[:4])
        except ValueError:
            return None

    if fiscal_years:
        years = set(fiscal_years)
        # Always read the newest 10-K in addition to the year-matched ones, so a
        # restatement (e.g. a stock split) is present and can win on filing date.
        annual_selected = []
        seen_accn: set[str] = set()
        for record in annual[:1] + [r for r in annual if report_year(r) in years]:
            accession = record.get("accessionNumber", "")
            if accession not in seen_accn:
                seen_accn.add(accession)
                annual_selected.append(record)
        quarterly_selected = [
            record for record in quarterly if report_year(record) in years
        ]
    else:
        annual_selected = annual[:1]
        quarterly_selected = quarterly[:4]

    selected = annual_selected if annual_mode else annual_selected + quarterly_selected
    return sorted(selected, key=lambda record: record.get("filingDate", ""))


def _instance_url(cik: str, filing: dict[str, Any]) -> str:
    """Build the SEC extracted-instance URL for an inline filing."""
    accession = filing["accessionNumber"].replace("-", "")
    primary = filing["primaryDocument"]
    stem = primary.rsplit(".", 1)[0]
    return (
        f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
        f"{accession}/{stem}_htm.xml"
    )


async def add_dimensional_per_share_facts(
    facts_json: dict[str, Any],
    symbol: str | None,
    period: str,
    fiscal_years: list[int] | None,
    use_cache: bool,
) -> int:
    """Fetch recent filing instances and add configured dimensional facts."""
    normalized_cik = _normalize_cik(facts_json.get("cik", ""))
    if normalized_cik not in _PER_SHARE_RULES:
        return 0

    # pylint: disable=import-outside-toplevel
    from aiohttp_client_cache import SQLiteBackend
    from aiohttp_client_cache.session import CachedSession
    from openbb_core.app.utils import get_user_cache_directory
    from openbb_core.provider.utils.helpers import amake_request, amake_requests
    from openbb_sec.utils.definitions import HEADERS
    from openbb_sec.utils.xbrl_taxonomy_helper import XBRLParser

    async def json_callback(response, _):
        """Return a successful SEC response as JSON."""
        response.raise_for_status()
        return await response.json()

    async def bytes_callback(response, _):
        """Return a successful SEC response as bytes."""
        response.raise_for_status()
        return await response.read()

    try:
        submissions_url = f"https://data.sec.gov/submissions/CIK{normalized_cik}.json"
        if use_cache:
            cache_dir = f"{get_user_cache_directory()}/http/sec_dimensional_facts"
            async with CachedSession(
                cache=SQLiteBackend(cache_dir, expire_after=3600 * 6)
            ) as session:
                submissions = await amake_request(
                    submissions_url,
                    headers=HEADERS,
                    session=session,
                    response_callback=json_callback,
                    timeout=300,
                )
        else:
            submissions = await amake_request(
                submissions_url,
                headers=HEADERS,
                response_callback=json_callback,
                timeout=300,
            )

        if not isinstance(submissions, dict):
            return 0
        filings = _select_filings(submissions, period, fiscal_years)
        if not filings:
            return 0

        urls = [_instance_url(normalized_cik, filing) for filing in filings]
        request_kwargs: dict[str, Any] = {
            "headers": HEADERS,
            "response_callback": bytes_callback,
            "return_exceptions": True,
            "timeout": 300,
        }
        if use_cache:
            cache_dir = f"{get_user_cache_directory()}/http/sec_dimensional_facts"
            request_kwargs["session"] = CachedSession(
                cache=SQLiteBackend(cache_dir, expire_after=3600 * 6)
            )
        responses = await amake_requests(urls, **request_kwargs)

        if len(responses) != len(filings):
            # amake_requests drops falsy results, which would silently shift
            # every filing after the dropped one onto the wrong response.
            warn(
                f"Skipping dimensional per-share facts for CIK {normalized_cik}: "
                f"expected {len(filings)} instance responses, got {len(responses)}."
            )
            return 0

        parser = XBRLParser()
        metadata = _metadata_index(facts_json)
        added = 0
        for filing, response in zip(filings, responses):
            if isinstance(response, Exception) or not isinstance(response, bytes):
                continue
            try:
                _, _, instance_facts = parser.parse_instance(BytesIO(response))
            except Exception as error:
                warn(
                    f"Failed to parse dimensional facts from "
                    f"{filing.get('accessionNumber', 'SEC filing')}: {error}"
                )
                continue
            try:
                added += merge_dimensional_per_share_facts(
                    facts_json,
                    instance_facts,
                    filing,
                    symbol,
                    metadata_index=metadata,
                )
            except Exception as error:  # one bad filing must not abandon the rest
                warn(
                    f"Failed to merge dimensional facts from "
                    f"{filing.get('accessionNumber', 'SEC filing')}: {error}"
                )
                continue
        return added
    except Exception as error:  # The original companyfacts result remains usable.
        warn(
            f"Failed to load dimensional per-share facts for CIK {normalized_cik}: "
            f"{error}"
        )
        return 0
