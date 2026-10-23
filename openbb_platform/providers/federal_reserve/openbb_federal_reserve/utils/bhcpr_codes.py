"""Bind each BHCPR schema line item to its FFIEC CSV code."""

from __future__ import annotations

import re
from typing import Any

from openbb_federal_reserve.utils.bhcpr import (
    _contained,
    _normalize,
    _token_list,
    _tokens,
    match_index,
)

_ID = re.compile(r"^([A-Za-z]+)(\d+)$")
_PG = re.compile(r"^(PG RATIO:|PG RANK:)\s*", re.IGNORECASE)
_DERIVED = ("PHSR", "RKSR")


def _prefix(code: str) -> str:
    """Return a CSV code's alphabetic prefix (e.g. ``BHSR``)."""
    match = _ID.match(code)
    return match.group(1) if match else ""


def _numeric_id(code: str) -> str:
    """Return a CSV code's numeric id (e.g. ``499``)."""
    match = _ID.match(code)
    return match.group(2) if match else ""


_OVERRIDES: dict[tuple[str, str, str], str] = {
    (
        "Parent Company Balance Sheet",
        "Assets Excluding Investment in Subsidiaries",
        "Balances Due from Subsidiaries and Related Institutions",
    ): "BHSR499",
    (
        "Parent Company Balance Sheet",
        "Assets Excluding Investment in Subsidiaries",
        "Premises, Furniture, Fixtures and Equipment",
    ): "BHCP2145",
    (
        "Parent Company Analysis—Part 1",
        "Past Due and Nonaccrual Loans and Leases as Percent of Total Loans and Leases",
        "90 Days and Over Past Due",
    ): "BHSR381",
    (
        "Parent Company Analysis—Part 1",
        "Past Due and Nonaccrual Loans and Leases as Percent of Total Loans and Leases",
        "Nonaccrual",
    ): "BHSR382",
    (
        "Parent Company Analysis—Part 1",
        "Past Due and Nonaccrual Loans and Leases as Percent of Total Loans and Leases",
        "Total",
    ): "BHSR383",
    (
        "Parent Company Analysis—Part 1",
        "Guaranteed Loans as a Percentage of Equity Capital",
        "To Subsidiary Holding Companies",
    ): "BHSR388",
    (
        "Parent Company Analysis—Part 1",
        "As a Percentage of Consolidated Holding Company Assets",
        "Combined Thrift Assets",
    ): "BHSR947",
    (
        "Regulatory Capital Components and Ratios",
        "Capital Ratios",
        "Tier 1 Leverage",
    ): "BHSR1340",
    (
        "Non-Interest Income and Expenses",
        "Percent of Adjusted Operating Income (Tax Equivalent)",
        "Insurance Activities Revenue",
    ): "BHSR1198",
    (
        "Liabilities and Changes in Capital",
        "Equity Capital",
        "Perpetual Preferred Stock (Including Surplus)",
    ): "BHCK3283",
    (
        "Parent Company Balance Sheet",
        "Liabilities and Capital",
        "Accumulated Other Comprehensive Income",
    ): "BHSR1011",
    (
        "Relative Income Statement and Margin Analysis",
        "Percent of Average Assets",
        "Realized Gains (Losses) on Held-to-Maturity Securities",
    ): "BHSR731",
    (
        "Relative Income Statement and Margin Analysis",
        "Percent of Average Assets",
        "Realized Gains (Losses) on Available-for-Sale Securities",
    ): "BHSR732",
    (
        "Past Due and Nonaccrual Loans and Leases (continued)",
        "Memoranda",
        "Closed-End—90 Days and Over Past Due, Junior Lien",
    ): "BHSR1185",
    (
        "Assets",
        "",
        "Total Assets",
    ): "BHCK2170",
    (
        "Liabilities and Changes in Capital",
        "Total Equity Capital, Including Minority Interest",
        "Total Liabilities and Capital",
    ): "BHCK3300",
    (
        "Liabilities and Changes in Capital",
        "Changes in Holding Company Equity Capital",
        "Changes in the Debit to ESOP Liability",
    ): "BHCK4591",
    (
        "Income Statement—Revenues and Expenses",
        "",
        "Net Income Attributable to Holding Company",
    ): "BHCK4340",
    (
        "Summary Ratios",
        "",
        "Net Income ($000)",
    ): "BHCK4340",
    (
        "Non-Interest Income and Expenses",
        "Non-Interest Income and Expenses ($000)",
        "Total Overhead Expenses",
    ): "BHSR967",
    (
        "Relative Income Statement and Margin Analysis",
        "Percent of Average Assets",
        "Overhead Expense",
    ): "BHSR019",
    (
        "Liquidity and Funding",
        "Percent of Total Assets",
        "Secured Federal Funds Purchased",
    ): "BHSR1249",
    (
        "Assets",
        "",
        "Allowance for Credit Losses on Loans and Leases",
    ): "BHSR110",
    (
        "Liquidity and Funding",
        "Percent of Total Assets",
        "Net Loans and Leases",
    ): "BHSR146",
    (
        "Insurance and Broker-Dealer Activities",
        "Analysis Ratios",
        "Credit-Related Premium Income / Total Premium Income",
    ): "BHSR1200",
    (
        "Parent Company Balance Sheet",
        "Liabilities and Capital",
        "Common Surplus",
    ): "BHCP3240",
    (
        "Servicing, Securitization, and Asset Sale Activities—Part 1",
        "Securitization Activities",
        "Home Equity Lines",
    ): "BHSR1069",
    (
        "Servicing, Securitization, and Asset Sale Activities—Part 1",
        "Securitization Activities",
        "Credit Card Receivables",
    ): "BHSR1070",
    (
        "Allowance and Net Credit Losses on Loans and Leases",
        "Change: Allowance for Credit Losses on Loans and Leases, Excluding Allocated Transfer Risk Reserve",
        "Ending Balance",
    ): "BHSR868",
    (
        "Liabilities and Changes in Capital",
        "Changes in Holding Company Equity Capital",
        "Net Income",
    ): "BHCP4340",
}

