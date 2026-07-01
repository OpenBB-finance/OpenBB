"""FR Q-1 report structure generator.

Parses the FR Q-1 (Capital and Asset Report for Supervised Insurance
Organizations, Building Block Approach) Reporting Central XML File Upload Format
Specification PDF into an ordered, hierarchical list of report items so the model
can render the form grouped by schedule like the other FFIEC financial reports.
The parsed result is committed as a static asset (``assets/frq1/structure.json``);
the live model loads that asset rather than re-parsing the PDF at request time.

Unlike the FR Y-9C guide (a banner-delimited, line-referenced listing) the FR Q-1
specification publishes its layout as a flat per-schedule ``Data Items`` table::

    <caption (wraps across lines)> <8-character MDRM> <Data Type> <Field Length> <Notes>

The schedule is introduced by a banner line (``"Schedule VIII - Framework
Information"``); the caption wraps across physical lines and is terminated by the
MDRM, after which the ``Data Type``/``Field Length``/``Notes`` cells (which may
themselves wrap onto a following physical line) are discarded.

The upload specification enumerates the *full* form, including the confidential
variable-schedule grids (Schedules VIII-XIV and their row-context MDRMs) that
never appear in the public per-institution feed. The public FR Q-1 report is
sparse: only the Cover Page contact/attestation block and the three Building
Block capital figures (Schedule I to VII) are surfaced. The committed structure
is therefore pruned to exactly the value-bearing codes that appear in at least
one sampled filer's ``ReturnFinancialReportCSV`` payload, so no permanently-empty
form row or confidential grid is ever rendered. The pruning is validated to 100%
coverage of that public-code union.

The shared primitives (the MDRM pattern, caption cleaning and the asset-payload
summary) are imported from ``report_structure``.

Run as a module to regenerate the asset::

    python -m openbb_federal_reserve.utils.frq1_structure

Pass ``--pdf`` to parse a local specification copy instead of fetching the
canonical URL.
"""

from __future__ import annotations

import csv as _csv
import io
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from openbb_federal_reserve.utils.report_structure import (
    MDRM,
    clean_caption,
    summarize,
)

USER_GUIDE_URL = (
    "https://www.frbservices.org/binaries/content/assets/crsocms/"
    "central-bank/reporting-central/frq-1-user-guide.pdf"
)

CSV_URL = (
    "https://www.ffiec.gov/npw/FinancialReport/ReturnFinancialReportCSV"
    "?rpt=FRQ1&id={rssd}&dt={date}"
)

# Supervised insurance organizations whose public FR Q-1 filings define the
# report's true value-bearing item set. The structure is pruned to (and validated
# against) the union of their filed codes so confidential variable-schedule grids
# and permanently-empty form rows are never committed. United Services Automobile
# Association and First American Financial Corporation each file the form.
VALIDATION_RSSDS = ("1447376", "1250101")

ASSET_PATH = (
    Path(__file__).resolve().parent.parent / "assets" / "frq1" / "structure.json"
)

# CSV ``ItemName`` rows carrying institution identity or submission-period
# metadata rather than a value-bearing MDRM; excluded from the public-code union.
_IDENTITY_ITEM_NAMES = {
    "institution name",
    "city and state",
    "city",
    "state",
    "zip code",
    "street address",
    "id_rssd",
    "regulatory district",
    "bank count",
    "total assets",
    "peer_grp",
    "report date",
}
_IDENTITY_PREFIXES = ("dt",)

# The MDRM table opens at this exact heading (page 5 of the specification); the
# preceding pages are XML-format prose. Extraction ends at the example upload.
_TABLE_START = "FR Q-1 Item Data MDRMs"
_TABLE_END = "Example FR Q-1 XML File Upload"

# The trailing section listing each variable schedule's row-context MDRM. Its
# codes index confidential variable-schedule occurrences and never appear in the
# public per-institution feed, so the section is dropped at extraction.
_CONTEXTS_MARKER = "Contexts used in variable schedules"

# A schedule banner, e.g. "Schedule VIII - Framework Information" or
# "Schedule XIII - Reinsurance Pool No. 1". The Cover Page block opens the table
# under its own bare "Cover Page" banner.
_SCHEDULE_BANNER = re.compile(r"^Schedule\s+([IVX]+(?:\s+to\s+[IVX]+)?)\s*-\s*(.+)$")
_COVER_BANNER = "Cover Page"

# The per-table column headers and the table title, dropped entirely.
_HEADERS = {
    "data items",
    "mdrm",
    "data",
    "type",
    "field",
    "length notes",
    "notes",
    "schedule",
    _TABLE_START.lower(),
}

