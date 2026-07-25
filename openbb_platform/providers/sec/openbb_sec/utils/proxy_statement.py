"""Helpers for extracting governance tables from proxy statements (DEF 14A)."""

from collections.abc import Callable


def _attr(tag, name: str) -> str:
    """Return a tag attribute as a string, joining multi-valued attributes."""
    value = tag.get(name)
    if isinstance(value, list):
        return " ".join(value)
    return value or ""


async def resolve_proxy_url(
    symbol: str, calendar_year: "int | None", use_cache: bool
) -> "str | None":
    """Return the ownership source URL for a symbol.

    Uses DEF 14A when available, otherwise falls back to 20-F/40-F
    annual filings for foreign private issuers.
    """
    from openbb_sec.models.company_filings import SecCompanyFilingsFetcher

    filings = await SecCompanyFilingsFetcher().fetch_data(
        {
            "symbol": symbol,
            "form_type": "DEF_14A,20-F,40-F,20-F/A,40-F/A",
            "use_cache": use_cache,
        },
        {},
    )
    proxy_rows: list[tuple[str, str]] = []
    foreign_rows: list[tuple[str, str]] = []

    for filing in filings:
        filing_date = str(getattr(filing, "filing_date", ""))
        report_url = getattr(filing, "report_url", None)
        report_type = str(getattr(filing, "report_type", "DEF_14A") or "").upper()
        if not report_url:
            continue
        if report_type.startswith("DEF 14A") or report_type.startswith("DEF_14A"):
            proxy_rows.append((filing_date, report_url))
        elif report_type.startswith(("20-F", "40-F")):
            foreign_rows.append((filing_date, report_url))

    def _pick(rows: list[tuple[str, str]]) -> str | None:
        if not rows:
            return None
        if calendar_year is not None:
            match = [(d, u) for d, u in rows if d[:4] == str(calendar_year)]
            if match:
                return max(match)[1]
        return max(rows)[1]

    picked_proxy = _pick(proxy_rows)
    if picked_proxy:
        return picked_proxy

    picked_foreign = _pick(foreign_rows)
    if picked_foreign:
        return picked_foreign

    return None


def _table_markdown(html: str, predicate: "Callable[[str], bool]") -> str:
    """Return the first table whose lowercased text matches ``predicate``."""
    import re

    from bs4 import BeautifulSoup

    from openbb_sec.utils.html2markdown import convert_table

    soup = BeautifulSoup(html, "html.parser")
    for table in soup.find_all("table"):
        text = re.sub(r"\s+", " ", table.get_text(" ", strip=True)).lower()
        if predicate(text):
            return convert_table(table).strip()
    return ""


def _table_from_section(
    html: str,
    section_pattern: str,
    table_predicate: "Callable[[str], bool] | None" = None,
) -> str:
    import re

    from bs4 import BeautifulSoup

    from openbb_sec.utils.html2markdown import convert_table

    soup = BeautifulSoup(html, "html.parser")
    section_re = re.compile(section_pattern, re.IGNORECASE)
    stop_re = re.compile(
        r"^\s*(?:[A-Z]\.\s+|ITEM\s+\d+[A-Z]?)",
        re.IGNORECASE,
    )

    fallback_table = ""

    for node in soup.find_all(string=section_re):
        parent = node.parent
        if not parent:
            continue
        first_table = ""
        for nxt in parent.find_all_next():
            if nxt.name == "table":
                normalized = re.sub(r"\s+", " ", nxt.get_text(" ", strip=True)).lower()
                markdown = convert_table(nxt).strip()
                if table_predicate is None:
                    return markdown
                if table_predicate(normalized):
                    return markdown
                if not first_table:
                    first_table = markdown
            text = nxt.get_text(" ", strip=True)
            if text and stop_re.match(text):
                break
        if first_table and not fallback_table:
            fallback_table = first_table

    return fallback_table


