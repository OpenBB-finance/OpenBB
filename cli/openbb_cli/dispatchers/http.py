"""HTTP dispatcher — thin client that talks to a long-running openbb-platform-api server."""

from __future__ import annotations

import contextlib
import inspect
import re
from datetime import datetime, timezone
from time import perf_counter_ns
from typing import Any

import httpx

from openbb_cli.auth import AuthContext, AuthDecision, AuthHook
from openbb_cli.dispatchers._unpack import unpack_response
from openbb_cli.dispatchers.openapi_schema import (
    PROVIDER_SECTION_SPLIT_RE,
    PROVIDER_TAG_RE,
)
from openbb_cli.dispatchers.protocol import Request, Response, ResponseError

_PATH_TEMPLATE_RE = re.compile(r"\{([^}]+)\}")


def _help_for_provider(text: str | None, provider: str) -> str | None:
    r"""Pick the sections of an OpenBB-merged help string that apply to ``provider``.

    OpenBB Platform concatenates per-provider help into one description,
    sections separated by ``;\\n    `` and tagged with ``(provider:
    <comma-list>)``. Shared sections carry no tag. Surfacing the merged
    blob under each provider in ``--describe`` produces nonsense — cboe's
    ``symbol`` shouldn't show ``(provider: intrinio)``. Keep only the
    sections this provider participates in (shared + own), strip the
    annotation, rejoin.
    """
    if not text:
        return text
    sections = PROVIDER_SECTION_SPLIT_RE.split(text)
    target = provider.lower()
    kept: list[str] = []
    for raw_section in sections:
        section = raw_section.strip()
        if not section:
            continue
        match = PROVIDER_TAG_RE.search(section)
        if match is None:
            kept.append(section)
            continue
        tag_providers = {
            p.strip().lower() for p in match.group(1).split(",") if p.strip()
        }
        if target in tag_providers:
            kept.append(PROVIDER_TAG_RE.sub("", section).rstrip())
    return "\n".join(kept) if kept else None


def _slim_param(p: dict[str, Any]) -> dict[str, Any]:
    """Strip empty / falsy fields from a normalized parameter entry.

    The on-disk spec stores every parameter with the full canonical key
    set so the dispatcher's parser builders are uniform. ``--describe``
    is consumer-facing — flags like ``is_list: false``, ``choices: []``,
    ``help: null`` are pure noise. Drop them.
    """
    out: dict[str, Any] = {
        "name": p["name"],
        "in": p.get("in", "query"),
        "type": p.get("type", "string"),
    }
    if p.get("is_list"):
        out["is_list"] = True
    if p.get("required"):
        out["required"] = True
    if p.get("default") is not None:
        out["default"] = p["default"]
    if p.get("choices"):
        out["choices"] = p["choices"]
    if p.get("help"):
        out["help"] = p["help"]
    return out


