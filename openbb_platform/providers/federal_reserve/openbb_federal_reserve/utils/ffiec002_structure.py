"""FFIEC 002 report structure generator."""

from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path
from typing import Any

from openbb_federal_reserve.utils.structure_common import (
    asset_path,
    collect_schedules,
    fetch_pdf_bytes,
    fetch_report_csv,
    latest_quarter_end,
)

USER_GUIDE_URL = (
    "https://www.frbservices.org/binaries/content/assets/crsocms/"
    "central-bank/reporting-central/2023/ffiec-002-user-guide.pdf"
)

VALIDATION_RPT = "FFIEC002"

VALIDATION_RSSDS = (317810, 413208)

ASSET_PATH = asset_path("ffiec002")


def _spaced(token: str) -> str:
    """Build a pattern matching ``token`` with optional whitespace between chars."""
    return r"\s*".join(re.escape(char) for char in token)


_CONTEXT_TRAILER = re.compile(
    r"\s*\(\s*"
    + _spaced("BANK")
    + r"\s+(?:"
    + _spaced("U.S.")
    + r"\s*\+?\s*"
    + _spaced("FOREIGN")
    + r"\s*"
    + _spaced("OFC")
    + r"|"
    + _spaced("FOREIGN")
    + r"\s+"
    + _spaced("OFC")
    + r"\s+"
    + _spaced("ONLY")
    + r"|"
    + _spaced("U.S.")
    + r"\s+"
    + _spaced("OFC")
    + r"\s+"
    + _spaced("ONLY")
    + r")\s*\)",
    re.IGNORECASE,
)

_APPENDIX_BANNER = "ffiec 002 report detailed field specifications"
_APPENDIX_END = "ffiec 002s report detailed field specifications"

_MDRM_PREFIX = r"(?:RCFD|RCFN|RCON|RCXX|RCXY|CRCB|TEXT)"
_MDRM_LINE = re.compile(rf"^({_MDRM_PREFIX}[A-Z0-9]{{4}})\b")

_SCHEDULE_VOCAB = sorted(
    {
        "Cover Page",
        "Cover",
        "C, Part 1",
        "C. Part 1",
        "C, Part 2",
        "C. Part 2",
        "M, Part 1",
        "M, Part 2",
        "M, Part 3",
        "M, Part 4",
        "M, Part 5",
        "Q, Part 1",
        "Q, Part 2",
        "RAL",
        "A",
        "C",
        "E",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "S",
        "T",
    },
    key=len,
    reverse=True,
)

_SCHEDULE_TITLES = {
    "Cover Page": "Cover Page",
    "RAL": "Schedule RAL - Assets and Liabilities",
    "A": "Schedule A - Cash and Balances Due From Depository Institutions",
    "C, Part 1": "Schedule C, Part I - Loans",
    "C, Part 2": "Schedule C, Part II - Loans to Small Businesses and Small Farms",
    "C": "Schedule C - Loans",
    "E": "Schedule E - Deposit Liabilities and Credit Balances",
    "K": "Schedule K - Quarterly Averages",
    "L": "Schedule L - Off-Balance-Sheet Items",
    "M, Part 1": "Schedule M, Part I - Claims on and Liabilities to Related "
    "Depository Institutions",
    "M, Part 2": "Schedule M, Part II - Loans to and Deposits of Related "
    "Depository Institutions",
    "M, Part 3": "Schedule M, Part III - Holdings of and Liabilities on Own "
    "Acceptances",
    "M, Part 4": "Schedule M, Part IV - Other Claims on and Liabilities to "
    "Related Depository Institutions",
    "M, Part 5": "Schedule M, Part V - Derivatives and Off-Balance-Sheet Items "
    "With Related Institutions",
    "N": "Schedule N - Past Due, Nonaccrual, and Restructured Loans",
    "O": "Schedule O - Other Data for Deposit Insurance Assessments",
    "P": "Schedule P - Other Borrowed Money",
    "Q": "Schedule Q - Financial Assets and Liabilities Measured at Fair Value",
    "S": "Schedule S - Servicing, Securitization, and Asset Sale Activities",
    "T": "Schedule T - Fiduciary and Related Services",
}

_SCHEDULE_ORDER = [
    "Cover Page",
    "RAL",
    "A",
    "C, Part 1",
    "C, Part 2",
    "C",
    "E",
    "K",
    "L",
    "M, Part 1",
    "M, Part 2",
    "M, Part 3",
    "M, Part 4",
    "M, Part 5",
    "N",
    "O",
    "P",
    "Q",
    "S",
    "T",
]