def _ownership_table_from_share_section(html: str) -> str:
    import re

    from bs4 import BeautifulSoup

    from openbb_sec.utils.html2markdown import convert_table

    soup = BeautifulSoup(html, "html.parser")
    section_re = re.compile(
        r"^\s*(?:[A-Z]\.\s*)?(?:share\s+ownership|security\s+ownership\s+of\s+certain\s+beneficial\s+owners)\b",
        re.IGNORECASE,
    )
    stop_re = re.compile(
        r"^\s*(?:[A-Z]\.\s+|ITEM\s+\d+[A-Z]?)",
        re.IGNORECASE,
    )

    for node in soup.find_all(string=section_re):
        parent = node.parent
        if not parent:
            continue

        section_tables: list[tuple[str, str]] = []
        for nxt in parent.find_all_next():
            if nxt.name == "table":
                normalized = re.sub(r"\s+", " ", nxt.get_text(" ", strip=True)).lower()
                markdown = convert_table(nxt).strip()
                if markdown:
                    section_tables.append((normalized, markdown))
            text = nxt.get_text(" ", strip=True)
            if text and stop_re.match(text):
                break

        if not section_tables:
            continue

        for idx, (normalized, markdown) in enumerate(section_tables):
            is_main = (
                "5% shareholder" in normalized
                or "5% shareholders" in normalized
                or "directors and executive officers" in normalized
            ) and (
                "voting power" in normalized
                or "beneficial ownership" in normalized
                or "percent" in normalized
            )
            if not is_main:
                continue

            content = markdown
            if idx + 1 < len(section_tables):
                next_normalized, next_markdown = section_tables[idx + 1]
                if (
                    "represents beneficial ownership" in next_normalized
                    or "voting power" in next_normalized
                ) and ("(1)" in next_normalized or "*" in next_normalized):
                    content = f"{content}\n\n{next_markdown}"
            return content

    return ""


def summary_compensation_table(html: str) -> str:
    """Return the Summary Compensation Table (Reg S-K Item 402(c)) as markdown."""
    return _table_markdown(
        html,
        lambda t: (
            "salary" in t
            and "total" in t
            and "stock award" in t
            and "principal position" in t
            and "year" in t
        ),
    )


def beneficial_owners_table(html: str) -> str:
    """Return the security-ownership table that lists 5%+ beneficial owners."""
    section_table = _ownership_table_from_share_section(html)
    if section_table:
        return section_table

    return _table_markdown(
        html,
        lambda t: (
            (
                (
                    "percent of class" in t
                    or "percent of common stock" in t
                    or "percent of common shares" in t
                    or "percent of outstanding" in t
                )
                and (
                    "beneficial owner" in t
                    or "name and address" in t
                    or "beneficially owned" in t
                )
            )
            or (
                ("5% shareholders" in t or "5% shareholder" in t)
                and (
                    "ownership" in t
                    or "voting power" in t
                    or "directors and executive officers" in t
                )
            )
        ),
    )


def management_profiles_table(html: str) -> str:
    """Return the directors-and-executive-officers share-ownership table."""
    return _table_markdown(
        html, lambda t: "directors and executive officers as a group" in t
    )


def management_information_from_proxy(html: str) -> str:
    """Return director/officer profile information from a proxy statement."""
    import re

    from bs4 import BeautifulSoup

    from openbb_sec.utils.html2markdown import html_to_markdown

    soup = BeautifulSoup(html, "html.parser")

    tables = []
    for table in soup.find_all("table"):
        normalized = re.sub(r"\s+", " ", table.get_text(" ", strip=True)).lower()
        if not normalized:
            continue
        tables.append((normalized, table))

    preferred = []
    for normalized, table in tables:
        if (
            "nominee and principal occupation" in normalized
            and "independent" in normalized
            and "age" in normalized
        ):
            preferred.append(table)
            continue

    if preferred:
        markdown = html_to_markdown(str(preferred[0]), keep_tables=True).strip()
        if markdown:
            return markdown

    fallback = []
    for normalized, table in tables:
        if "age" in normalized and (
            "director" in normalized
            or "position" in normalized
            or "business experience" in normalized
            or "nominee" in normalized
            or "executive officer" in normalized
        ):
            fallback.append(table)

    if fallback:
        markdown = html_to_markdown(str(fallback[0]), keep_tables=True).strip()
        if markdown:
            return markdown

    markdown = html_to_markdown(html, keep_tables=True).strip()
    if markdown:
        return markdown

    return ""


