"""FFIEC Central Data Repository (CDR) Public Data Distribution bulk client.

The CDR publishes bank-level Call Report and UBPR data as bulk downloads behind
an ASP.NET WebForms page. Retrieving a file is a three-step postback: load the
page for its view state, select a product to populate the reporting-period
dropdown, then post the download. The tab-delimited schedule files carry a
two-row header - each column's MDRM code, then its description - so the line-item
labels are embedded alongside the data.
"""

from __future__ import annotations

import csv
import io
import re
import zipfile
from typing import Any

from openbb_federal_reserve.utils.curl_session import get_session

URL = "https://cdr.ffiec.gov/public/PWS/DownloadBulkData.aspx"

# Friendly key -> the ASP.NET list-box product value.
PRODUCTS = {
    "call_single": "ReportingSeriesSinglePeriod",
    "call_four": "ReportingSeriesSubsetSchedulesFourPeriods",
    "ubpr_ratio_single": "PerformanceReportingSeriesSinglePeriod",
    "ubpr_ratio_four": "PerformanceReportingSeriesFourPeriods",
    "ubpr_rank": "PerformanceReportingSeriesRank",
    "ubpr_stats": "PerformanceReportingSeriesStats",
}

_PREFIX = "ctl00$MainContentHolder$"


def _get_session() -> Any:
    """Return a browser-impersonating ``curl_cffi`` session."""
    return get_session("cdr")


def _viewstate(html: str) -> dict[str, str]:
    """Extract the ASP.NET view-state fields carried across postbacks."""

    def _field(name: str) -> str:
        match = re.search(rf'id="{name}"[^>]*value="([^"]*)"', html)
        return match.group(1) if match else ""

    return {
        "__VIEWSTATE": _field("__VIEWSTATE"),
        "__VIEWSTATEGENERATOR": _field("__VIEWSTATEGENERATOR"),
    }


def _select_product(
    session: Any, value: str, radio: str = "TSVRadioButton"
) -> tuple[dict[str, str], list[tuple[str, str]]]:
    """Load the page, select a product, and return its view state and periods."""
    html = session.get(URL, timeout=60).text
    select = {
        **_viewstate(html),
        "__EVENTTARGET": f"{_PREFIX}ListBox1",
        "__EVENTARGUMENT": "",
        f"{_PREFIX}ListBox1": value,
        f"{_PREFIX}FormatType": radio,
        "AjaxScriptManager_HiddenField": "",
    }
    refreshed = session.post(URL, data=select, timeout=120).text
    block = re.search(r"DatesDropDownList[^>]*>(.*?)</select>", refreshed, re.DOTALL)
    periods = (
        re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)</option>', block.group(1))
        if block
        else []
    )
    return _viewstate(refreshed), [(value, text.strip()) for value, text in periods]


def list_periods(product: str) -> list[dict[str, str]]:
    """Return the available reporting periods for a product (cached quarterly).

    The period dropdown is sourced from the same ASP.NET postback the bulk
    download uses, so it is disk-cached on the release cadence to avoid re-running
    the GET/POST navigation every time the widget loads its date choices.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> list[dict[str, str]]:
        """Run the postback navigation and parse the period dropdown."""
        _, periods = _select_product(_get_session(), PRODUCTS[product])
        return [{"date_id": date_id, "date": date} for date_id, date in periods]

    return cached(
        ("cdr_periods", product),
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )


def fetch_bulk(product: str, period: str | None = None, fmt: str = "xbrl") -> bytes:
    """Download a product's bulk ZIP for a reporting period (cached quarterly).

    Parameters
    ----------
    product : str
        A key of :data:`PRODUCTS`.
    period : str | None
        The reporting period end date as ``MM/DD/YYYY``; defaults to the latest.
    fmt : str
        ``"xbrl"`` for the XBRL instances (precise types, units, signs) or
        ``"tsv"`` for the flat tab-delimited files.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    radio = "XBRLRadiobutton" if fmt == "xbrl" else "TSVRadioButton"

    def _producer() -> bytes:
        """Run the three-step postback flow and return the ZIP bytes."""
        session = _get_session()
        value = PRODUCTS[product]
        state, periods = _select_product(session, value, radio)
        if not periods:
            return b""
        date_id = next((pid for pid, text in periods if text == period), periods[0][0])
        download = {
            **state,
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            f"{_PREFIX}ListBox1": value,
            f"{_PREFIX}DatesDropDownList": date_id,
            f"{_PREFIX}FormatType": radio,
            f"{_PREFIX}TabStrip1$Download_0": "Download",
            "AjaxScriptManager_HiddenField": "",
        }
        return session.post(URL, data=download, timeout=400).content

    return cached(
        ("cdr", product, period or "latest", fmt),
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )


