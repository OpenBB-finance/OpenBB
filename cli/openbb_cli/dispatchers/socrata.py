"""Generate a ``.spec`` file from a Socrata story JSON.

Socrata datasets have no OpenAPI spec — instead, each portal exposes per-
asset metadata at ``/api/views/{uid}.json`` (columns + types + description)
and serves data at ``/resource/{uid}.json`` with the SoQL query model
(``$select`` / ``$where`` / ``$limit`` / ``$offset`` / ``$order`` / ``$group``
/ ``$having`` / ``$q``). A Socrata "story" is a curated narrative document
that embeds visualizations, each pointing at a backing dataset by 4x4 UID.

This module turns a story URL (or a path to a previously-downloaded story
JSON) into a single ``.spec`` document that the existing fetcher_gen /
pydantic_gen pipeline can consume unchanged. The strategy:

1. Walk the story document for every ``datasetUid`` value (deduped).
2. For each UID, fetch ``/api/views/{uid}.json`` and skip anything whose
   ``assetType`` isn't ``"dataset"`` (charts / maps / filtered views are
   reachable through the same backing dataset, so wrapping them is noise).
3. Slugify the dataset's ``name`` — that becomes the command's namespace.
4. Build one ``{namespace}.query`` command per dataset whose
   ``response_schema`` reflects the column shape and whose ``parameters``
   are the constant SoQL set.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

# Concurrency for the parallel HTTP fan-out in the spec generator.
# Socrata's per-IP rate limit is generous enough to handle this size
# without throttling, and the throughput win versus serial fetches
# (~10× on a 12-dataset story) is the main reason story → spec
# generation dropped from ~30s to ~3s.
_DISCOVERY_MAX_WORKERS = 20

from openbb_cli.dispatchers.spec import SPEC_VERSION, _generator_identifier

# Socrata caps ``cachedContents.top`` at 20 entries — when a column hits
# that cap, more distinct values exist that aren't shown in metadata. We
# fall back to a server-side SoQL query for the full set in that case.
_CACHED_TOP_CAP = 20

# Hard ceiling on the number of distinct values we'll embed in a
# generated ``Literal`` / ``choices`` constraint. Past this the resulting
# argparse / Pydantic surface becomes unwieldy (multi-thousand-line
# ``--help`` output, slow validation) and the column probably isn't a
# true enumeration anyway. We probe with ``limit + 1`` so we can detect
# overflow.
_MAX_RESOLVED_CHOICES = 1000

# Numeric columns get a much tighter cap. ``month`` (12 values) /
# ``year`` (a few decades' worth) are real enums; prices / percentages /
# observation counts are continuous measures that happen to have a
# bounded distinct set within a single dataset. Enumerating 700 fuel
# prices as a ``Literal`` produces a useless UX, so anything past this
# threshold falls through to "no constraint, free numeric input."
_NUMERIC_CHOICE_CAP = 50

_NUMERIC_TYPES: frozenset[str] = frozenset({"number", "money", "percent", "double"})


def _coerce_choices_to_type(values: list[Any], data_type: str) -> list[Any]:
    """Cast distinct-value strings to match the column's declared type.

    Socrata's ``/resource/`` endpoint serializes everything as strings —
    ``year`` columns typed ``number`` come back as ``"2024"``. The
    ``Literal[...]`` set we generate has to match the field type the
    Pydantic model declares, otherwise valid input (``year=2024`` int)
    gets rejected against ``Literal["2024", ...]``. Skip a value
    silently if it can't be coerced cleanly — typically a stray null or
    sentinel string in an otherwise-numeric column.
    """
    if data_type in _NUMERIC_TYPES:
        coerced: list[Any] = []
        for v in values:
            try:
                num = float(v)
            except (TypeError, ValueError):
                continue
            # Prefer ``int`` for whole-number values so the Literal
            # reads cleanly (``Literal[2024, 2025]`` not ``Literal[2024.0,
            # 2025.0]``) AND so ``year=2024`` from the caller matches.
            if num.is_integer():
                coerced.append(int(num))
            else:
                coerced.append(num)
        return coerced
    if data_type == "checkbox":
        coerced_bool: list[Any] = []
        for v in values:
            if v is None:
                continue
            if isinstance(v, bool):
                coerced_bool.append(v)
            elif isinstance(v, str) and v.lower() in {"true", "false"}:
                # Socrata serializes booleans as the strings ``"true"`` /
                # ``"false"`` — parse properly rather than relying on
                # truthy-string coercion (``bool("false") is True``).
                coerced_bool.append(v.lower() == "true")
        return coerced_bool
    return values


def _cached_top_values(column: dict[str, Any]) -> list[Any]:
    """Pull the items out of a column's ``cachedContents.top`` list."""
    cached = column.get("cachedContents") or {}
    top = cached.get("top") or []
    values: list[Any] = []
    for entry in top:
        if isinstance(entry, dict):
            item = entry.get("item")
            if item is not None:
                values.append(item)
        elif entry is not None:
            values.append(entry)
    return values


def _is_categorical_column(column: dict[str, Any]) -> bool:
    """Return True when querying for distinct values is worthwhile.

    Only text-typed columns are reasonable enumeration candidates —
    numeric columns (revenue, quantity, lat/lon) are continuous, dates
    are continuous-shaped, and object-typed columns (URL, location) are
    structured records that don't filter sensibly via equality.
    """
    return (column.get("dataTypeName") or "text") in ("text", "html")


async def afetch_column_distinct_values(
    client: httpx.AsyncClient,
    host: str,
    uid: str,
    field_name: str,
    *,
    limit: int = _MAX_RESOLVED_CHOICES,
) -> list[Any] | None:
    """Resolve a column's full distinct-value set via SoQL (async).

    Issues ``?$select=<col>&$group=<col>&$order=<col>&$limit=<n>+1`` and
    returns the values when the response stays within ``limit``. Returns
    ``None`` when:

    * The response hits ``limit + 1`` rows (overflow — column has too
      many distinct values to inline as a closed set).
    * The HTTP request fails for any reason — network, rate limit,
      schema mismatch — in which case the caller falls back to the
      cached top values from metadata.
    """
    query = urllib.parse.urlencode(
        {
            "$select": field_name,
            "$group": field_name,
            "$order": field_name,
            "$limit": str(limit + 1),
        }
    )
    url = f"{host.rstrip('/')}/resource/{uid}.json?{query}"
    try:
        response = await client.get(url)
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError, OSError):
        return None
    if not isinstance(payload, list) or len(payload) > limit:
        return None
    out: list[Any] = []
    for row in payload:
        if not isinstance(row, dict):
            continue
        value = row.get(field_name)
        if value is not None:
            out.append(value)
    return out