_LOAN_TYPES = (
    ("1–4 family", "1_4_family"),
    ("1-4 family", "1_4_family"),
    ("home equity", "home_equity"),
    ("credit card", "credit_card"),
    ("auto", "auto"),
    ("commercial and industrial", "c_i"),
    ("c&i", "c_i"),
    ("all other", "all_other"),
)


def _loan_type(text: str) -> str | None:
    """Return the loan-type dimension tag found in a lowercased caption."""
    return next((tag for key, tag in _LOAN_TYPES if key in text), None)


def _pastdue_bucket(text: str) -> str | None:
    """Return the past-due/net-loss/nonaccrual bucket of a lowercased caption."""
    if any(key in text for key in ("30-89", "30–89", "30 to 89")):
        return "30_89"
    if any(
        key in text for key in ("90+", "90 days and over", "90 days or more", "90 days")
    ):
        return "90_over"
    if "net loss" in text:
        return "net_loss"
    if "nonaccrual" in text:
        return "nonaccrual"
    return None


_PASTDUE_LOAN_TYPES = (
    ("owner occ", "owner_occupied"),
    ("owner-occ", "owner_occupied"),
    ("closed-end", "closed_end"),
    ("closed end", "closed_end"),
    ("revolving", "revolving"),
    ("multifamily", "multifamily"),
    ("nonfarm nonres", "nonfarm_nonres"),
    ("nonfarm non-res", "nonfarm_nonres"),
    ("commercial real estate", "commercial_re"),
    ("commercial re", "commercial_re"),
    ("construction", "construction"),
    ("land dev", "construction"),
    ("farmland", "farmland"),
    ("credit card", "credit_card"),
    ("1–4 family", "1_4_family"),
    ("1-4 family", "1_4_family"),
    ("commercial and industrial", "c_i"),
    ("c&i", "c_i"),
    ("real estate", "real_estate"),
    ("individuals", "individuals"),
    ("depository", "depository"),
    ("dep inst", "depository"),
    ("foreign gov", "foreign_government"),
    ("agricultural", "agricultural"),
)