_UNIT_LABELS = {
    "USD": "USD (thousands)",
    "PURE": "Rate or ratio",
    "NONMONETARY": "Non-monetary",
}


def parse_xbrl_instance(content: bytes, rssd_id: str) -> dict[str, Any]:
    """Parse one bank's XBRL instance from a bulk ZIP.

    Reads the per-bank instance (named by RSSD), resolving each fact's value,
    unit, decimals, reporting period, and period type (instant for balance-sheet
    items, duration for income/flow items). Returns ``{name, date, items}``.
    """
    from xml.etree import ElementTree

    target = str(rssd_id).strip()
    archive = zipfile.ZipFile(io.BytesIO(content))
    member = next(
        (
            m
            for m in archive.namelist()
            if m.lower().endswith((".xbrl.xml", ".xbrl"))
            and re.search(rf"(?<!\d){re.escape(target)}(?!\d)", m)
        ),
        None,
    )
    name = _por_name(archive, target)
    if member is None:
        return {"name": name, "date": None, "form_type": None, "items": []}

    xbrli = "{http://www.xbrl.org/2003/instance}"
    raw = archive.read(member)
    # The schemaRef names the report form (Call: report031/041/051).
    form_match = re.search(rb"report(0\d\d)", raw)
    form_type = form_match.group(1).decode() if form_match else None
    # Source is the FFIEC CDR government endpoint; ElementTree does not resolve
    # external entities by default.
    root = ElementTree.fromstring(raw)  # noqa: S314

    contexts: dict[str, tuple[str, str]] = {}
    for context in root.findall(f"{xbrli}context"):
        period = context.find(f"{xbrli}period")
        if period is None:
            continue
        instant = period.find(f"{xbrli}instant")
        end = period.find(f"{xbrli}endDate")
        if instant is not None and instant.text:
            contexts[context.get("id", "")] = (instant.text, "instant")
        elif end is not None and end.text:
            contexts[context.get("id", "")] = (end.text, "duration")

    units: dict[str, str] = {}
    for unit in root.findall(f"{xbrli}unit"):
        measure = unit.find(f"{xbrli}measure")
        if measure is not None and measure.text:
            units[unit.get("id", "")] = measure.text.split(":")[-1].upper()

    items: list[dict[str, Any]] = []
    for fact in root:
        context_ref = fact.get("contextRef")
        if not context_ref or context_ref not in contexts:
            continue
        period_date, period_type = contexts[context_ref]
        unit = units.get(fact.get("unitRef", ""))
        items.append(
            {
                "mdrm": fact.tag.split("}")[-1],
                "value": (fact.text or "").strip(),
                "unit": _UNIT_LABELS.get(unit, unit),
                "decimals": fact.get("decimals"),
                # The "single period" filing also carries prior-period comparison
                # facts; each fact keeps its own period so they can be separated.
                "period": period_date,
                "period_type": period_type,
            }
        )
    report_date = max((item["period"] for item in items), default=None)
    return {
        "name": name,
        "date": report_date,
        "form_type": form_type,
        "items": items,
    }


def _por_name(archive: zipfile.ZipFile, rssd_id: str) -> str | None:
    """Look up a bank's name from a bulk ZIP's POR roster, if present."""
    member = next((m for m in archive.namelist() if "POR" in m), None)
    if member is None:
        return None
    rows = _reader(archive, member)
    header = [cell.strip('"') for cell in next(rows, [])]
    try:
        name_index = header.index("Financial Institution Name")
    except ValueError:
        return None
    for row in rows:
        if row and row[0].strip('"') == rssd_id and name_index < len(row):
            return row[name_index].strip()
    return None