def _column_choices(
    column: dict[str, Any],
    *,
    host: str | None = None,
    uid: str | None = None,
    resolver: Any = None,
    choices_cache: dict[tuple[str, str], list[Any] | None] | None = None,
) -> list[Any]:
    """Return the closed ``choices`` set for a column, or ``[]`` if unbounded.

    Lookup order:

    * ``choices_cache`` (when supplied AND the ``(uid, field)`` key is
      present) — pre-computed by the spec generator's parallel probe
      pass. No HTTP issued.
    * ``resolver`` — single-fetch path used by unit tests that inject a
      stub. Falls back to the module-level ``fetch_column_distinct_values``
      when ``host`` / ``uid`` are present and no resolver is given.
    * ``cachedContents.top`` from the metadata — used only when no
      host/uid is available (also unit-test path).
    """
    field_name = column.get("fieldName") or column.get("name")
    if (
        choices_cache is not None
        and host
        and uid
        and field_name
        and (uid, field_name) in choices_cache
    ):
        cached = choices_cache[(uid, field_name)]
        if cached is None:
            return []
        type_name = column.get("dataTypeName") or ""
        return _coerce_choices_to_type(cached, type_name)
    if not host or not uid:
        return _cached_top_values(column)
    if not field_name:
        return []
    if resolver is None:
        # No sync resolver injected and no async loop available here —
        # fall back to whatever the metadata's cached top can offer
        # rather than dereferencing an undefined symbol. The live
        # discovery path uses ``afetch_column_distinct_values`` via
        # ``_abuild_discovery`` and pre-populates ``choices_cache``,
        # so this branch only fires when a caller side-steps that
        # pipeline.
        return _cached_top_values(column)
    fetch = resolver
    type_name = column.get("dataTypeName") or ""
    # Numeric columns get a tight cap — enum-like columns (``month``,
    # ``year``) stay under it, continuous measures (prices, ratios) trip
    # the overflow and fall through to no-constraint.
    cap = _NUMERIC_CHOICE_CAP if type_name in _NUMERIC_TYPES else _MAX_RESOLVED_CHOICES
    resolved = fetch(host, uid, field_name, limit=cap)
    if resolved is not None:
        return _coerce_choices_to_type(resolved, type_name)
    # SoQL fetch failed (network / overflow) — surface the cached top as a
    # best-effort fallback so the help text still has something useful,
    # but only when the cached list isn't itself capped (capped == we
    # know there's more, so claiming the top-20 is the full set would
    # mislead).
    cached = column.get("cachedContents") or {}
    if 0 < len(cached.get("top") or []) < _CACHED_TOP_CAP:
        return _cached_top_values(column)
    return []


def _column_help(column: dict[str, Any]) -> str:
    """Compose the per-column help text shown under ``--<col>=<value>``.

    Combines the column's own description with a "most common values"
    line drawn from ``cachedContents.top`` so REPL users see candidate
    filter values without having to round-trip the API. Skips the values
    line when the column is already constrained to a closed ``choices``
    set (the choices listing already appears in the help output).
    """
    parts: list[str] = []
    description = column.get("description")
    if description:
        parts.append(description.strip().rstrip(".") + ".")
    cached = column.get("cachedContents") or {}
    top = cached.get("top") or []
    if top and len(top) >= _CACHED_TOP_CAP:
        sample = []
        for entry in top[:5]:
            item = entry.get("item") if isinstance(entry, dict) else entry
            if item is not None:
                sample.append(str(item))
        if sample:
            parts.append(f"Examples: {', '.join(sample)}.")
    smallest = cached.get("smallest")
    largest = cached.get("largest")
    # Only attach the range hint when ``cachedContents.top`` is at the cap
    # (signals high cardinality — there are values outside the cached
    # set). For below-cap columns the cached top IS the complete set, so
    # range would be redundant.
    if smallest is not None and largest is not None and len(top) >= _CACHED_TOP_CAP:
        parts.append(f"Range: {smallest} – {largest}.")
    return " ".join(parts)


def _column_param_type(column: dict[str, Any]) -> str:
    """Map a Socrata ``dataTypeName`` to a spec ``type`` value.

    The spec only knows about the same primitives the OpenAPI translator
    produces — ``string`` / ``integer`` / ``number`` / ``boolean``. Date /
    datetime columns flow through as ``string`` because Socrata accepts
    ISO timestamps as filter values via the standard ``?col=<iso>`` form.
    Object-shaped columns (``location`` / ``url`` / ``photo``) aren't
    sensibly filterable as scalars, so they collapse to ``string`` —
    user can still query the JSON-encoded form if they really want.
    """
    type_name = column.get("dataTypeName") or "text"
    if type_name in ("number", "money", "double", "percent"):
        return "number"
    if type_name == "checkbox":
        return "boolean"
    return "string"


_DATE_COLUMN_TYPES: frozenset[str] = frozenset({"calendar_date", "date"})

# Column names commonly used for the "time axis" of a dataset — datasets
# without a true ``calendar_date`` column often store the time dimension
# as text (``year`` = ``"2024"``, ``month`` = ``"03"``). The per-command
# ordering + most-recent-per-item collapse keys off the time axis, so
# detecting it by name lets us treat year-as-text the same as a real
# date column for those purposes (without trying to emit ``start_date``
# / ``end_date`` against a text column where range filtering would be
# semantically iffy).
_TIME_AXIS_NAME_PATTERNS: tuple[str, ...] = (
    "month_year",
    "year_month",
    "yearmonth",
    "monthyear",
    "as_of_date",
    "as_of",
    "asof",
    "observation_date",
    "report_date",
    "release_date",
    "effective_date",
    "date",
    "datetime",
    "timestamp",
    "time",
    "year",
    "quarter",
    "month",
    "week",
    "period",
)


def _is_date_column(column: dict[str, Any]) -> bool:
    """Return True when the column's data type calls for range-style filtering."""
    return (column.get("dataTypeName") or "") in _DATE_COLUMN_TYPES


def _is_time_axis_named(field_name: str) -> bool:
    """Return True when the column's name suggests it carries a time value."""
    name = (field_name or "").lower()
    return name in _TIME_AXIS_NAME_PATTERNS


def _detect_time_axis_column(meta: dict[str, Any]) -> str | None:
    """Pick the column to sort by descending for "most recent" semantics.

    Prefers true ``calendar_date`` / ``date`` columns; falls back to
    text columns whose names match a known time-axis pattern (``year``,
    ``month``, ``date``, ``timestamp``, etc.) so a dataset that stores
    its time dimension as ``"2024"`` strings still gets meaningful
    most-recent ordering. Returns the longer-form name when multiple
    matches exist (``month_year`` wins over ``year``) — the longer name
    is usually the more specific timestamp.
    """
    for col in meta.get("columns") or []:
        if not isinstance(col, dict):
            continue
        if _is_date_column(col):
            field_name = col.get("fieldName") or col.get("name")
            if field_name:
                return field_name
    candidates: list[str] = []
    for col in meta.get("columns") or []:
        if not isinstance(col, dict):
            continue
        field_name = col.get("fieldName") or col.get("name")
        if field_name and _is_time_axis_named(field_name):
            candidates.append(field_name)
    if not candidates:
        return None
    candidates.sort(key=len, reverse=True)
    return candidates[0]


