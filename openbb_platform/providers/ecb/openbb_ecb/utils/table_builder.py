"""Resolve an ECB presentation table's series into an indented hierarchy."""

from __future__ import annotations

import asyncio
import re
from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openbb_ecb.utils.metadata import EcbMetadata

_BATCH = 25
_CONCURRENCY = 10
_INDENT = " " * 4
_SEGMENT = re.compile(r",\s+|\s+-\s+")
_AREA_DIMS = {"COUNTERPART_AREA", "COUNTER_AREA"}
_ENTITY_LAST = {"REF_AREA", "COUNTERPART_AREA", "COUNTER_AREA", "COUNT_AREA"}
_FREQ_RANK = {"D": 7, "B": 7, "W": 6, "M": 5, "Q": 4, "S": 3, "H": 3, "A": 2}


def _scale(value, unit_mult):
    """Scale an observation by ``10^UNIT_MULT``."""
    if value is None:
        return None
    try:
        return value * 10 ** int(unit_mult) if unit_mult not in (None, "") else value
    except (TypeError, ValueError):
        return value


def _or_key(keys: list[str], wildcard: int | None = None) -> str:
    """OR each dimension position across keys into one query key."""
    positions: list[set[str]] = []
    for series_key in keys:
        for pos, part in enumerate(series_key.split(".")):
            if pos >= len(positions):
                positions.append(set())
            positions[pos].add(part)
    return ".".join(
        "" if pos == wildcard else "+".join(sorted(part))
        for pos, part in enumerate(positions)
    )


def _batch_keys(keys: list[str], cap: int = 5000) -> list[list[str]]:
    """Chunk keys so an OR'd query's cartesian expansion stays bounded."""
    batches: list[list[str]] = []
    current: list[str] = []
    positions: list[set[str]] = []

    def expansion(pos_sets: list[set[str]]) -> int:
        total = 1
        for values in pos_sets:
            total *= len(values)
        return total

    for key in keys:
        parts = key.split(".")
        trial = [set(values) for values in positions]
        for pos, part in enumerate(parts):
            if pos >= len(trial):
                trial.append(set())
            trial[pos].add(part)
        if current and (len(current) >= _BATCH or expansion(trial) > cap):
            batches.append(current)
            current = []
            trial = [{part} for part in parts]
        current.append(key)
        positions = trial
    if current:
        batches.append(current)
    return batches


def _blank(series_key: str, index: int) -> str:
    """Return the key with dimension ``index`` blanked."""
    parts = series_key.split(".")
    if 0 <= index < len(parts):
        parts[index] = ""
    return ".".join(parts)


def _segments(title: str) -> list[str]:
    """Split an ECB ``TITLE`` into its comma/dash-separated hierarchy segments."""
    return [seg.strip() for seg in _SEGMENT.split(title) if seg.strip()]


def _short_unit(code: str, label: str) -> str:
    """Return a compact unit label."""
    text = label or code
    if "gross domestic product" in text.lower():
        return "% of GDP"
    text = re.split(r"[;(]", text, maxsplit=1)[0].strip()
    if len(text) > 32:
        text = text.split(",", 1)[0].strip()
    return text if text and len(text) <= 32 else code


def _as_of(obs: dict, date: str):
    """Return the observation at ``date`` or the most recent one before it."""
    if date in obs:
        return obs[date]
    prior = [d for d in obs if d < date]
    return obs[max(prior)] if prior else None


def _area_index(metadata: EcbMetadata, flow: str) -> int | None:
    """Return the position of a flow's counterpart-area dimension."""
    from openbb_core.app.model.abstract.error import OpenBBError

    try:
        dsd = metadata.get_dsd_for_dataflow(flow)
    except OpenBBError:
        return None
    for index, dim in enumerate(dsd.get("dimensions", [])):
        if (dim.get("id") or "").upper() in _AREA_DIMS:
            return index
    return None


