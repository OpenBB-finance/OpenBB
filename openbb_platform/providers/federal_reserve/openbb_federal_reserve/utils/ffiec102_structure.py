"""FFIEC 102 report structure generator.

Builds the ordered, hierarchical item list for the FFIEC 102 Market Risk
Regulatory Report from the form's published line layout, validated against the
union of value-bearing item codes actually present in real per-institution
filings (``ReturnFinancialReportCSV?rpt=FFIEC102``).

The committed form table (:data:`_COVER` and :data:`_BODY`) carries every code
that appears in the public report, each with its form line reference, the clean
form caption, and its section grouping. Captions follow the FFIEC 102 form; the
line numbers and section groupings are verified against the self-referencing
item descriptions in the live CSV. Codes that the form defines but no institution
files (confidential or conditional-approval grid rows, and cover administrative
rows suppressed from the public download) are deliberately excluded so that no
structure value-item is permanently empty.

Run as a module to regenerate the asset::

    python -m openbb_federal_reserve.utils.ffiec102_structure

Pass ``--rssd`` one or more times to validate the table against additional
filers; the build fails if any sampled filing carries a value-bearing code the
table omits, or if the table carries a code absent from every sampled filing.
"""

from __future__ import annotations

import csv
import io
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

ASSET_PATH = (
    Path(__file__).resolve().parent.parent / "assets" / "ffiec102" / "structure.json"
)

SOURCE = (
    "https://www.frbservices.org/binaries/content/assets/crsocms/"
    "central-bank/reporting-central/ffiec-102-user-guide.pdf"
)

VALIDATION_RPT = "FFIEC102"
VALIDATION_RSSDS = ("852218", "480228")

SCHEDULE_COVER = ("COVER", "Cover Page")
SCHEDULE_BODY = ("RC", "Market Risk Regulatory Report")

# Identity / administrative rows that are never report items: excluded from the
# filed-code union and never rendered.
_IDENTITY = frozenset(
    {
        "INSTITUTION NAME",
        "CITY AND STATE",
        "CITY",
        "STATE",
        "ZIP CODE",
        "STREET ADDRESS",
        "ID_RSSD",
        "REGULATORY DISTRICT",
        "BANK COUNT",
        "TOTAL ASSETS",
        "PEER_GRP",
        "REPORT DATE",
    }
)

_MDRM = re.compile(r"^[A-Z]{4}[A-Z0-9]{4}$")
_DT_ROW = re.compile(r"^DT($|_)")

# Cover page items, in form order: (mdrm, caption).
_COVER: tuple[tuple[str, str], ...] = (
    ("MRRRC490", "Printed Name of Senior Officer"),
    ("MRRRC491", "Title of Officer"),
    ("MRRRJ196", "Date of Signature"),
    ("MRRR8901", "Name/Title of Person to Whom Questions Should Be Directed"),
    (
        "MRRR8902",
        "Area Code/Phone Number of Person to Whom Questions Should Be Directed",
    ),
    ("MRRR9116", "FAX Number of Person to Whom Questions Should Be Directed"),
    ("MRRR4086", "E-mail Address of Contact to Whom Questions Should Be Directed"),
    (
        "MRRR9224",
        "Legal Entity Identifier (LEI) of the Reporting Entity "
        "(Report only if the Reporting Entity has an LEI)",
    ),
)

_NET_LONG = (
    "Standardized Specific Risk Add-Ons for Net Long Correlation Trading Positions"
)
_NET_SHORT = (
    "Standardized Specific Risk Add-Ons for Net Short Correlation Trading Positions"
)
_PREV_DAY_VAR = "Items Related to the Previous Day's Value-at-Risk (VaR)-Based Measure"
_AVG_VAR = (
    "Items Related to the Average of the Daily VaR-Based Measure for Each of the "
    "Preceding 60 Business Day's (with Applicable Multiplication Factor)"
)
_BACKTEST = "Backtesting (Over the Most Recent Calendar Quarter)"