def _to_plain_date(value: Any) -> Any:
    """Trim the time component off a Socrata datetime string.

    Socrata's ``cachedContents.smallest`` / ``largest`` come back as ISO
    timestamps (``2010-01-01T00:00:00.000``) even for date-only
    semantics. Users want plain ``2010-01-01`` for the ``start_date`` /
    ``end_date`` filter — Socrata still accepts it in SoQL ``$where``
    clauses against ``calendar_date`` columns. Anything that isn't an
    obvious ISO datetime passes through unchanged.
    """
    if not isinstance(value, str):
        return value
    if "T" in value and len(value) >= 10 and value[4] == "-" and value[7] == "-":
        return value.split("T", 1)[0]
    return value


def _date_range_parameters(column: dict[str, Any]) -> list[dict[str, Any]]:
    """Emit a uniform ``start_date`` / ``end_date`` pair for a date column.

    The names are deliberately not column-derived (``monthyear_start``
    etc.) — every Socrata dataset that has a date axis gets the same
    ``start_date`` / ``end_date`` filter, so calling code can apply the
    same date narrowing across any dataset without first looking up the
    underlying column name.

    Defaults come from ``cachedContents.smallest`` / ``largest`` so the
    filter naturally spans the dataset's full extent on first use — the
    REPL's ``--help`` shows the actual data range, and the user can
    narrow either side without having to know what values exist.

    The two emitted params carry ``_socrata_op`` (``date_min`` /
    ``date_max``) and ``_socrata_column`` markers; ``fetcher_gen`` reads
    those at codegen time to produce a SoQL ``$where`` clause keyed on
    the actual column name (not the parameter name).
    """
    field_name = column.get("fieldName") or column.get("name")
    cached = column.get("cachedContents") or {}
    smallest = _to_plain_date(cached.get("smallest"))
    largest = _to_plain_date(cached.get("largest"))
    description = column.get("description") or ""
    base_help = description.strip().rstrip(".")
    range_text = (
        f" Dataset spans {smallest} to {largest}." if smallest and largest else ""
    )
    # Defaults stay ``None`` so omitting the param gets ALL the data the
    # other filters allow — clamping to the cached bounds would silently
    # exclude rows added after the metadata snapshot. Cached bounds still
    # surface in ``example`` and the help text so callers know the
    # available range up front.
    return [
        {
            "name": "start_date",
            "in": "query",
            "type": "string",
            "is_list": False,
            "required": False,
            "default": None,
            "choices": [],
            "example": smallest,
            "help": (
                f"Earliest date (YYYY-MM-DD) to include — filters on ``{field_name}``."
                f" Omit to fetch from the dataset's earliest record."
                f"{(' ' + base_help + '.') if base_help else ''}"
                f"{range_text}"
            ).strip(),
            "providers": [],
            "_socrata_op": "date_min",
            "_socrata_column": field_name,
        },
        {
            "name": "end_date",
            "in": "query",
            "type": "string",
            "is_list": False,
            "required": False,
            "default": None,
            "choices": [],
            "example": largest,
            "help": (
                f"Latest date (YYYY-MM-DD) to include — filters on ``{field_name}``."
                f" Omit to fetch through the dataset's latest record."
                f"{(' ' + base_help + '.') if base_help else ''}"
                f"{range_text}"
            ).strip(),
            "providers": [],
            "_socrata_op": "date_max",
            "_socrata_column": field_name,
        },
    ]


def _build_query_parameters(
    meta: dict[str, Any],
    *,
    host: str | None = None,
    uid: str | None = None,
    resolver: Any = None,
    choices_cache: dict[tuple[str, str], list[Any] | None] | None = None,
) -> list[dict[str, Any]]:
    """Build the per-dataset query parameter list.

    Output structure:

    * One filter parameter per column (``?<column>=<value>`` is the
      Socrata-native equality filter — much more discoverable than
      writing raw ``$where`` clauses). Columns with a small enumeration
      of values get those values as ``choices`` so the generated CLI
      validates the input up-front; high-cardinality columns surface
      sample values in their help text instead.
    * ``$limit`` / ``$offset`` for pagination — the only two SoQL
      directives kept, since they're the universal "page through it"
      controls every consumer needs. Field aliases preserve the
      ``$``-prefixed wire names so the generated Pydantic class lets
      callers pass them as plain ``limit`` / ``offset``.

    The advanced SoQL controls (``$select`` / ``$where`` / ``$group`` /
    ``$having`` / ``$order`` / ``$q``) are intentionally absent — power
    users can build the URL directly with ``urllib`` or ``httpx``.
    """
    parameters: list[dict[str, Any]] = []
    date_range_emitted = False
    for column in meta.get("columns") or []:
        if not isinstance(column, dict):
            continue
        field_name = column.get("fieldName") or column.get("name")
        if not field_name:
            continue
        # Date columns get a unified ``start_date`` / ``end_date`` pair —
        # but only ONCE per dataset, keyed on the first date column we
        # encounter. Exact-date equality is useless against a multi-year
        # time series, and a per-column ``<col>_start`` would force the
        # caller to know which date column to filter on.
        if _is_date_column(column):
            if not date_range_emitted:
                parameters.extend(_date_range_parameters(column))
                date_range_emitted = True
            continue
        parameters.append(
            {
                "name": field_name,
                "in": "query",
                "type": _column_param_type(column),
                "is_list": False,
                "required": False,
                "default": None,
                "choices": _column_choices(
                    column,
                    host=host,
                    uid=uid,
                    resolver=resolver,
                    choices_cache=choices_cache,
                ),
                "example": None,
                "help": _column_help(column),
                "providers": [],
            }
        )
    parameters.extend(
        [
            {
                "name": "limit",
                "in": "query",
                "type": "integer",
                "is_list": False,
                "required": False,
                "default": 1000,
                "choices": [],
                "example": None,
                "help": (
                    "Max rows returned. Socrata's API default is 1000; up to "
                    "50000 per request without pagination."
                ),
                "providers": [],
                # ``wire_name`` carries the actual URL parameter name —
                # Socrata's SoQL prefix (``$``) stays inside the dispatcher.
                "wire_name": "$limit",
            },
            {
                "name": "offset",
                "in": "query",
                "type": "integer",
                "is_list": False,
                "required": False,
                "default": None,
                "choices": [],
                "example": None,
                "help": "Row offset for pagination — pair with limit.",
                "providers": [],
                "wire_name": "$offset",
            },
        ]
    )
    return parameters


