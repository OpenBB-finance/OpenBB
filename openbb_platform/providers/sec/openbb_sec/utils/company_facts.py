"""SEC Company Facts Utilities."""

# pylint: disable=import-outside-toplevel

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from aiohttp_client_cache import SQLiteBackend
from aiohttp_client_cache.session import CachedSession
from openbb_core.app.utils import get_user_cache_directory
from openbb_core.provider.utils.helpers import amake_request
from openbb_sec.utils.definitions import HEADERS
from openbb_sec.utils.helpers import symbol_map
from pandas import isna

if TYPE_CHECKING:
    from pandas import DataFrame

TAXONOMY_DIR = Path(__file__).parent


@lru_cache(maxsize=8)
def load_taxonomy(name: str) -> dict:
    """Load a taxonomy mapping JSON file by name (cached in memory)."""
    filepath = TAXONOMY_DIR / f"{name}_taxonomy.json"
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


async def get_company_facts(
    symbol: str,
    use_cache: bool = True,
) -> dict:
    """Fetch all XBRL facts for a company from SEC EDGAR.

    Source: https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json

    Parameters
    ----------
    symbol : str
        The ticker symbol.
    use_cache : bool
        Whether to use cache. Defaults to True.

    Returns
    -------
    dict
        The raw company facts JSON response.
    """
    cik = await symbol_map(symbol, use_cache=use_cache)
    if not cik:
        return {}

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    response: dict = {}

    if use_cache:
        cache_dir = f"{get_user_cache_directory()}/http/sec_company_facts"
        async with CachedSession(
            cache=SQLiteBackend(cache_dir, expire_after=3600 * 24)
        ) as session:
            await session.delete_expired_responses()
            response = await amake_request(url, headers=HEADERS, session=session)  # type: ignore
    else:
        response = await amake_request(url, headers=HEADERS)  # type: ignore

    return response


def resolve_fact(
    facts: dict,
    try_order: list[str],
    taxonomy: str = "us-gaap",
    units: str = "USD",
) -> list[dict]:
    """Resolve a standardized line item from company facts using try_order.

    Iterates through ALL concepts in try_order and merges data, deduplicating
    by period end date. Earlier concepts in try_order take priority for
    overlapping periods, so newer XBRL tags and older tags are both captured.

    Note: A single field's time series may be sourced from different XBRL
    concepts across periods (e.g., a newer tag for recent years and an older
    tag for historical data). This maximises historical coverage but means
    the underlying concept may change at the boundary.

    Parameters
    ----------
    facts : dict
        The 'facts' dict from the company facts API response.
    try_order : list[str]
        List of XBRL concept names to try, in priority order.
    taxonomy : str
        The taxonomy namespace. Defaults to "us-gaap".
    units : str
        The unit of measure. Defaults to "USD".

    Returns
    -------
    list[dict]
        The merged list of fact entries across all matching concepts, or [].
    """
    taxonomy_facts = facts.get(taxonomy, {})
    merged: dict[str, dict] = {}

    # Track which concept resolved each period for priority ordering
    merged_concept: dict[str, int] = {}

    for priority, concept in enumerate(try_order):
        concept_data = taxonomy_facts.get(concept, {})
        unit_data = concept_data.get("units", {}).get(units, [])
        for entry in unit_data:
            key = entry.get("end", "")
            if not key:
                continue
            if key not in merged:
                merged[key] = entry
                merged_concept[key] = priority
            elif priority == merged_concept.get(key):
                # Same concept priority: prefer latest filing (amendments).
                # Only within the same base form type (10-K vs 10-Q) to avoid
                # 10-Q comparison-period entries overwriting 10-K data.
                merged_form = merged[key].get("form", "").split("/")[0]
                entry_form = entry.get("form", "").split("/")[0]
                if entry_form == merged_form and entry.get("filed", "") > merged[
                    key
                ].get("filed", ""):
                    merged[key] = entry

    return list(merged.values())


