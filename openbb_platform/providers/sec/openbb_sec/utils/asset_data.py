"""Server-side row model backing for SEC ABS-EE asset data XML.

The full document is stream-parsed once into a compact columnar form and
stored in the on-disk cache; paging, sorting and filtering are then served
from cache so an AgGrid datasource can scroll the whole file (100MB+) without
ever loading it into the browser.
"""

import contextlib
from typing import Any

from openbb_sec.utils.xml_render import _is_record, _local, is_asset_data_root

_FETCH_TIMEOUT = 120


def _fetch_stream(url: str):
    """Open a streaming, uncompressed response for a SEC document."""
    from openbb_sec.utils.definitions import SEC_HEADERS
    from openbb_sec.utils.ratelimit import sec_make_request

    headers = {**SEC_HEADERS, "Accept-Encoding": "identity"}
    resp = sec_make_request(url, headers=headers, stream=True, timeout=_FETCH_TIMEOUT)
    with contextlib.suppress(Exception):
        resp.raw.decode_content = True
    return resp


def parse_records_stream(stream) -> "tuple[list[str], list[tuple]]":
    """Stream-parse XML records into ordered columns and aligned value rows."""
    from lxml import etree

    columns: list[str] = []
    col_index: dict[str, int] = {}
    raw_rows: list[dict] = []
    saw_definition_tail = False
    context = etree.iterparse(
        stream,
        events=("start", "end"),
        recover=True,
        huge_tree=True,
        resolve_entities=False,
        no_network=True,
    )
    checked_root = False
    for event, elem in context:
        if event == "start":
            if not checked_root:
                checked_root = True
                if not is_asset_data_root(elem.tag):
                    return [], []
            continue
        if not _is_record(elem):
            continue
        record: dict = {}
        for child in elem:
            name = _local(child.tag)
            if name is None:
                continue
            tail = (child.tail or "").strip()
            if tail:
                saw_definition_tail = True
            if name not in col_index:
                col_index[name] = len(columns)
                columns.append(name)
            record[name] = (child.text or "").strip()
        if record:
            raw_rows.append(record)
        elem.clear()
        parent = elem.getparent()
        if parent is not None:
            while elem.getprevious() is not None:
                del parent[0]

    if saw_definition_tail:
        return [], []

    rows = [tuple(r.get(c, "") for c in columns) for r in raw_rows]
    return columns, rows


def load_asset_data(url: str) -> "tuple[list[str], list[tuple]]":
    """Return cached ``(columns, rows)`` for a document, parsing on a miss."""
    from openbb_sec.utils.cache import _cache_get, _cache_set, _make_key

    key = _make_key(url, suffix=" ::asset_rows")
    cached = _cache_get(key)
    if cached is not None:
        return cached

    resp = _fetch_stream(url)
    try:
        columns, rows = parse_records_stream(resp.raw)
    finally:
        with contextlib.suppress(Exception):
            resp.close()

    _cache_set(key, (columns, rows), None)
    return columns, rows


def _as_number(value: Any) -> "float | None":
    """Best-effort float conversion, returning None when not numeric."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _build_predicate(idx: int, cond: Any):
    """Build a row predicate from one AgGrid filter condition."""
    ftype = (getattr(cond, "filterType", None) or "text").lower()
    op = (getattr(cond, "type", None) or "").lower()
    val = getattr(cond, "filter", None)
    val_to = getattr(cond, "filterTo", None)
    values = getattr(cond, "values", None)

    if ftype == "set" or values is not None:
        allowed = {str(v) for v in (values or [])}
        return lambda r: r[idx] in allowed

    if ftype == "number":
        target = _as_number(val)
        target_to = _as_number(val_to)
        ops = {
            "equals": lambda n: n is not None and n == target,
            "notequal": lambda n: n is None or n != target,
            "greaterthan": lambda n: n is not None and n > target,
            "greaterthanorequal": lambda n: n is not None and n >= target,
            "lessthan": lambda n: n is not None and n < target,
            "lessthanorequal": lambda n: n is not None and n <= target,
            "inrange": lambda n: (
                None not in (n, target, target_to) and target <= n <= target_to
            ),
        }
        func = ops.get(op)
        return (lambda r, _f=func: bool(_f(_as_number(r[idx])))) if func else None

    needle = ("" if val is None else str(val)).lower()
    ops = {
        "contains": lambda s: needle in s,
        "notcontains": lambda s: needle not in s,
        "equals": lambda s: s == needle,
        "notequal": lambda s: s != needle,
        "startswith": lambda s: s.startswith(needle),
        "endswith": lambda s: s.endswith(needle),
        "blank": lambda s: s == "",
        "notblank": lambda s: s != "",
    }
    func = ops.get(op)
    if func:
        return lambda r: func(str(r[idx]).lower())
    return (lambda r: needle in str(r[idx]).lower()) if needle else None


def _apply_filters(col_index: dict, rows: list, filter_model: dict) -> list:
    """Filter rows by an AgGrid ``filterModel``."""
    predicates = []
    for col, cond in (filter_model or {}).items():
        idx = col_index.get(col)
        if idx is None:
            continue
        pred = _build_predicate(idx, cond)
        if pred is not None:
            predicates.append(pred)
    if not predicates:
        return rows
    return [r for r in rows if all(p(r) for p in predicates)]


def _apply_sort(col_index: dict, rows: list, sort_model: list) -> list:
    """Sort rows by an AgGrid ``sortModel`` (numeric-aware, multi-key)."""
    if not sort_model:
        return rows
    ordered = list(rows)
    for entry in reversed(sort_model):
        idx = col_index.get(entry.colId)
        if idx is None:
            continue
        descending = entry.sort == "desc"
        # Keep blanks last in both directions: rank them ahead of values when
        # descending (reverse flips them to the end) and after when ascending.
        blank_rank = -1 if descending else 1

        def key(row, i=idx, blank=blank_rank):
            value = row[i]
            if value is None or value == "":
                return (blank, 0.0, "")
            number = _as_number(value)
            if number is not None:
                return (0, number, "")
            return (0, 0.0, str(value).lower())

        ordered.sort(key=key, reverse=descending)
    return ordered


def query(columns: list, rows: list, request: Any) -> "tuple[list[dict], int]":
    """Filter, sort and page rows for an SSRM request; return page and total."""
    col_index = {name: i for i, name in enumerate(columns)}
    filtered = _apply_filters(col_index, rows, request.filterModel)
    ordered = _apply_sort(col_index, filtered, request.sortModel)
    total = len(ordered)
    start = max(request.startRow, 0)
    end = request.endRow if request.endRow > 0 else total
    page = ordered[start:end]
    return [dict(zip(columns, r)) for r in page], total