def fetch_taxonomy(product: str, form_type: str | None = None) -> bytes:
    """Download a product's XBRL taxonomy ZIP (cached quarterly).

    Parameters
    ----------
    product : str
        A key of :data:`PRODUCTS`.
    form_type : str | None
        For Call Reports the taxonomy is per form (``"031"``, ``"041"``,
        ``"051"``); the download requires picking one. UBPR needs no form.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> bytes:
        """Select the product, request the taxonomy, and post the download."""
        session = _get_session()
        value = PRODUCTS[product]
        html = session.get(URL, timeout=60).text
        select = {
            **_viewstate(html),
            "__EVENTTARGET": f"{_PREFIX}ListBox1",
            "__EVENTARGUMENT": "",
            f"{_PREFIX}ListBox1": value,
            f"{_PREFIX}FormatType": "XBRLRadiobutton",
            "AjaxScriptManager_HiddenField": "",
        }
        refreshed = session.post(URL, data=select, timeout=120).text
        block = re.search(
            r"DatesDropDownList[^>]*>(.*?)</select>", refreshed, re.DOTALL
        )
        periods = (
            re.findall(r'<option[^>]*value="([^"]*)"', block.group(1)) if block else []
        )
        download = {
            **_viewstate(refreshed),
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            f"{_PREFIX}ListBox1": value,
            f"{_PREFIX}DatesDropDownList": periods[0] if periods else "",
            f"{_PREFIX}FormatType": "XBRLRadiobutton",
            f"{_PREFIX}TabStrip1$Download_Taxonomy_1": "Download Taxonomy",
            "AjaxScriptManager_HiddenField": "",
        }
        response = session.post(URL, data=download, timeout=300)
        if form_type is None:
            return response.content
        # Call Reports present a form-type chooser; post that selection.
        panel = response.text
        pick = {
            **_viewstate(panel),
            "__EVENTTARGET": f"{_PREFIX}FormTypeControl1$LinkButton{form_type}",
            "__EVENTARGUMENT": "",
            "AjaxScriptManager_HiddenField": "",
        }
        return session.post(URL, data=pick, timeout=300).content

    return cached(
        ("cdr_taxonomy", product, form_type or ""),
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )


_TYPE_LABELS = {
    "monetary": "Monetary",
    "nonNegativeMonetary": "Monetary",
    "pure": "Rate or ratio",
    "percent": "Percentage",
    "integer": "Integer",
    "nonNegativeInteger": "Integer",
    "decimal": "Decimal",
    "string": "Text",
    "date": "Date",
    "boolean": "Boolean",
}


def _type_label(raw_type: str) -> str | None:
    """Map an XBRL element type to a display label.

    Falls back to the base label for any unrecognized monetary or integer variant
    (e.g. a future ``nonPositiveMonetary``) so dollar and integer concepts are
    never silently left unscaled.
    """
    if raw_type in _TYPE_LABELS:
        return _TYPE_LABELS[raw_type]
    lower = raw_type.lower()
    if "monetary" in lower:
        return "Monetary"
    if "integer" in lower:
        return "Integer"
    return raw_type or None


def parse_taxonomy(content: bytes) -> list[dict[str, Any]]:
    """Parse an XBRL taxonomy ZIP into the concept schema.

    Returns one record per concept with its MDRM code, data type, period type
    (instant/duration), and debit/credit balance - the metadata needed to read
    the corresponding XBRL values correctly.
    """
    archive = zipfile.ZipFile(io.BytesIO(content))
    concepts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for member in archive.namelist():
        if not member.lower().endswith("concepts.xsd"):
            continue
        xml = archive.read(member).decode("utf-8", "ignore")
        for element in re.finditer(r"<(?:xsd:|xs:)?element\s+([^>]*?)/?>", xml):
            attrs = dict(re.findall(r'([\w:]+)="([^"]*)"', element.group(1)))
            code = attrs.get("name")
            if not code or code in seen:
                continue
            seen.add(code)
            raw_type = attrs.get("type", "").split(":")[-1].removesuffix("ItemType")
            concepts.append(
                {
                    "mdrm": code,
                    "data_type": _type_label(raw_type),
                    "period_type": attrs.get("xbrli:periodType"),
                    "balance": attrs.get("xbrli:balance"),
                }
            )
    return concepts


_XLINK = "{http://www.w3.org/1999/xlink}"


def _linkbase_member(archive: zipfile.ZipFile, suffixes: tuple[str, ...]) -> str | None:
    """Find the linkbase member whose name ends in one of the given suffixes."""
    return next(
        (m for m in archive.namelist() if m.lower().endswith(suffixes)),
        None,
    )


def _resolve_labels(archive: zipfile.ZipFile, member: str) -> dict[str, str]:
    """Resolve each presentation element's caption from a label linkbase."""
    from xml.etree import ElementTree

    labels: dict[str, str] = {}
    # Source is the FFIEC CDR government endpoint; ElementTree does not resolve
    # external entities by default.
    root = ElementTree.fromstring(archive.read(member))  # noqa: S314
    for link in root:
        locators: dict[str, str] = {}
        arcs: dict[str, str] = {}
        text: dict[str, str] = {}
        for element in link:
            tag = element.tag.split("}")[-1]
            if tag == "loc":
                locators[element.get(f"{_XLINK}label", "")] = element.get(
                    f"{_XLINK}href", ""
                ).split("#")[-1]
            elif tag == "labelArc":
                arcs[element.get(f"{_XLINK}from", "")] = element.get(f"{_XLINK}to", "")
            elif tag == "label":
                text[element.get(f"{_XLINK}label", "")] = (element.text or "").strip()
        for locator_label, concept in locators.items():
            target = arcs.get(locator_label)
            if target and text.get(target):
                labels[concept] = _clean_caption(text[target])
    return labels