def _group_by_provider(
    raw_params: list[dict[str, Any]],
    body_params: list[dict[str, Any]],
    providers: list[str],
    output_schema: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    """Group parameters and output schemas per provider.

    Multi-provider OpenBB endpoints are a discriminated union: the
    ``provider`` flag selects a different parameter set *and* a different
    response data class. Showing one merged ``parameters`` array misleads
    the user — flags only valid for ``intrinio`` look like they apply to
    ``cboe``. Group instead: for each provider, list every parameter that
    targets it (shared params with no ``providers`` tag are repeated under
    every provider, since they're inputs every variant accepts) plus the
    request body fields, and pick the matching response schema variant.
    """
    out: dict[str, dict[str, Any]] = {}
    for provider in providers:
        provider_params: list[dict[str, Any]] = []
        for p in raw_params:
            if p.get("name") == "provider":
                continue
            tags = p.get("providers") or []
            if tags and provider not in tags:
                continue
            slim = _slim_param(p)
            slim["help"] = _help_for_provider(slim.get("help"), provider)
            if not slim.get("help"):
                slim.pop("help", None)
            provider_params.append(slim)
        provider_params.extend(body_params)
        out[provider] = {
            "parameters": provider_params,
            "output_schema": _provider_output_schema(output_schema, provider),
        }
    return out


def _provider_output_schema(
    output_schema: dict[str, Any] | None, provider: str
) -> dict[str, Any] | None:
    """Pick the per-provider variant out of a OneOf-of-data-classes results list.

    OpenBB Platform multi-provider endpoints declare ``results`` as
    ``anyOf[{items: {oneOf: [<ProviderA>Data, <ProviderB>Data, ...]}, type:
    array}, null]``. Each variant's ``title`` starts with the provider name
    in mixed case (``IntrinioEquityQuoteData``, ``FMPEquityQuoteData``,
    ``YFinanceEquityQuoteData``). Match case-insensitively on the title
    prefix and return that single variant — the OBBject wrapper above
    ``results`` is dropped because the user asked for "the actual output
    schema", not the envelope.
    """
    if not isinstance(output_schema, dict):
        return None
    results = (output_schema.get("properties") or {}).get("results")
    if not isinstance(results, dict):
        return None
    candidates: list[Any] = []
    for variant in results.get("anyOf") or [results]:
        if not isinstance(variant, dict) or variant.get("type") == "null":
            continue
        if variant.get("type") == "array" and isinstance(variant.get("items"), dict):
            inner = variant["items"]
            candidates.extend(inner.get("oneOf") or [inner])
        else:
            candidates.extend(variant.get("oneOf") or [variant])
    target = provider.lower()
    for cand in candidates:
        if not isinstance(cand, dict):
            continue
        title = (cand.get("title") or "").lower()
        if title.startswith(target):
            return cand
    if len(candidates) == 1 and isinstance(candidates[0], dict):
        return candidates[0]
    return None


def _body_schema_to_params(
    body_schema: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Flatten a request-body object schema into per-field parameter entries.

    POST endpoints (econometrics, technical, quantitative, charting routes)
    declare their inputs in ``requestBody.content[json].schema``, not in
    ``parameters[]``. Surfacing those properties as ``in: "body"`` entries
    in ``--describe`` lets a script writer see every input — query, path,
    *and* body — in one flat list. Items schemas for arrays of objects
    (e.g. ``data: list[Data]``) are kept inline so the user can see the
    element shape.
    """
    if not isinstance(body_schema, dict) or body_schema.get("type") != "object":
        return []
    properties = body_schema.get("properties") or {}
    required_set = set(body_schema.get("required") or [])
    out: list[dict[str, Any]] = []
    for name, schema in properties.items():
        if not isinstance(schema, dict):
            continue
        schema_type = schema.get("type")
        is_list = schema_type == "array"
        if is_list:
            items = schema.get("items") or {}
            type_name = items.get("type") if isinstance(items, dict) else None
            type_name = type_name or "object"
        else:
            type_name = schema_type or "string"
        entry: dict[str, Any] = {
            "name": name,
            "in": "body",
            "type": type_name,
        }
        if is_list:
            entry["is_list"] = True
        if name in required_set:
            entry["required"] = True
        if "default" in schema and schema["default"] is not None:
            entry["default"] = schema["default"]
        help_text = schema.get("description") or schema.get("title")
        if help_text:
            entry["help"] = help_text
        if is_list:
            items = schema.get("items")
            if isinstance(items, dict) and items.get("type") == "object":
                entry["items"] = items
        out.append(entry)
    return out


def _decode_response(response: httpx.Response) -> Any:
    """Return the response body as JSON when the server says so, otherwise text.

    Servers that honor a ``--format`` query param (e.g. Congress.gov accepts
    ``?format=xml`` and returns an XML body with ``content-type:
    application/xml``) would otherwise hit ``response.json()`` and raise
    ``JSONDecodeError``. Sniff the content type first and fall back gracefully.
    """
    content_type = (response.headers.get("content-type") or "").lower().split(";", 1)[0]
    if content_type.endswith("json") or content_type == "":
        try:
            return response.json()
        except ValueError:
            return response.text
    return response.text


_NUMERIC_RESPONSE_TYPES: frozenset[str] = frozenset(
    {"number", "money", "percent", "double"}
)

# Socrata's per-request page size. The portal's dispatcher rejects any
# single ``$limit`` above this — larger volumes have to be fetched via
# paginated ``$offset`` requests. We use this as both the wire cap on
# every page AND the chunk size for ``limit=0`` "fetch all" mode.
_SOCRATA_PAGE_SIZE = 5000

# Safety cap on automatic pagination — at 5000 rows/page, this is
# 5,000,000 rows max per command. Anything that needs more should be
# fetching from a flat-file dump, not through the ``/resource/`` API.
_SOCRATA_MAX_PAGES = 1000


def _user_requested_all_rows(request: Request) -> bool:
    """Return True when the caller asked for the full dataset (``limit=0``)."""
    raw = (request.params or {}).get("limit")
    if raw is None:
        return False
    try:
        return int(raw) == 0
    except (TypeError, ValueError):
        return False


def _user_limit_for_per_item(request: Request) -> int | None:
    """Return the user's ``limit`` as an int, or ``None`` if unusable.

    Treats ``0`` as "no cap" (per-item collapse returns every distinct
    item it finds) so the ``limit=0`` semantics flow through to the
    collapse pass.
    """
    raw = (request.params or {}).get("limit")
    if raw is None:
        return None
    try:
        n = int(raw)
    except (TypeError, ValueError):
        return None
    if n < 0:
        return None
    return n if n > 0 else None


async def _fetch_until_n_distinct_dates(
    client: httpx.AsyncClient,
    url: str,
    base_query: dict[str, Any],
    extra_headers: dict[str, str] | None,
    time_axis: str,
    n: int,
) -> list[dict[str, Any]]:
    """Page until the response covers ≥ ``n + 1`` distinct ``time_axis`` values.

    Used by date-snapshot ``limit=N`` semantics: we need every row from
    the N most recent distinct dates, so the fetch stops once we've
    confirmed the boundary (the N+1-th date appears) — at that point
    the local truncation can safely cut off the tail. Stops early if
    the upstream returns a short page (no more data to page through)
    or hits ``_SOCRATA_MAX_PAGES``.
    """
    rows: list[dict[str, Any]] = []
    distinct_dates: set[Any] = set()
    base = dict(base_query)
    base["$limit"] = _SOCRATA_PAGE_SIZE
    for page in range(_SOCRATA_MAX_PAGES):
        page_params = dict(base)
        page_params["$offset"] = page * _SOCRATA_PAGE_SIZE
        response = await client.get(url, params=page_params, headers=extra_headers)
        response.raise_for_status()
        payload = _decode_response(response)
        if not isinstance(payload, list) or not payload:
            break
        rows.extend(payload)
        for row in payload:
            if isinstance(row, dict):
                value = row.get(time_axis)
                if value is not None:
                    distinct_dates.add(value)
        # Once we've seen ``n + 1`` distinct dates, the (n+1)-th appearance
        # marks where the truncate pass will cut — no need to keep paging.
        if len(distinct_dates) > n:
            break
        if len(payload) < _SOCRATA_PAGE_SIZE:
            break
    return rows


async def _fetch_all_pages(
    client: httpx.AsyncClient,
    url: str,
    base_query: dict[str, Any],
    extra_headers: dict[str, str] | None,
) -> list[dict[str, Any]]:
    """Page through ``$offset`` until the upstream returns an empty page.

    Used by ``limit=0`` semantics — the caller asked for "every row",
    so we issue ``_SOCRATA_PAGE_SIZE``-sized pages sequentially and
    concatenate. Sequential is intentional: parallel pagination breaks
    when the dataset isn't strictly date-ordered (rows shift between
    pages between requests), and Socrata's per-IP rate limit is gentle
    enough for sequential issue not to bottleneck typical 10–50 page
    fetches.

    Stops at ``_SOCRATA_MAX_PAGES`` as a safety net — anything larger
    is better fetched from the dataset's flat-file dump rather than
    the resource API.
    """
    rows: list[dict[str, Any]] = []
    base = dict(base_query)
    base["$limit"] = _SOCRATA_PAGE_SIZE
    for page in range(_SOCRATA_MAX_PAGES):
        page_params = dict(base)
        page_params["$offset"] = page * _SOCRATA_PAGE_SIZE
        response = await client.get(url, params=page_params, headers=extra_headers)
        response.raise_for_status()
        payload = _decode_response(response)
        if not isinstance(payload, list) or not payload:
            break
        rows.extend(payload)
        if len(payload) < _SOCRATA_PAGE_SIZE:
            # Short page — this was the last batch the upstream had.
            break
    return rows


def _request_with_page_size_limit(request: Request) -> Request:
    """Return a copy of ``request`` with ``limit`` capped to one page.

    Used by the most-recent-per-item path: we issue a single page-sized
    request, collapse to most-recent-per-item locally, then cap to the
    user's requested ``limit``. One page is usually enough to cover
    every distinct item in a date-DESC sort.
    """
    bumped = dict(request.params or {})
    bumped["limit"] = _SOCRATA_PAGE_SIZE
    return Request(id=request.id, command=request.command, params=bumped)


def _truncate_to_top_n_dates(
    shaped: Any, time_axis: str, user_limit: int | None
) -> Any:
    """Keep every row whose ``time_axis`` is among the ``user_limit`` most recent.

    Rows are assumed pre-sorted DESC by ``time_axis`` (the dispatcher
    sets ``$order=<time_axis> DESC`` by default). Walks the list once,
    tracking distinct date values; once the (``user_limit``+1)-th
    distinct date appears, stops including further rows. Returns the
    full set when ``user_limit`` is ``None`` (the ``limit=0`` case
    where the user asked for every row already).

    Falls through unchanged when the payload isn't a row list — nothing
    to truncate.
    """
    rows = _extract_rows(shaped)
    if rows is None or user_limit is None:
        return shaped
    seen_dates: list[Any] = []
    seen_set: set[Any] = set()
    kept: list[Any] = []
    for row in rows:
        if not isinstance(row, dict):
            kept.append(row)
            continue
        date = row.get(time_axis)
        if date is None:
            kept.append(row)
            continue
        if date not in seen_set:
            if len(seen_dates) >= user_limit:
                break
            seen_dates.append(date)
            seen_set.add(date)
        kept.append(row)
    return _replace_rows(shaped, kept)


def _extract_rows(shaped: Any) -> list[Any] | None:
    """Pull the row list out of a shaped result, or return ``None``.

    Handles three carriers: a bare list, a ``{results: [...]}`` dict, or
    an actual ``OBBject`` instance (the dispatcher's spec-mode wrap).
    """
    if isinstance(shaped, list):
        return shaped
    if isinstance(shaped, dict):
        results = shaped.get("results")
        if isinstance(results, list):
            return results
        return None
    # Duck-typed OBBject — we don't import the type here to keep this
    # module independent of openbb_core. ``results`` plus ``extra``
    # together are a tight enough fingerprint.
    results = getattr(shaped, "results", None)
    if isinstance(results, list) and hasattr(shaped, "extra"):
        return results
    return None


def _replace_rows(shaped: Any, rows: list[Any]) -> Any:
    """Inverse of ``_extract_rows`` — substitute the collapsed row list back in.

    Mutates an OBBject in place (keeps the original instance, including
    its private attrs like ``_standard_params``) so registry insertion
    downstream still sees the canonical instance.
    """
    if isinstance(shaped, list):
        return rows
    if isinstance(shaped, dict) and isinstance(shaped.get("results"), list):
        return {**shaped, "results": rows}
    if isinstance(getattr(shaped, "results", None), list) and hasattr(shaped, "extra"):
        shaped.results = rows
        return shaped
    return shaped


def _coerce_response_value(value: Any, type_name: str, fmt: str) -> Any:
    """Cast a single field value to the type declared by the response schema.

    Socrata serializes everything as strings on the wire — even
    ``calendar_date``, ``number``, and ``boolean`` columns — so the raw
    payload comes back with ``"3.14"`` for a number field and
    ``"2024-01-01T00:00:00.000"`` for a date. The Pydantic ``Data``
    class handles this automatically when the installed-extension path
    runs (``Data(**row)`` parses each value), but spec-mode dispatch
    skips Pydantic and returns the raw dict — so we coerce here to keep
    the user-facing shape consistent across both backends.
    """
    if not isinstance(value, str):
        return value
    if type_name in _NUMERIC_RESPONSE_TYPES:
        try:
            num = float(value)
        except ValueError:
            return value
        return int(num) if num.is_integer() else num
    if type_name == "integer":
        try:
            return int(value)
        except ValueError:
            return value
    if type_name == "boolean":
        if value.lower() in {"true", "false"}:
            return value.lower() == "true"
        return value
    # Drop the time component from ``2024-01-01T00:00:00.000`` — the
    # column is date-only by intent, the timestamp form is just how
    # Socrata serializes it.
    if type_name == "string" and fmt == "date" and "T" in value and len(value) >= 10:
        return value.split("T", 1)[0]
    return value


def _row_column_types(cmd_spec: dict[str, Any]) -> dict[str, tuple[str, str]]:
    """Extract ``{field_name: (type, format)}`` from a command's response schema.

    Walks the ``{results: array<row>}`` envelope the spec generators
    emit. Returns an empty dict when the schema doesn't fit that shape
    (most non-Socrata commands), in which case ``_coerce_row_types``
    becomes a no-op.
    """
    response = cmd_spec.get("response_schema") or {}
    results = (response.get("properties") or {}).get("results") or {}
    items = results.get("items") or {}
    item_props = items.get("properties") or {}
    out: dict[str, tuple[str, str]] = {}
    for name, schema in item_props.items():
        if not isinstance(schema, dict):
            continue
        out[name] = (
            schema.get("type") or "",
            schema.get("format") or "",
        )
    return out


def _command_to_route(command: str) -> str:
    """Translate a dotted CLI command into the slash-separated route shape
    that ``Metadata.route`` carries in the installed-extension path.

    ``equity.price.historical`` → ``/equity/price/historical``. Mirrors the
    convention ``command_runner`` uses so downstream telemetry parses
    spec-mode and installed-extension routes identically.
    """
    return "/" + command.replace(".", "/").strip("/")


def _row_column_metadata(cmd_spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Extract per-column description / format hints from the response schema.

    Mirrors the codegen path in ``fetcher_gen._column_metadata_from_data_schema``
    so spec-mode dispatch surfaces the same ``{field: {description?, format?,
    socrata_format?}}`` map under ``AnnotatedResult.metadata['columns']``
    as the installed-extension fetcher does. Empty dict when the schema
    doesn't carry such metadata.
    """
    response = cmd_spec.get("response_schema") or {}
    results = (response.get("properties") or {}).get("results") or {}
    items = results.get("items") or {}
    item_props = items.get("properties") or {}
    out: dict[str, dict[str, Any]] = {}
    for name, schema in item_props.items():
        if not isinstance(schema, dict):
            continue
        meta: dict[str, Any] = {}
        if schema.get("description"):
            meta["description"] = schema["description"]
        if schema.get("format"):
            meta["format"] = schema["format"]
        if schema.get("socrata_format"):
            meta["socrata_format"] = schema["socrata_format"]
        if meta:
            out[name] = meta
    return out


def _coerce_row_types(
    rows: list[dict[str, Any]], column_types: dict[str, tuple[str, str]]
) -> list[dict[str, Any]]:
    """Apply schema-driven coercion to every row in a response."""
    if not column_types:
        return rows
    coerced: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            coerced.append(row)
            continue
        new_row = {}
        for k, v in row.items():
            type_info = column_types.get(k)
            if type_info is None:
                new_row[k] = v
            else:
                new_row[k] = _coerce_response_value(v, type_info[0], type_info[1])
        coerced.append(new_row)
    return coerced


def _is_plotly_figure(payload: Any) -> bool:
    """Detect a Plotly figure-shaped payload.

    A Plotly figure is a top-level dict with both ``data`` (a list of
    trace objects, each itself a dict carrying a ``type`` field
    naming a Plotly trace kind: ``scatter``, ``scattergeo``, ``bar``,
    ``heatmap`` etc.) and ``layout`` (a dict). Without this guard the
    generic ``unpack_response`` strips the structure: it sees one
    list-keyed field (``data``) and treats it as a row array, putting
    ``layout`` into ``metadata`` and losing the figure semantics.

    Conservative on purpose — both keys must be present in the right
    shapes, and at least one trace must declare a ``type``. Random
    APIs that happen to expose ``data`` + ``layout`` won't trigger
    this unless the data list also looks like Plotly traces.
    """
    if not isinstance(payload, dict):
        return False
    data = payload.get("data")
    layout = payload.get("layout")
    if not isinstance(data, list) or not isinstance(layout, dict):
        return False
    if not data:
        return False
    return any(
        isinstance(trace, dict) and isinstance(trace.get("type"), str) for trace in data
    )


def _wrap_plotly_figure(
    payload: dict[str, Any],
    *,
    command: str,
    params: dict[str, Any] | None,
    timestamp: datetime | None,
    duration_ns: int | None,
) -> Any:
    """Wrap a Plotly figure dict in an ``OBBject`` with ``results=figure``.

    The figure IS the result — the full Plotly dict (``data`` + ``layout``
    and any other Plotly keys) rides at ``OBBject.results`` so callers
    reading ``obbject.results`` see the actual content the endpoint
    returned, instead of ``None`` with the data buried under ``chart``.
    ``OBBject.chart`` also carries a ``Chart`` mirror of the figure so
    chart-aware renderers (``obbject.charting.show()``, etc.) keep
    working — same data, two valid access points.

    Execution metadata (route / args / timing) lands at
    ``extra["metadata"]`` exactly like every other dispatch.

    Falls back to returning the raw payload dict when ``openbb_core``
    isn't importable, preserving the figure structure even in
    minimal-install environments.
    """
    try:
        from openbb_core.app.model.charts.chart import Chart
        from openbb_core.app.model.metadata import Metadata
        from openbb_core.app.model.obbject import OBBject
    except ImportError:
        return payload

    extra: dict[str, Any] = {}
    if timestamp is not None and duration_ns is not None:
        with contextlib.suppress(Exception):
            extra["metadata"] = Metadata(
                arguments={
                    "provider_choices": {},
                    "standard_params": dict(params or {}),
                    "extra_params": {},
                },
                duration=duration_ns,
                route=_command_to_route(command),
                timestamp=timestamp,
            )

    return OBBject(
        results=payload,
        chart=Chart(content=payload, format="plotly"),
        extra=extra,
    )


def _shape_result(payload: Any) -> Any:
    """Apply the same envelope unwrap codegen does, then return a tidy result.

    Wraps the unpacked rows + metadata in the OBBject-shaped dict the rest of
    the CLI rendering expects: a single row dict (when there's exactly one)
    or the row list otherwise. Metadata, when present, is exposed alongside
    so downstream renderers can still surface it.
    """
    if not isinstance(payload, (dict, list)):
        return payload
    rows, metadata = unpack_response(payload)
    if not rows and not metadata:
        return payload
    body: Any
    if len(rows) == 1:
        sole = rows[0]
        body = sole.get("value", sole) if set(sole.keys()) == {"value"} else sole
    else:
        body = [r.get("value", r) if set(r.keys()) == {"value"} else r for r in rows]
    if metadata:
        return {"results": body, "metadata": metadata}
    return body


class HttpDispatcher:
    """Multi-tenant dispatcher backed by openbb-platform-api over HTTP.

    The heavy ``import openbb`` cost lives on the server, so cold-starting this
    dispatcher is fast — useful when ``openbb foo bar`` is invoked many times
    or by many users sharing a server.

    Two per-command maps drive routing:

    * ``command_methods``: ``{dotted.command: "get" | "post"}``. OpenBB
      Platform endpoints are mostly GET, a few POST; without this the
      dispatcher falls back to POST and 405s on GETs.
    * ``command_url_paths``: ``{dotted.command: "/api/.../{template}"}``.
      For specs whose URLs include path placeholders (NY Fed Markets API,
      Stripe, GitHub, etc.) the dispatcher needs the original URL template
      to substitute path params into. Without it the dispatcher reconstructs
      the URL from the dotted command — fine for OpenBB Platform but loses
      placeholders.
    """

    def __init__(
        self,
        base_url: str,
        *,
        client: httpx.AsyncClient | None = None,
        timeout: float = 60.0,
        api_prefix: str = "/api/v1",
        command_methods: dict[str, str] | None = None,
        command_url_paths: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        query_params: dict[str, str] | None = None,
        spec_doc: dict[str, Any] | None = None,
        auth_hook: AuthHook | None = None,
        namespace: str | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_prefix = "/" + api_prefix.strip("/")
        self._timeout = timeout
        if client is not None:
            self._client: httpx.AsyncClient | None = client
            self._owns_client = False
        else:
            self._client = None
            self._owns_client = True
        self._command_methods = command_methods or {}
        self._command_url_paths = command_url_paths or {}
        self._headers = dict(headers) if headers else {}
        self._query_params = dict(query_params) if query_params else {}
        self._spec_doc = spec_doc or {}
        self._auth_hook = auth_hook
        self._namespace = namespace

    def _url_for(self, command: str) -> str:
        """Build the fully-qualified URL for a command, no path-param substitution.

        Used when no URL template is registered for the command (the OpenBB
        Platform default). For specs that register templates, see
        ``_resolve_url`` which also handles ``{placeholder}`` substitution.
        """
        path = command.replace(".", "/").strip("/")
        return f"{self._base_url}{self._api_prefix}/{path}"

    def _resolve_url(
        self, command: str, params: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        """Build the URL for ``command`` and split path-substituted params off.

        Returns ``(url, remaining_params)``. ``remaining_params`` is what goes
        on the query string (GET) or in the JSON body (POST). The remaining
        params are also passed through ``_apply_param_transforms`` so any
        ``wire_name`` renames or Socrata-style date-range folding declared in
        the spec take effect — same translation the generated fetcher
        applies, kept in sync between spec-mode and installed-extension flows.
        """
        template = self._command_url_paths.get(command)
        if template is None:
            return self._url_for(command), self._apply_param_transforms(
                command, dict(params)
            )

        consumed: set[str] = set()

        def _substitute(match: re.Match[str]) -> str:
            key = match.group(1)
            consumed.add(key)
            value = params.get(key)
            if value is None:
                return match.group(0)
            return str(value)

        path = _PATH_TEMPLATE_RE.sub(_substitute, template)
        remaining = {k: v for k, v in params.items() if k not in consumed}
        return f"{self._base_url}{path}", self._apply_param_transforms(
            command, remaining
        )

    def _date_snapshot_context(self, request: Request) -> tuple[str | None, int | None]:
        """Detect the "rows-from-N-most-recent-dates" branch for ``limit``.

        Returns ``(time_axis_column, user_limit)`` when the spec marks a
        time-axis column AND the user supplied a positive ``limit``.
        ``(None, None)`` otherwise — the caller falls back to plain
        single-page dispatch with no truncation.

        ``limit=0`` (fetch-all) doesn't trigger date-snapshot truncation
        because the caller asked for every row regardless of date.
        """
        cmd_spec = (self._spec_doc.get("commands") or {}).get(request.command) or {}
        time_axis = cmd_spec.get("_socrata_time_axis")
        if not time_axis:
            return None, None
        raw_limit = (request.params or {}).get("limit")
        if raw_limit is None:
            return None, None
        try:
            user_limit = int(raw_limit)
        except (TypeError, ValueError):
            return None, None
        if user_limit <= 0:
            return None, None
        return time_axis, user_limit

    def _shape_and_coerce(
        self,
        command: str,
        payload: Any,
        *,
        params: dict[str, Any] | None = None,
        timestamp: datetime | None = None,
        duration_ns: int | None = None,
    ) -> Any:
        """Unpack envelopes, coerce row types, then return a real ``OBBject``.

        ``_shape_result`` strips the OBBject / single-key wrappers. After
        that, when the spec carries a typed ``response_schema``, the per
        column ``(type, format)`` map drives a row-by-row coercion so
        date-only columns lose the ``T00:00:00.000`` suffix and numeric
        columns become ``int`` / ``float`` instead of strings — matching
        what the installed-extension Pydantic ``Data`` class would do.

        Whenever there's *any* metadata to surface (column descriptions,
        sibling API metadata like NY-Fed's ``asOfDate``, or execution
        info from ``command_runner``-style timing), the dispatcher
        wraps the rows in a real ``OBBject``. ``metadata`` is *never*
        a top-level property of the result — it lives under
        ``extra["metadata"]`` (execution info, ``command_runner``
        shape) or under ``extra["results_metadata"]`` (per-column
        descriptions + sibling API metadata folded together).

        Returns bare rows only when nothing in the spec or upstream
        response calls for an OBBject envelope (no spec, no sibling
        metadata) — keeping the simplest possible shape for
        single-row OpenBB Platform calls without a response_schema.

        Plotly figure payloads (``{data: [...traces...], layout: {...}}``)
        bypass the regular unwrap and land at ``OBBject.chart.content``
        with ``format="plotly"`` — the canonical OBBject home for charts.
        Without this guard the generic envelope-stripper would treat
        ``data`` as a row array and silently drop the ``layout``,
        leaving callers with a list of half-traces.
        """
        if _is_plotly_figure(payload):
            return _wrap_plotly_figure(
                payload,
                command=command,
                params=params,
                timestamp=timestamp,
                duration_ns=duration_ns,
            )
        shaped = _shape_result(payload)
        cmd_spec = (self._spec_doc.get("commands") or {}).get(command) or {}
        column_types = _row_column_types(cmd_spec)
        column_metadata = _row_column_metadata(cmd_spec)

        # Pull rows + any sibling metadata out of whatever shape
        # ``_shape_result`` produced. Three cases:
        #   * bare list of dicts (most Socrata responses)
        #   * ``{results, metadata}`` envelope from sibling-metadata APIs
        #   * single dict (one-row response)
        api_metadata: dict[str, Any] = {}
        rows: Any
        if isinstance(shaped, list):
            rows = shaped
        elif isinstance(shaped, dict):
            inner = shaped.get("results")
            if isinstance(inner, list) or inner is not None:
                rows = inner
                api_metadata = dict(shaped.get("metadata") or {})
            else:
                rows = shaped
        else:
            return shaped

        if column_types:
            if isinstance(rows, list):
                rows = _coerce_row_types(rows, column_types)
            elif isinstance(rows, dict):
                rows = _coerce_row_types([rows], column_types)[0]

        # Nothing in the spec or upstream signals user-visible metadata —
        # return bare rows. ``column_types`` alone (response_schema with
        # only type info) doesn't justify a wrap because there's nothing
        # to surface beyond the rows themselves; the type coercion that
        # already ran is the only behavior driven by it.
        if not column_metadata and not api_metadata:
            return rows

        # Construct a real ``OBBject`` and return the live instance.
        # Pydantic serializes it for the wire JSON path; interactive
        # callers get the actual instance for registry insertion.
        #
        # Three distinct extra keys, never conflated:
        #
        # * ``extra["results_metadata"]`` — per-row / per-column
        #   metadata (the ``AnnotatedResult.metadata`` shape from
        #   codegen). Carries ``columns`` describing each column's
        #   description / Socrata format hints.
        # * ``extra["metadata"]`` — execution ``Metadata`` (the
        #   ``command_runner`` shape). Route, arguments, duration,
        #   timestamp.
        # * Sibling API fields (NY-Fed ``asOfDate``, etc.) — each lands
        #   under its own key in ``extra`` directly. They are not
        #   row-level metadata and they are not execution telemetry,
        #   so folding them into either bucket would lie about what
        #   they are.

        # Deferred import: ``openbb_core`` is an optional runtime
        # dependency of the CLI (only required for paths that surface
        # OBBject metadata). Falling back to a plain dict keeps the
        # dispatcher usable in environments without it — but the
        # fallback still puts metadata under ``extra`` so the schema
        # never sprouts a top-level ``metadata`` field.
        try:
            from openbb_core.app.model.metadata import Metadata
            from openbb_core.app.model.obbject import OBBject
        except ImportError:
            extra_fallback: dict[str, Any] = dict(api_metadata)
            if column_metadata:
                extra_fallback["results_metadata"] = {"columns": column_metadata}
            return {"results": rows, "extra": extra_fallback}

        extra: dict[str, Any] = dict(api_metadata)
        if column_metadata:
            extra["results_metadata"] = {"columns": column_metadata}

        # Mirror ``command_runner``: attach a ``Metadata`` instance under
        # ``extra["metadata"]`` carrying the route, arguments, timestamp,
        # and duration. ``arguments`` follows the canonical
        # ``{provider_choices, standard_params, extra_params}`` shape so
        # downstream consumers (renderers, registries) parse it the same
        # way they do for installed-extension responses.
        if timestamp is not None and duration_ns is not None:
            # Telemetry is best-effort — a malformed Metadata payload
            # shouldn't kill an otherwise-good response.
            with contextlib.suppress(Exception):
                extra["metadata"] = Metadata(
                    arguments={
                        "provider_choices": {},
                        "standard_params": dict(params or {}),
                        "extra_params": {},
                    },
                    duration=duration_ns,
                    route=_command_to_route(command),
                    timestamp=timestamp,
                )

        return OBBject(results=rows, extra=extra)

    def _apply_param_transforms(
        self, command: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Translate user-facing param names into the upstream wire form.

        Two transforms drive off per-parameter spec metadata:

        * ``wire_name`` — rename the dict key. Lets Socrata expose
          clean ``limit`` / ``offset`` to the user while sending
          ``$limit`` / ``$offset`` on the wire.
        * ``_socrata_op`` (``date_min`` / ``date_max``) plus
          ``_socrata_column`` — fold the date-range params into a
          single SoQL ``$where`` clause keyed on the underlying
          column name. Mirrors ``fetcher_gen``'s codegen so spec-mode
          dispatch and installed-extension dispatch produce the same URL.

        Returns a new dict; ``params`` is not mutated.
        """
        cmd_spec = (self._spec_doc.get("commands") or {}).get(command) or {}
        param_specs = cmd_spec.get("parameters") or []
        if not param_specs:
            return params
        out = dict(params)
        # Date-range fold into ``$where`` — collect first so the rename
        # pass below sees the populated ``$where`` (avoids stomping a
        # user-supplied one).
        where_parts: list[str] = []
        for p in param_specs:
            if not isinstance(p, dict):
                continue
            op = p.get("_socrata_op")
            if op not in {"date_min", "date_max"}:
                continue
            value = out.pop(p["name"], None)
            if value is None:
                continue
            column = p.get("_socrata_column")
            if not column:
                continue
            cmp = ">=" if op == "date_min" else "<="
            where_parts.append(f"{column} {cmp} '{value}'")
        if where_parts:
            existing = out.pop("$where", None)
            joined = " AND ".join(where_parts)
            out["$where"] = f"({existing}) AND ({joined})" if existing else joined
        # Default ordering when the spec marks a time axis: sort by it
        # descending so ``limit=N`` naturally returns the N most recent
        # records. The time axis is whatever the spec generator marked
        # as ``_socrata_time_axis`` — could be a true ``calendar_date``
        # column or a text column named ``year`` / ``month_year`` etc.
        # Datasets without any time-shaped column skip this step.
        time_axis = cmd_spec.get("_socrata_time_axis")
        if time_axis and "$order" not in out:
            out["$order"] = f"{time_axis} DESC"
        # ``wire_name`` renames — apply after the where-fold so range
        # params (already removed) don't get processed twice.
        for p in param_specs:
            if not isinstance(p, dict):
                continue
            wire = p.get("wire_name")
            name = p.get("name")
            if wire and name and wire != name and name in out:
                out[wire] = out.pop(name)
        return out

    def _method_for(self, command: str, override: str | None) -> str:
        """Resolve the HTTP method for ``command``: explicit override > map > default."""
        if override is not None:
            return override.lower()
        return self._command_methods.get(command, "post").lower()

    async def _invoke_auth_hook(
        self, request: Request, method_lower: str
    ) -> AuthDecision:
        """Run the configured auth hook (if any) and return its decision.

        Hooks may be sync or async — we await coroutines and pass plain
        callables straight through. A hook that raises is converted into an
        ``allow=False`` decision so the rest of ``dispatch`` reports it as a
        structured error response instead of letting it crash the dispatch
        loop. Returns an empty allow-decision when no hook is configured so
        the caller's merge logic stays one branch.
        """
        if self._auth_hook is None:
            return AuthDecision()
        ctx = AuthContext(
            namespace=self._namespace,
            command=request.command,
            params=dict(request.params or {}),
            method=method_lower,
        )
        try:
            result = self._auth_hook(ctx)
            if inspect.isawaitable(result):
                result = await result
        except Exception as exc:  # noqa: BLE001 — surface hook failures as deny
            return AuthDecision(allow=False, deny_reason=f"auth hook raised: {exc}")
        if not isinstance(result, AuthDecision):
            return AuthDecision(
                allow=False,
                deny_reason=(
                    f"auth hook returned {type(result).__name__}; expected AuthDecision"
                ),
            )
        return result

    async def dispatch(self, request: Request, method: str | None = None) -> Response:
        """Send ``request`` to the platform-api endpoint that maps to its command.

        Reserved introspection commands ``__commands__`` and ``__schema__``
        short-circuit before HTTP routing — they read directly from the spec
        the dispatcher was built from, so they work in one-shot, batch, and
        REPL flows without round-tripping the upstream server.

        Method resolution order: explicit ``method`` > constructor's
        ``command_methods`` map > fallback ``"post"``. Path parameters
        registered in ``command_url_paths`` are substituted into the URL and
        excluded from the query string / body.

        When this dispatcher owns its ``httpx.AsyncClient``, a fresh client is
        created per dispatch so each ``asyncio.run`` invocation (the REPL's
        sync-bridge path) gets a client bound to the current event loop —
        cached clients leak ``Event loop is closed`` after the first call.
        """
        if request.command == "__commands__":
            return await self._list_commands(request)
        if request.command == "__schema__":
            return await self._describe_command(request)
        # ``limit=N`` against a dataset with a time axis means "every row
        # from the N most recent distinct dates" (a snapshot semantic),
        # not "N rows total." We fetch pages until we've gathered at
        # least N+1 distinct dates' worth of rows, then truncate locally
        # to keep only the top N. ``limit=0`` keeps its existing
        # "fetch every row" meaning.
        time_axis, user_limit = self._date_snapshot_context(request)
        fetch_all = _user_requested_all_rows(request)
        wire_request = request
        if time_axis is not None or fetch_all:
            wire_request = _request_with_page_size_limit(request)
        # Capture wall-clock + monotonic clock for ``Metadata`` — same
        # pair ``command_runner`` records before invoking the command.
        timestamp = datetime.now(timezone.utc)
        start_ns = perf_counter_ns()
        try:
            url, body_or_query = self._resolve_url(
                wire_request.command, wire_request.params or {}
            )
            method_lower = self._method_for(wire_request.command, method)
            decision = await self._invoke_auth_hook(wire_request, method_lower)
            if not decision.allow:
                return Response(
                    id=request.id,
                    ok=False,
                    error=ResponseError(
                        type="AccessDenied",
                        message=decision.deny_reason or "auth hook denied request",
                    ),
                )
            extra_headers = decision.headers or None
            extra_query = decision.query_params or None
            async with self._client_context() as client:
                if method_lower == "get":
                    merged_query = {
                        **self._query_params,
                        **(extra_query or {}),
                        **body_or_query,
                    }
                    if fetch_all:
                        # ``limit=0`` mode: page through ``$offset``
                        # until the response runs dry.
                        payload = await _fetch_all_pages(
                            client, url, merged_query, extra_headers
                        )
                    elif time_axis is not None:
                        # Date-snapshot mode: page until we've seen at
                        # least ``user_limit + 1`` distinct dates, so
                        # the local truncation knows exactly where the
                        # cutoff date is.
                        payload = await _fetch_until_n_distinct_dates(
                            client,
                            url,
                            merged_query,
                            extra_headers,
                            time_axis,
                            user_limit or 0,
                        )
                    else:
                        response = await client.get(
                            url, params=merged_query, headers=extra_headers
                        )
                        response.raise_for_status()
                        payload = _decode_response(response)
                else:
                    merged_query = {**self._query_params, **(extra_query or {})}
                    response = await client.post(
                        url,
                        params=merged_query or None,
                        json=body_or_query,
                        headers=extra_headers,
                    )
                    response.raise_for_status()
                    payload = _decode_response(response)
            duration_ns = perf_counter_ns() - start_ns
            shaped = self._shape_and_coerce(
                wire_request.command,
                payload,
                params=request.params or {},
                timestamp=timestamp,
                duration_ns=duration_ns,
            )
            if time_axis is not None and not fetch_all:
                shaped = _truncate_to_top_n_dates(shaped, time_axis, user_limit)
            return Response(
                id=request.id,
                ok=True,
                result=shaped,
                error=None,
            )
        except httpx.HTTPStatusError as exc:
            try:
                detail = exc.response.json()
            except ValueError:
                detail = exc.response.text
            return Response(
                id=request.id,
                ok=False,
                error=ResponseError(
                    type=f"HTTP{exc.response.status_code}",
                    message=str(detail),
                ),
            )
        except httpx.RequestError as exc:
            return Response(
                id=request.id,
                ok=False,
                error=ResponseError(type=type(exc).__name__, message=str(exc)),
            )
        except Exception as exc:  # noqa: BLE001 — same isolation contract as LocalDispatcher
            return Response(
                id=request.id,
                ok=False,
                error=ResponseError(type=type(exc).__name__, message=str(exc)),
            )

    async def _list_commands(self, request: Request) -> Response:
        """Return ``[{name, description}, ...]`` for every command the auth hook permits.

        When an auth hook is configured, every command is gated through it
        so RBAC implementations can hide endpoints the caller isn't
        authorized to call. Hook signature is the same as for dispatch
        (``AuthContext`` → ``AuthDecision``); a deny silently drops the
        entry from the listing — visibility, not an error. With no hook
        configured every command is included, matching the original
        behavior.
        """
        commands = self._spec_doc.get("commands", {})
        rows: list[dict[str, Any]] = []
        for name, meta in commands.items():
            if self._auth_hook is not None:
                decision = await self._invoke_auth_hook(
                    Request(command=name), method_lower="list"
                )
                if not decision.allow:
                    continue
            rows.append(
                {
                    "name": name,
                    "description": (meta.get("description") or "").split(".")[0] or "",
                }
            )
        rows.sort(key=lambda r: r["name"])
        return Response(id=request.id, ok=True, result=rows, error=None)

    async def _describe_command(self, request: Request) -> Response:
        """Return ``{name, parameters, output_schema}`` for one command.

        Slim by design — anyone scripting against the CLI needs to know "what
        flags do I pass" and "what comes back." Method / url_path /
        description / per-status response matrices are noise at that layer
        and live in the raw spec for the few cases they're needed.

        ``parameters`` is the unified input surface: query + path entries
        from OpenAPI ``parameters[]`` followed by the request body's
        top-level fields (each tagged ``in: "body"``). Empty / null per-
        parameter fields (``default``, ``choices``, ``is_list`` when false,
        etc.) are stripped so each entry shows only what's meaningful.

        ``output_schema`` is the success-response body schema, already
        dereferenced — for OpenBB Platform that's the ``OBBject[...]``
        wrapper with the concrete results model spliced in.

        When an auth hook is configured it gates the describe response too
        — RBAC implementations can deny schema introspection for
        unauthorized commands so the surface stays consistent with what
        the caller is allowed to actually invoke.
        """
        name = (request.params or {}).get("name")
        if not name:
            return Response(
                id=request.id,
                ok=False,
                error=ResponseError(
                    type="MissingParameter",
                    message="__schema__ requires --name=<command>",
                ),
            )
        cmd_spec = self._spec_doc.get("commands", {}).get(name)
        if cmd_spec is None:
            return Response(
                id=request.id,
                ok=False,
                error=ResponseError(
                    type="UnknownCommand",
                    message=(
                        f"command not in spec: {name!r}. "
                        "Use __commands__ to list available commands."
                    ),
                ),
            )
        if self._auth_hook is not None:
            decision = await self._invoke_auth_hook(
                Request(command=name), method_lower="schema"
            )
            if not decision.allow:
                return Response(
                    id=request.id,
                    ok=False,
                    error=ResponseError(
                        type="AccessDenied",
                        message=decision.deny_reason or "auth hook denied describe",
                    ),
                )
        body_params = _body_schema_to_params(cmd_spec.get("request_body_schema"))
        providers = cmd_spec.get("providers") or []
        if providers:
            # Optional ``provider`` param narrows the response to one
            # provider's slice — same shape a single-provider command
            # would return ({name, parameters, output_schema}). Lets
            # callers request just ``equity.price.quote:intrinio``
            # without scrolling past the other five providers.
            requested_provider = (request.params or {}).get("provider")
            grouped = _group_by_provider(
                cmd_spec.get("parameters") or [],
                body_params,
                providers,
                cmd_spec.get("response_schema"),
            )
            if requested_provider:
                slice_ = grouped.get(requested_provider)
                if slice_ is None:
                    return Response(
                        id=request.id,
                        ok=False,
                        error=ResponseError(
                            type="UnknownProvider",
                            message=(
                                f"provider {requested_provider!r} not declared "
                                f"by {name!r}. Available: "
                                f"{', '.join(sorted(grouped))}."
                            ),
                        ),
                    )
                return Response(
                    id=request.id,
                    ok=True,
                    result={
                        "name": name,
                        "provider": requested_provider,
                        **slice_,
                    },
                    error=None,
                )
            return Response(
                id=request.id,
                ok=True,
                result={"name": name, "providers": grouped},
                error=None,
            )
        params: list[dict[str, Any]] = [
            _slim_param(p) for p in (cmd_spec.get("parameters") or [])
        ]
        params.extend(body_params)
        return Response(
            id=request.id,
            ok=True,
            result={
                "name": name,
                "parameters": params,
                "output_schema": cmd_spec.get("response_schema"),
            },
            error=None,
        )

    def _client_context(self):
        """Yield an ``httpx.AsyncClient`` for one dispatch.

        Fresh client when we own ourselves (avoids cross-loop reuse from
        repeated ``asyncio.run`` calls in the REPL). Otherwise a no-op
        wrapper around the externally-managed client.
        """
        from contextlib import asynccontextmanager

        owns = self._owns_client
        client_ref = self._client
        timeout = self._timeout
        headers = self._headers or None

        @asynccontextmanager
        async def _ctx():
            if owns:
                async with httpx.AsyncClient(timeout=timeout, headers=headers) as c:
                    yield c
            else:
                yield client_ref

        return _ctx()

    async def aclose(self) -> None:
        """No-op.

        Owned clients are created and torn down per dispatch via
        ``_client_context``. Externally-supplied clients are owned by the
        caller and must be closed by them — closing them here would surprise
        callers that share a single client across multiple dispatchers.
        """
        return None


def http_dispatcher_from_spec(
    spec_doc: dict[str, Any],
    *,
    headers: dict[str, str] | None = None,
    query_params: dict[str, str] | None = None,
    auth_hook: AuthHook | None = None,
    namespace: str | None = None,
) -> HttpDispatcher:
    """Build an ``HttpDispatcher`` from a loaded ``.spec`` document.

    Pre-extracted methods + URL templates come straight from the spec — no
    network fetch. ``headers`` and ``query_params`` are sent on every
    dispatched request. ``auth_hook`` (when supplied) runs before each
    network dispatch and may inject extra headers / query params or deny
    the call outright; ``namespace`` is what the hook sees in
    ``AuthContext.namespace`` and lets a single shared hook tell which
    backend it was invoked for.
    """
    commands = spec_doc.get("commands", {})
    methods = {cmd: meta.get("method", "post") for cmd, meta in commands.items()}
    url_paths = {
        cmd: meta["url_path"] for cmd, meta in commands.items() if meta.get("url_path")
    }
    return HttpDispatcher(
        spec_doc["base_url"],
        api_prefix=spec_doc.get("api_prefix", "/api/v1"),
        command_methods=methods,
        command_url_paths=url_paths,
        headers=headers,
        query_params=query_params,
        spec_doc=spec_doc,
        auth_hook=auth_hook,
        namespace=namespace,
    )


def http_dispatcher_from_server(
    base_url: str,
    *,
    headers: dict[str, str] | None = None,
    query_params: dict[str, str] | None = None,
    auth_hook: AuthHook | None = None,
    namespace: str | None = None,
) -> HttpDispatcher:
    """Build an ``HttpDispatcher`` by fetching the server's OpenAPI document.

    Delegates to ``build_spec_document`` so the live-fetch path goes through
    the same spec normalization the ``--generate-spec`` path uses: HTML-
    embedded specs are auto-extracted, ``$ref`` parameters are resolved, the
    ``servers[0].url`` segment is prepended to the base URL (so
    ``--server https://api.congress.gov`` correctly hits ``/v3/...``), and
    api-prefix detection is applied. ``headers`` and ``query_params`` are
    sent on both the OpenAPI fetch and every dispatched request. The
    ``auth_hook`` only fires on dispatches — the initial OpenAPI fetch uses
    static auth so the spec discovery path stays predictable.
    """
    from openbb_cli.dispatchers.openapi_schema import fetch_openapi
    from openbb_cli.dispatchers.spec import build_spec_document

    openapi = fetch_openapi(base_url, headers=headers, query_params=query_params)
    spec_doc = build_spec_document(openapi, base_url=base_url)
    return http_dispatcher_from_spec(
        spec_doc,
        headers=headers,
        query_params=query_params,
        auth_hook=auth_hook,
        namespace=namespace,
    )