def _pastdue_loan(text: str) -> str | None:
    """Return the past-due matrix loan-type tag of a lowercased caption."""
    return next((tag for key, tag in _PASTDUE_LOAN_TYPES if key in text), None)


def _pastdue_sig(descriptions: dict[str, str]) -> dict[tuple, str]:
    """Map each ``(loan type, bucket)`` to its clean past-due ratio code."""
    signatures: dict[tuple, str] = {}
    for base, text in descriptions.items():
        lower = text.lower()
        if _prefix(base) in _DERIVED or "/" not in text:
            continue
        if "securitiz" in lower or "managed" in lower:
            continue
        numerator = lower.split("/", 1)[0]
        bucket, loan = _pastdue_bucket(numerator), _pastdue_loan(numerator)
        if bucket is None or loan is None:
            continue
        signatures.setdefault((loan, bucket), base)
    return signatures


def _pastdue_bind(
    items: list[tuple[dict[str, Any], str]],
    signatures: dict[tuple, str],
    used: set[str],
) -> dict[int, str]:
    """Bind past-due matrix rows to their loan-type ratio code by dimension join."""
    bound: dict[int, str] = {}
    for position, (item, context) in enumerate(items):
        label = item["label"].lower()
        loan = _pastdue_loan(label)
        bucket = _pastdue_bucket(label) or _pastdue_bucket(context.lower())
        if loan is None or bucket is None:
            continue
        code = signatures.get((loan, bucket))
        if code and code not in used:
            bound[position] = code
            used.add(code)
    return bound


_PARENT_INCOME = re.compile(
    r"income|gains|losses|expense|dividend|interest from|\bfee|salaries|taxes|undistributed|provision",
    re.IGNORECASE,
)
_PARENT_SYNONYMS = {
    "borrowing": "loan",
    "borrowings": "loan",
    "loans": "loan",
    "advances": "loan",
    "advance": "loan",
    "bonds": "note",
    "notes": "note",
    "debentures": "note",
    "balances": "cash",
    "banks": "bank",
    "nonbanks": "nonbank",
    "subsidiaries": "subsidiary",
    "companies": "company",
    "receivables": "receivable",
    "repos": "repo",
    "repurchase": "repo",
    "resell": "repo",
    "reverse": "repo",
}


def _parent_entity(text: str) -> str | None:
    """Return the subsidiary-entity dimension (nonbank / bhcs / bank) of a caption."""
    lower = text.lower()
    if "nonbank" in lower:
        return "nonbank"
    if "holding" in lower or "bhcs" in lower:
        return "bhcs"
    if "bank" in lower:
        return "bank"
    return None


def _parent_norm(text: str) -> set[str]:
    """Tokenise a caption with parent-balance-sheet synonyms and plurals folded."""
    return {_PARENT_SYNONYMS.get(token, token) for token in _tokens(text)}