# Socrata column ``dataTypeName`` → JSON schema fragment. Anything not in
# this map falls back to ``string`` — which is a safe lossy default since
# the upstream serializes most exotic types (geometry, blob refs) as
# JSON objects or strings.
_SOCRATA_TYPE_MAP: dict[str, dict[str, Any]] = {
    "text": {"type": "string"},
    "html": {"type": "string"},
    "number": {"type": "number"},
    "money": {"type": "number"},
    "percent": {"type": "number"},
    "double": {"type": "number"},
    "checkbox": {"type": "boolean"},
    # Both Socrata date types resolve to plain ``date`` (not ``datetime``).
    # The wire format is always ``YYYY-MM-DDTHH:MM:SS.fff`` even for
    # date-only semantics; Pydantic v2's ``date`` validator accepts the
    # timestamp form and discards the time component, so the user-facing
    # row carries a clean ``date`` value with no zero-time noise.
    "calendar_date": {"type": "string", "format": "date"},
    "date": {"type": "string", "format": "date"},
    "url": {
        "type": "object",
        "properties": {
            "url": {"type": "string"},
            "description": {"type": "string"},
        },
    },
    "email": {"type": "string"},
    "phone": {"type": "object"},
    "point": {"type": "object"},
    "location": {"type": "object"},
    "multipoint": {"type": "object"},
    "line": {"type": "object"},
    "multiline": {"type": "object"},
    "polygon": {"type": "object"},
    "multipolygon": {"type": "object"},
    "photo": {"type": "object"},
    "document": {"type": "object"},
}


def _slugify(name: str) -> str:
    """Translate a free-form dataset name to a snake_case identifier.

    Socrata names are human prose — ``"Waterborne Agricultural Trade
    Data"``. The router namespace must be a valid Python attribute (and
    survive both REPL completion and URL templating), so non-alphanumeric
    chunks collapse to ``_``. Leading digits get an underscore prefix to
    keep the result a legal identifier.
    """
    cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_").lower()
    if not cleaned:
        cleaned = "dataset"
    if cleaned[0].isdigit():
        cleaned = f"_{cleaned}"
    return cleaned


# Stop words that often appear at the end of a shared prefix (``Port
# Profiles BY Commodity``). Stripping them keeps the router name from
# ending with a connector preposition.
_PREFIX_STOP_TOKENS: frozenset[str] = frozenset(
    {"by", "for", "of", "in", "at", "to", "with", "and", "the"}
)


def _common_token_prefix(token_lists: list[list[str]]) -> list[str]:
    """Return the longest leading token sequence shared by every input."""
    if not token_lists:
        return []
    shortest = min(len(tl) for tl in token_lists)
    common: list[str] = []
    for i in range(shortest):
        token = token_lists[0][i]
        if all(tl[i] == token for tl in token_lists):
            common.append(token)
        else:
            break
    return common


def _longest_common_token_run(token_lists: list[list[str]]) -> list[str]:
    """Return the longest contiguous token run shared by every input list.

    Unlike ``_common_token_prefix`` this looks at every contiguous
    substring, not just the leading one — so
    ``["idle", "container", "vessel", "fleet"]`` and
    ``["container", "vessel", "fleet", "data"]`` cluster on the
    ``[container, vessel, fleet]`` middle/edge run, not on the empty
    leading prefix.

    Brute force over the first list's substrings (longest first). The
    spec generator runs on small inputs (≤20 datasets per story, each
    with ≤8 name tokens), so the worst case is trivial.
    """
    if not token_lists:
        return []
    first = token_lists[0]
    n = len(first)
    others = token_lists[1:]
    for length in range(n, 0, -1):
        for start in range(n - length + 1):
            candidate = first[start : start + length]
            if all(
                any(
                    tl[i : i + length] == candidate for i in range(len(tl) - length + 1)
                )
                for tl in others
            ):
                return candidate
    return []


def _strip_stop_tokens(tokens: list[str]) -> list[str]:
    """Trim leading and trailing connector words from a token list."""
    out = list(tokens)
    while out and out[-1] in _PREFIX_STOP_TOKENS:
        out.pop()
    while out and out[0] in _PREFIX_STOP_TOKENS:
        out.pop(0)
    return out


# Minimum shared-token-run length to merge two datasets into the same
# router bucket. A single common token like ``"data"`` or ``"the"``
# would over-cluster unrelated datasets; two consecutive content words
# is a strong signal that the names belong together.
_MIN_SHARED_RUN = 2


def _assign_router_namespaces(
    slugs: dict[str, str],
) -> dict[str, tuple[str | None, str]]:
    """Group dataset slugs into ``(router, command)`` pairs.

    Strategy: cluster pairs of datasets whose names share a contiguous
    token run of length ≥ ``_MIN_SHARED_RUN`` (after stripping
    connector words like ``by`` / ``for``). Connected components form
    router buckets; the bucket's longest common token run becomes the
    router name, and each member's command is the rest of its name.

    Singleton buckets emit ``(None, slug)`` so the dataset becomes a
    top-level command — forcing a router around a single dataset
    would leave the user typing ``idle_container_vessel_fleet`` to
    enter a menu that only contains ``query``.

    For three datasets like ``idle_container_vessel_fleet`` /
    ``container_vessel_fleet_data`` /
    ``global_container_vessel_fleet_and_spot_rates``, the shared run
    ``[container, vessel, fleet]`` makes them cluster into a
    ``container_vessel_fleet`` router with commands ``idle`` / ``data``
    / ``global_and_spot_rates``.

    Parameters
    ----------
    slugs : dict
        Mapping of dataset UID → slugified dataset name.

    Returns
    -------
    dict
        Mapping of dataset UID → ``(router_or_None, command)`` tuple.
    """
    if not slugs:
        return {}
    token_lists: dict[str, list[str]] = {
        uid: slug.split("_") for uid, slug in slugs.items()
    }
    uids = list(slugs.keys())

    # Union-find clustering — pairs whose meaningful shared run is at
    # least ``_MIN_SHARED_RUN`` tokens go in the same bucket.
    parent: dict[str, str] = {uid: uid for uid in uids}

    def find(u: str) -> str:
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u

    def union(u: str, v: str) -> None:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv

    # Cluster-threshold uses the *unstripped* run length: ``[sales, by]``
    # (2 tokens) qualifies for clustering even though stripping the
    # trailing ``by`` later leaves just ``sales`` as the router name.
    for i in range(len(uids)):
        for j in range(i + 1, len(uids)):
            run = _longest_common_token_run(
                [token_lists[uids[i]], token_lists[uids[j]]]
            )
            if len(run) >= _MIN_SHARED_RUN:
                union(uids[i], uids[j])

    groups: dict[str, list[str]] = {}
    for uid in uids:
        groups.setdefault(find(uid), []).append(uid)

    out: dict[str, tuple[str | None, str]] = {}
    for group_uids in groups.values():
        if len(group_uids) == 1:
            uid = group_uids[0]
            out[uid] = (None, slugs[uid])
            continue
        group_tokens = [token_lists[u] for u in group_uids]
        router_tokens = _strip_stop_tokens(_longest_common_token_run(group_tokens))
        if not router_tokens:
            for uid in group_uids:
                out[uid] = (None, slugs[uid])
            continue
        router = "_".join(router_tokens)
        run_len = len(router_tokens)
        member_commands = {
            uid: _command_tokens_around_run(token_lists[uid], router_tokens, run_len)
            for uid in group_uids
        }
        # When every member's slug *equals* the router (no remaining
        # tokens for any of them), the group is a pile of identically-
        # named datasets. Promote them all to top-level commands —
        # the path-collision disambiguator below appends the UID so
        # they stay distinct, which is friendlier than a router named
        # ``X`` containing N copies of ``X.query``.
        if all(not c for c in member_commands.values()):
            for uid in group_uids:
                out[uid] = (None, slugs[uid])
            continue
        for uid in group_uids:
            tokens = member_commands[uid]
            command = "_".join(tokens) if tokens else "query"
            out[uid] = (router, command)
    return out


