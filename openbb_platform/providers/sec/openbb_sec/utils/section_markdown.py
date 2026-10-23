"""Render SEC filing sections as a single markdown string for Workspace widgets."""

import re
from types import SimpleNamespace

_YEAR = re.compile(r"^(?:19|20)\d{2}$")


def _cells(row: str) -> list:
    """Split a markdown table row into trimmed cell values."""
    return [c.strip() for c in row.strip().strip("|").split("|")]


def _md_table(header: list, rows: list, ncol: int) -> str:
    """Build a markdown table from a header and data rows, padded to ncol."""

    def pad(cells: list) -> list:
        return (cells + [""] * ncol)[:ncol]

    head = "| " + " | ".join(pad(header)) + " |"
    sep = "| " + " | ".join(["---"] * ncol) + " |"
    body = "\n".join("| " + " | ".join(pad(r)) + " |" for r in rows)
    return f"{head}\n{sep}\n{body}"


def _split_year_block(block: list) -> str:
    """Split a single markdown table stacked by year into one table per year."""
    header: list | None = None
    groups: list = []
    current: list | None = None
    for row in block:
        if re.fullmatch(r"[\s|:\-]+", row.strip()):
            continue
        cells = _cells(row)
        nonempty = [c for c in cells if c]
        if len(nonempty) == 1 and _YEAR.fullmatch(nonempty[0]):
            current = []
            groups.append((nonempty[0], current))
        elif not any(any(ch.isdigit() for ch in c) for c in cells):
            if header is None and len(nonempty) >= 2:
                header = cells
        elif current is not None:
            current.append(cells)

    if not groups or header is None:
        return "\n".join(block)
    ncol = len(header)
    return "\n\n".join(
        f"### {year}\n\n{_md_table(header, rows, ncol)}" for year, rows in groups
    )


def _split_year_tables(text: str) -> str:
    """Rewrite multi-year stacked tables in markdown as one table per year."""
    lines = text.split("\n")
    out: list = []
    i = 0
    while i < len(lines):
        if "|" not in lines[i]:
            out.append(lines[i])
            i += 1
            continue
        block: list = []
        while i < len(lines) and "|" in lines[i]:
            block.append(lines[i])
            i += 1
        out.append(_split_year_block(block))
    return "\n".join(out)


def _join(pairs: list) -> str:
    """Join (heading, text) pairs into one markdown document."""
    blocks: list = []
    for heading, text in pairs:
        body = (text or "").strip()
        if not body:
            continue
        title = heading.lstrip("-–— ").strip() if heading else heading
        blocks.append(f"## {title}\n\n{body}" if title else body)
    return "\n\n".join(blocks)


async def get_section_markdown(
    symbol: str,
    section: str,
    calendar_year: str | None = None,
    calendar_period: str | None = None,
    use_cache: bool = True,
) -> str:
    """Return a filing section rendered as one markdown string."""
    from openbb_sec.models.sec_financials import (
        FinancialStatements,
        no_filing_message,
        resolve_section_url,
    )

    query = SimpleNamespace(
        symbol=symbol,
        url=None,
        calendar_year=calendar_year,
        calendar_period=calendar_period,
        use_cache=use_cache,
    )
    annual_sections = {"company_overview", "risk_factors", "legal_proceedings"}
    url = await resolve_section_url(query, annual_default=section in annual_sections)
    if not url:
        return no_filing_message(symbol)

    statements = FinancialStatements.from_url(url, use_cache)

    if section == "company_overview":
        return statements.business() or (
            "No Business (Item 1) section was found in this filing. It is present"
            " in annual reports (10-K) but not in quarterly reports (10-Q)."
        )
    if section == "risk_factors":
        rendered = _join(
            [(f.get("risk_factor"), f.get("text")) for f in statements.risk_factors()]
        )
        return rendered or (
            "No Risk Factors (Item 1A) section was found in this filing. Item 1A"
            " was not required before 2005, and some filings incorporate it by"
            " reference to other sections."
        )
    if section == "segment_revenue":
        return _join(
            [
                (s.get("name"), _split_year_tables(s.get("text") or ""))
                for s in statements.segment_revenue()
            ]
        )
    if section == "legal_proceedings":
        item = statements.legal_proceedings()
        return (item.get("text") or "") if item else ""
    if section == "disclosures":
        from openbb_sec.utils.filing_sections import reflow_plain_text

        disclosures = statements.disclosures
        is_xbrl = statements.is_xbrl
        pairs = []
        for key in disclosures:
            info = disclosures[key]
            if not (isinstance(info, dict) and (info.get("text") or "").strip()):
                continue
            text_value = (
                info["text"] if is_xbrl else reflow_plain_text(info["text"], force=True)
            )
            pairs.append((info.get("name") or key, text_value))
        return _join(pairs)
    return ""