def _parent_bind(
    items: list[tuple[dict[str, Any], str]], descriptions: dict[str, str]
) -> dict[int, str]:
    """Bind parent-balance-sheet rows to their ``BHCP`` code by subsidiary entity."""
    candidates = [
        (base, clean, _parent_entity(clean))
        for base, description in descriptions.items()
        if _prefix(base) not in _DERIVED
        and not _PARENT_INCOME.search(description)
        and (_prefix(base) == "BHCP" or "parent" in description.lower())
        and "percent" not in description.lower()
        and "/" not in description
        for clean in [
            re.sub(
                r"\s*\((?:bhc )?parent(?:-only)?\)",
                "",
                description,
                flags=re.IGNORECASE,
            )
        ]
    ]
    candidate_norms = [
        (base, _parent_norm(clean), ent) for base, clean, ent in candidates
    ]
    rows: list[tuple[int, str | None, set[str]]] = []
    current_entity: str | None = None
    entity_context: str | None = None
    for position, (item, context) in enumerate(items):
        lower = item["label"].lower()
        if context != entity_context:
            current_entity, entity_context = None, context
        if "investment in" in lower and _parent_entity(lower):
            current_entity = _parent_entity(lower)
        rows.append(
            (
                position,
                _parent_entity(lower) or current_entity,
                _parent_norm(item["label"]),
            )
        )

    bound: dict[int, str] = {}
    used: set[str] = set()

    def consistent(entity: str | None, candidate_entity: str | None) -> bool:
        """Whether a row's entity agrees with a candidate code's entity."""
        return candidate_entity == entity if entity else candidate_entity is None

    for position, entity, query in rows:
        for base, other, candidate_entity in candidate_norms:
            if (
                base not in used
                and consistent(entity, candidate_entity)
                and query == other
            ):
                bound[position] = base
                used.add(base)
                break
    for position, entity, query in rows:
        if position in bound:
            continue
        scored: list[tuple[float, str]] = []
        for base, other, candidate_entity in candidate_norms:
            if base in used or not consistent(entity, candidate_entity):
                continue
            overlap = len(query & other) / len(query | other) if query | other else 0.0
            if query and query <= other:
                overlap = max(overlap, 0.8)
            scored.append((overlap, base))
        if scored:
            best_overlap, base = max(scored)
            if best_overlap >= (0.34 if entity else 0.6):
                bound[position] = base
                used.add(base)
    return bound


def _scope(text: str) -> str | None:
    """Return the securitized/managed scope dimension of a lowercased caption."""
    if "managed" in text:
        return "managed"
    if "securitiz" in text:
        return "securitized"
    return None


def _securitization_sig(descriptions: dict[str, str]) -> dict[tuple, str]:
    """Map each securitization matrix dimension signature to its CSV code."""
    signatures: dict[tuple, str] = {}
    for base, text in descriptions.items():
        if _prefix(base) in _DERIVED:
            continue
        lower = text.lower()
        bucket, scope = _pastdue_bucket(lower), _scope(lower)
        if bucket is None or scope is None:
            continue
        measure = "pct" if ("percent" in lower or "/managed assets" in lower) else "amt"
        loan = _loan_type(lower)
        total = loan is None and "total" in lower
        signatures.setdefault((loan, bucket, measure, scope, total), base)
    return signatures


def _matrix_bind(
    items: list[tuple[dict[str, Any], str]],
    section_percent: bool,
    signatures: dict[tuple, str],
    used: set[str],
) -> dict[int, str]:
    """Bind securitization matrix rows to codes by exact dimension join."""
    bound: dict[int, str] = {}
    for position, (item, context) in enumerate(items):
        ctx, label = context.lower(), item["label"].lower()
        bucket = _pastdue_bucket(ctx) or _pastdue_bucket(label)
        scope = _scope(ctx) or _scope(label)
        if bucket is None or scope is None:
            continue
        loan = _loan_type(label) or _loan_type(ctx)
        total = loan is None and "total" in label
        if loan is None and not total:
            continue
        measure = "pct" if ("percent" in ctx or (section_percent and bucket)) else "amt"
        code = signatures.get((loan, bucket, measure, scope, total))
        if code and code not in used:
            bound[position] = code
            used.add(code)
    return bound


def _sec_block(text: str) -> str | None:
    """Return the securitization seller/retained/outstanding block of a caption."""
    lower = text.lower()
    if "seller" in lower and "interest" in lower:
        return "seller"
    if "retained credit exposure of" in lower or (
        "retained credit exposure" in lower and "/" not in lower
    ):
        return "retained"
    if "outstanding princip" in lower or "securitization activities" in lower:
        return "outstanding"
    return None


