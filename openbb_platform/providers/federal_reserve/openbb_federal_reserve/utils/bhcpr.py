"""Parser for the FR BHCPR (Bank Holding Company Performance Report) PDF.

The per-institution BHCPR PDF is the ``ReturnFinancialReportPDF?rpt=BHCPR``
download. Page 0 is the cover and table of contents; every later page is one
report section laid out as a header band (institution line, the section title,
and a banner of five period-end dates) followed by sub-header and metric rows.

A metric row is a caption, a dotted leader, and the period figures. Three column
regimes appear, distinguished by the banner that precedes the rows:

* a ``BHC Peer # <n> Pct`` banner gives each period three figures -- the holding
  company's value, the peer-group average, and the percentile rank;
* a ``Dollar Amount in Thousands`` banner with paired ``% of Total`` columns
  gives the first three periods two figures (a dollar amount and a percent) and
  the last two a single dollar amount, optionally with trailing percent-change
  columns;
* any other banner gives each period a single figure, optionally with trailing
  percent-change columns.

In every regime the holding company's value is the first figure of each period's
group, so the parser keeps the five per-period bank values plus, for the latest
period, the peer-group average and percentile rank when the regime carries them.
"""

from __future__ import annotations

import re
from typing import Any

_NUM = re.compile(r"-?\d[\d,]*(?:\.\d+)?$")
_DATE = re.compile(r"^\d{2}/\d{2}/\d{4}$")
_PCT_BANNER = re.compile(r"BHC\s+Peer\s+#")
_DOLLAR_BANNER = "Dollar Amount in Thousands"
# Paired ``% of Total`` column pages print a ``% of`` band above the dollar
# banner; the band's repetition of ``% of`` marks the paired regime.
_PERCENT_COL = re.compile(r"(?:%\s+of\s+){2,}")
# The paired band's second physical line repeats the ``% of`` column noun (e.g.
# ``Total Total Total Percent Change``); it carries no metric and is skipped.
_PERCENT_COL_LABEL = re.compile(r"^(?:Total\s+){2,}.*Percent Change\s*$")

# Lines that belong to every section's repeating header band and carry no data.
_SKIP_PREFIXES = (
    "BHC Name City/State",
    "Page ",
    _DOLLAR_BANNER,
    "Percent Change",
)

# A caption marked ``($000)`` reports its figure in thousands even on a section
# whose other amounts are ratios or percents, so its bank series is scaled.
_THOUSANDS_MARK = "($000)"


def _to_number(token: str, *, scale: int = 1) -> int | float | None:
    """Coerce a figure token to a number, scaling thousands to full dollars."""
    if not _NUM.match(token):
        return None
    parsed = float(token.replace(",", ""))
    scaled = parsed * scale
    return int(scaled) if parsed == int(parsed) else scaled


def _split_label_figures(line: str) -> tuple[str, list[str]]:
    """Split a row into its caption and the trailing figure tokens.

    The caption ends at the dotted leader; when a row has no leader the caption
    ends at its first numeric token. A row whose trailing tokens are not all
    numeric is treated as a caption-only sub-header (no figures).
    """
    leader = re.search(r"\.{2,}", line)
    if leader:
        label = line[: leader.start()].strip().rstrip(".")
        rest = line[leader.end() :].strip()
    else:
        tokens = line.split()
        index = next((i for i, t in enumerate(tokens) if _NUM.match(t)), None)
        if index is None:
            return line.strip(), []
        label = " ".join(tokens[:index]).strip()
        rest = " ".join(tokens[index:])
    figures = rest.split()
    if figures and not all(_NUM.match(token) for token in figures):
        return line.strip(), []
    return label, figures


def _bank_series(figures: list[str], regime: str) -> list[str]:
    """Return the five per-period bank figures for a row under the given regime.

    ``pct`` rows carry ``(bank, peer, pct)`` per period; ``paired`` rows carry a
    dollar amount and a percent for the first three periods and a single amount
    for the last two; every other regime carries one figure per period. In all
    regimes the bank figure is the first of each period's group.
    """
    if regime == "pct" and len(figures) >= 15 and len(figures) % 3 == 0:
        return figures[0:15:3]
    if regime == "paired" and len(figures) >= 8:
        return [figures[0], figures[2], figures[4], figures[6], figures[7]]
    return figures[:5]


def _section_rows(lines: list[str], dollars: bool) -> list[dict[str, Any]]:
    """Parse one section's body lines into ordered header and metric rows.

    ``dollars`` selects whether the section's amounts are reported in thousands
    (scaled to full dollars) or are ratios and percents (left as filed). The
    active column regime is tracked as banners appear so each metric row is read
    against the regime in force.
    """
    section_scale = 1000 if dollars else 1
    regime = "plain"
    rows: list[dict[str, Any]] = []
    for line in lines:
        if _PCT_BANNER.search(line):
            regime = "pct"
            continue
        if _PERCENT_COL.search(line):
            regime = "paired"
            continue
        if _PERCENT_COL_LABEL.match(line):
            continue
        if line.startswith(_DOLLAR_BANNER):
            if regime != "paired":
                regime = "plain"
            continue
        if any(line.startswith(prefix) for prefix in _SKIP_PREFIXES):
            continue
        if len([token for token in line.split() if _DATE.match(token)]) == 5:
            continue
        label, figures = _split_label_figures(line)
        if not label:
            continue
        if not figures:
            rows.append({"label": label, "is_header": True})
            continue
        scale = 1000 if _THOUSANDS_MARK in label else section_scale
        bank = [
            _to_number(token, scale=scale) for token in _bank_series(figures, regime)
        ]
        bank += [None] * (5 - len(bank))
        row: dict[str, Any] = {
            "label": label,
            "is_header": False,
            "bank": bank,
            "peer": None,
            "percentile": None,
        }
        if regime == "pct" and len(figures) >= 15 and len(figures) % 3 == 0:
            row["peer"] = _to_number(figures[1])
            row["percentile"] = _to_number(figures[2])
        rows.append(row)
    return rows