def _clean_caption(caption: str) -> str:
    """Normalize a presentation caption into a readable table/line label.

    Strips the leading presentation marker (``#SectionTitle#`` keeps its text;
    ``#BlankLine#`` collapses to empty so the spacer is dropped), the
    ``(Form Type - NNN)`` suffix, the UBPR ``--Page N`` page-number suffix, and
    a trailing dollar-amount ``$`` marker; then collapses whitespace.
    """
    caption = re.sub(r"^#[^#]*#", "", caption)
    caption = re.sub(r"\s*\(Form Type - \d+\)\s*$", "", caption)
    caption = re.sub(r"\s*--\s*Page\s+\w+\s*$", "", caption)
    caption = re.sub(r"\s*\$\s*$", "", caption)
    return re.sub(r"\s+", " ", caption).strip()


def _is_column(caption: str | None) -> bool:
    """Return whether a caption is a column header rather than a line item."""
    if not caption:
        return False
    collapsed = caption.replace(" ", "").lower()
    return collapsed.startswith("column") or collapsed == "dummycolumn"


def _link_children(link: Any) -> dict[str, list[tuple[float, str]]]:
    """Build one presentation role's parent -> ordered-children map."""
    locators: dict[str, str] = {}
    children: dict[str, list[tuple[float, str]]] = {}
    for element in link:
        tag = element.tag.split("}")[-1]
        if tag == "loc":
            locators[element.get(f"{_XLINK}label", "")] = element.get(
                f"{_XLINK}href", ""
            ).split("#")[-1]
        elif tag == "presentationArc":
            parent = locators.get(
                element.get(f"{_XLINK}from", ""), element.get(f"{_XLINK}from", "")
            )
            child = locators.get(
                element.get(f"{_XLINK}to", ""), element.get(f"{_XLINK}to", "")
            )
            children.setdefault(parent, []).append(
                (float(element.get("order", "0")), child)
            )
    return children


