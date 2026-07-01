"""Resolve an ECB presentation table's series and fetch its recent values."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openbb_ecb.utils.metadata import EcbMetadata

_BATCH = 25
_CONCURRENCY = 10
_TITLE_SKIP = {"FREQ", "ADJUSTMENT"}


def _scale(value, unit_mult):
    """Scale an observation by ``10^UNIT_MULT``."""
    if value is None:
        return None
    try:
        return value * 10 ** int(unit_mult) if unit_mult not in (None, "") else value
    except (TypeError, ValueError):
        return value


def _or_key(keys: list[str]) -> str:
    """OR each dimension position across a batch of series keys into one query key."""
    positions: list[set[str]] = []
    for series_key in keys:
        for pos, part in enumerate(series_key.split(".")):
            if pos >= len(positions):
                positions.append(set())
            positions[pos].add(part)
    return ".".join("+".join(sorted(part)) for part in positions)


def _first(record: dict, name: str) -> str:
    """Return an attribute's text, preferring the decoded ``__label`` over the id."""
    return record.get(f"{name}__label") or record.get(name) or ""


def _dim_labels(record: dict) -> list[tuple[str, str]]:
    """Return ordered ``[(dimension_id, label)]`` from a parsed SDMX-JSON record."""
    return [
        (dim_id, record[f"{dim_id}__label"])
        for dim_id in record.get("_dim_ids") or []
        if record.get(f"{dim_id}__label")
    ]


def _resolve_labels(row: dict, varying: set[str]) -> tuple[str, str]:
    """Return ``(title, description)`` for a resolved row."""
    if row["dims"]:
        description = ", ".join(label for _, label in row["dims"])
        distinguishing = [(d, label) for d, label in row["dims"] if d in varying]
        title = (
            " · ".join(label for d, label in distinguishing if d not in _TITLE_SKIP)
            or " · ".join(label for _, label in distinguishing)
            or description
        )
        return title, description
    return (row["title"] or row["compl"]), (row["compl"] or row["title"])


async def _fetch_flow_records(
    table_id: str,
    flow: str,
    keys: list[str],
    limit: int,
    use_cache: bool,
    semaphore: asyncio.Semaphore,
) -> list[dict]:
    """Fetch every batch of a flow's keys concurrently and return all records."""
    from openbb_ecb.utils.data_cache import cached_records, make_key
    from openbb_ecb.utils.query_builder import fetch_sdmx_data

    async def fetch_batch(batch: list[str]) -> list[dict]:
        or_key = _or_key(batch)

        async def loader() -> list[dict]:
            return await fetch_sdmx_data(
                flow, or_key, detail="full", last_n=limit, raise_empty=False
            )

        cache_key = make_key(
            "presentation_table", table=table_id, flow=flow, key=or_key, n=limit
        )
        async with semaphore:
            return await cached_records(
                "indicators", cache_key, loader, use_cache=use_cache
            )

    batches = [keys[i : i + _BATCH] for i in range(0, len(keys), _BATCH)]
    results = await asyncio.gather(*(fetch_batch(b) for b in batches))
    return [record for batch in results for record in batch]


async def build_presentation_table(
    metadata: EcbMetadata,
    table_id: str,
    use_cache: bool = True,
    limit: int = 8,
) -> list[dict]:
    """Return the wide presentation table for a data-portal publication."""
    rows = metadata.get_table_rows(table_id)
    by_flow: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        by_flow[row["flow"]].append(row["key"])

    resolved: dict[tuple[str, str], dict] = {}
    order: list[tuple[str, str]] = []
    for row in rows:
        ident = (row["flow"], row["key"])
        if ident not in resolved:
            resolved[ident] = {
                "dims": [],
                "title": "",
                "compl": "",
                "unit": "",
                "obs": {},
            }
            order.append(ident)

    semaphore = asyncio.Semaphore(_CONCURRENCY)
    fetched = await asyncio.gather(
        *(
            _fetch_flow_records(table_id, flow, keys, limit, use_cache, semaphore)
            for flow, keys in by_flow.items()
        )
    )
    for flow, records in zip(by_flow, fetched):
        wanted = set(by_flow[flow])
        for record in records:
            series_key = record.get("series_key")
            if series_key not in wanted:
                continue
            row = resolved[(flow, series_key)]
            if not row["dims"] and not row["title"] and not row["compl"]:
                row["dims"] = _dim_labels(record)
                row["title"] = record.get("TITLE") or ""
                row["compl"] = record.get("TITLE_COMPL") or ""
                row["unit"] = _first(record, "UNIT") or _first(record, "UNIT_MEASURE")
            value = record.get("OBS_VALUE")
            if value is not None:
                row["obs"][record["date"]] = _scale(value, record.get("UNIT_MULT"))

    seen_by_dim: dict[str, set[str]] = defaultdict(set)
    for ident in order:
        for dim_id, label in resolved[ident]["dims"]:
            seen_by_dim[dim_id].add(label)
    varying = {dim_id for dim_id, labels in seen_by_dim.items() if len(labels) > 1}

    dates = sorted({d for ident in order for d in resolved[ident]["obs"]}, reverse=True)
    output: list[dict] = []
    for ident in order:
        row = resolved[ident]
        title, description = _resolve_labels(row, varying)
        if not title and not row["obs"]:
            continue
        output.append(
            {
                "title": title or ident[1],
                "description": description,
                "unit": row["unit"],
                **{d: row["obs"].get(d) for d in dates},
            }
        )
    return output