# Body items, in form line order: (mdrm, line, caption, section | None).
_BODY: tuple[tuple[str, str, str, str | None], ...] = (
    ("MRRRS298", "1", "Previous day's VaR-based measure", None),
    (
        "MRRRS299",
        "2",
        "Average of the immediately preceding 60 business days VaR-based measures",
        None,
    ),
    (
        "MRRRS300",
        "3",
        "Multiplication factor: equal to a value of 3.00 or higher "
        "(based on backtesting)",
        None,
    ),
    ("MRRRS301", "4", "Greater of item 1 or (item 2 multiplied by item 3)", None),
    ("MRRRS302", "5", "Most recent stressed VaR-based measure", None),
    (
        "MRRRS303",
        "6",
        "Item 3 times the average of the preceding 12 weeks stressed "
        "VaR-based measures",
        None,
    ),
    ("MRRRS304", "7", "Greater of item 5 or item 6", None),
    ("MRRRS305", "8", "Debt positions", "Specific Risk Add-Ons"),
    ("MRRRS306", "9", "Equity positions", "Specific Risk Add-Ons"),
    (
        "MRRRS307",
        "10",
        "For all institutions, capital requirements for securitization positions "
        "using the Simplified Supervisory Formula Approach (SSFA) or applying a "
        "specific risk-weighting factor of 100 percent",
        "Specific Risk Add-Ons",
    ),
    (
        "MRRRS308",
        "11",
        "For advanced approaches institutions, capital requirements for "
        "securitization positions using the Supervisory Formula Approach (SFA)",
        "Specific Risk Add-Ons",
    ),
    (
        "MRRRS309",
        "12",
        "For advanced approaches institutions, capital requirements for "
        "securitization positions using the SSFA or applying a specific "
        "risk-weighting factor of 100 percent",
        "Specific Risk Add-Ons",
    ),
    (
        "MRRRS310",
        "13",
        "For advanced approaches institutions, sum of items 11 and 12",
        "Specific Risk Add-Ons",
    ),
    (
        "MRRRS311",
        "14",
        "Standardized measure of specific risk add-ons (sum of items 8, 9, and 10)",
        "Specific Risk Add-Ons",
    ),
    (
        "MRRRS312",
        "15",
        "For advanced approaches institutions, advanced measure of specific risk "
        "add-ons (sum of items 8, 9, and 13)",
        "Specific Risk Add-Ons",
    ),
    ("MRRRS313", "16", "Most recent incremental risk measure", None),
    (
        "MRRRS314",
        "17",
        "Average of the previous 12 weeks measure of incremental risk",
        None,
    ),
    ("MRRRS315", "18", "Greater of item 16 or item 17", None),
    (
        "MRRRS316",
        "19",
        "Most recent modeled measure of all price risk",
        "Comprehensive Risk Capital Requirement",
    ),
    ("MRRRS325", "20", "Debt positions", None),
    ("MRRRS326", "21", "Equity positions", None),
    (
        "MRRRS319",
        "22",
        "For all institutions, capital requirements for securitization positions "
        "using the SSFA or applying a specific risk-weighting factor of 100 percent",
        _NET_LONG,
    ),
    (
        "MRRRS320",
        "23",
        "For advanced approaches institutions, capital requirements for "
        "securitization positions using the SFA",
        _NET_LONG,
    ),
    (
        "MRRRS321",
        "24",
        "For advanced approaches institutions, capital requirements for "
        "securitization positions using the SSFA or applying a specific "
        "risk-weighting factor of 100 percent",
        _NET_LONG,
    ),
    (
        "MRRRS322",
        "25",
        "For advanced approaches institutions, sum of items 23 and 24",
        _NET_LONG,
    ),
    (
        "MRRRS323",
        "26",
        "Standardized measure of specific risk add-ons for net long correlation "
        "trading positions (sum of items 20, 21, and 22)",
        _NET_LONG,
    ),
    (
        "MRRRS324",
        "27",
        "For advanced approaches institutions, advanced measure of specific risk "
        "add-ons for net long correlation trading positions "
        "(sum of items 20, 21, and 25)",
        _NET_LONG,
    ),
    ("MRRRS333", "28", "Debt positions", None),
    ("MRRRS334", "29", "Equity positions", None),
    (
        "MRRRS327",
        "30",
        "For all institutions, capital requirements for securitization positions "
        "using the SSFA or applying a specific risk-weighting factor of 100 percent",
        _NET_SHORT,
    ),
    (
        "MRRRS328",
        "31",
        "For advanced approaches institutions, capital requirements for "
        "securitization positions using the SFA",
        _NET_SHORT,
    ),
    (
        "MRRRS329",
        "32",
        "For advanced approaches institutions, capital requirements for "
        "securitization positions using the SSFA or applying a specific "
        "risk-weighting factor of 100 percent",
        _NET_SHORT,
    ),
    (
        "MRRRS330",
        "33",
        "For advanced approaches institutions, sum of items 31 and 32",
        _NET_SHORT,
    ),
    (
        "MRRRS331",
        "34",
        "Standardized measure of specific risk add-ons for net short correlation "
        "trading positions (sum of items 28, 29, and 30)",
        _NET_SHORT,
    ),
    (
        "MRRRS332",
        "35",
        "For advanced approaches institutions, advanced measure of specific risk "
        "add-ons for net short correlation trading positions "
        "(sum of items 28, 29, and 33)",
        _NET_SHORT,
    ),
    (
        "MRRRS335",
        "36",
        "Standardized measure of specific risk add-ons (greater of item 26 or item 34)",
        None,
    ),
    (
        "MRRRS336",
        "37",
        "Surcharge for modeled correlation trading positions "
        "(item 36 multiplied by 0.08)",
        None,
    ),
    (
        "MRRRS337",
        "38",
        "For advanced approaches institutions, advanced measure of specific risk "
        "add-ons (greater of item 27 or item 35)",
        None,
    ),
    (
        "MRRRS338",
        "39",
        "For advanced approaches institutions, surcharge for modeled correlation "
        "trading positions (item 38 multiplied by 0.08)",
        None,
    ),
    (
        "MRRRH327",
        "46",
        "Most recent standardized comprehensive risk measure "
        "(greater of item 19 or item 37)",
        None,
    ),
    (
        "MRRRH328",
        "47",
        "Average standardized comprehensive risk measure over the previous 12 weeks",
        None,
    ),
    (
        "MRRRS341",
        "48",
        "Standardized comprehensive risk measure (greater of item 46 or item 47)",
        None,
    ),
    (
        "MRRRH329",
        "49",
        "For advanced approaches institutions, most recent advanced comprehensive "
        "risk measure (greater of item 19 or item 39)",
        None,
    ),
    (
        "MRRRH330",
        "50",
        "For advanced approaches institutions, average advanced comprehensive risk "
        "measure over the previous 12 weeks",
        None,
    ),
    (
        "MRRRS342",
        "51",
        "For advanced approaches institutions, advanced comprehensive risk measure "
        "(greater of item 49 or item 50)",
        None,
    ),
    (
        "MRRRS343",
        "52",
        "Capital requirement for all de minimis exposures",
        "De Minimis Positions and Other Adjustments",
    ),
    (
        "MRRRS344",
        "53",
        "Additional capital requirement",
        "De Minimis Positions and Other Adjustments",
    ),
    (
        "MRRRS345",
        "54",
        "Sum of items 52 and 53",
        "De Minimis Positions and Other Adjustments",
    ),
    (
        "MRRRS581",
        "55",
        "Standardized market risk-weighted assets: Sum of items 4, 7, 14, 18 "
        "(if applicable), 42 or 48 (as appropriate), and 54, all multiplied by 12.5",
        "Market Risk-Weighted Assets",
    ),
    (
        "MRRRS347",
        "56",
        "For advanced approaches institutions, advanced market risk-weighted "
        "assets: Sum of items 4, 7, 15, 18 (if applicable), 45 or 51 "
        "(as appropriate), and 54, all multiplied by 12.5",
        "Market Risk-Weighted Assets",
    ),
    ("MRRRS348", "M.1", "VaR-based measure for interest rate positions", _PREV_DAY_VAR),
    ("MRRRS349", "M.2", "VaR-based measure for debt positions", _PREV_DAY_VAR),
    ("MRRRS350", "M.3", "VaR-based measure for equity positions", _PREV_DAY_VAR),
    (
        "MRRRS351",
        "M.4",
        "VaR-based measure for foreign exchange positions",
        _PREV_DAY_VAR,
    ),
    (
        "MRRRS352",
        "M.5",
        "VaR-based measure for commodity and other positions",
        _PREV_DAY_VAR,
    ),
    (
        "MRRRS353",
        "M.6",
        "Modeled specific risk included in the previous day's VaR-based measure "
        "that is not included in Memorandum items 1 through 5",
        _PREV_DAY_VAR,
    ),
    ("MRRRS354", "M.7", "VaR-based measure for interest rate positions", _AVG_VAR),
    ("MRRRS355", "M.8", "VaR-based measure for debt positions", _AVG_VAR),
    ("MRRRS356", "M.9", "VaR-based measure for equity positions", _AVG_VAR),
    ("MRRRS357", "M.10", "VaR-based measure for foreign exchange positions", _AVG_VAR),
    (
        "MRRRS358",
        "M.11",
        "VaR-based measure for commodity and other positions",
        _AVG_VAR,
    ),
    (
        "MRRRS359",
        "M.12",
        "Modeled specific risk included in the average of the daily VaR-based "
        "measure that is not included in Memorandum items 7 through 11",
        _AVG_VAR,
    ),
    (
        "MRRRS360",
        "M.13",
        "Number of trading days in the calendar quarter with a trading profit",
        _BACKTEST,
    ),
    (
        "MRRRS361",
        "M.14",
        "Number of trading days in the calendar quarter with a trading loss",
        _BACKTEST,
    ),
    (
        "MRRRS362",
        "M.15",
        "Number of trading days in the calendar quarter where the trading day's "
        "trading loss exceeded the respective VaR estimate",
        _BACKTEST,
    ),
    (
        "MRRRS363",
        "M.16",
        "The largest ratio of a daily trading loss to that trading day's VaR "
        "measure in the calendar quarter",
        _BACKTEST,
    ),
    (
        "MRRRS364",
        "M.17",
        "The second largest ratio of a daily trading loss to that trading day's "
        "VaR measure in the calendar quarter",
        _BACKTEST,
    ),
    (
        "MRRRS365",
        "M.18",
        "The third largest ratio of a daily trading loss to that trading day's "
        "VaR measure in the calendar quarter",
        _BACKTEST,
    ),
    (
        "MRRRS366",
        "M.19",
        "The starting date of the stress period used to measure the stressed VaR",
        None,
    ),
    (
        "MRRRS367",
        "M.20",
        "Number of changes to stress period starting date used in calculations "
        "for the preceding 12 weeks",
        None,
    ),
    (
        "MRRRS368",
        "M.21",
        "Total specific risk add-ons for non-modeled net long securitization positions",
        None,
    ),
    (
        "MRRRS369",
        "M.22",
        "Total specific risk add-ons for non-modeled net short securitization "
        "positions",
        None,
    ),
)