def _section_title(lines: list[str]) -> str | None:
    """Return a page's section title, the line after the column-label band."""
    for index, line in enumerate(lines):
        if line.startswith("BHC Name City/State") and index + 1 < len(lines):
            return lines[index + 1].strip()
    return None


def _period_dates(lines: list[str]) -> list[str]:
    """Return the five period-end dates as ISO strings from a page's date row."""
    for line in lines:
        dates = [token for token in line.split() if _DATE.match(token)]
        if len(dates) == 5:
            return [f"{d[6:]}-{d[:2]}-{d[3:5]}" for d in dates]
    return []


# Section titles whose figures are dollar amounts in thousands rather than
# ratios or percents; matched against the parsed title, accent-insensitively.
_DOLLAR_SECTIONS = {
    "income statement-revenues and expenses",
    "non-interest income and expenses",
    "assets",
    "liabilities and changes in capital",
    "derivatives and off-balance-sheet transactions",
    "derivative instruments",
    "allowance and net credit losses on loans and leases",
    "past due and nonaccrual assets",
    "regulatory capital components and ratios",
    "insurance and broker-dealer activities",
    "foreign activities",
    "servicing, securitization and asset sale activities-part 1",
    "servicing, securitization and asset sale activities-part 2",
    "parent company income statement",
    "parent company balance sheet",
}


def _normalize_title(title: str) -> str:
    """Lower-case a title and fold its en/em dashes to a plain hyphen."""
    return title.lower().replace("—", "-").replace("–", "-")


def _identity(lines: list[str]) -> dict[str, str | None]:
    """Return the institution name, city/state, and RSSD from the cover page."""
    institution: str | None = None
    city_state: str | None = None
    rssd: str | None = None
    for index, line in enumerate(lines):
        rssd_match = re.search(r"RSSD Number:\s*(\d+)", line)
        if rssd_match:
            rssd = rssd_match.group(1)
        if line.startswith("BHC Name") and index:
            institution = lines[index - 1].strip() or None
        if line.startswith("City/State"):
            rest = line[len("City/State") :].split("Section")[0].strip()
            city_state = rest or None
    return {
        "institution_name": institution,
        "city_state": city_state,
        "rssd_id": rssd,
    }


def parse_bhcpr_pdf(content: bytes) -> dict[str, Any]:
    """Parse a BHCPR PDF into the institution's identity, periods, and sections.

    Parameters
    ----------
    content : bytes
        The raw ``ReturnFinancialReportPDF?rpt=BHCPR`` PDF bytes.

    Returns
    -------
    dict[str, Any]
        ``{"identity", "period_dates", "sections"}`` where ``identity`` carries
        the institution name and RSSD, ``period_dates`` is the five ISO period
        ends (latest first), and ``sections`` is an ordered list of
        ``{"section", "rows"}`` whose rows are header or metric dicts.
    """
    import io

    import pdfplumber

    sections: list[dict[str, Any]] = []
    identity: dict[str, str | None] = {
        "institution_name": None,
        "city_state": None,
        "rssd_id": None,
    }
    period_dates: list[str] = []

    if not content.startswith(b"%PDF"):
        # A firm that does not file the BHCPR (e.g. a commercial bank — its holding
        # company files it) gets a NIC HTML error page instead of a PDF. Return no
        # sections so the fetcher raises EmptyDataError rather than letting
        # pdfplumber crash the request with a 500.
        return {
            "identity": identity,
            "period_dates": period_dates,
            "sections": sections,
        }

    with pdfplumber.open(io.BytesIO(content)) as pdf:
        cover = [
            line
            for line in (pdf.pages[0].extract_text() or "").split("\n")
            if line.strip()
        ]
        identity = _identity(cover)
        for page in pdf.pages[1:]:
            lines = [
                line for line in (page.extract_text() or "").split("\n") if line.strip()
            ]
            if not lines:
                continue
            title = _section_title(lines)
            if not title:
                continue
            if not period_dates:
                period_dates = _period_dates(lines)
            label_index = next(
                index
                for index, line in enumerate(lines)
                if line.startswith("BHC Name City/State")
            )
            body = lines[label_index + 2 :]
            dollars = _normalize_title(title) in _DOLLAR_SECTIONS
            sections.append({"section": title, "rows": _section_rows(body, dollars)})

    return {
        "identity": identity,
        "period_dates": period_dates,
        "sections": sections,
    }