def _secblock_sig(descriptions: dict[str, str]) -> dict[tuple, str]:
    """Map each securitization ``(block, loan type)`` to its outstanding/exposure code."""
    signatures: dict[tuple, str] = {}
    for base, text in descriptions.items():
        if _prefix(base) in _DERIVED or "/" in text or "percent" in text.lower():
            continue
        block, loan = _sec_block(text), _loan_type(text.lower())
        if block and loan:
            signatures.setdefault((block, loan), base)
    return signatures


def _secblock_bind(
    items: list[tuple[dict[str, Any], str]],
    signatures: dict[tuple, str],
    used: set[str],
) -> dict[int, str]:
    """Bind securitization seller/retained/outstanding rows by (block, loan) join."""
    bound: dict[int, str] = {}
    for position, (item, context) in enumerate(items):
        if "percent" in context.lower():
            continue
        block = _sec_block(context)
        loan = _loan_type(item["label"].lower())
        if block is None or loan is None:
            continue
        code = signatures.get((block, loan))
        if code and code not in used:
            bound[position] = code
            used.add(code)
    return bound


def _period_dates(csv: dict[str, Any]) -> dict[str, str]:
    """Map each CSV period suffix to its ``YYYY-MM-DD`` date."""
    return {
        suffix: f"{date[:4]}-{date[4:6]}-{date[6:8]}"
        for suffix, date in csv["periods"].items()
        if len(date) == 8
    }


def _series(
    csv: dict[str, Any],
) -> tuple[
    dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]
]:
    """Return ``(primary, peer, pct)`` value series keyed for value matching."""
    dates = _period_dates(csv)
    primary: dict[str, dict[str, Any]] = {}
    peer: dict[str, dict[str, Any]] = {}
    pct: dict[str, dict[str, Any]] = {}
    for base, periods in csv["values"].items():
        prefix, item_id = _prefix(base), _numeric_id(base)
        cells = {
            dates[suffix]: value
            for suffix, value in periods.items()
            if value is not None and suffix in dates
        }
        if prefix == "PHSR":
            peer[item_id] = cells
        elif prefix == "RKSR":
            pct[item_id] = cells
        else:
            primary[base] = cells
    return primary, peer, pct


def _close(printed: float, coded: float) -> bool:
    """Whether a printed value equals a coded value (coded amounts are ×1000)."""
    printed, coded = float(printed), float(coded)
    return (
        abs(printed - coded) <= 0.5001
        or abs(printed - coded * 1000) <= abs(coded) * 1e-3 + 1
    )


def _printed_values(row: dict[str, Any]) -> dict[tuple[str, str], Any]:
    """Return a PDF row's values keyed by ``(sub-column, iso-date)``."""
    out: dict[tuple[str, str], Any] = {}
    for date, period in row.get("periods", {}).items():
        for sub, value in period.items():
            column = {"amount": "bhc", "bhc": "bhc", "peer": "peer", "pct": "pct"}.get(
                sub
            )
            if column and value is not None:
                out[(column, date)] = value
    return out


def _value_code(
    row: dict[str, Any],
    primary: dict[str, dict[str, Any]],
    peer: dict[str, dict[str, Any]],
    pct: dict[str, dict[str, Any]],
    used: set[str],
) -> str | None:
    """Return the unused code whose full fingerprint certainly matches the row."""
    printed = _printed_values(row)
    if len(printed) < 2:
        return None
    scored: list[tuple[int, str]] = []
    for base, cells in primary.items():
        if base in used:
            continue
        item_id = _numeric_id(base)
        fingerprint = {("bhc", date): value for date, value in cells.items()}
        fingerprint.update(
            {("peer", date): value for date, value in peer.get(item_id, {}).items()}
        )
        fingerprint.update(
            {("pct", date): value for date, value in pct.get(item_id, {}).items()}
        )
        agree = nonzero = conflict = 0
        for key, value in printed.items():
            if key not in fingerprint:
                continue
            if _close(value, fingerprint[key]):
                agree += 1
                nonzero += int(float(fingerprint[key]) != 0)
            else:
                conflict += 1
        if conflict == 0 and agree >= 2 and nonzero:
            scored.append((agree, base))
    if not scored:
        return None
    scored.sort(key=lambda pair: (-pair[0], pair[1]))
    if len(scored) > 1 and scored[0][0] == scored[1][0]:
        return None
    return scored[0][1]