def _latest_quarter_end() -> str:
    """Return the most recent completed calendar quarter end as ``YYYYMMDD``."""
    today = date.today()
    ends = (
        date(today.year, 3, 31),
        date(today.year, 6, 30),
        date(today.year, 9, 30),
        date(today.year, 12, 31),
        date(today.year - 1, 12, 31),
    )
    completed = sorted(end for end in ends if end < today)
    return completed[-1].strftime("%Y%m%d")


def _fetch_filer_csv(rssd: str, dt: str) -> str:
    """Fetch one per-institution ``ReturnFinancialReportCSV`` payload."""
    from openbb_federal_reserve.utils.ffiec import _fetch_bytes

    raw = _fetch_bytes(
        "FinancialReport/ReturnFinancialReportCSV"
        f"?rpt={VALIDATION_RPT}&id={rssd}&dt={dt}",
        referer="https://www.ffiec.gov/npw/FinancialReport/FinancialDataDownload",
    )
    return raw.decode("utf-8", "replace")


def _filed_codes(csv_text: str) -> set[str]:
    """Return the value-bearing item codes in one filing, excluding admin rows."""
    codes: set[str] = set()
    for row in list(csv.reader(io.StringIO(csv_text)))[1:]:
        if len(row) < 3:
            continue
        name = row[0].strip()
        if name.upper() in _IDENTITY or _DT_ROW.match(name.upper()):
            continue
        if not _MDRM.match(name) or row[2].strip() == "":
            continue
        codes.add(name)
    return codes