def _freq_index(metadata: EcbMetadata, flow: str) -> int | None:
    """Return the position of a flow's frequency dimension."""
    from openbb_core.app.model.abstract.error import OpenBBError

    try:
        dsd = metadata.get_dsd_for_dataflow(flow)
    except OpenBBError:
        return None
    for index, dim in enumerate(dsd.get("dimensions", [])):
        if (dim.get("id") or "").upper() == "FREQ":
            return index
    return None


def _freq_code(positions: dict, flow: str, key: str) -> str:
    """Return a key's frequency code."""
    position = positions[flow]
    parts = key.split(".")
    return parts[position] if position is not None and position < len(parts) else ""


def _filter_frequency(
    metadata: EcbMetadata, published: list[tuple[str, str]], frequency: str | None
) -> list[tuple[str, str]]:
    """Keep the published rows of a single frequency."""
    positions = {
        flow: _freq_index(metadata, flow) for flow in {flow for flow, _ in published}
    }
    counts: dict[str, int] = defaultdict(int)
    for flow, key in published:
        code = _freq_code(positions, flow, key)
        if code:
            counts[code] += 1
    if not counts:
        return published
    target = (
        frequency
        if frequency in counts
        else max(counts, key=lambda code: (counts[code], _FREQ_RANK.get(code, 0)))
    )
    return [
        (flow, key)
        for flow, key in published
        if _freq_code(positions, flow, key) in ("", target)
    ]


def publication_frequencies(metadata: EcbMetadata, table_id: str) -> list[str]:
    """Return the frequency codes available in a publication table."""
    table = metadata.get_table(table_id)
    published = [(row["flow"], row["key"]) for row in table.get("rows") or []]
    positions = {
        flow: _freq_index(metadata, flow) for flow in {flow for flow, _ in published}
    }
    codes = {
        code for flow, key in published if (code := _freq_code(positions, flow, key))
    }
    return sorted(codes, key=lambda code: -_FREQ_RANK.get(code, 0))


def _strip_common(entries: list[tuple[tuple, list[str], dict]]) -> list:
    """Drop segments shared by every row unless they root a shared hierarchy."""
    if len(entries) < 2:
        return entries
    heads = {segments[0] for _, segments, _ in entries}
    if len(heads) == 1:
        return entries
    common = set(entries[0][1])
    for _, segments, _ in entries[1:]:
        common &= set(segments)
    if not common:
        return entries
    return [
        (sort_key, [s for s in segments if s not in common] or segments[-1:], row)
        for sort_key, segments, row in entries
    ]


def _flow_dims(metadata: EcbMetadata, flow: str) -> tuple[list[str], dict[str, dict]]:
    """Return a flow's dimension ids and their ``{code: label}`` maps."""
    from openbb_core.app.model.abstract.error import OpenBBError

    try:
        dsd = metadata.get_dsd_for_dataflow(flow)
    except OpenBBError:
        return [], {}
    dim_ids: list[str] = []
    labels: dict[str, dict] = {}
    for dim in dsd.get("dimensions", []):
        dim_id = dim.get("id")
        if not dim_id:
            continue
        dim_ids.append(dim_id)
        codelist_id = dim.get("codelist_id")
        labels[dim_id] = metadata.get_codelist(codelist_id) if codelist_id else {}
    return dim_ids, labels


async def _fetch_flow_records(
    table_id: str,
    flow: str,
    keys: list[str],
    limit: int,
    use_cache: bool,
    semaphore: asyncio.Semaphore,
    wildcard: int | None,
) -> list[dict]:
    """Fetch a flow's keys and return every observation record."""
    from openbb_ecb.utils.data_cache import cached_records, make_key
    from openbb_ecb.utils.query_builder import fetch_sdmx_data_csv

    async def fetch_batch(batch: list[str]) -> list[dict]:
        or_key = _or_key(batch, wildcard)

        async def loader() -> list[dict]:
            return await fetch_sdmx_data_csv(flow, or_key, detail="full", last_n=limit)

        cache_key = make_key(
            "presentation_table", table=table_id, flow=flow, key=or_key, n=limit
        )
        async with semaphore:
            return await cached_records(
                "indicators", cache_key, loader, use_cache=use_cache
            )

    batches = [[key] for key in keys] if wildcard is not None else _batch_keys(keys)
    results = await asyncio.gather(*(fetch_batch(b) for b in batches))
    return [record for batch in results for record in batch]


