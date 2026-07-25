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
    full_markdown = html_to_markdown(html, keep_tables=True).strip()

    def _toc_entries() -> list[tuple[str, str | None]]:
        entries: list[tuple[str, str | None]] = []
        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                cells = row.find_all(["td", "th"])
                if len(cells) < 2:
                    continue
                first_cell = cells[0]
                last_cell = cells[-1]
                page_text = re.sub(
                    r"\s+", " ", last_cell.get_text(" ", strip=True)
                ).strip()
                if not page_text or not re.fullmatch(r"\d{1,3}|[A-Z]-\d+", page_text):
                    continue
                anchor = first_cell.find("a")
                if anchor:
                    title = re.sub(
                        r"\s+", " ", anchor.get_text(" ", strip=True)
                    ).strip()
                    href = _attr(anchor, "href").strip()
                else:
                    title = re.sub(
                        r"\s+", " ", first_cell.get_text(" ", strip=True)
                    ).strip()
                    href = ""
                if len(title) < 4:
                    continue
                entries.append((title, href if href.startswith("#") else None))
        return entries

    def _extract_management_section_from_toc_anchors(
        entries: list[tuple[str, str | None]],
    ) -> str:
        if not entries:
            return ""

        start_matchers = (
            re.compile(r"(?i)^\s*executive\s+officers\s*$"),
            re.compile(r"(?i)^\s*directors\s*$"),
            re.compile(r"(?i)\bnominees?\s+for\s+election\b"),
            re.compile(r"(?i)\bnominees?\s+to\s+.*board\s+of\s+directors\b"),
            re.compile(r"(?i)\bdirectors?\s+and\s+executive\s+officers\b"),
        )
        stop_re = re.compile(
            r"(?i)\b(executive\s+compensation|compensation\s+discussion|management\s+proposals|shareholder\s+proposals|other\s+information)\b"
        )

        start_idx = -1
        for matcher in start_matchers:
            for i, (title, href) in enumerate(entries):
                if not href:
                    continue
                if not matcher.search(title):
                    continue
                anchor_id = href[1:]
                if soup.find(id=anchor_id):
                    start_idx = i
                    break
            if start_idx >= 0:
                break

        if start_idx < 0:
            return ""

        end_id: str | None = None
        for title, href in entries[start_idx + 1 :]:
            if not href:
                continue
            if stop_re.search(title):
                candidate_id = href[1:]
                if soup.find(id=candidate_id):
                    end_id = candidate_id
                    break

        start_href = entries[start_idx][1]
        if not start_href:
            return ""
        start_id = start_href[1:]
        start_anchor = soup.find(id=start_id)
        if not start_anchor:
            return ""

        start_node = start_anchor
        while start_node.parent and start_node.name not in {
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "p",
            "div",
            "table",
        }:
            start_node = start_node.parent

        section_nodes = [start_node]
        for sib in start_node.find_next_siblings():
            if end_id and (sib.get("id") == end_id or sib.find(id=end_id)):
                break
            section_nodes.append(sib)

        section_html = "".join(str(n) for n in section_nodes).strip()
        if not section_html:
            return ""
        return html_to_markdown(section_html, keep_tables=True).strip()

    def _toc_titles() -> list[str]:
        titles: list[str] = []
        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                cells = row.find_all(["td", "th"])
                if len(cells) < 2:
                    continue
                first = re.sub(r"\s+", " ", cells[0].get_text(" ", strip=True)).strip()
                last = re.sub(r"\s+", " ", cells[-1].get_text(" ", strip=True)).strip()
                if not first or not last:
                    continue
                if not re.fullmatch(r"\d{1,3}", last):
                    continue
                if len(first) < 6:
                    continue
                titles.append(first)
        return titles

    def _extract_management_section_from_markdown(
        markdown: str, toc_titles: list[str]
    ) -> str:
        if not markdown:
            return ""
        lines = markdown.splitlines()

        def _is_toc_line(line: str) -> bool:
            stripped = line.strip()
            if not stripped:
                return False
            bare = re.sub(r"^#{1,6}\s+", "", stripped)
            return bool(re.search(r"\s\d{1,3}$", bare))

        start_patterns = (
            r"^directors$",
            r"^executive\s+officers$",
            r"nominees?\s+for\s+election",
            r"nominees?\s+to\s+.*board\s+of\s+directors",
            r"directors?\s+and\s+(?:executive\s+officers|senior\s+management)",
        )
        stop_pattern = re.compile(
            r"(?i)\b(executive\s+compensation|compensation\s+discussion|pay\s+versus\s+performance|security\s+ownership|related\s+party|proposal\s+\d+|audit\s+committee|board\s+meetings\s+and\s+attendance|corporate\s+governance\s+framework)\b"
        )

        def _is_heading_like(line: str) -> bool:
            stripped = line.strip()
            if not stripped:
                return False
            if stripped.startswith("#"):
                return True
            bare = re.sub(r"^#{1,6}\s+", "", stripped)
            if len(bare) > 140:
                return False
            if bare.endswith((".", ";", ":")):
                return False
            if "," in bare:
                return False
            if re.search(r"(?i)\bproxy\s+statement\b", bare):
                return False
            return len(bare.split()) <= 18

        def _normalized(s: str) -> str:
            return re.sub(r"\s+", " ", s.strip()).lower()

        def _find_line_index(target: str, start_at: int = 0) -> int:
            norm_target = _normalized(target)
            for i in range(start_at, len(lines)):
                stripped = lines[i].strip()
                if not stripped or _is_toc_line(stripped):
                    continue
                if stripped.startswith("|"):
                    continue
                if "|" in stripped and re.search(r"\|\s*\d{1,3}\s*\|\s*$", stripped):
                    continue
                norm_line = _normalized(re.sub(r"^#{1,6}\s+", "", stripped))
                if norm_line == norm_target or norm_line.startswith(f"{norm_target} "):
                    return i
                if not _is_heading_like(stripped):
                    continue
                if norm_line == norm_target or norm_line.startswith(f"{norm_target} "):
                    return i
            return -1

        toc_start_title_idx = -1
        toc_start_line_idx = -1
        for pat in start_patterns:
            for i, title in enumerate(toc_titles):
                title_norm = _normalized(title)
                if not re.search(pat, title_norm, re.IGNORECASE):
                    continue
                line_idx = _find_line_index(title)
                if line_idx >= 0:
                    toc_start_title_idx = i
                    toc_start_line_idx = line_idx
                    break
            if toc_start_line_idx >= 0:
                break

        if toc_start_line_idx >= 0:
            end_idx = len(lines)
            for next_title in toc_titles[toc_start_title_idx + 1 :]:
                cand = _find_line_index(next_title, start_at=toc_start_line_idx + 1)
                if cand >= 0:
                    end_idx = cand
                    break
            if end_idx == len(lines):
                for i in range(toc_start_line_idx + 1, len(lines)):
                    stripped = lines[i].strip()
                    if not stripped or _is_toc_line(stripped):
                        continue
                    if stop_pattern.search(stripped):
                        end_idx = i
                        break
            section = "\n".join(lines[toc_start_line_idx:end_idx]).strip()
            if section:
                section_lines = [
                    line.strip() for line in section.splitlines() if line.strip()
                ]
                if section_lines and all(
                    line.startswith("|") or _is_toc_line(line) for line in section_lines
                ):
                    section = ""
            if section:
                return section

        start_idx = -1
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or _is_toc_line(stripped) or not _is_heading_like(stripped):
                continue
            for pat in start_patterns:
                if re.search(pat, stripped, re.IGNORECASE):
                    start_idx = i
                    break
            if start_idx >= 0:
                break

        if start_idx < 0:
            return ""

        end_idx = len(lines)
        for i in range(start_idx + 1, len(lines)):
            stripped = lines[i].strip()
            if not stripped or _is_toc_line(stripped):
                continue
            if stop_pattern.search(stripped):
                end_idx = i
                break

        section = "\n".join(lines[start_idx:end_idx]).strip()
        return section

    def _extract_management_section_markdown(toc_titles: list[str]) -> str:
        heading_re = re.compile(
            r"(?i)\b(nominees?\s+for\s+election\s+as\s+directors?|nominees?\s+to\s+.*board\s+of\s+directors|directors?\s+and\s+(?:executive\s+officers|senior\s+management)|executive\s+officers?)\b"
        )
        stop_re = re.compile(
            r"(?i)\b(executive\s+compensation|compensation\s+discussion|pay\s+versus\s+performance|security\s+ownership|related\s+party|proposal\s+\d+|audit\s+committee|board\s+meetings\s+and\s+attendance|corporate\s+governance\s+framework)\b"
        )

        preferred_titles = {
            re.sub(r"\s+", " ", title).strip().lower()
            for title in toc_titles
            if re.search(
                r"(?i)\b(nominees?\s+for\s+election\s+as\s+directors?|nominees?\s+to\s+.*board\s+of\s+directors|directors?|executive\s+officers?)\b",
                title,
            )
        }

        start = None
        for tag in soup.find_all(True):
            if tag.name in {"table", "tr", "td", "th", "script", "style", "noscript"}:
                continue
            text = re.sub(r"\s+", " ", tag.get_text(" ", strip=True)).strip().lower()
            if text and text in preferred_titles:
                start = tag
                break

        if not start:
            for tag in soup.find_all(True):
                if tag.name in {
                    "table",
                    "tr",
                    "td",
                    "th",
                    "script",
                    "style",
                    "noscript",
                }:
                    continue
                text = re.sub(r"\s+", " ", tag.get_text(" ", strip=True))
                if text and heading_re.search(text):
                    start = tag
                    break

        if not start:
            return ""

        section_nodes = [start]
        for sib in start.find_next_siblings():
            sib_text = re.sub(r"\s+", " ", sib.get_text(" ", strip=True))
            if sib_text and stop_re.search(sib_text):
                break
            section_nodes.append(sib)

        section_html = "".join(str(n) for n in section_nodes)
        if not section_html.strip():
            return ""

        markdown = html_to_markdown(section_html, keep_tables=True).strip()
        return markdown

    anchored_section = _extract_management_section_from_toc_anchors(_toc_entries())
    if anchored_section:
        return anchored_section

    markdown_section = _extract_management_section_from_markdown(
        full_markdown, _toc_titles()
    )
    if markdown_section:
        return markdown_section

    section_markdown = _extract_management_section_markdown(_toc_titles())
    if section_markdown:
        return section_markdown

    tables = []
    for table in soup.find_all("table"):
        normalized = re.sub(r"\s+", " ", table.get_text(" ", strip=True)).lower()
        if not normalized:
            continue
        toc_like = len(re.findall(r"\b\d{1,3}\b", normalized)) >= 6 and (
            "proxy statement summary" in normalized
            or "notice of" in normalized
            or "corporate governance" in normalized
            or "shareholder" in normalized
        )
        if toc_like:
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
        if (
            "director since" in normalized
            and "age" in normalized
            and ("director" in normalized or "nominee" in normalized)
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
            or "director since" in normalized
        ):
            fallback.append(table)

    if fallback:
        markdown = html_to_markdown(str(fallback[0]), keep_tables=True).strip()
        if markdown:
            return markdown

    if full_markdown:
        return ""

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