def _description_sim(label: str, description: str) -> float:
    """Word-overlap of a guide label and a CSV item description."""
    query, candidate = _tokens(label), _tokens(_PG.sub("", description))
    if not query or not candidate:
        return 0.0
    overlap = len(query & candidate) / len(query | candidate)
    if _contained(_token_list(label), _token_list(description)) or _contained(
        _token_list(description), _token_list(label)
    ):
        overlap = max(overlap, 0.75)
    return overlap


def _items_with_context(entry: dict[str, Any]) -> list[tuple[dict[str, Any], str]]:
    """Return a section's items paired with their nearest sub-header."""
    items: list[tuple[dict[str, Any], str]] = []
    context = ""
    for element in entry["entries"]:
        if element["kind"] == "subheader":
            context = element["label"]
        else:
            items.append((element, context))
    return items


def _align(
    items: list[tuple[dict[str, Any], str]], rows: list[dict[str, Any]]
) -> dict[int, int]:
    """Align schema items to PDF rows (positional when counts match, else fuzzy)."""
    positional = len(items) == len(rows) and bool(rows)
    if positional:
        probe: set[int] = set()
        for position, (item, _context) in enumerate(items):
            index = match_index(item["label"], rows, probe, exact_only=True)
            if index is None:
                continue
            probe.add(index)
            if index != position:
                positional = False
                break
    if positional:
        return {position: position for position in range(len(items))}
    n, m = len(items), len(rows)
    score = [
        [
            max(
                _description_sim(items[i][0]["label"], rows[j]["label"]),
                _description_sim(
                    f"{items[i][1]} {items[i][0]['label']}", rows[j]["label"]
                ),
            )
            for j in range(m)
        ]
        for i in range(n)
    ]
    dp = [[0.0] * (m + 1) for _ in range(n + 1)]
    back = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            best, move = dp[i - 1][j], 0
            if dp[i][j - 1] > best:
                best, move = dp[i][j - 1], 1
            if (
                score[i - 1][j - 1] >= 0.5
                and dp[i - 1][j - 1] + score[i - 1][j - 1] > best
            ):
                best, move = dp[i - 1][j - 1] + score[i - 1][j - 1], 2
            dp[i][j], back[i][j] = best, move
    assigned: dict[int, int] = {}
    i, j = n, m
    while i > 0 and j > 0:
        move = back[i][j]
        if move == 2:
            assigned[i - 1] = j - 1
            i, j = i - 1, j - 1
        elif move == 0:
            i -= 1
        else:
            j -= 1
    return assigned


_INSURANCE_CONCEPTS = (
    (("separate account", "asset"), ("life",), ("separate account", "asset")),
    (("separate account", "liab"), ("life",), ("separate account", "liab")),
    (("reinsurance recoverable",), ("life",), ("reinsurance recoverable", "life")),
    (
        ("reinsurance recoverable",),
        ("property",),
        ("reinsurance recoverable", "property"),
    ),
)
_INSURANCE_LINES = {"life": ("l/h", "life"), "property": ("p/c", "p&c", "property")}