def _collapse(entries: list[tuple[tuple, list[str], dict]]) -> list:
    """Merge hierarchy levels not shared with an adjacent series into the leaf."""
    paths = [segments for _, segments, _ in entries]
    collapsed = []
    for index, (_, segments, row) in enumerate(entries):
        neighbors = paths[max(index - 1, 0) : index] + paths[index + 1 : index + 2]
        kept = [
            depth
            for depth in range(1, len(segments))
            if any(other[:depth] == segments[:depth] for other in neighbors)
        ]
        bounds = [0, *kept, len(segments)]
        merged = [
            ", ".join(segments[start:stop])
            for start, stop in zip(bounds, bounds[1:])
            if start < stop
        ]
        collapsed.append((merged, row))
    return collapsed


def _emit_hierarchy(
    entries: list[tuple[list[str], dict]], dates: list[str]
) -> list[dict]:
    """Turn sorted ``(segments, row)`` pairs into indented hierarchy rows."""
    output: list[dict] = []
    previous: list[str] = []
    for segments, row in entries:
        for level in range(len(segments) - 1):
            if previous[: level + 1] != segments[: level + 1]:
                output.append(
                    {
                        "title": _INDENT * level + segments[level],
                        "description": segments[level],
                        "unit": "",
                        **dict.fromkeys(dates),
                    }
                )
        leaf_level = len(segments) - 1
        output.append(
            {
                "title": _INDENT * leaf_level + segments[leaf_level],
                "description": row["definition"] or segments[leaf_level],
                "unit": row["unit"],
                **{d: row["obs"].get(d) for d in dates},
            }
        )
        previous = segments
    return output


def _flatten(structure: list[dict]) -> tuple[list[dict], list[tuple], dict[str, set]]:
    """Flatten a resolved JDF tree into rows, ``(row, path_codes)``, and dim codes."""
    rows: list[dict] = []
    node_paths: list[tuple] = []
    table_dim_codes: dict[str, set] = {}

    def walk(nodes: list[dict], depth: int, path: dict) -> None:
        for node in nodes:
            codes = dict(path)
            dim_id = node.get("dimension_id")
            if dim_id and node.get("code"):
                codes[dim_id] = node["code"]
                table_dim_codes.setdefault(dim_id, set()).add(node["code"])
            row = {"level": depth, "label": node.get("label"), "obs": {}}
            rows.append(row)
            node_paths.append((row, codes))
            walk(node.get("children", []), depth + 1, codes)

    walk(structure, 0, {})
    return rows, node_paths, table_dim_codes


def _jdf_units(
    metadata: EcbMetadata, dataflow_id: str, dims_order: list[str]
) -> dict[str, tuple[int, dict]]:
    """Return the position and codes of the unit-bearing dimensions."""
    from openbb_core.app.model.abstract.error import OpenBBError

    try:
        dsd = metadata.get_dsd_for_dataflow(dataflow_id)
    except OpenBBError:
        return {}
    out: dict[str, tuple[int, dict]] = {}
    for dim in dsd.get("dimensions", []):
        dim_id = dim.get("id")
        if (
            dim_id in ("UNIT_MEASURE", "UNIT", "TRANSFORMATION")
            and dim_id in dims_order
        ):
            codes = metadata.get_codelist(dim.get("codelist_id") or "")
            out[dim_id] = (dims_order.index(dim_id), codes)
    return out