def _command_tokens_around_run(
    tokens: list[str], router_tokens: list[str], run_len: int
) -> list[str]:
    """Return ``tokens`` minus the first occurrence of ``router_tokens``."""
    for i in range(len(tokens) - run_len + 1):
        if tokens[i : i + run_len] == router_tokens:
            return tokens[:i] + tokens[i + run_len :]
    return list(tokens)


def _walk_for_dataset_uids(node: Any, sink: set[str]) -> None:
    """Recursively collect every ``datasetUid`` value in a JSON tree.

    Socrata stories nest ``datasetUid`` inside visualization components,
    layout blocks, and filter clauses — multiple levels deep. A flat
    regex over the source text picks up false positives (any 4x4-shaped
    string), so we walk the parsed structure instead and trust only
    values keyed by the literal ``datasetUid`` field.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "datasetUid" and isinstance(value, str):
                sink.add(value)
            else:
                _walk_for_dataset_uids(value, sink)
    elif isinstance(node, list):
        for item in node:
            _walk_for_dataset_uids(item, sink)


def extract_dataset_uids(story: dict[str, Any]) -> list[str]:
    """Return the unique dataset UIDs referenced by a story, in stable order."""
    sink: set[str] = set()
    _walk_for_dataset_uids(story, sink)
    return sorted(sink)


_STORY_URL_RE = re.compile(
    r"^(?P<base>https?://[^/]+/stories/s/[a-z0-9]{4}-[a-z0-9]{4})(?P<rest>.*)$"
)

# Direct ``/resource/{uid}.json`` or ``/api/views/{uid}.json`` URL —
# the user pointed at one specific dataset / view rather than at a
# story document. We extract the UID and treat it as a single-entry
# discovery seed so the same code path handles "give me everything
# this story references" and "give me just this one dataset."
_SINGLE_VIEW_URL_RE = re.compile(
    r"^(?P<host>https?://[^/]+)"
    r"/(?:resource|api/views)/(?P<uid>[a-z0-9]{4}-[a-z0-9]{4})"
    r"(?:\.json)?(?:\?.*)?$"
)


def _direct_dataset_seed(source: str) -> tuple[str, str] | None:
    """Detect ``/resource/`` or ``/api/views/`` URLs → ``(host, uid)``.

    These URLs aren't stories — they point at a single dataset (or
    view). Returning the seed lets the caller skip the story-fetch
    step and run the same downstream discovery loop with one UID
    instead of N.
    """
    match = _SINGLE_VIEW_URL_RE.match(source)
    if match:
        return match.group("host"), match.group("uid")
    return None


def _normalize_story_url(source: str) -> str:
    """Append ``.json`` when the user pastes the browser-facing story URL.

    Socrata stories are reachable two ways: the human form
    ``/stories/s/<id>`` (HTML) and the JSON sibling ``/stories/s/<id>.json``.
    Users almost always paste the former. We rewrite to the JSON form
    transparently so they don't have to remember the suffix; non-story
    URLs and local file paths pass through untouched.
    """
    match = _STORY_URL_RE.match(source)
    if not match:
        return source
    rest = match.group("rest")
    if rest.startswith(".json") or rest.startswith("?") and ".json" in rest:
        return source
    if not rest:
        return f"{match.group('base')}.json"
    if rest.startswith("?"):
        return f"{match.group('base')}.json{rest}"
    # Some other suffix on the path (``/stories/s/<id>/embed`` etc.) — pass through.
    return source


async def _aread_json_url_or_path(source: str, *, timeout: float = 15.0) -> Any:
    """Load JSON from an HTTP URL (async via httpx) or local file path (sync)."""
    if source.startswith(("http://", "https://")):
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout)) as client:
            response = await client.get(source)
            response.raise_for_status()
            return response.json()
    return json.loads(Path(source).read_text())


def _story_host(story_source: str, story: dict[str, Any]) -> str:
    """Pick the portal base URL the story's datasets live on.

    Story documents include a ``domainCName`` in the ``dataSource`` block
    on most portals; when present that's the canonical host. Fall back to
    the URL the story was fetched from (so a file-on-disk story can still
    drive generation if the JSON itself doesn't carry a host hint).
    """
    domain = (story.get("dataSource") or {}).get("domainCName")
    if isinstance(domain, str) and domain:
        return f"https://{domain}".rstrip("/")
    if story_source.startswith(("http://", "https://")):
        parsed = urllib.parse.urlparse(story_source)
        return f"{parsed.scheme}://{parsed.netloc}"
    raise ValueError(
        "story has no ``dataSource.domainCName`` and the source is a local "
        "file — pass an HTTP URL or add the host to the story document."
    )


async def _afetch_json(client: httpx.AsyncClient, url: str) -> Any:
    """Async GET + JSON-decode, raising on HTTP errors."""
    response = await client.get(url)
    response.raise_for_status()
    return response.json()


async def _amaybe_call(callable_: Any, *args: Any, **kwargs: Any) -> Any:
    """Invoke ``callable_`` and ``await`` the result if it's a coroutine.

    Lets test stubs stay regular sync functions — production runs go
    through ``async def`` paths but the few stub-injected entry points
    (``fetch=`` / ``choice_resolver=``) accept either form.
    """
    result = callable_(*args, **kwargs)
    if inspect.isawaitable(result):
        return await result
    return result


async def _aone_metadata(
    client: httpx.AsyncClient,
    host: str,
    uid: str,
    fetcher: Any,
) -> dict[str, Any] | None:
    """Fetch one view's metadata, returning ``None`` on any failure.

    ``fetcher`` may be ``None`` (use the default async path),
    ``afetch_dataset_metadata`` (same), or a test stub (sync or
    async). The stub gets the ``client`` injected as its first
    positional argument so test stubs can mirror the production
    signature if they want to.
    """
    if fetcher is None or fetcher is afetch_dataset_metadata:
        try:
            return await afetch_dataset_metadata(client, host, uid)
        except (httpx.HTTPError, ValueError, OSError):
            return None
    try:
        # Test-stub signature: ``(host, uid)`` (sync or async). Tests
        # that don't need the client argument keep the simpler form.
        return await _amaybe_call(fetcher, host, uid)
    except (httpx.HTTPError, OSError, ValueError):
        return None


async def _afetch_metadata_batch(
    client: httpx.AsyncClient,
    host: str,
    uids: list[str],
    fetcher: Any,
) -> dict[str, dict[str, Any] | None]:
    """Concurrently fetch metadata for many UIDs.

    Returns ``{uid: meta_dict_or_None}`` — ``None`` marks UIDs that
    couldn't be reached (404 / DNS failure / malformed response).
    Concurrency is bounded by ``_DISCOVERY_MAX_WORKERS`` so a story
    with hundreds of UIDs doesn't tip the portal's per-IP rate limit.
    """
    if not uids:
        return {}
    sem = asyncio.Semaphore(_DISCOVERY_MAX_WORKERS)

    async def _one(uid: str) -> dict[str, Any] | None:
        async with sem:
            return await _aone_metadata(client, host, uid, fetcher)

    results = await asyncio.gather(*(_one(uid) for uid in uids))
    return dict(zip(uids, results))


async def _aone_choice(
    client: httpx.AsyncClient,
    host: str,
    uid: str,
    field: str,
    cap: int,
    resolver: Any,
) -> list[Any] | None:
    """Fetch one column's distinct values, ``None`` on overflow / error."""
    if resolver is None or resolver is afetch_column_distinct_values:
        return await afetch_column_distinct_values(client, host, uid, field, limit=cap)
    try:
        # Test-stub signature: ``(host, uid, field, *, limit=...)``
        # (sync or async). Mirrors the public async function but
        # without the ``client`` argument since stubs typically don't
        # need it.
        return await _amaybe_call(resolver, host, uid, field, limit=cap)
    except (httpx.HTTPError, OSError, ValueError):
        return None


async def _abuild_discovery(
    story_source: str,
    host_override: str | None,
    fetcher: Any,
    choice_resolver: Any,
    direct_seed: tuple[str, str] | None = None,
) -> tuple[
    dict[str, Any],
    str,
    dict[str, dict[str, Any]],
    dict[str, str],
    list[tuple[str, str]],
    dict[tuple[str, str], list[Any] | None],
]:
    """Run the full async discovery pipeline end-to-end.

    Three phases, all sharing a single ``httpx.AsyncClient`` so
    keep-alive connections are reused across every fetch:

    1. **Seeding** — either fetch the story JSON and walk it for
       ``datasetUid`` references, or skip straight to a one-UID seed
       when ``direct_seed`` is supplied (caller pointed at a single
       ``/resource/`` or ``/api/views/`` URL).
    2. **BFS metadata** — issue every wave's UIDs concurrently
       (semaphore-limited to ``_DISCOVERY_MAX_WORKERS``); collect
       backing UIDs from chart / map / filter views; loop until no
       new UIDs appear.
    3. **Column-choice probe** — fan out one
       ``$select=<col>&$group=<col>`` query per column across every
       kept dataset so command-build time later runs HTTP-free.

    Returns ``(story, host, metas, slugs, skipped, choices_cache)``.
    """
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        limits=httpx.Limits(
            max_connections=_DISCOVERY_MAX_WORKERS * 2,
            max_keepalive_connections=_DISCOVERY_MAX_WORKERS,
        ),
    ) as client:
        if direct_seed is not None:
            # Single-view URL — synthesize a one-UID "story" stub so
            # downstream stays uniform. The host comes straight from
            # the URL since there's no story document to consult.
            seed_host, seed_uid = direct_seed
            story = {"_synthetic_single_view": True, "uid": seed_uid}
            host = host_override or seed_host
            uids = [seed_uid]
        else:
            story = await _aload_story(client, story_source)
            host = host_override or _story_host(story_source, story)
            uids = extract_dataset_uids(story)

        metas: dict[str, dict[str, Any]] = {}
        slugs: dict[str, str] = {}
        skipped: list[tuple[str, str]] = []
        pending: list[str] = list(dict.fromkeys(uids))
        processed: set[str] = set()

        while pending:
            wave = [uid for uid in pending if uid not in processed]
            pending = []
            if not wave:  # pragma: no cover — defensive safety net
                # Unreachable by construction: ``processed.update(wave)``
                # runs before backing UIDs get appended, and the
                # ``if backing not in processed`` filter on append means
                # ``pending`` never accumulates already-processed UIDs.
                # Kept as a guard against future refactors that might
                # change those invariants.
                break
            processed.update(wave)
            wave_metas = await _afetch_metadata_batch(client, host, wave, fetcher)
            for uid, meta in wave_metas.items():
                if meta is None:
                    skipped.append((uid, "unreachable"))
                    continue
                asset_type = meta.get("assetType")
                if asset_type in {"dataset", "filter"}:
                    metas[uid] = meta
                    slugs[uid] = _slugify(meta.get("name") or uid)
                else:
                    skipped.append((uid, asset_type or "unknown"))
                backing = _backing_dataset_uid(meta)
                if backing and backing not in processed:
                    pending.append(backing)
        choices_cache = await _aprobe_choices_batch(
            client, host, metas, choice_resolver
        )
    return story, host, metas, slugs, skipped, choices_cache