# The ``Data Type``/``Field Length``/``Notes`` cell that trails an MDRM wraps
# onto its own physical lines, where it can leak forward into the next row's
# buffered caption. Every such fragment belongs to one of a fixed boilerplate
# vocabulary - the reporting-note sentences, the precision/length tokens, and the
# unspaced ("0=No, 1=Yes") enumeration - none of which open a caption. A wrapped
# *caption* enumeration is spaced ("(0 = No, 1 = Yes)"), so the two never collide.
_NOTE_FRAGMENTS = {
    "commas and leading zeroes.",
    "maximum of 10 digits before the",
    "decimal and 4 digits after the",
    "decimal.",
    "positive number only",
    "a context tag.",
}
_NOTE_PREFIXES = ("reported", "every data item")
_LENGTH_TOKEN = re.compile(r"^\d+$|^10[.,]4$")
_UNSPACED_ENUM = re.compile(r"\b\d=(?:No|Yes|Opt)\b")

# A literal HTML line break embedded in some captions ("Material Financial
# Building Block Parent</br>(0 = No, 1 = Yes)").
_HTML_BREAK = re.compile(r"</?br\s*/?>")


def _fetch_bytes(url: str) -> bytes:
    """Download a canonical source URL as raw bytes.

    The FFIEC per-institution CSV endpoint sits behind Cloudflare and is fetched
    through the shared browser-impersonating session; the public PDF is served by
    ordinary clients.
    """
    host = (urlparse(url).hostname or "").lower()
    if host == "ffiec.gov" or host.endswith(".ffiec.gov"):
        from openbb_federal_reserve.utils.curl_session import get_session

        def warmup(session: Any) -> None:
            session.get("https://www.ffiec.gov/npw/", timeout=30)

        session = get_session("ffiec_nic", warmup)
        response = session.get(
            url, headers={"Referer": "https://www.ffiec.gov/npw/"}, timeout=180
        )
        response.raise_for_status()
        return response.content

    import requests

    response = requests.get(url, timeout=180)
    response.raise_for_status()
    return response.content


def _table_lines(pdf_bytes: bytes) -> list[str]:
    """Return the MDRM table's stripped, non-empty lines in document order.

    Extraction starts at the ``FR Q-1 Item Data MDRMs`` heading (the front matter
    is XML-format prose) and stops at the ``Example FR Q-1 XML File Upload``
    heading or the ``Contexts used in variable schedules`` section, whichever
    comes first. ``</br>`` caption breaks are normalized to a space.
    """
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(pdf_bytes))
    lines: list[str] = []
    in_table = False
    for page in reader.pages:
        text = page.extract_text() or ""
        for raw in text.splitlines():
            stripped = _HTML_BREAK.sub(" ", raw).strip()
            stripped = re.sub(r"\s+", " ", stripped).strip()
            if not stripped:
                continue
            if not in_table:
                if stripped == _TABLE_START:
                    in_table = True
                continue
            if stripped == _TABLE_END or stripped.startswith(_CONTEXTS_MARKER):
                return lines
            lines.append(stripped)
    return lines


def _schedule_code(roman: str, name: str) -> str:
    """Derive a stable schedule code from a banner's roman numeral and name.

    The reinsurance/liquidity pool schedules (XIII, XIV) repeat their roman
    numeral across a description block and one block per pool, so the pool number
    (or ``DESC`` for the description block) is appended to keep the codes
    distinct.
    """
    code = roman.replace(" ", "-")
    pool = re.search(r"Pool No\.\s*(\d)", name)
    if pool:
        return f"{code}-{pool.group(1)}"
    if "Description" in name:
        return f"{code}-DESC"
    return code


def _is_header(line: str) -> bool:
    """Return ``True`` for a column-header or table-title line."""
    return line.lower() in _HEADERS


def _is_note_tail(line: str) -> bool:
    """Return ``True`` for a wrapped ``Field Length``/``Notes`` tail fragment.

    A data-items row's trailing ``Data Type``/``Field Length``/``Notes`` cell
    wraps onto its own physical lines, where it can leak forward past the
    MDRM-terminated caption into the next row. Each such fragment is a bare field
    length (``"72"``), a precision token (``"10,4"``), an unspaced enumeration
    note (``"Reported in up to 1 digit, 0=No, 1=Yes"``) or one of a fixed set of
    reporting-note sentence fragments; none open a caption.
    """
    lowered = line.lower()
    if lowered in _NOTE_FRAGMENTS:
        return True
    if any(lowered.startswith(prefix) for prefix in _NOTE_PREFIXES):
        return True
    if _LENGTH_TOKEN.match(line):
        return True
    return bool(_UNSPACED_ENUM.search(line))