def _row_unit(key: str | None, units: dict[str, tuple[int, dict]]) -> str:
    """Return the compact unit for a resolved series key."""
    if not key:
        return ""
    parts = key.split(".")
    trans = units.get("TRANSFORMATION")
    if trans and trans[0] < len(parts) and parts[trans[0]] not in ("", "N", "_Z"):
        code = parts[trans[0]]
        return _short_unit(code, trans[1].get(code, ""))
    for dim in ("UNIT_MEASURE", "UNIT"):
        entry = units.get(dim)
        if entry and entry[0] < len(parts) and parts[entry[0]]:
            code = parts[entry[0]]
            return _short_unit(code, entry[1].get(code, ""))
    return ""


async def _build_jdf_table(
    metadata: EcbMetadata,
    table_id: str,
    context: dict,
    use_cache: bool,
    limit: int,
) -> list[dict]:
    """Build a JDF hierarchical table from its resolved node keys."""
    from openbb_ecb.utils.data_cache import cached_records, make_key
    from openbb_ecb.utils.query_builder import fetch_sdmx_data_csv

    table = metadata.get_table(table_id)
    dataflow_id = table["dataflow_id"]
    structure = metadata.get_table_structure(table_id)
    rows, node_paths, _ = _flatten(structure)
    leaf_keys = table.get("leaf_keys") or []
    dims_order = [d["id"] for d in metadata.get_dataflow_dimensions(dataflow_id)]
    default = metadata.get_table_default_context(table_id)
    overrides = {
        dim: value
        for dim, value in (context or {}).items()
        if dim in dims_order and default.get(dim) != value
    }

    row_of: dict[str, list[dict]] = defaultdict(list)
    for (row, _), key in zip(node_paths, leaf_keys):
        if not key:
            continue
        parts = key.split(".")
        for dim, value in overrides.items():
            parts[dims_order.index(dim)] = value
        final = ".".join(parts)
        row["key"] = final
        row_of[final].append(row)

    async def fetch_batch(batch: list[str]) -> list[dict]:
        or_key = _or_key(batch)

        async def loader() -> list[dict]:
            return await fetch_sdmx_data_csv(
                dataflow_id, or_key, detail="full", last_n=limit
            )

        cache_key = make_key("presentation_table", table=table_id, key=or_key, n=limit)
        return await cached_records(
            "indicators", cache_key, loader, use_cache=use_cache
        )

    keys = sorted(row_of)
    batches = _batch_keys(keys)
    results = await asyncio.gather(*(fetch_batch(b) for b in batches))
    for record in (r for batch in results for r in batch):
        record_key = ".".join(record.get(d) or "" for d in dims_order)
        for row in row_of.get(record_key, []):
            if not row.get("definition"):
                row["definition"] = (
                    record.get("TITLE_COMPL") or record.get("TITLE") or ""
                )
            if not row.get("unit_code"):
                row["unit_code"] = (
                    record.get("UNIT") or record.get("UNIT_MEASURE") or ""
                )
            value = record.get("OBS_VALUE")
            if value is not None:
                row["obs"][record["date"]] = _scale(value, record.get("UNIT_MULT"))

    dates = sorted({d for row in rows for d in row["obs"]}, reverse=True)[:limit]
    units = _jdf_units(metadata, dataflow_id, dims_order)
    unit_labels = metadata.get_codelist("CL_UNIT")

    def row_unit(row: dict) -> str:
        unit = _row_unit(row.get("key"), units)
        code = row.get("unit_code") or ""
        return unit or _short_unit(code, unit_labels.get(code, ""))

    return [
        {
            "title": _INDENT * row["level"] + (row["label"] or ""),
            "description": row.get("definition") or row["label"] or "",
            "unit": row_unit(row),
            **{d: _as_of(row["obs"], d) for d in dates},
        }
        for row in rows
    ]