def _fetch_validation_csvs() -> list[str]:
    """Fetch each sampled filer's latest per-institution CSV that resolves.

    Returns
    -------
    list[str]
        One ``ReturnFinancialReportCSV`` payload per :data:`VALIDATION_RSSDS`
        entry that the FFIEC 002 endpoint serves. A filer the endpoint does not
        serve (the request returns the NIC error page rather than a CSV) is
        skipped so it contributes nothing to the membership union.
    """
    period = latest_quarter_end()
    payloads: list[str] = []
    for rssd in VALIDATION_RSSDS:
        text = fetch_report_csv(VALIDATION_RPT, rssd, period)
        if text.lstrip().startswith("<"):
            continue
        payloads.append(text)
    return payloads


def _appendix_lines(pdf_bytes: bytes) -> list[str]:
    """Return the Appendix A physical lines, stripped and non-empty, in order."""
    from openbb_federal_reserve.utils.report_structure import read_pdf_pages

    lines: list[str] = []
    in_appendix = False
    for text in read_pdf_pages(pdf_bytes):
        for raw in text.splitlines():
            stripped = raw.strip()
            if not stripped:
                continue
            lowered = re.sub(r"\s+", " ", stripped).lower()
            if not in_appendix:
                if lowered == _APPENDIX_BANNER:
                    in_appendix = True
                continue
            if lowered == _APPENDIX_END:
                return lines
            lines.append(stripped)
    return lines


def _normalize_schedule(schedule: str) -> str:
    """Normalize a printed schedule reference to its canonical code."""
    schedule = schedule.strip()
    if schedule in ("Cover", "Cover Page"):
        return "Cover Page"
    if schedule.startswith("Q"):
        return "Q"
    if schedule == "C.":
        return "C"
    return schedule.replace("C. ", "C, ")


def _logical_rows(lines: list[str]) -> list[tuple[str, str]]:
    """Group the physical lines into ``(mdrm, body)`` logical data rows."""
    rows: list[tuple[str, str]] = []
    index = 0
    count = len(lines)
    while index < count:
        line = re.sub(r"\s+", " ", lines[index].strip())
        match = _MDRM_LINE.match(line)
        if not match:
            index += 1
            continue
        code = match.group(1)
        body = line[len(code) :].strip()
        cursor = index
        while _needs_continuation(body) and cursor + 1 < count:
            following = re.sub(r"\s+", " ", lines[cursor + 1].strip())
            if _MDRM_LINE.match(following):
                break
            body = f"{body} {following}".strip()
            cursor += 1
        index = cursor + 1
        rows.append((code, body))
    return rows


def _needs_continuation(body: str) -> bool:
    """Return ``True`` while a wrapped row still lacks its structure tokens."""
    remainder = re.sub(r"^(?:\d+\s+)?(?:Y\s+)?", "", body)
    return len(remainder.split()) < 2


def _parse_row(code: str, body: str) -> tuple[str, str | None, str | None] | None:
    """Resolve a logical row into ``(schedule, line, column)``."""
    body = re.sub(r"\+[A-Z0-9]+", "", body)
    body = re.sub(r"^(\d+)\s+", "", body)  # occurrence column
    body = re.sub(r"^Y\s+", "", body).strip()  # text-item flag
    schedule: str | None = None
    tail = ""
    for candidate in _SCHEDULE_VOCAB:
        if body == candidate or body.startswith(f"{candidate} "):
            schedule = _normalize_schedule(candidate)
            tail = body[len(candidate) :].strip()
            break
    if schedule is None:
        comma_q = re.match(r"^Q,?\s+(.*)$", body)
        if not comma_q:
            return None
        schedule = "Q"
        tail = comma_q.group(1).strip()
    parts = tail.split() if tail else []
    column: str | None = None
    line: str | None = tail or None
    if len(parts) >= 2 and re.fullmatch(r"[A-Z]", parts[-1]):
        column = parts[-1]
        line = " ".join(parts[:-1])
    return schedule, line, column


def _clean_caption(caption: str) -> str:
    """Strip the column-context trailer and collapse whitespace in a caption."""
    caption = _CONTEXT_TRAILER.sub("", caption)
    caption = re.sub(r"\s+", " ", caption).strip()
    return caption


def _captions(csv_texts: list[str]) -> dict[str, str]:
    """Map each value-bearing MDRM to its cleaned caption across the filings."""
    captions: dict[str, str] = {}
    for csv_text in csv_texts:
        for row in list(csv.reader(io.StringIO(csv_text)))[1:]:
            if len(row) < 2:
                continue
            name = row[0].strip()
            if name in captions or not re.fullmatch(r"[A-Z]{4}[A-Z0-9]{4}", name):
                continue
            caption = _clean_caption(row[1])
            if caption:
                captions[name] = caption
    return captions


