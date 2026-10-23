"""Parse per-institution FR BHCPR report PDFs into structured section/line-item data."""

from __future__ import annotations

import re
from typing import Any

_DATE = re.compile(r"^\d{2}/\d{2}/\d{4}$")
_NUMBER = re.compile(r"^-?[\d,]+(?:\.\d+)?$")
_CHANGE = re.compile(r"^(1|5)-Year$")
_COUNT = re.compile(r"(?i)\bnumber\b")
_STATUS = re.compile(r"(?i)((?:30[\s–—-]+89|90\+?)\s+days past due|nonaccrual)\s*$")


def _iso(date: str) -> str:
    """Convert a ``MM/DD/YYYY`` date to an ISO ``YYYY-MM-DD`` string."""
    return f"{date[6:]}-{date[:2]}-{date[3:5]}"


def _to_number(token: str, *, scale: int) -> int | float | None:
    """Coerce a figure token to a number, scaling whole dollars from thousands."""
    text = (token or "").strip()
    if not _NUMBER.match(text):
        return None
    value = float(text.replace(",", "")) * scale
    return int(value) if value == int(value) else value


def _normalize(text: str) -> str:
    """Lower-case a caption to alphanumerics and single spaces for schema matching."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]", " ", (text or "").lower())).strip()


_SYNONYMS = {
    "oreo": "other real estate owned",
    "alll": "allowance for credit losses on loans and leases",
    "cre": "commercial real estate",
    "tps": "trust preferred securities",
    "subs": "subsidiaries",
    "sub": "subsidiary",
    "div": "dividends",
    "op": "operating",
    "ops": "operating",
    "commit": "commitments to fund",
    "te": "tax equivalent",
    "250k": "250 thousand",
    "nonresidential": "non residential",
    "bhc": "holding company",
    "hc": "holding company",
    "hcs": "holding companies",
    "expenses": "expense",
    "losses": "loss",
    "changes": "change",
    "gains": "gain",
    "institutions": "institution",
    "contracts": "contract",
    "interests": "interest",
    "derivatives": "derivative",
    "noninvest": "non investment",
    "commecial": "commercial",
    "cap": "capital",
    "ps": "preferred stock",
    "t1": "tier 1",
    "qual": "qualifying",
    "inc": "income",
    "pref": "preferred",
    "x": "",
}


def _token_list(text: str) -> list[str]:
    """Return a caption's word tokens in order, report abbreviations expanded."""
    out: list[str] = []
    for word in re.sub(r"\bu s\b", "us", _normalize(text)).split():
        out.extend(token for token in _SYNONYMS.get(word, word).split() if token)
    return out


def _tokens(text: str) -> frozenset[str]:
    """Return normalized word tokens of a caption with report abbreviations expanded."""
    return frozenset(_token_list(text))


def _contained(short: list[str], long: list[str]) -> bool:
    """Whether ``short``'s words sit inside ``long`` as a genuine containment."""
    if not short or not (set(short) <= set(long)):
        return False
    return long[: len(short)] == short or len(short) / len(long) >= 0.5


def match_index(  # noqa: PLR0911
    label: str, rows: list[dict[str, Any]], used: set[int], exact_only: bool = False
) -> int | None:
    """Return the index of the report row matching a guide line item, or ``None``."""
    key = _normalize(label)
    for index, row in enumerate(rows):
        if index not in used and _normalize(row["label"]) == key:
            return index
    if exact_only:
        return None
    query = _tokens(label)
    query_list = _token_list(label)
    if not query:
        return None

    def score(row_label: str) -> float:
        """Word-overlap score, boosted when one caption genuinely contains the other"""
        candidate = _tokens(row_label)
        candidate_list = _token_list(row_label)
        overlap = (
            len(query & candidate) / len(query | candidate)
            if query | candidate
            else 0.0
        )
        if _contained(query_list, candidate_list) or _contained(
            candidate_list, query_list
        ):
            return max(overlap, 0.75)
        return overlap

    scored = sorted(
        (
            (score(rows[index]["label"]), index)
            for index in range(len(rows))
            if index not in used
        ),
        key=lambda pair: (-pair[0], pair[1]),
    )
    if not scored:
        return None
    best, index = scored[0]
    if best >= 0.75:
        return index
    if best >= 0.6 and (len(scored) < 2 or best - scored[1][0] >= 0.12):
        return index
    return None


def _section_title(lines: list[str]) -> str | None:
    """Return a page's section title, the line after the column-label band."""
    for index, line in enumerate(lines):
        if line.startswith("BHC Name City/State") and index + 1 < len(lines):
            return lines[index + 1].strip()
    return None


def _identity(page: Any) -> dict[str, str | None]:
    """Return the institution name, city/state, and RSSD from the cover page."""
    lines = [line for line in (page.extract_text() or "").split("\n") if line.strip()]
    institution = city_state = rssd = None
    for index, line in enumerate(lines):
        match = re.search(r"RSSD Number:\s*(\d+)", line)
        if match:
            rssd = match.group(1)
        if line.startswith("BHC Name") and index:
            institution = lines[index - 1].strip() or None
        if line.startswith("City/State"):
            city_state = line[len("City/State") :].split("Section")[0].strip() or None
    return {"institution_name": institution, "city_state": city_state, "rssd_id": rssd}