async def build_presentation_table(
    metadata: EcbMetadata,
    table_id: str,
    use_cache: bool = True,
    limit: int = 8,
    context: dict | None = None,
) -> list[dict]:
    """Return a presentation table as an indented hierarchy of line items."""
    table = metadata.get_table(table_id)
    if table.get("source") == "jdf":
        slice_ = (
            context
            if context is not None
            else metadata.get_table_default_context(table_id)
        )
        return await _build_jdf_table(metadata, table_id, slice_, use_cache, limit)
    return await _build_publications_table(
        metadata, table_id, use_cache, limit, (context or {}).get("FREQ")
    )


def _entity_segments(
    ident: tuple[str, str],
    group: list[tuple[str, str]],
    dims_of: dict,
    labels: dict[str, dict],
    key_fallback: bool = True,
) -> list[str]:
    """Return the labels of the dimensions distinguishing ``ident`` in its group."""
    differing = [
        (dim, code)
        for dim, code in dims_of[ident].items()
        if code and len({dims_of[member].get(dim) for member in group}) > 1
    ]
    if not differing:
        if not key_fallback:
            return []
        own = ident[1].split(".")
        others = [member[1].split(".") for member in group]
        parts = [
            part
            for pos, part in enumerate(own)
            if len({o[pos] for o in others if pos < len(o)}) > 1
        ]
        return [", ".join(parts)]
    head = [
        labels.get(dim, {}).get(code, code)
        for dim, code in differing
        if dim not in _ENTITY_LAST
    ]
    tail = [
        labels.get(dim, {}).get(code, code)
        for dim, code in differing
        if dim in _ENTITY_LAST
    ]
    return head + tail


def _ingest(
    by_flow: dict[str, list[str]],
    fetched: list[list[dict]],
    wildcard: dict[str, int | None],
    flow_dims: dict[str, tuple[list[str], dict]],
    unit_labels: dict[str, str],
) -> tuple[dict, dict, dict]:
    """Collect series rows, dimension values and parent keys from the records."""
    series: dict[tuple[str, str], dict] = {}
    dims_of: dict[tuple[str, str], dict] = {}
    parent_of: dict[tuple[str, str], tuple[str, str]] = {}
    for flow, records in zip(by_flow, fetched):
        area = wildcard[flow]
        keys = set(by_flow[flow])
        blank_to_key: dict[str, str] = {}
        if area is not None:
            for key in by_flow[flow]:
                blank_to_key.setdefault(_blank(key, area), key)
        dim_ids = flow_dims[flow][0]
        for record in records:
            series_key = record.get("series_key")
            if not series_key:
                continue
            if area is not None:
                parent_key = blank_to_key.get(_blank(series_key, area))
            else:
                parent_key = series_key if series_key in keys else None
            if parent_key is None:
                continue
            ident = (flow, series_key)
            if ident not in series:
                title = record.get("TITLE") or ""
                unit = record.get("UNIT") or record.get("UNIT_MEASURE") or ""
                series[ident] = {
                    "title": title,
                    "definition": record.get("TITLE_COMPL") or title,
                    "unit": _short_unit(unit, unit_labels.get(unit, "")),
                    "obs": {},
                }
                dims_of[ident] = {d: record.get(d) for d in dim_ids}
                parent_of[ident] = (flow, parent_key)
            value = record.get("OBS_VALUE")
            if value is not None:
                series[ident]["obs"][record["date"]] = _scale(
                    value, record.get("UNIT_MULT")
                )
    return series, dims_of, parent_of


def _geo_entry(
    ident: tuple[str, str],
    parent: tuple[str, str],
    area: int,
    group: list[tuple[str, str]],
    series: dict,
    flow_dims: dict[str, tuple[list[str], dict]],
) -> tuple[tuple, list[str]]:
    """Return ``(sub_key, segments)`` for a counterpart-expanded series."""
    anchor = (
        parent
        if parent in series
        else min(group, key=lambda member: len(series[member]["title"]))
    )
    segments = _segments(series[anchor]["title"]) or [parent[1]]
    if ident == anchor:
        return (0, ""), segments
    flow, series_key = ident
    dim_ids, labels = flow_dims[flow]
    code = series_key.split(".")[area]
    label = labels.get(dim_ids[area], {}).get(code, code)
    return (1, label.lower()), segments + [label]