def _build_items() -> list[dict[str, Any]]:
    """Build the ordered structure items from the committed form table."""
    items: list[dict[str, Any]] = []
    for code, caption in _COVER:
        items.append(
            {
                "schedule": SCHEDULE_COVER[0],
                "schedule_name": SCHEDULE_COVER[1],
                "line": None,
                "caption": caption,
                "mdrm": code,
                "columns": [code],
                "level": 1,
                "is_header": False,
            }
        )
    active: str | None = None
    for code, line, caption, section in _BODY:
        if section != active:
            active = section
            if section is not None:
                items.append(
                    {
                        "schedule": SCHEDULE_BODY[0],
                        "schedule_name": SCHEDULE_BODY[1],
                        "line": None,
                        "caption": section,
                        "mdrm": None,
                        "columns": None,
                        "level": 1,
                        "is_header": True,
                    }
                )
        items.append(
            {
                "schedule": SCHEDULE_BODY[0],
                "schedule_name": SCHEDULE_BODY[1],
                "line": line,
                "caption": caption,
                "mdrm": code,
                "columns": [code],
                "level": 2 if section is not None else 1,
                "is_header": False,
            }
        )
    return items


def validate(filer_csvs: list[str]) -> set[str]:
    """Validate the form table against the union of sampled filings.

    Parameters
    ----------
    filer_csvs : list[str]
        Per-institution ``ReturnFinancialReportCSV`` payloads.

    Returns
    -------
    set[str]
        The union of value-bearing item codes across the sampled filings.

    Raises
    ------
    ValueError
        If a sampled filing carries a code the table omits, or the table
        carries a code absent from every sampled filing.
    """
    union: set[str] = set()
    for text in filer_csvs:
        union |= _filed_codes(text)
    table = {code for code, *_ in _COVER} | {code for code, *_ in _BODY}
    missing = sorted(union - table)
    permanent_empty = sorted(table - union)
    if missing:
        raise ValueError(f"filed codes missing from the form table: {missing}")
    if permanent_empty:
        raise ValueError(
            f"form-table codes absent from every sampled filing: {permanent_empty}"
        )
    return union