def _parse_data_items(lines: list[str]) -> list[dict[str, Any]]:
    """Parse the per-schedule ``Data Items`` tables into ordered report items.

    Physical lines are buffered into a caption until one carries an MDRM, which
    terminates the logical row; the caption is the text before the MDRM and the
    trailing ``Data Type``/``Field Length``/``Notes`` cell is discarded. Because
    that cell wraps onto following physical lines, the parser consumes (drops)
    every wrapped note fragment after an MDRM until the next caption begins. A
    schedule banner switches the active schedule.
    """
    items: list[dict[str, Any]] = []
    schedule = "COVER"
    schedule_name = "Cover Page"
    buffer: list[str] = []
    consuming_tail = False

    for line in lines:
        if line == _COVER_BANNER:
            buffer = []
            consuming_tail = False
            schedule, schedule_name = "COVER", "Cover Page"
            continue
        banner = _SCHEDULE_BANNER.match(line)
        if banner and not MDRM.search(line):
            buffer = []
            consuming_tail = False
            roman, name = banner.group(1), clean_caption(banner.group(2))
            schedule = _schedule_code(roman, name)
            schedule_name = clean_caption(line)
            continue
        if _is_header(line):
            continue
        if MDRM.search(line):
            # The MDRM terminates the logical row: emit the buffered caption and
            # discard the trailing Data Type/Field Length/Notes cell, then consume
            # the cell's wrapped continuation lines until the next caption begins.
            joined = " ".join([*buffer, line])
            buffer = []
            consuming_tail = True
            row_match = MDRM.search(joined)
            assert row_match is not None  # noqa: S101 - the row line carries the MDRM
            caption = clean_caption(joined[: row_match.start()])
            if caption:
                items.append(
                    {
                        "schedule": schedule,
                        "schedule_name": schedule_name,
                        "line": None,
                        "caption": caption,
                        "mdrm": row_match.group(0),
                        "columns": [row_match.group(0)],
                        "level": 1,
                        "is_header": False,
                    }
                )
            continue
        if consuming_tail and _is_note_tail(line):
            # A wrapped note fragment trailing the previous row's MDRM.
            continue
        consuming_tail = False
        buffer.append(line)
    return items


def parse_structure(pdf_bytes: bytes) -> list[dict[str, Any]]:
    """Parse the FR Q-1 upload specification PDF into an ordered list of items.

    Parameters
    ----------
    pdf_bytes : bytes
        The raw FR Q-1 XML File Upload Format Specification PDF.

    Returns
    -------
    list[dict[str, Any]]
        One record per reported item in form order, each with the keys
        ``schedule``, ``schedule_name``, ``line``, ``caption``, ``mdrm``,
        ``columns``, ``level`` and ``is_header``. FR Q-1 carries no line
        references and no code-less form sub-headers, so ``line`` is always
        ``None`` and every item is value-bearing. The full per-schedule layout is
        parsed here; :func:`generate` prunes it to the public value-bearing codes.
    """
    return _parse_data_items(_table_lines(pdf_bytes))


def _csv_value_codes(csv_bytes: bytes) -> set[str]:
    """Return a CSV's value-bearing MDRM codes, excluding identity/admin rows.

    Each data row is ``ItemName,Description,Value``. An identity or
    submission-period ``ItemName`` (institution name, address, ``ID_RSSD``, any
    ``DT``/``DT_*Q`` reporting date) carries entity profile rather than a filed
    metric and is dropped; every remaining MDRM-shaped ``ItemName`` is a public
    value-bearing code.
    """
    codes: set[str] = set()
    reader = _csv.reader(io.StringIO(csv_bytes.decode("utf-8-sig", "ignore")))
    for row in reader:
        if not row:
            continue
        name = row[0].strip()
        lowered = name.lower()
        if lowered in _IDENTITY_ITEM_NAMES or lowered.startswith(_IDENTITY_PREFIXES):
            continue
        if re.fullmatch(r"[A-Z]{4}[A-Z0-9]{4}", name):
            codes.add(name)
    return codes


def _public_code_union(csv_payloads: list[bytes]) -> set[str]:
    """Return the union of value-bearing codes across the sampled filer CSVs."""
    union: set[str] = set()
    for payload in csv_payloads:
        union |= _csv_value_codes(payload)
    return union


def _prune_to_union(
    items: list[dict[str, Any]], union: set[str]
) -> list[dict[str, Any]]:
    """Keep only structure items whose code appears in the public-code union.

    Every FR Q-1 item is value-bearing (single MDRM), so an item survives only
    when its code is in the union; this drops the confidential variable-schedule
    grids and permanently-empty form rows the upload specification enumerates.
    """
    return [item for item in items if item["mdrm"] in union]


