"""Resolve an ECB presentation table to series keys and fetch its values."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openbb_ecb.utils.metadata import EcbMetadata

# A ">" plus non-breaking spaces, repeated per hierarchy level, gives the
# Blue-Book-style indentation in the (string) ``title`` column — matching the
# OECD presentation table's look (a plain table cannot indent on its own).
_INDENT = ">" + " " * 8


def _indent_title(label: str | None, level: int) -> str:
    """Indent a row label by its hierarchy depth."""
    label = label or ""
    return _INDENT * level + label if level > 0 else label


def _flatten(structure: list[dict]) -> tuple[list[dict], list[tuple], dict[str, set]]:
    """Flatten the resolved tree into rows, ``(row, path_codes)`` pairs, and the
    set of codes used per table dimension.

    ``path_codes`` holds the deepest dimension code seen along the path to a row
    (a child code overrides its ancestor for the same dimension).
    """
    rows: list[dict] = []
    node_paths: list[tuple] = []
    table_dim_codes: dict[str, set] = {}

    def walk(nodes: list[dict], depth: int, path: dict[str, str]) -> None:
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


async def build_presentation_table(
    metadata: EcbMetadata,
    table_id: str,
    context: dict[str, str],
    use_cache: bool = True,
    limit: int = 8,
) -> list[dict]:
    """Build a presentation table: an indented ``title`` per hierarchy row with
    the last ``limit`` periods pivoted into one column each (latest first).

    ``context`` fixes the non-hierarchy dimensions and supplies the aggregate
    (e.g. "total") value for any table dimension a given row does not pin —
    so a row that fixes only ``BS_ITEM``/``BS_COUNT_SECTOR`` still resolves the
    remaining table dimension from ``context``. One batched SDMX request fetches
    every cell's observations; series are matched back to rows by their full
    table-dimension code set.
    """
    from openbb_ecb.utils.data_cache import cached_records, make_key
    from openbb_ecb.utils.query_builder import fetch_sdmx_data

    table = metadata.get_table(table_id)
    dataflow_id = table["dataflow_id"]
    structure = metadata.get_table_structure(table_id)
    rows, node_paths, table_dim_codes = _flatten(structure)
    table_dims = set(table_dim_codes)

    # Each row's expected series is its path codes + context for unpinned table dims.
    fragment_to_row: dict = {}
    for row, path_codes in node_paths:
        if not path_codes:
            continue  # pure label header
        expected = {}
        for dim in table_dims:
            value = path_codes.get(dim) or context.get(dim)
            if value is None:
                expected = {}
                break
            expected[dim] = value
        if expected:
            fragment_to_row[frozenset(expected.items())] = row

    # A table dimension may be pinned by the hierarchy on some branches and by
    # context (an aggregate code) on others, so the fetch ORs both sets.
    dimensions = metadata.get_dataflow_dimensions(dataflow_id)

    def _key_part(dim_id: str) -> str:
        if dim_id in table_dims:
            codes = set(table_dim_codes[dim_id])
            if dim_id in context:
                codes.add(context[dim_id])
            return "+".join(sorted(codes))
        return context.get(dim_id, "")

    key = ".".join(_key_part(d["id"]) for d in dimensions)

    async def loader() -> list[dict]:
        return await fetch_sdmx_data(
            dataflow_id, key, detail="dataonly", last_n=limit, raise_empty=False
        )

    cache_key = make_key("presentation_table", table=table_id, key=key, n=limit)
    records = await cached_records("indicators", cache_key, loader, use_cache=use_cache)

    for record in records:
        if record.get("OBS_VALUE") is None:
            continue
        fragment = frozenset(
            (dim, record[dim]) for dim in table_dims if record.get(dim) is not None
        )
        row = fragment_to_row.get(fragment)
        if row is not None:
            row["obs"][record["date"]] = record["OBS_VALUE"]

    # Pivot: one column per observed period, latest first, with an indented title.
    dates = sorted({d for row in rows for d in row["obs"]}, reverse=True)
    return [
        {
            "title": _indent_title(row["label"], row["level"]),
            **{d: row["obs"].get(d) for d in dates},
        }
        for row in rows
    ]