def generate(rssds: tuple[str, ...] = VALIDATION_RSSDS) -> dict[str, Any]:
    """Build, validate, and return the structured asset payload."""
    dt = _latest_quarter_end()
    filer_csvs = [_fetch_filer_csv(rssd, dt) for rssd in rssds]
    validate(filer_csvs)
    items = _build_items()
    schedules: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
        code = item["schedule"]
        if code not in seen:
            seen.add(code)
            schedules.append({"schedule": code, "name": item["schedule_name"]})
    return {
        "source": SOURCE,
        "schedule_count": len(schedules),
        "item_count": len(items),
        "schedules": schedules,
        "items": items,
    }


def write_asset(rssds: tuple[str, ...] = VALIDATION_RSSDS) -> Path:
    """Generate the structure and write it to the committed static asset."""
    payload = generate(rssds)
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    ASSET_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return ASSET_PATH


def _main() -> None:
    """Command-line entry point for regenerating the asset."""
    import argparse

    parser = argparse.ArgumentParser(description="Regenerate the FFIEC 102 structure.")
    parser.add_argument(
        "--rssd",
        action="append",
        default=None,
        help="Filer RSSD to validate against (repeatable).",
    )
    args = parser.parse_args()
    rssds = tuple(args.rssd) if args.rssd else VALIDATION_RSSDS
    path = write_asset(rssds)
    payload = json.loads(path.read_text(encoding="utf-8"))
    print(  # noqa: T201
        f"Wrote {path} -> {payload['schedule_count']} schedules, "
        f"{payload['item_count']} items"
    )


if __name__ == "__main__":  # pragma: no cover - module-as-script entry guard
    _main()