def validate(items: list[dict[str, Any]], union: set[str]) -> dict[str, Any]:
    """Validate the pruned structure against the public value-bearing-code union.

    Parameters
    ----------
    items : list[dict[str, Any]]
        The pruned structure items.
    union : set[str]
        The union of value-bearing codes across the sampled filer CSVs.

    Returns
    -------
    dict[str, Any]
        ``available`` (whether any filer CSV yielded codes), the union size, the
        covered count, the sorted uncovered union codes, the coverage percentage
        (mapped/union) and ``permanent_empty_items`` (structure codes absent from
        every sampled CSV, which must be zero).
    """
    structure_codes = {item["mdrm"] for item in items if item["mdrm"]}
    if not union:
        return {
            "available": False,
            "union_count": 0,
            "covered_count": 0,
            "missing": [],
            "coverage": None,
            "permanent_empty_items": len(structure_codes),
        }
    covered = union & structure_codes
    return {
        "available": True,
        "union_count": len(union),
        "covered_count": len(covered),
        "missing": sorted(union - structure_codes),
        "coverage": round(100 * len(covered) / len(union), 2),
        "permanent_empty_items": len(structure_codes - union),
    }


def _sample_csv_payloads() -> list[bytes]:
    """Fetch each validation filer's latest filed FR Q-1 CSV.

    Resolves each RSSD's most recent filed FR Q-1 period from its NIC Institution
    Profile and downloads that period's ``ReturnFinancialReportCSV``. A filer with
    no filed FR Q-1 period or an HTML error-shell response contributes nothing.
    """
    from openbb_federal_reserve.utils.ffiec import (
        fetch_institution_financial_reports,
    )

    payloads: list[bytes] = []
    for rssd in VALIDATION_RSSDS:
        periods = (
            fetch_institution_financial_reports(rssd).get("FRQ1", {}).get("periods")
            or []
        )
        if not periods:
            continue
        latest = periods[0]
        month, day = latest["month_day"].split("/")
        date = f"{latest['year']}{month.zfill(2)}{day.zfill(2)}"
        try:
            payloads.append(_fetch_bytes(CSV_URL.format(rssd=rssd, date=date)))
        except Exception:  # noqa: BLE001, S112 - a single filer fetch is best-effort
            continue
    return payloads


def generate(
    pdf_path: str | None = None, csv_paths: list[str] | None = None
) -> dict[str, Any]:
    """Parse the upload specification and return the pruned asset payload.

    The full per-schedule layout is parsed from the specification, then pruned to
    the union of value-bearing codes across the sampled filers' latest public
    ``ReturnFinancialReportCSV`` payloads, so no confidential grid or
    permanently-empty form row is committed. The result is validated to 100%
    coverage of that union with zero permanently-empty items.

    Parameters
    ----------
    pdf_path : str | None
        Local FR Q-1 upload specification PDF; fetched from ``USER_GUIDE_URL``
        when omitted.
    csv_paths : list[str] | None
        Local per-institution validation CSVs; each :data:`VALIDATION_RSSDS`
        filer's latest filed period is fetched when omitted.
    """
    pdf_bytes = (
        Path(pdf_path).read_bytes() if pdf_path else _fetch_bytes(USER_GUIDE_URL)
    )
    items = parse_structure(pdf_bytes)
    csv_payloads = (
        [Path(path).read_bytes() for path in csv_paths]
        if csv_paths
        else _sample_csv_payloads()
    )
    union = _public_code_union(csv_payloads)
    pruned = _prune_to_union(items, union)
    payload = summarize(pruned, USER_GUIDE_URL)
    payload["caption_source"] = USER_GUIDE_URL
    payload["validation"] = validate(pruned, union)
    return payload


def write_asset(
    pdf_path: str | None = None, csv_paths: list[str] | None = None
) -> Path:
    """Generate the structure and write it to the committed static asset."""
    payload = generate(pdf_path, csv_paths)
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    ASSET_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return ASSET_PATH


def _main() -> None:
    """Command-line entry point for regenerating the asset."""
    import argparse

    parser = argparse.ArgumentParser(description="Regenerate the FR Q-1 structure.")
    parser.add_argument("--pdf", default=None, help="Local upload specification PDF.")
    parser.add_argument(
        "--csv",
        action="append",
        default=None,
        help="Local validation CSV path (repeatable, one per sampled filer).",
    )
    args = parser.parse_args()
    path = write_asset(args.pdf, args.csv)
    payload = json.loads(path.read_text(encoding="utf-8"))
    validation = payload["validation"]
    coverage = validation["coverage"]
    coverage_text = "n/a (CSV unavailable)" if coverage is None else f"{coverage}%"
    print(  # noqa: T201
        f"Wrote {path} -> {payload['schedule_count']} schedules, "
        f"{payload['item_count']} items, coverage {coverage_text} "
        f"({validation['covered_count']}/{validation['union_count']}), "
        f"permanent_empty_items {validation['permanent_empty_items']}, "
        f"missing {validation['missing']}"
    )


if __name__ == "__main__":  # pragma: no cover - module-as-script entry guard
    _main()