async def _aload_story(client: httpx.AsyncClient, story_source: str) -> dict[str, Any]:
    """Async version of ``_aread_json_url_or_path`` that reuses the client."""
    if story_source.startswith(("http://", "https://")):
        response = await client.get(story_source)
        response.raise_for_status()
        return response.json()
    return json.loads(Path(story_source).read_text())


async def _aprobe_choices_batch(
    client: httpx.AsyncClient,
    host: str,
    metas: dict[str, dict[str, Any]],
    resolver: Any,
) -> dict[tuple[str, str], list[Any] | None]:
    """Concurrently probe distinct-value choices for every column on every dataset.

    Date columns (which become ``start_date`` / ``end_date`` range
    params) and object-typed columns (URL / location / photo —
    not sensibly enumerable as scalars) are skipped from the probe
    list entirely.
    """
    tasks: list[tuple[str, str, int]] = []
    for uid, meta in metas.items():
        for col in meta.get("columns") or []:
            if not isinstance(col, dict):
                continue
            field = col.get("fieldName") or col.get("name")
            if not field:
                continue
            if _is_date_column(col):
                continue
            type_name = col.get("dataTypeName") or "text"
            if type_name not in _NUMERIC_TYPES and type_name not in {
                "text",
                "html",
                "checkbox",
            }:
                continue
            cap = (
                _NUMERIC_CHOICE_CAP
                if type_name in _NUMERIC_TYPES
                else _MAX_RESOLVED_CHOICES
            )
            tasks.append((uid, field, cap))

    if not tasks:
        return {}

    sem = asyncio.Semaphore(_DISCOVERY_MAX_WORKERS)

    async def _one(
        uid: str, field: str, cap: int
    ) -> tuple[tuple[str, str], list[Any] | None]:
        async with sem:
            value = await _aone_choice(client, host, uid, field, cap, resolver)
        return (uid, field), value

    results = await asyncio.gather(
        *(_one(uid, field, cap) for uid, field, cap in tasks)
    )
    return dict(results)