def _derive_quarterly_field(
    df: DataFrame,
    field_name: str,
) -> tuple[DataFrame, set]:
    """Convert cumulative YTD values to pure quarterly values for one field.

    SEC 10-Q filings report income/cash flow as cumulative YTD:
    - Q1: 3-month value (already quarterly)
    - Q2: 6-month cumulative (Q1+Q2)
    - Q3: 9-month cumulative (Q1+Q2+Q3)
    - FY (10-K): 12-month annual value (kept as-is)

    Returns the modified DataFrame and a set of fiscal years where Q4 was
    successfully derived (i.e. both FY and Q3 data were present).
    """
    q4_derived: set = set()

    if df.empty or "fy" not in df.columns or "fp" not in df.columns:
        return df, q4_derived

    df = df.copy()

    for fy in df["fy"].unique():
        fy_mask = df["fy"] == fy
        group = df.loc[fy_mask]

        cumulative: dict[str, float] = {}
        for fp in ("Q1", "Q2", "Q3", "FY"):
            # Check both FY and Q4 labels since fp rename hasn't happened yet
            # but be defensive in case of reprocessing.
            fp_rows = group[group["fp"].isin([fp] if fp != "FY" else ["FY", "Q4"])]
            if not fp_rows.empty:
                val = fp_rows[field_name].iloc[0]
                if val is not None and not (isinstance(val, float) and isna(val)):
                    cumulative[fp] = val

        if "Q2" in cumulative and "Q1" in cumulative:
            idx = df.index[fy_mask & (df["fp"] == "Q2")]
            df.loc[idx, field_name] = cumulative["Q2"] - cumulative["Q1"]

        if "Q3" in cumulative and "Q2" in cumulative:
            idx = df.index[fy_mask & (df["fp"] == "Q3")]
            df.loc[idx, field_name] = cumulative["Q3"] - cumulative["Q2"]

        # Q4 = FY (12-month) - Q3 cumulative (9-month YTD).
        # Do NOT rename FY→Q4 here; that's done in a single pass after all
        # fields are derived, to avoid breaking subsequent fields' lookups.
        if "FY" in cumulative and "Q3" in cumulative:
            fy_idx = df.index[fy_mask & (df["fp"].isin(["FY", "Q4"]))]
            df.loc[fy_idx, field_name] = cumulative["FY"] - cumulative["Q3"]
            q4_derived.add(fy)

    return df, q4_derived


def _apply_formula(
    df: DataFrame, field_name: str, formula: str, fill_only: bool = False
) -> None:
    """Apply a simple arithmetic formula (a - b or a + b) to a DataFrame.

    When fill_only=True, only fill null values in the existing column rather
    than overwriting the entire column.
    """
    match = re.match(r"^(\w+)\s*([+\-])\s*(\w+)$", formula)
    if not match:
        return
    left, op, right = match.group(1), match.group(2), match.group(3)
    if left not in df.columns or right not in df.columns:
        return
    computed = df[left] - df[right] if op == "-" else df[left] + df[right]
    if fill_only and field_name in df.columns:
        df[field_name] = df[field_name].fillna(computed)
    else:
        df[field_name] = computed