def build_presentation(content: bytes) -> dict[str, dict[str, Any]]:
    """Build the report's line-item hierarchy from a taxonomy ZIP.

    Each presentation role (a report page) is walked depth-first - the order
    line items appear on the page - resolving every level's caption from the
    label linkbase and collapsing the column layer (Column A, B, ...). A concept
    appearing in more than one role keeps its richest (deepest) placement.
    Returns ``{mdrm: {order, section, parent, label, level}}`` in report order.
    """
    from collections import defaultdict
    from xml.etree import ElementTree

    archive = zipfile.ZipFile(io.BytesIO(content))
    presentation = _linkbase_member(archive, ("presentation.xml", "-pres.xml"))
    label = _linkbase_member(archive, ("label.xml", "-cap.xml"))
    if not presentation or not label:
        return {}

    labels = _resolve_labels(archive, label)
    best: dict[str, dict[str, Any]] = {}
    counter = [0]

    def descend(
        node: str, chain: list[str], children: dict[str, list[tuple[float, str]]]
    ) -> None:
        """Walk a role, accumulating the non-column caption chain."""
        caption = labels.get(node)
        # Skip empties (e.g. dropped #BlankLine# spacers) and column headers so
        # they never become a parent or label in the row hierarchy.
        updated = chain if not caption or _is_column(caption) else [*chain, caption]
        code = node.split("_", 1)[1] if "_" in node else ""
        if node not in children and re.fullmatch(r"[A-Z0-9]+", code):
            section = updated[0] if updated else None
            # The section is the table, never a parent; the parent is the line
            # above within the table (or None for a top-level line).
            parent = updated[-2] if len(updated) >= 3 else None
            placement = {
                "order": counter[0],
                "section": section,
                "parent": parent if parent != section else None,
                "label": updated[-1] if updated else None,
                "level": max(len(updated) - 1, 0),
            }
            counter[0] += 1
            if code not in best or placement["level"] > best[code]["level"]:
                best[code] = placement
        for _, child in sorted(children.get(node, [])):
            descend(child, updated, children)

    # Source is the FFIEC CDR government endpoint; ElementTree does not resolve
    # external entities by default.
    root = ElementTree.fromstring(archive.read(presentation))  # noqa: S314
    for link in root:
        children = _link_children(link)
        nested = {child for arcs in children.values() for _, child in arcs}
        for node in sorted(n for n in children if n not in nested):
            descend(node, [], children)

    # Re-number per section: each section is a table with its own 1..N order,
    # and sections are sequenced by where they first appear in the report.
    grouped: dict[Any, list[str]] = defaultdict(list)
    for code, placement in best.items():
        grouped[placement["section"]].append(code)
    sections = sorted(grouped, key=lambda s: min(best[c]["order"] for c in grouped[s]))
    for section_rank, section in enumerate(sections, start=1):
        for rank, code in enumerate(
            sorted(grouped[section], key=lambda c: best[c]["order"]), start=1
        ):
            best[code]["order"] = rank
            best[code]["section_order"] = section_rank
    return best


def presentation_map(
    report: str, form_type: str | None = None
) -> dict[str, dict[str, Any]]:
    """Return a report's cached line-item hierarchy keyed by MDRM code."""
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    return cached(
        ("cdr-presentation", report, form_type or ""),
        lambda: seconds_until_next_release("quarterly"),
        lambda: build_presentation(fetch_taxonomy(report, form_type)),
    )


def _reader(zip_file: zipfile.ZipFile, member: str):
    """Return a tab-delimited reader over a ZIP member."""
    return csv.reader(
        io.TextIOWrapper(zip_file.open(member), "utf-8", "ignore"), delimiter="\t"
    )


def bulk_rssids(content: bytes) -> set[str]:
    """Return the RSSDs present as filings in a bulk ZIP (from instance names)."""
    archive = zipfile.ZipFile(io.BytesIO(content))
    rssds: set[str] = set()
    for member in archive.namelist():
        match = re.search(r" FI (\d+)\(ID RSSD\)", member)
        if match:
            rssds.add(match.group(1))
    return rssds


def total_assets_by_rssd(
    period: str | None, rssd_ids: set[str] | list[str]
) -> dict[str, float]:
    """Map each bank RSSD to its Call Report total assets for the period.

    Used to choose a holding company's largest subsidiary bank. Reads RCFD2170
    (consolidated) or RCON2170 (domestic) at the most recent reported period;
    a missing value resolves to ``0.0``.
    """
    content = fetch_bulk("call_single", period, fmt="xbrl")
    assets: dict[str, float] = {}
    for rssd_id in rssd_ids:
        parsed = parse_xbrl_instance(content, str(rssd_id))
        best_period, best_value = "", 0.0
        for item in parsed["items"]:
            if item["mdrm"] in ("RCFD2170", "RCON2170") and item["value"]:
                try:
                    value = float(item["value"])
                except ValueError:
                    continue
                best_period, best_value = max(
                    (best_period, best_value), (item["period"] or "", value)
                )
        assets[str(rssd_id)] = best_value
    return assets


def resolve_fdic_cert(content: bytes, fdic_cert: str) -> str | None:
    """Map an FDIC certificate number to the bank's RSSD via the POR roster."""
    target = str(fdic_cert).strip()
    archive = zipfile.ZipFile(io.BytesIO(content))
    member = next((m for m in archive.namelist() if "POR" in m), None)
    if member is None:
        return None
    rows = _reader(archive, member)
    header = [cell.strip('"') for cell in next(rows, [])]
    try:
        cert_index = header.index("FDIC Certificate Number")
    except ValueError:
        return None
    for row in rows:
        if cert_index < len(row) and row[cert_index].strip() == target:
            return row[0].strip('"')
    return None