_PVP_NUMERIC = {
    "PeoTotalCompAmt": "peo_total_compensation",
    "PeoActuallyPaidCompAmt": "peo_compensation_actually_paid",
    "NonPeoNeoAvgTotalCompAmt": "average_neo_total_compensation",
    "NonPeoNeoAvgCompActuallyPaidAmt": "average_neo_compensation_actually_paid",
    "TotalShareholderRtnAmt": "total_shareholder_return",
    "PeerGroupTotalShareholderRtnAmt": "peer_group_total_shareholder_return",
    "NetIncomeLoss": "net_income",
    "CoSelectedMeasureAmt": "company_selected_measure",
}

_PVP_REQUIRED_FIELDS = {
    "peo_total_compensation",
    "peo_compensation_actually_paid",
    "average_neo_total_compensation",
    "average_neo_compensation_actually_paid",
    "total_shareholder_return",
    "peer_group_total_shareholder_return",
    "company_selected_measure",
}


def _ix_number(tag) -> "float | None":
    """Parse an inline-XBRL numeric fact, applying sign and scale."""
    text = tag.get_text(strip=True).replace(",", "").replace("$", "").replace("%", "")
    text = text.replace("—", "").replace("\xa0", "").strip()
    if not text or text in {"-", "--", "N/A", "n/a"}:
        return None
    try:
        value = float(text)
    except ValueError:
        return None
    value *= 10 ** int(tag.get("scale") or 0)
    if (tag.get("sign") or "") == "-":
        value = -value
    return value


def pay_versus_performance(html: str) -> list[dict]:
    """Return the Pay Versus Performance table from inline XBRL facts, by year."""
    import re

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")

    ctx_year: dict[str, str] = {}
    for ctx in soup.find_all(name=re.compile(r"context$", re.IGNORECASE)):
        if ctx.find(name=re.compile(r"explicitmember$", re.IGNORECASE)):
            continue
        period = ctx.find(name=re.compile(r"period$", re.IGNORECASE))
        if not period:
            continue
        date = period.find(name=re.compile(r"(enddate|instant)$", re.IGNORECASE))
        if date and date.get_text(strip=True)[:4].isdigit():
            ctx_year[_attr(ctx, "id")] = date.get_text(strip=True)[:4]

    rows: dict[str, dict] = {}
    for fact in soup.find_all(name=re.compile(r"nonfraction$", re.IGNORECASE)):
        concept = _attr(fact, "name").split(":")[-1]
        field = _PVP_NUMERIC.get(concept)
        year = ctx_year.get(_attr(fact, "contextref"))
        if not field or not year:
            continue
        rows.setdefault(year, {"year": int(year)})[field] = _ix_number(fact)

    if not rows:
        return []

    measure = None
    for candidate in soup.find_all(name=re.compile(r"nonnumeric$", re.IGNORECASE)):
        concept = _attr(candidate, "name").split(":")[-1]
        if concept in {"MeasureName", "CoSelectedMeasureName"}:
            measure = candidate
            break
    measure_name = measure.get_text(" ", strip=True) if measure else None
    if measure_name:
        for row in rows.values():
            row["company_selected_measure_name"] = measure_name

    if not any(
        any(
            field in row and row.get(field) is not None
            for field in _PVP_REQUIRED_FIELDS
        )
        for row in rows.values()
    ):
        return []

    return [rows[y] for y in sorted(rows, reverse=True)]