def extract_balance_sheet_data(  # noqa: PLR0912
    company_facts: dict,
    taxonomy_map: dict,
    period: str = "annual",
) -> list[dict]:
    """Extract standardized balance sheet data from company facts.

    Parameters
    ----------
    company_facts : dict
        Raw response from the SEC company facts API.
    taxonomy_map : dict
        The balance sheet taxonomy mapping.
    period : str
        Filter by 'annual' (10-K) or 'quarter' (10-Q). Defaults to 'annual'.

    Returns
    -------
    list[dict]
        List of dicts, one per reporting period, with standardized field names.
    """
    # pylint: disable=import-outside-toplevel
    from pandas import DataFrame

    facts = company_facts.get("facts", {})
    if not facts:
        return []

    entity_name = company_facts.get("entityName", "")
    cik = company_facts.get("cik", "")

    # Collect all fact entries per standardized field.
    field_frames: dict[str, DataFrame] = {}

    for field_name, field_def in taxonomy_map.items():
        try_order = field_def.get("try_order", [])
        tax = field_def.get("taxonomy", "us-gaap")
        unit = field_def.get("units", "USD")

        entries = resolve_fact(facts, try_order, taxonomy=tax, units=unit)
        if not entries:
            continue

        df = DataFrame(entries)
        # Filter by form type based on period parameter.
        if "form" in df.columns:
            form_filter = ["10-K"] if period == "annual" else ["10-Q"]
            df = df[df["form"].isin(form_filter)]
        if df.empty:
            continue

        # For instantaneous (balance sheet) items, we need point-in-time values.
        # Deduplicate: keep the latest filing for each period end date.
        if "end" in df.columns and "filed" in df.columns:
            df = df.sort_values("filed", ascending=False)
            df = df.drop_duplicates(subset=["end"], keep="first")

        df = df.rename(columns={"val": field_name, "end": "period_ending"})
        optional_cols = [c for c in ("fy", "fp", "form", "filed") if c in df.columns]
        cols_to_keep = ["period_ending", field_name] + optional_cols

        field_frames[field_name] = df[[c for c in cols_to_keep if c in df.columns]]

    if not field_frames:
        return []

    # Build a master metadata frame from the union of ALL fields' periods.
    meta_cols = ["period_ending"] + [
        c
        for c in ("fy", "fp", "form", "filed")
        if any(c in df.columns for df in field_frames.values())
    ]
    meta_frames = []
    for df in field_frames.values():
        available = [c for c in meta_cols if c in df.columns]
        meta_frames.append(df[available].drop_duplicates(subset=["period_ending"]))

    from pandas import concat

    master_meta = concat(meta_frames, ignore_index=True)
    master_meta = master_meta.drop_duplicates(subset=["period_ending"], keep="first")

    # Left-join each field's values onto the master metadata frame.
    result_df = master_meta
    for field_name, df in field_frames.items():
        right_cols = ["period_ending", field_name]
        right_df = df[[c for c in right_cols if c in df.columns]]
        result_df = result_df.merge(right_df, on="period_ending", how="left")

    if result_df.empty:
        return []

    # Compute derived fields in two passes to handle dependencies
    # (e.g., net_debt depends on total_debt which is also derived).
    # If a column already exists (from XBRL data) but has null rows, fill
    # those nulls from the derived formula rather than skipping entirely.
    for _pass in range(2):
        for field_name, field_def in taxonomy_map.items():
            has_column = field_name in result_df.columns
            has_nulls = has_column and result_df[field_name].isna().any()

            # Skip if column exists and is fully populated.
            if has_column and not has_nulls:
                continue

            derived_from = field_def.get("derived_from")
            formula = field_def.get("derived_from_formula")

            if derived_from:
                source_cols = [c for c in derived_from if c in result_df.columns]
                if source_cols:
                    derived_vals = result_df[source_cols].sum(
                        axis=1, min_count=len(source_cols)
                    )
                    if has_column:
                        result_df[field_name] = result_df[field_name].fillna(
                            derived_vals
                        )
                    else:
                        result_df[field_name] = derived_vals
            elif formula:
                _apply_formula(result_df, field_name, formula, fill_only=has_column)

    # Map fiscal period labels.
    if "fp" in result_df.columns:
        result_df = result_df.rename(columns={"fp": "fiscal_period"})
    if "fy" in result_df.columns:
        result_df = result_df.rename(columns={"fy": "fiscal_year"})
    if "filed" in result_df.columns:
        result_df = result_df.rename(columns={"filed": "filing_date"})

    # Add entity metadata.
    result_df["entity_name"] = entity_name
    result_df["cik"] = cik

    # Drop the SEC form column (internal use only).
    if "form" in result_df.columns:
        result_df = result_df.drop(columns=["form"])

    # Sort by period descending.
    result_df = result_df.sort_values("period_ending", ascending=False)

    # Replace NaN with None.
    result_df = result_df.where(result_df.notna(), None)

    return result_df.to_dict("records")