def _insurance_bind(
    items: list[tuple[dict[str, Any], str]],
    descriptions: dict[str, str],
    used: set[str],
) -> dict[int, str]:
    """Bind insurance underwriting balance-sheet rows by concept-keyword join."""
    bound: dict[int, str] = {}
    for position, (item, _context) in enumerate(items):
        label = item["label"].lower()
        for label_keys, lines, desc_keys in _INSURANCE_CONCEPTS:
            if not all(key in label for key in label_keys):
                continue
            if not any(
                tag in label for line in lines for tag in _INSURANCE_LINES[line]
            ):
                continue
            matches = [
                base
                for base, description in descriptions.items()
                if base not in used
                and "/" not in description
                and all(key in description.lower() for key in desc_keys)
            ]
            if len(matches) == 1:
                bound[position] = matches[0]
                used.add(matches[0])
            break
    return bound


def bind_codes(
    schema: list[dict[str, Any]],
    filings: list[tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]],
    description_floor: float = 0.6,
) -> dict[str, Any]:
    """Attach a ``code`` and ``code_source`` to each schema item and report counts."""
    per_filing = [
        (
            {_normalize(name): rows for name, rows in pdf.items()},
            *_series(csv),
            csv["descriptions"],
        )
        for pdf, csv in filings
    ]
    counts = {
        "value": 0,
        "description": 0,
        "sequence": 0,
        "matrix": 0,
        "curated": 0,
        "unbound": 0,
    }
    unbound: list[tuple[str, str]] = []
    conflicts: list[tuple[str, ...]] = []
    descriptions: dict[str, str] = {}
    for *_ignored, filing_desc in per_filing:
        for base, text in filing_desc.items():
            descriptions.setdefault(base, text)
    ranked_ids = {
        item_id for _pdf, _pr, _peer, pct, _d in per_filing for item_id in pct
    }
    securitization = _securitization_sig(descriptions)
    secblock = _secblock_sig(descriptions)
    pastdue = _pastdue_sig(descriptions)
    resolved: set[str] = set()

    for entry in schema:
        items = _items_with_context(entry)
        candidates: dict[int, set[str]] = {}
        for pdf_sections, primary, peer, pct, _filing_desc in per_filing:
            rows = pdf_sections.get(_normalize(entry["section"]), [])
            aligned = _align(items, rows)
            used_local: set[str] = set()
            for position, (_item, _context) in enumerate(items):
                if position not in aligned:
                    continue
                code = _value_code(
                    rows[aligned[position]], primary, peer, pct, used_local
                )
                if code:
                    used_local.add(code)
                    candidates.setdefault(position, set()).add(code)
        codes: dict[int, tuple[str, str]] = {}

        def _context_label(position: int) -> str:
            """Return an item's label folded with its sub-header."""
            item, context = items[position]
            return f"{context} {item['label']}" if context else item["label"]

        scored = sorted(
            (
                (
                    _description_sim(
                        _context_label(position), descriptions.get(code, "")
                    ),
                    position,
                    code,
                )
                for position, cset in candidates.items()
                for code in cset
            ),
            key=lambda triple: (-triple[0], triple[1], triple[2]),
        )
        taken_positions: set[int] = set()
        used_codes: set[str] = set()
        for _score, position, code in scored:
            if position in taken_positions or code in used_codes:
                continue
            codes[position] = (code, "value")
            taken_positions.add(position)
            used_codes.add(code)
        conflicts.extend(
            (entry["section"], items[position][0]["label"], *sorted(cset)[:2])
            for position, cset in candidates.items()
            if len(cset) > 1
        )
        if "Servicing" in entry["section"]:
            section_percent = sum(
                "percent" in element["label"].lower()
                for element in entry["entries"]
                if element["kind"] == "subheader"
            ) >= max(1, sum(e["kind"] == "subheader" for e in entry["entries"]) / 2)
            matrix = _matrix_bind(items, section_percent, securitization, set())
            for position, code in matrix.items():
                codes = {
                    other: binding
                    for other, binding in codes.items()
                    if binding[0] != code or other == position
                }
                codes[position] = (code, "matrix")
            used_codes = {code for code, _source in codes.values()}
            for position, code in _secblock_bind(items, secblock, used_codes).items():
                codes.setdefault(position, (code, "matrix"))
        if entry["section"].startswith("Past Due and Nonaccrual Loans and Leases"):
            used_codes = {code for code, _source in codes.values()}
            for position, code in _pastdue_bind(items, pastdue, used_codes).items():
                codes.setdefault(position, (code, "matrix"))
        if entry["section"] == "Parent Company Balance Sheet":
            for position, code in _parent_bind(items, descriptions).items():
                codes.setdefault(position, (code, "matrix"))
        if entry["section"] == "Insurance and Broker-Dealer Activities":
            used_codes = {code for code, _source in codes.values()}
            for position, code in _insurance_bind(
                items, descriptions, used_codes
            ).items():
                codes.setdefault(position, (code, "matrix"))
        matrix_section = (
            "Servicing" in entry["section"]
            or "Past Due" in entry["section"]
            or entry["section"] == "Parent Company Balance Sheet"
        )
        used_codes = {code for code, _source in codes.values()}
        for position, (item, context) in enumerate(items):
            if position in codes:
                continue
            if matrix_section:
                target = _normalize(item["label"])
                exact = [
                    base
                    for base, description in descriptions.items()
                    if base not in used_codes
                    and base not in resolved
                    and _normalize(description) == target
                ]
                if len(exact) == 1:
                    codes[position] = (exact[0], "description")
                    used_codes.add(exact[0])
                continue
            label = f"{context} {item['label']}" if context else item["label"]
            peer_count = (
                "number of" in item["label"].lower() and "peer" in label.lower()
            )
            scored_codes = sorted(
                (
                    (_description_sim(label, description), base)
                    for base, description in descriptions.items()
                    if base not in used_codes
                    and base not in resolved
                    and (peer_count or _prefix(base) not in _DERIVED)
                    and "percent change" not in description.lower()
                ),
                reverse=True,
            )
            if scored_codes and scored_codes[0][0] >= description_floor:
                best_score, best_code = scored_codes[0]
                runner_score, runner_code = (
                    scored_codes[1] if len(scored_codes) > 1 else (0.0, None)
                )
                same_metric = runner_code is not None and _normalize(
                    descriptions[best_code]
                ) == _normalize(descriptions[runner_code])
                if best_score - runner_score >= 0.1 or same_metric:
                    codes[position] = (best_code, "description")
                    used_codes.add(best_code)
        for position, (item, context) in enumerate(items):
            if position in codes:
                continue
            code = _OVERRIDES.get((entry["section"], context, item["label"]))
            if code:
                codes[position] = (code, "curated")
        for position, (item, _context) in enumerate(items):
            code, source = codes.get(position, (None, None))
            item["code"], item["code_source"] = code, source
            if code and source:
                resolved.add(code)
                counts[source] += 1
                if source in ("matrix", "curated") or not item.get("basis"):
                    item["basis"] = _infer_basis(
                        item["label"], code, descriptions, ranked_ids
                    )
            else:
                counts["unbound"] += 1
                unbound.append((entry["section"], item["label"]))

    return {"counts": counts, "unbound": unbound, "conflicts": conflicts}


def _infer_basis(
    label: str, code: str, descriptions: dict[str, str], ranked_ids: set[str]
) -> str:
    """Complete a bound item's basis from its code, so no dollar item is basis-null."""
    item_id = _numeric_id(code)
    description = descriptions.get(code, "")
    if re.search(r"\(x\)\s*$", label, re.IGNORECASE):
        return "Multiple (X)"
    if re.match(r"(?i)^number\b", label) or "number of" in label.lower():
        return "Number"
    is_ratio = bool(re.search(r"[A-Za-z]{2,}\s*/|/\s*[A-Za-z]{2,}", description))
    if (
        (code.startswith("BHSR") and item_id in ranked_ids)
        or is_ratio
        or "percent" in description.lower()
    ):
        return "Percent"
    return "Dollar Amount in Thousands"