def _words_by_line(words: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """Group words into visual lines by baseline, each sorted left to right."""
    ordered = sorted(words, key=lambda word: (round(word["top"]), word["x0"]))
    lines: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    last: float | None = None
    for word in ordered:
        if last is not None and abs(word["top"] - last) > 2.5:
            lines.append(current)
            current = []
        current.append(word)
        last = word["top"]
    if current:
        lines.append(current)
    return lines


def _anchors(page: Any, table: Any) -> list[tuple[float, str]]:
    """Return this table's column anchors: ``(x-center, label)`` left to right."""
    top, left, right = table.bbox[1], table.bbox[0] - 6, table.bbox[2] + 6
    header = [
        word
        for word in page.extract_words()
        if left <= word["x0"] <= right and word["top"] <= top + 34
    ]
    dated = [
        line
        for line in _words_by_line(header)
        if sum(bool(_DATE.match(w["text"])) for w in line) >= 3
    ]
    anchors: list[tuple[float, str]] = []
    if dated:
        line = min(dated, key=lambda group: abs(group[0]["top"] - top))
        for word in line:
            center = (word["x0"] + word["x1"]) / 2
            if _DATE.match(word["text"]):
                anchors.append((center, _iso(word["text"])))
            elif _CHANGE.match(word["text"]):
                anchors.append((center, f"change_{word['text'][0]}y"))
    for line in _words_by_line(header):
        for word in line:
            if _CHANGE.match(word["text"]):
                center = (word["x0"] + word["x1"]) / 2
                if not any(abs(center - x) < 4 for x, _ in anchors):
                    anchors.append((center, f"change_{word['text'][0]}y"))
    return sorted(anchors)


def parse_bhcpr_pdf(content: bytes) -> dict[str, Any]:
    """Parse a per-institution BHCPR report PDF into its identity and values.

    Parameters
    ----------
    content : bytes
        The raw ``ReturnFinancialReportPDF?rpt=BHCPR`` PDF bytes.

    Returns
    -------
    dict[str, Any]
        ``{"identity", "sections"}`` where ``sections`` maps each section title to a
        ``{normalized-label: {"label", "regime", "periods", "change"}}`` map.
        ``periods`` is ``{ISO-date: {sub-column: value}}`` with sub-columns ``bhc``,
        ``peer``, ``pct`` (ratio) or ``amount`` and ``pct_total`` (dollar); ``change``
        holds the trailing one- and five-year percent changes. Dollar amounts are
        scaled to full dollars; percents, ratios, and ranks are left as filed. A firm
        that did not file the BHCPR (a non-PDF error page) yields no sections.
    """
    import io

    import pdfplumber

    identity: dict[str, str | None] = {
        "institution_name": None,
        "city_state": None,
        "rssd_id": None,
    }
    sections: dict[str, list[dict[str, Any]]] = {}
    if not content.startswith(b"%PDF"):
        return {"identity": identity, "sections": sections}

    with pdfplumber.open(io.BytesIO(content)) as pdf:
        identity = _identity(pdf.pages[0])
        for page in pdf.pages[1:]:
            lines = [ln for ln in (page.extract_text() or "").split("\n") if ln.strip()]
            title = _section_title(lines)
            if not title:
                continue
            section = sections.setdefault(title, [])
            tables = []
            for table in page.find_tables():
                grid = table.extract()
                if not grid:
                    continue
                header = " ".join(cell or "" for cell in grid[0])
                if "BHC" in header and "Pct" in header:
                    regime, subs = "percent", ("bhc", "peer", "pct")
                elif "%" in header and "Total" in header:
                    regime, subs = "thousands", ("amount", "pct_total")
                else:
                    regime, subs = "thousands", ("amount",)
                anchors = _anchors(page, table)
                if not any(label.startswith("2") for _, label in anchors):
                    continue
                tables.append((table.bbox, anchors, regime, subs))

            pending = ""
            loan_type = ""
            for words in _words_by_line(page.extract_words()):
                top = words[0]["top"]
                match = next(
                    (t for t in tables if t[0][1] - 2 <= top <= t[0][3] + 2), None
                )
                if match is None:
                    continue
                bbox, anchors, regime, subs = match
                raw = " ".join(w["text"] for w in words if w["x1"] <= bbox[0] + 1)
                has_leader = bool(re.search(r"\.{2,}", raw))
                caption = re.sub(r"\.{2,}.*$", "", raw).strip().rstrip(".").strip()
                if not caption:
                    continue
                scale = 1 if regime == "percent" or _COUNT.search(caption) else 1000
                grouped: dict[str, list[dict[str, Any]]] = {}
                for word in words:
                    if word["x0"] < bbox[0] - 1 or not _NUMBER.match(word["text"]):
                        continue
                    center = (word["x0"] + word["x1"]) / 2
                    label = min(anchors, key=lambda a: abs(a[0] - center))[1]
                    grouped.setdefault(label, []).append(word)
                periods: dict[str, dict[str, Any]] = {}
                change: dict[str, Any] = {}
                for label, group in grouped.items():
                    values = [w["text"] for w in sorted(group, key=lambda w: w["x0"])]
                    if label.startswith("change"):
                        change[label[7:]] = _to_number(values[-1], scale=1)
                    else:
                        cell: dict[str, Any] = {}
                        for sub, token in zip(subs, values):
                            cell[sub] = _to_number(
                                token, scale=1 if sub == "pct_total" else scale
                            )
                        if cell:
                            periods[label] = cell
                if not periods and not change and not has_leader:
                    # status row completes.
                    pending = caption
                    continue
                status = _STATUS.search(caption)
                if status:
                    lead = caption[: status.start()].strip()
                    if lead:
                        loan_type = (
                            f"{pending} {lead}".strip()
                            if pending and len(pending.split()) <= 2
                            else lead
                        )
                    caption = f"{loan_type} {status.group(0)}".strip()
                pending = ""
                section.append(
                    {
                        "label": caption,
                        "regime": regime,
                        "periods": periods,
                        "change": {k: v for k, v in change.items() if v is not None},
                    }
                )

    return {"identity": identity, "sections": sections}