def extract_duration_data(  # noqa: PLR0912  # pylint: disable=too-many-branches
    company_facts: dict,
    taxonomy_map: dict,
    period: str = "annual",
) -> list[dict]:
    """Extract duration-based data (income statement / cash flow) from company facts.

    Handles quarterly derivation: SEC 10-Q filings report cumulative YTD
    values for duration items. Pure quarterly values are derived by subtracting
    the prior quarter's YTD figure.

    Parameters
    ----------
    company_facts : dict
        Raw response from the SEC company facts API.
    taxonomy_map : dict
        The taxonomy mapping (income_statement or cash_flow).
    period : str
        Filter by 'annual' (10-K only) or 'quarter' (10-Q only).
        Defaults to 'annual'.

    Returns
    -------
    list[dict]
        List of dicts, one per reporting period, with standardized field names.
    """
    # pylint: disable=import-outside-toplevel
    from pandas import DataFrame

    facts = company_facts.get("facts", {})
    if not facts:
        return []

    entity_name = company_facts.get("entityName", "")
    cik = company_facts.get("cik", "")

    field_frames: dict[str, DataFrame] = {}
    # Track which fields need quarterly derivation (additive USD items only).
    fields_to_derive: list[str] = []

    for field_name, field_def in taxonomy_map.items():
        try_order = field_def.get("try_order", [])
        tax = field_def.get("taxonomy", "us-gaap")
        unit = field_def.get("units", "USD")

        entries = resolve_fact(facts, try_order, taxonomy=tax, units=unit)
        if not entries:
            continue

        df = DataFrame(entries)

        # Filter filings. For annual: 10-K only. For quarter: keep both
        # 10-K and 10-Q during extraction (FY values needed for Q4 derivation),
        # then filter to quarterly rows after derivation.
        if "form" not in df.columns:
            continue
        form_filter = ["10-K"] if period == "annual" else ["10-K", "10-Q"]
        df = df[df["form"].isin(form_filter)]
        if df.empty:
            continue

        # Duration items must have start and end dates.
        if "start" not in df.columns or "end" not in df.columns:
            continue

        # Deduplicate: for each period end date, prefer the shortest-duration
        # entry (pure quarterly ~90 days) over cumulative YTD entries.
        # SEC XBRL data includes comparison period entries tagged with the
        # current filing's (fy, fp), so we dedup by end date, not (fy, fp).
        has_cumulative = False
        if "filed" in df.columns:
            from pandas import to_datetime

            df["_duration"] = (
                to_datetime(df["end"]) - to_datetime(df["start"])
            ).dt.days
            df = df.sort_values(["_duration", "filed"], ascending=[True, False])
            df = df.drop_duplicates(subset=["end"], keep="first")

            # Flag fields that still have cumulative Q2/Q3 entries.
            has_cumulative = (
                (df["_duration"] > 120) & df["fp"].isin(["Q2", "Q3"])
            ).any()
            df = df.drop(columns=["_duration"])

        df = df.rename(columns={"val": field_name, "end": "period_ending"})

        optional_cols = [c for c in ("fy", "fp", "form", "filed") if c in df.columns]
        cols_to_keep = ["period_ending", field_name] + optional_cols
        field_frames[field_name] = df[[c for c in cols_to_keep if c in df.columns]]

        # Only derive quarterly for additive USD items with cumulative entries.
        if unit == "USD" and has_cumulative:
            fields_to_derive.append(field_name)

    if not field_frames:
        return []

    # Build a master metadata frame from the union of ALL fields' periods.
    # This prevents outer-join metadata loss where later fields introduce
    # periods not present in earlier fields (BUG 3 fix).
    meta_cols = ["period_ending"] + [
        c
        for c in ("fy", "fp", "form", "filed")
        if any(c in df.columns for df in field_frames.values())
    ]
    meta_frames = []
    for df in field_frames.values():
        available = [c for c in meta_cols if c in df.columns]
        meta_frames.append(df[available].drop_duplicates(subset=["period_ending"]))

    from pandas import concat

    master_meta = concat(meta_frames, ignore_index=True)
    master_meta = master_meta.drop_duplicates(subset=["period_ending"], keep="first")

    # Left-join each field's values onto the master metadata frame.
    result_df = master_meta
    for field_name, df in field_frames.items():
        right_cols = ["period_ending", field_name]
        right_df = df[[c for c in right_cols if c in df.columns]]
        result_df = result_df.merge(right_df, on="period_ending", how="left")

    if result_df.empty:
        return []

    # Drop rows missing essential metadata.
    for col in ("fy", "fp"):
        if col in result_df.columns:
            result_df = result_df.dropna(subset=[col])

    if result_df.empty:
        return []

    # Remove comparison-period entries: SEC XBRL tags prior-year comparison
    # data with the current filing's (fy, fp). Within each (fy, fp), keep
    # only the row with the latest period_ending (the actual current period).
    if "fy" in result_df.columns and "fp" in result_df.columns:
        result_df = result_df.sort_values("period_ending", ascending=False)
        result_df = result_df.drop_duplicates(subset=["fy", "fp"], keep="first")

    # Derive quarterly values from cumulative YTD for additive fields.
    # Track which fiscal years had Q4 successfully derived (Q3 data present).
    all_q4_derived_years: set = set()
    for field_name in fields_to_derive:
        if field_name in result_df.columns:
            result_df, q4_years = _derive_quarterly_field(result_df, field_name)
            all_q4_derived_years.update(q4_years)

    # Single-pass FY→Q4 rename AFTER all fields have been derived.
    # Only rename FY→Q4 for fiscal years where Q3 data existed (meaning Q4
    # was actually derived).  If Q3 is missing, the FY row still holds the
    # full 12-month annual value and must NOT be relabelled as quarterly Q4.
    if "fp" in result_df.columns and all_q4_derived_years:
        result_df.loc[
            (result_df["fp"] == "FY") & (result_df["fy"].isin(all_q4_derived_years)),
            "fp",
        ] = "Q4"

    # For quarterly mode, keep only quarterly rows (Q1-Q4) after derivation.
    if period == "quarter" and "fp" in result_df.columns:
        result_df = result_df[result_df["fp"].isin(["Q1", "Q2", "Q3", "Q4"])]
        if result_df.empty:
            return []

    # Compute derived fields in two passes to handle dependencies
    # (e.g., EBITDA depends on fields that may themselves be derived).
    for _pass in range(2):
        for field_name, field_def in taxonomy_map.items():
            has_column = field_name in result_df.columns
            has_nulls = has_column and result_df[field_name].isna().any()

            if has_column and not has_nulls:
                continue

            derived_from = field_def.get("derived_from")
            formula = field_def.get("derived_from_formula")

            if derived_from:
                source_cols = [c for c in derived_from if c in result_df.columns]
                if source_cols:
                    derived_vals = result_df[source_cols].sum(
                        axis=1, min_count=len(source_cols)
                    )
                    if has_column:
                        result_df[field_name] = result_df[field_name].fillna(
                            derived_vals
                        )
                    else:
                        result_df[field_name] = derived_vals
            elif formula:
                _apply_formula(result_df, field_name, formula, fill_only=has_column)

    # Rename metadata columns.
    if "fp" in result_df.columns:
        result_df = result_df.rename(columns={"fp": "fiscal_period"})
    if "fy" in result_df.columns:
        result_df = result_df.rename(columns={"fy": "fiscal_year"})
    if "filed" in result_df.columns:
        result_df = result_df.rename(columns={"filed": "filing_date"})

    # Add entity metadata.
    result_df["entity_name"] = entity_name
    result_df["cik"] = cik

    # Drop the SEC form column.
    if "form" in result_df.columns:
        result_df = result_df.drop(columns=["form"])

    # Sort by period descending.
    result_df = result_df.sort_values("period_ending", ascending=False)

    # Replace NaN with None.
    result_df = result_df.where(result_df.notna(), None)

    return result_df.to_dict("records")