async def afetch_dataset_metadata(
    client: httpx.AsyncClient, host: str, uid: str
) -> dict[str, Any]:
    """Fetch a Socrata view's metadata JSON (async).

    The same endpoint serves dataset, chart, map, and filter views — the
    caller filters on ``assetType`` to keep only true datasets, since the
    derived views all resolve to the same ``/resource/`` data path.

    Pure async: the spec generator opens one ``httpx.AsyncClient`` for
    the whole discovery pass and fans out via ``asyncio.gather`` so
    keep-alive connections are reused across the dozens of per-story
    fetches.
    """
    url = f"{host.rstrip('/')}/api/views/{uid}.json"
    response = await client.get(url)
    response.raise_for_status()
    return response.json()


def _backing_dataset_uid(meta: dict[str, Any]) -> str | None:
    """Return the UID of a non-dataset view's backing dataset, or ``None``.

    Socrata stores the backing reference in ``modifyingViewUid`` for
    chart / map / filter views; the older ``query.viewSourceId`` slot
    serves the same purpose on legacy assets. Both are checked so the
    resolver works across portal vintages.
    """
    backing = meta.get("modifyingViewUid")
    if isinstance(backing, str) and backing:
        return backing
    query = meta.get("query")
    if isinstance(query, dict):
        source = query.get("viewSourceId")
        if isinstance(source, str) and source:
            return source
    return None


def _column_to_schema(column: dict[str, Any]) -> dict[str, Any]:
    """Translate one Socrata column descriptor into a JSON-schema fragment.

    Preserves ``description`` when the column carries one — that text
    flows through to the generated Pydantic ``Field(description=...)`` and
    surfaces in the REPL's ``--help`` output. Socrata format hints
    (currency / percent precision style, decimal & group separators)
    land under a ``socrata_format`` extension key so downstream
    formatters can render values correctly without re-fetching the
    column metadata.
    """
    type_name = column.get("dataTypeName") or "text"
    schema = dict(_SOCRATA_TYPE_MAP.get(type_name, {"type": "string"}))
    description = column.get("description")
    if description:
        # Socrata descriptions frequently arrive with trailing whitespace
        # ("Quarter number. ", "Price, measured in dollars per ton. ").
        # Strip both edges so downstream renderers don't have to deal
        # with the noise.
        cleaned = description.strip()
        if cleaned:
            schema["description"] = cleaned
    fmt = column.get("format")
    if isinstance(fmt, dict) and fmt:
        # Keep only the rendering-hint keys we actually use; the raw
        # ``format`` dict on Socrata sometimes carries internal flags
        # (e.g. ``align``) that aren't useful downstream.
        rendering_hints = {
            k: v
            for k, v in fmt.items()
            if k
            in {
                "precisionStyle",
                "currency",
                "decimalSeparator",
                "groupSeparator",
                "noCommas",
                "precision",
                "view",
                "mask",
            }
        }
        if rendering_hints:
            schema["socrata_format"] = rendering_hints
    return schema


def _build_response_schema(meta: dict[str, Any]) -> dict[str, Any]:
    """Build a row-shape schema from a dataset's column metadata.

    Output is a single-key envelope ``{results: array<row>}`` so the
    existing ``_unwrap_schema_envelopes`` (which descends single-array
    properties) lands on the row schema and the generated ``Data`` class
    describes one row, not the whole list.
    """
    columns = meta.get("columns") or []
    properties: dict[str, dict[str, Any]] = {}
    for column in columns:
        if not isinstance(column, dict):
            continue
        field_name = column.get("fieldName") or column.get("name")
        if not field_name:
            continue
        properties[field_name] = _column_to_schema(column)
    return {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "items": {"type": "object", "properties": properties},
            }
        },
    }


def _build_command(
    host: str,
    uid: str,
    meta: dict[str, Any],
    *,
    choice_resolver: Any = None,
    choices_cache: dict[tuple[str, str], list[Any] | None] | None = None,
) -> dict[str, Any]:
    """Synthesize one spec command entry for a dataset.

    The command keys off the dataset's UID (immutable) for the URL path
    while the namespace comes from its slugified name (human-readable).
    Renames upstream don't break installed extensions because the URL
    still resolves; namespaces do drift, which is the intended trade-off
    — readable REPL paths beat permanent-but-cryptic 4x4 namespaces.

    ``choices_cache`` (when supplied) short-circuits the per-column
    distinct-value probe — keys are ``(uid, field_name)`` and values
    are the resolved choice list (or ``None`` for overflow / failure).
    The spec generator pre-populates this cache via a single parallel
    batch so per-command construction never has to issue HTTP calls.
    """
    name = (meta.get("name") or uid).strip()
    description = (meta.get("description") or "").strip()
    # ``description`` lands first because the REPL menu renderer takes
    # only the first sentence (``description.split(".")[0]``) — leading
    # with the dataset name there would just duplicate the command name
    # and waste the menu's one-line summary slot. Fall back to the name
    # when the dataset has no description text.
    summary = description or name
    parameters = _build_query_parameters(
        meta,
        host=host,
        uid=uid,
        resolver=choice_resolver,
        choices_cache=choices_cache,
    )
    time_axis = _detect_time_axis_column(meta)
    return {
        "url_path": f"/resource/{uid}.json",
        "method": "get",
        "description": summary,
        "parameters": parameters,
        "providers": [],
        "request_body_schema": None,
        "request_body_schemas": {},
        "response_schema": _build_response_schema(meta),
        "response_schemas": {},
        # ``_socrata_time_axis`` is the column the dispatcher sorts by
        # descending so ``limit=N`` returns the most recent records
        # — even when the dataset stores time as text (``year`` =
        # ``"2024"``) instead of a true ``calendar_date``.
        "_socrata_time_axis": time_axis,
        # ``_socrata_primary_item`` is the text column with the highest
        # distinct-value count, excluding time-axis columns — what
        # ``limit`` keys off in spec-mode dispatch ("most recent record
        # per item, capped at N items"). Falls back to ``None`` when no
        # column qualifies (continuous-only datasets).
        "_socrata_primary_item": _primary_item_column(parameters, time_axis),
    }