def _schedule_sort_key(schedule: str) -> tuple[int, str]:
    """Return a stable sort key placing schedules in form order."""
    try:
        return (_SCHEDULE_ORDER.index(schedule), "")
    except ValueError:
        return (len(_SCHEDULE_ORDER), schedule)


def parse_structure(
    pdf_bytes: bytes, csv_texts: list[str] | None = None
) -> list[dict[str, Any]]:
    """Parse the FFIEC 002 user guide into an ordered list of report items.

    The guide's field listing enumerates confidential grids and form rows no
    public filing populates. When ``csv_texts`` is supplied it is treated as the
    membership sample: only MDRMs that at least one sampled filing reports become
    items, so the result carries no permanently-empty row, and each item's caption
    is sourced (cleaned) from that filing. When ``csv_texts`` is omitted every
    parsed MDRM is emitted with its code as the caption.

    Parameters
    ----------
    pdf_bytes : bytes
        The raw FFIEC 002 Reporting Central user guide PDF.
    csv_texts : list[str], optional
        The sampled per-institution ``ReturnFinancialReportCSV`` payloads whose
        unioned value-bearing codes define the public report's true item set and
        source each MDRM's caption.

    Returns
    -------
    list[dict[str, Any]]
        One record per reported cell (MDRM) in schedule order, each with the keys
        ``schedule``, ``schedule_name``, ``line``, ``caption``, ``mdrm``,
        ``columns``, ``level`` and ``is_header``. Every MDRM is its own item so no
        reported value is hidden; the cell's form line and column are folded into
        the ``line`` reference, and ``columns`` holds the single MDRM.
    """
    captions = _captions(csv_texts) if csv_texts else {}
    parsed: list[tuple[str, str | None, str | None, str]] = []
    for code, body in _logical_rows(_appendix_lines(pdf_bytes)):
        result = _parse_row(code, body)
        if result is None:
            parsed.append(("", None, None, code))
            continue
        schedule, line, column = result
        parsed.append((schedule, line, column, code))

    items = _build_items(parsed, captions, filter_to_sample=bool(csv_texts))
    items.sort(key=lambda item: _schedule_sort_key(item["schedule"]))
    return items


def _line_reference(line: str | None, column: str | None) -> str | None:
    """Combine a form line and column letter into one line reference."""
    if line is None:
        return None
    return f"{line}.{column}" if column else line


def _build_items(
    parsed: list[tuple[str, str | None, str | None, str]],
    captions: dict[str, str],
    filter_to_sample: bool,
) -> list[dict[str, Any]]:
    """Emit one report item per reported MDRM in document order."""
    items: list[dict[str, Any]] = []
    for schedule, line, column, code in parsed:
        caption = captions.get(code)
        if filter_to_sample and caption is None:
            continue
        items.append(
            {
                "schedule": schedule,
                "schedule_name": _SCHEDULE_TITLES.get(schedule, schedule),
                "line": _line_reference(line, column),
                "caption": caption or code,
                "mdrm": code,
                "columns": [code],
                "level": 1,
                "is_header": False,
            }
        )
    return items


def generate(
    pdf_path: str | None = None, csv_paths: list[str] | None = None
) -> dict[str, Any]:
    """Parse the user guide and return the structured asset payload."""
    pdf_bytes = (
        Path(pdf_path).read_bytes() if pdf_path else fetch_pdf_bytes(USER_GUIDE_URL)
    )
    if csv_paths:
        csv_texts = [Path(path).read_text(encoding="utf-8") for path in csv_paths]
    else:
        csv_texts = _fetch_validation_csvs()
    if not csv_texts:
        raise RuntimeError(
            "No sampled FFIEC 002 filing resolved; cannot define the report's "
            "item set. Supply --csv with a per-institution payload."
        )
    items = parse_structure(pdf_bytes, csv_texts)
    schedules = collect_schedules(items)
    return {
        "source": USER_GUIDE_URL,
        "schedule_count": len(schedules),
        "item_count": len(items),
        "schedules": schedules,
        "items": items,
    }


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

    parser = argparse.ArgumentParser(description="Regenerate the FFIEC 002 structure.")
    parser.add_argument("--pdf", default=None, help="Local PDF path to parse.")
    parser.add_argument(
        "--csv",
        action="append",
        default=None,
        help="Local per-institution CSV path (repeatable to union filers).",
    )
    args = parser.parse_args()
    path = write_asset(args.pdf, args.csv)
    payload = json.loads(path.read_text(encoding="utf-8"))
    print(  # noqa: T201
        f"Wrote {path} -> {payload['schedule_count']} schedules, "
        f"{payload['item_count']} items"
    )


if __name__ == "__main__":  # pragma: no cover - module-as-script entry guard
    _main()