def _pub_segments(
    ident: tuple[str, str],
    row: dict,
    series: dict,
    title_groups: dict,
    dims_of: dict,
    flow_dims: dict,
) -> list[str]:
    """Return the hierarchy segments for a publication series."""
    flow, series_key = ident
    segments = _segments(row["title"])
    group = title_groups[(flow, row["title"])]
    if len(group) > 1:
        segments = segments + _entity_segments(
            ident, group, dims_of, flow_dims[flow][1]
        )
    if not segments:
        flow_group = [i for i in series if i[0] == flow]
        if len(flow_group) > 1:
            segments = _entity_segments(
                ident, flow_group, dims_of, flow_dims[flow][1], key_fallback=False
            )
        if not segments:
            segments = [series_key]
    return segments


async def _build_publications_table(
    metadata: EcbMetadata,
    table_id: str,
    use_cache: bool = True,
    limit: int = 8,
    frequency: str | None = None,
) -> list[dict]:
    """Return a data-portal publication table as an indented hierarchy."""
    table = metadata.get_table(table_id)
    unit_labels = metadata.get_codelist("CL_UNIT")
    geographical = "geographical" in (
        f"{table.get('title', '')} {table.get('subcategory', '')}".lower()
    )
    published = [(row["flow"], row["key"]) for row in table.get("rows") or []]
    published = _filter_frequency(metadata, published, frequency)
    pub_index: dict[tuple[str, str], int] = {}
    for index, ident in enumerate(published):
        pub_index.setdefault(ident, index)
    by_flow: dict[str, list[str]] = defaultdict(list)
    for flow, key in published:
        by_flow[flow].append(key)
    wildcard = {
        flow: (_area_index(metadata, flow) if geographical else None)
        for flow in by_flow
    }
    flow_dims = {flow: _flow_dims(metadata, flow) for flow in by_flow}

    semaphore = asyncio.Semaphore(_CONCURRENCY)
    fetched = await asyncio.gather(
        *(
            _fetch_flow_records(
                table_id, flow, keys, limit, use_cache, semaphore, wildcard[flow]
            )
            for flow, keys in by_flow.items()
        )
    )

    series, dims_of, parent_of = _ingest(
        by_flow, fetched, wildcard, flow_dims, unit_labels
    )

    geo_groups: dict[tuple[str, str], list] = defaultdict(list)
    title_groups: dict[tuple[str, str], list] = defaultdict(list)
    for ident in series:
        if wildcard[ident[0]] is not None:
            geo_groups[parent_of[ident]].append(ident)
        else:
            title_groups[(ident[0], series[ident]["title"])].append(ident)

    entries: list[tuple[tuple, list[str], dict]] = []
    for ident, row in series.items():
        flow, series_key = ident
        parent = parent_of[ident]
        rank = pub_index[parent]
        area = wildcard[flow]
        if area is not None:
            sub, segments = _geo_entry(
                ident, parent, area, geo_groups[parent], series, flow_dims
            )
        else:
            segments = _pub_segments(
                ident, row, series, title_groups, dims_of, flow_dims
            )
            if not row["definition"]:
                row["definition"] = ", ".join(segments)
            sub = (0, "")
        entries.append(((rank, *sub), segments, row))

    entries.sort(key=lambda entry: entry[0])
    entries = _strip_common(entries)
    dates = sorted(
        {date for row in series.values() for date in row["obs"]}, reverse=True
    )[:limit]
    for row in series.values():
        row["obs"] = {date: _as_of(row["obs"], date) for date in dates}
    return _emit_hierarchy(_collapse(entries), dates)