def _primary_item_column(
    parameters: list[dict[str, Any]], time_axis: str | None
) -> str | None:
    """Pick the column to use as the per-item key for ``limit`` semantics.

    The "primary item" is the categorical column with the highest
    distinct-value count — for ``port_profiles_by_commodity`` that's
    ``port`` (215 values), not ``exim`` (2). We exclude:

    * The time-axis column (so ``year`` doesn't get picked as the
      "item" on a yearly dataset).
    * Other time-axis-named columns (``month``, ``quarter``) since
      they're typically secondary time axes, not entities.
    * Pagination params and date-range markers.
    * Columns with fewer than three choices (boolean-like flags
      aren't useful entities to enumerate).
    """
    excluded: set[str] = {"limit", "offset"}
    if time_axis:
        excluded.add(time_axis)
    candidates: list[tuple[int, str]] = []
    for p in parameters:
        if not isinstance(p, dict):
            continue
        if p.get("_socrata_op") in {"date_min", "date_max"}:
            continue
        name = p.get("name")
        if not name or name in excluded:
            continue
        if _is_time_axis_named(name):
            continue
        if p.get("type") != "string":
            continue
        choices = p.get("choices") or []
        if len(choices) < 3:
            continue
        candidates.append((len(choices), name))
    if not candidates:
        return None
    # Highest cardinality wins; ties broken by spec declaration order.
    candidates.sort(key=lambda pair: -pair[0])
    return candidates[0][1]


def build_socrata_spec(
    story_source: str,
    *,
    host_override: str | None = None,
    fetch: Any = None,
    choice_resolver: Any = None,
) -> dict[str, Any]:
    """Build a complete spec document from a Socrata story URL or local path.

    Parameters
    ----------
    story_source : str
        Either a story URL (``https://<portal>/stories/s/<id>.json``) or a
        path to a previously-downloaded story JSON file.
    host_override : str, optional
        Portal base URL to use instead of the one inferred from the story.
        Useful for testing against a captured story without making live
        ``/api/views/`` calls.
    fetch : callable, optional
        Override the metadata fetcher — signature ``(host, uid) -> dict``.
        Tests inject a stub here to avoid network IO; production passes
        ``None`` and the module's own ``fetch_dataset_metadata`` is used.
    choice_resolver : callable, optional
        Override the per-column distinct-value resolver — signature
        ``(host, uid, field_name) -> list | None``. Returning ``None``
        signals overflow / failure (no closed choices). Tests inject a
        stub; production passes ``None`` so every column is resolved
        live via ``fetch_column_distinct_values``.

    Returns
    -------
    dict
        A spec document conforming to ``SpecDocument`` with one
        namespace per dataset and one ``query`` command per namespace.
    """
    story_source = _normalize_story_url(story_source)
    # Single ``asyncio.run`` covers the entire network workload —
    # story fetch, BFS-wave metadata fetches, and per-column
    # distinct-value probes — all sharing one ``httpx.AsyncClient``
    # for keep-alive connection reuse. ``build_socrata_spec`` itself
    # stays a sync function so existing CLI / test entry points
    # don't need to change.
    direct_seed = _direct_dataset_seed(story_source)
    story, host, metas, slugs, skipped, choices_cache = asyncio.run(
        _abuild_discovery(
            story_source,
            host_override,
            fetch,
            choice_resolver,
            direct_seed=direct_seed,
        )
    )

    # Second pass: cluster slugs by leading token so related datasets
    # (``port_profiles_by_*``) collapse into a single router with one
    # command per variant — instead of N flat routers.
    assignments = _assign_router_namespaces(slugs)

    commands: dict[str, dict[str, Any]] = {}
    seen_paths: set[str] = set()
    for uid, (router, command) in assignments.items():
        # Singletons (``router is None``) live at the spec root — the
        # command name IS the path. Grouped datasets get the
        # ``router.command`` form.
        path = command if router is None else f"{router}.{command}"
        # Two datasets that slugify identically would produce identical
        # paths — disambiguate with the UID.
        if path in seen_paths:
            path = f"{path}_{uid.replace('-', '')}"
        seen_paths.add(path)
        commands[path] = _build_command(
            host,
            uid,
            metas[uid],
            choice_resolver=choice_resolver,
            choices_cache=choices_cache,
        )

    return {
        "version": SPEC_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": _generator_identifier(),
        "source_url": story_source,
        # Socrata's SODA v2.1 is the only public version of the data API
        # — record it so a downstream consumer can branch on the upstream
        # variant without sniffing the URL shape.
        "api_version": "socrata-soda-2.1",
        "base_url": host,
        "api_prefix": "",
        "commands": commands,
        "routers": _build_routers(commands),
        "reference": _build_reference(commands),
        "_socrata": {
            "story_uid": story.get("uid"),
            "dataset_count": len(commands),
            "skipped": [{"uid": u, "asset_type": t} for u, t in skipped],
        },
    }


def _build_routers(commands: dict[str, dict[str, Any]]) -> dict[str, str]:
    """Mark every namespace prefix as ``menu`` and every leaf as ``command``."""
    out: dict[str, str] = {}
    for cmd_path in commands:
        parts = cmd_path.split(".")
        for i in range(1, len(parts)):
            out[".".join(parts[:i])] = "menu"
        out[cmd_path] = "command"
    return out


def _build_reference(
    commands: dict[str, dict[str, Any]],
) -> dict[str, dict[str, dict[str, str]]]:
    """Build the slash-style reference index the REPL renders menu help from."""
    paths: dict[str, dict[str, str]] = {}
    routers: dict[str, dict[str, str]] = {}
    for cmd_path, cmd_spec in commands.items():
        parts = cmd_path.split(".")
        slash_path = "/" + "/".join(parts)
        paths[slash_path] = {"description": cmd_spec.get("description", "")}
        for i in range(1, len(parts)):
            slash_router = "/" + "/".join(parts[:i]) + "/"
            routers.setdefault(slash_router, {"description": ""})
    return {"paths": paths, "routers": routers}
