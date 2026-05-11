"""Build CLI menu / parser structures from an OpenAPI 3.x schema.

Mirrors the surface of in-process ``obb`` reflection used by
``cli_controller._generate_platform_commands`` and ``PlatformControllerFactory``,
so the HTTP dispatcher path can offer the same REPL menu / argparse / completer
behavior without importing ``openbb`` locally.

This is the schema discovery layer only — it returns argparse parsers and a
router map. Wiring those into the existing controller machinery is a separate
step that lives in ``cli_controller`` once this layer is stable.

Supports both JSON and YAML specs. Handles three parameter locations:

* ``query`` — sent as URL query string on GET, JSON body on POST.
* ``path`` — substituted into the URL template (e.g. ``{operation}``) at
  dispatch time. Path params are always required.
* Other locations (``header``, ``cookie``, ``body``) are not currently
  surfaced; OpenBB Platform and NY Fed Markets API don't use them in the
  CLI surface.
"""

from __future__ import annotations

import argparse
import json
import re
from typing import Any

import httpx

PROVIDER_TAG_RE = re.compile(r"\s*\(provider:\s*([^)]+)\)\s*$")
PROVIDER_SECTION_SPLIT_RE = re.compile(r";\s*\n\s*")


def parse_provider_sections(text: str) -> tuple[set[str], bool]:
    r"""Split an OpenBB-merged help string and return ``(tagged_providers, has_untagged)``.

    OpenBB Platform concatenates per-provider help into one description.
    Sections are separated by ``;\\n    `` and each tagged with ``(provider:
    <comma-list>)`` — except sections shared across every provider, which
    have no tag. Returns the union of providers named in any tag and a
    boolean indicating whether at least one section was untagged (meaning
    the parameter applies to every provider, not just the tagged set).
    """
    tagged: set[str] = set()
    has_untagged = False
    for raw_section in PROVIDER_SECTION_SPLIT_RE.split(text):
        section = raw_section.strip()
        if not section:
            continue
        match = PROVIDER_TAG_RE.search(section)
        if match is None:
            has_untagged = True
            continue
        for p in match.group(1).split(","):
            name = p.strip().lower()
            if name:
                tagged.add(name)
    return tagged, has_untagged


def param_provider_membership(
    schema: dict[str, Any],
    description: str | None,
    providers_set: set[str],
) -> list[str]:
    """Return the providers a parameter belongs to, or ``[]`` if shared by all.

    Detection priority:

    1. Parse ``description`` for ``(provider: ...)`` tags. A section
       without any tag means the parameter is genuinely shared — return
       ``[]``. Otherwise return the union of tagged providers (intersected
       with the operation's declared provider list to avoid drift).
    2. Fall back to schema-level per-provider extension keys
       (``{"intrinio": {...}}``) for params whose description carries no
       sections.
    3. Last resort: schema ``title`` naming a single provider, used when
       the param is single-provider and lacks both per-provider keys and
       a tagged description.
    """
    providers_lower = {p.lower(): p for p in providers_set}
    if description:
        tagged, has_untagged = parse_provider_sections(description)
        if has_untagged:
            return []
        if tagged:
            return [providers_lower[t] for t in tagged if t in providers_lower]
    keys = [
        k
        for k, v in schema.items()
        if k in providers_set
        and k not in _OPENAPI_RESERVED_SCHEMA_KEYS
        and isinstance(v, dict)
    ]
    if keys:
        return keys
    title = schema.get("title")
    if isinstance(title, str) and title.lower() in providers_lower:
        return [providers_lower[title.lower()]]
    return []


_TYPE_MAP: dict[str, type] = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
}

_OPENAPI_RESERVED_SCHEMA_KEYS = frozenset(
    {
        "type",
        "format",
        "title",
        "description",
        "default",
        "enum",
        "const",
        "anyOf",
        "oneOf",
        "allOf",
        "items",
        "properties",
        "additionalProperties",
        "required",
        "nullable",
        "minimum",
        "maximum",
        "minLength",
        "maxLength",
        "pattern",
    }
)


def resolve_ref(spec: dict[str, Any], ref: str) -> dict[str, Any]:
    """Resolve a local OpenAPI ``$ref`` JSON pointer against ``spec``.

    Pointers like ``"#/components/parameters/foo"`` resolve to the
    referenced object. Only local document refs (``#/...``) are supported;
    external refs are left untouched and resolve to ``{}``.
    """
    if not ref.startswith("#/"):
        return {}
    node: Any = spec
    for raw_part in ref[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            return {}
        node = node[part]
    return node if isinstance(node, dict) else {}


def deref_parameter(spec: dict[str, Any], param: dict[str, Any]) -> dict[str, Any]:
    """Resolve a parameter that may be a ``$ref``.

    Congress.gov, for example, inlines every parameter as
    ``{"$ref": "#/components/parameters/limit"}``. Recurses in case the
    resolved object is itself a ``$ref``. Also resolves any ``$ref`` inside
    the parameter's ``schema``.
    """
    seen: set[str] = set()
    while "$ref" in param:
        ref = param["$ref"]
        if ref in seen:
            return {}
        seen.add(ref)
        param = resolve_ref(spec, ref) or {}
    schema = param.get("schema")
    if isinstance(schema, dict) and "$ref" in schema:
        param = {**param, "schema": resolve_ref(spec, schema["$ref"]) or schema}
    return param


def deref_schema(
    spec: dict[str, Any],
    node: Any,
    seen: frozenset[str] | None = None,
    max_depth: int = 32,
) -> Any:
    """Recursively expand every ``$ref`` inside an OpenAPI schema fragment.

    Cycle-safe (a self-referential schema like a tree node ``Comment`` whose
    ``children`` is ``[Comment, ...]`` would otherwise recurse forever) — when
    we re-enter a ``$ref`` already on the resolution stack, that branch is
    replaced by ``{"$ref": ref}`` so consumers can see the cycle without it
    blowing the stack. ``max_depth`` is a belt-and-braces cap.
    """
    if max_depth <= 0:
        return node
    if seen is None:
        seen = frozenset()
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str):
            if ref in seen:
                return {"$ref": ref}
            target = resolve_ref(spec, ref)
            if not target:
                return node
            return deref_schema(spec, target, seen | {ref}, max_depth - 1)
        return {k: deref_schema(spec, v, seen, max_depth - 1) for k, v in node.items()}
    if isinstance(node, list):
        return [deref_schema(spec, v, seen, max_depth - 1) for v in node]
    return node


_SUCCESS_PRIORITY = ("200", "2XX", "201", "default")
_JSON_CONTENT_TYPES = ("application/json", "application/vnd.api+json")


def _deref_response(spec: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    if "$ref" in response:
        return resolve_ref(spec, response["$ref"]) or {}
    return response


def extract_response_schema(
    spec: dict[str, Any], operation: dict[str, Any]
) -> dict[str, Any] | None:
    """Pull the primary success-response JSON schema for an operation.

    Convenience accessor returning a single schema for the common case —
    callers wanting the full ``{status: {content_type: schema}}`` matrix
    (multiple success codes, ``text/csv`` alongside JSON, etc.) should use
    ``extract_response_schemas`` instead. Tries ``200`` → ``2XX`` → ``201``
    → ``default`` and ``application/json`` → first content type within
    that response.
    """
    responses = operation.get("responses") or {}
    response: dict[str, Any] | None = None
    for key in _SUCCESS_PRIORITY:
        candidate = responses.get(key)
        if isinstance(candidate, dict):
            response = _deref_response(spec, candidate)
            break
    if response is None:
        for value in responses.values():
            if isinstance(value, dict):
                response = _deref_response(spec, value)
                break
    if response is None:
        return None
    content = response.get("content") or {}
    media: dict[str, Any] | None = None
    for ct in _JSON_CONTENT_TYPES:
        candidate = content.get(ct)
        if isinstance(candidate, dict):
            media = candidate
            break
    if media is None:
        for value in content.values():
            if isinstance(value, dict) and "schema" in value:
                media = value
                break
    if media is None:
        return None
    schema = media.get("schema")
    if not isinstance(schema, dict):
        return None
    return deref_schema(spec, schema)


def extract_request_body_schema(
    spec: dict[str, Any], operation: dict[str, Any]
) -> dict[str, Any] | None:
    """Pull the primary request-body JSON schema for an operation.

    POST/PUT endpoints — common across OpenBB Platform's econometrics /
    technical / quantitative / charting routes — declare their input shape
    here, NOT in ``parameters[]``. Without this, ``__schema__`` would only
    show the query-string subset and miss the actual body fields the user
    must POST. Tries ``application/json`` → first content type. Returns
    the fully-dereferenced schema dict, or ``None`` for body-less ops.
    """
    rb = operation.get("requestBody")
    if not isinstance(rb, dict):
        return None
    if "$ref" in rb:
        rb = resolve_ref(spec, rb["$ref"]) or {}
    content = rb.get("content") or {}
    media: dict[str, Any] | None = None
    for ct in _JSON_CONTENT_TYPES:
        candidate = content.get(ct)
        if isinstance(candidate, dict):
            media = candidate
            break
    if media is None:
        for value in content.values():
            if isinstance(value, dict) and "schema" in value:
                media = value
                break
    if media is None:
        return None
    schema = media.get("schema")
    if not isinstance(schema, dict):
        return None
    return deref_schema(spec, schema)


def extract_request_body_schemas(
    spec: dict[str, Any], operation: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    """Return the request-body schema per content type as ``{ct: schema}``.

    Mirrors ``extract_response_schemas`` for the request side — captures the
    full content-type matrix when an endpoint accepts both ``application/json``
    and (e.g.) ``application/x-www-form-urlencoded`` or ``multipart/form-data``.
    Each schema is fully dereferenced (cycle-safe).
    """
    out: dict[str, dict[str, Any]] = {}
    rb = operation.get("requestBody")
    if not isinstance(rb, dict):
        return out
    if "$ref" in rb:
        rb = resolve_ref(spec, rb["$ref"]) or {}
    content = rb.get("content") or {}
    for content_type, media in content.items():
        if not isinstance(media, dict):
            continue
        schema = media.get("schema")
        if isinstance(schema, dict):
            out[content_type] = deref_schema(spec, schema)
    return out


def extract_response_schemas(
    spec: dict[str, Any], operation: dict[str, Any]
) -> dict[str, dict[str, dict[str, Any]]]:
    """Return every response schema as ``{status_code: {content_type: schema}}``.

    Captures multi-status responses (``200``, ``400``, ``422``, ``default``)
    and multi-media responses (``application/json``, ``text/csv``, ...) so
    callers can introspect the full surface — which matters for servers like
    OpenBB Platform that publish CSV alongside JSON for the same endpoint
    and document distinct error shapes for ``422`` validation failures vs
    ``500`` server errors. Each schema is fully dereferenced (cycle-safe).
    """
    out: dict[str, dict[str, dict[str, Any]]] = {}
    responses = operation.get("responses") or {}
    for status, response in responses.items():
        if not isinstance(response, dict):
            continue
        deref_resp = _deref_response(spec, response)
        content = deref_resp.get("content") or {}
        per_content: dict[str, dict[str, Any]] = {}
        for content_type, media in content.items():
            if not isinstance(media, dict):
                continue
            schema = media.get("schema")
            if isinstance(schema, dict):
                per_content[content_type] = deref_schema(spec, schema)
        if per_content:
            out[status] = per_content
    return out


def _resolve_schema(schema: dict[str, Any]) -> tuple[type, list[Any], bool]:
    """Resolve an OpenAPI parameter schema to ``(py_type, choices, is_list)``.

    Optionals (``anyOf`` containing ``{"type": "null"}``) collapse to their
    non-null variant; multi-type unions fall back to ``str`` and union the
    enums (matching how ``ArgparseTranslator`` handles ``str | int`` etc.).
    """
    if "anyOf" in schema:
        non_null = [s for s in schema["anyOf"] if s.get("type") != "null"]
        if not non_null:
            return (str, [], False)
        if len(non_null) == 1:
            return _resolve_schema(non_null[0])
        choices: list[Any] = []
        is_list = False
        for s in non_null:
            if s.get("type") == "array":
                is_list = True
            for v in s.get("enum", []):
                if v not in choices:
                    choices.append(v)
        return (str, choices, is_list)

    if schema.get("type") == "array":
        items = schema.get("items", {}) or {}
        py_type, item_choices, _ = _resolve_schema(items)
        return (py_type, item_choices, True)

    if "const" in schema:
        return (type(schema["const"]), [schema["const"]], False)

    py_type = _TYPE_MAP.get(schema.get("type", "string"), str)
    return (py_type, list(schema.get("enum", [])), False)


def _provider_choices(schema: dict[str, Any]) -> list[Any]:
    """Union of per-provider ``choices`` lists found in OpenBB extension keys.

    OpenBB embeds per-provider metadata under non-OpenAPI-reserved keys, e.g.
    ``"fred": {"choices": [...]}``. When a parameter is shared across providers,
    we want the parser's ``choices`` to be the union of all providers' lists.
    """
    out: list[Any] = []
    for key, value in schema.items():
        if key in _OPENAPI_RESERVED_SCHEMA_KEYS:
            continue
        if isinstance(value, dict) and isinstance(value.get("choices"), list):
            for c in value["choices"]:
                if c not in out:
                    out.append(c)
    return out


def _escape_help(text: str | None) -> str | None:
    """Escape lone ``%`` so argparse's %-formatting validator accepts the help text."""
    if text is None:
        return None
    return text.replace("%", "%%")


def parameter_to_kwargs(param: dict[str, Any]) -> tuple[str, dict[str, Any]] | None:
    """Translate one OpenAPI parameter to ``(flag, add_argument kwargs)``.

    Returns ``None`` for parameters the CLI does not surface (e.g. ``chart``,
    which is handled by an output-adapter flag, not the command parser).
    """
    name = param.get("name")
    if not name or name == "chart":
        return None

    schema = param.get("schema", {}) or {}
    py_type, enum_choices, is_list = _resolve_schema(schema)
    provider_choices = _provider_choices(schema)
    choices: list[Any] = list(enum_choices)
    for c in provider_choices:
        if c not in choices:
            choices.append(c)

    kwargs: dict[str, Any] = {
        "dest": name,
        "help": _escape_help(param.get("description") or schema.get("description")),
    }

    if py_type is bool:
        kwargs.update(action="store_true", default=bool(schema.get("default", False)))
        return (f"--{name}", kwargs)

    kwargs["type"] = py_type
    if "default" in schema:
        kwargs["default"] = schema["default"]
    if choices:
        kwargs["choices"] = choices
    if is_list:
        kwargs["nargs"] = "+"
    if param.get("required") and "default" not in kwargs:
        kwargs["required"] = True

    return (f"--{name}", kwargs)


def build_parser_from_operation(op: dict[str, Any]) -> argparse.ArgumentParser:
    """Build an ``ArgumentParser`` from an OpenAPI operation object."""
    parser = argparse.ArgumentParser(
        prog=op.get("operationId", "cmd"),
        description=(op.get("description") or op.get("summary") or "").strip() or None,
        add_help=False,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    for param in op.get("parameters", []):
        translated = parameter_to_kwargs(param)
        if translated is None:
            continue
        flag, kwargs = translated
        try:
            parser.add_argument(flag, **kwargs)
        except argparse.ArgumentError:
            continue
    return parser


def _strip_placeholders(segment: str) -> str:
    """Remove ``{placeholder}`` substrings from a URL segment.

    ``latest.{format}`` → ``latest``, ``{operation}`` → ``""``,
    ``timeseries.csv`` → ``timeseries.csv`` (no placeholders, untouched).
    """
    out = segment
    while "{" in out and "}" in out:
        i = out.find("{")
        j = out.find("}", i)
        if j < 0:
            break
        out = out[:i] + out[j + 1 :]
    return out.strip(".")


def detect_api_prefix(spec: dict[str, Any]) -> str:
    """Compute the longest slash-segmented prefix shared by every path.

    Lets one ``--generate-spec`` invocation work against arbitrary OpenAPI
    servers — OpenBB Platform's ``/api/v1``, NY Fed's ``/api``, the empty
    prefix some specs use, etc. Falls back to ``/api/v1`` when the spec is
    empty or paths share no common segments.

    Each path's last segment is excluded from the comparison so the
    detected prefix never absorbs a leaf endpoint name.
    """
    paths = list(spec.get("paths", {}).keys())
    if not paths:
        return "/api/v1"
    parts_lists = [p.split("/")[:-1] for p in paths]
    common: list[str] = parts_lists[0]
    for parts in parts_lists[1:]:
        new_common: list[str] = []
        for a, b in zip(common, parts):
            if a == b:
                new_common.append(a)
            else:
                break
        common = new_common
        if not common:
            break
    prefix = "/".join(common).rstrip("/")
    return prefix or ""


def url_to_command(url: str, api_prefix: str = "/api/v1") -> str:
    """``/api/v1/commodity/price/spot`` → ``commodity.price.spot``.

    URL templates with ``{path_params}`` have those placeholders dropped,
    yielding a clean dotted command that the user types. Path params are
    surfaced as required CLI flags and substituted into the URL at dispatch
    time. Example: ``/api/ambs/{operation}/{status}/{include}/latest.{format}``
    → ``ambs.latest``.
    """
    prefix_parts = [p for p in api_prefix.strip("/").split("/") if p]
    parts = [p for p in url.strip("/").split("/") if p]
    if parts[: len(prefix_parts)] == prefix_parts:
        parts = parts[len(prefix_parts) :]
    cleaned = [_strip_placeholders(p) for p in parts]
    return ".".join(p for p in cleaned if p)


def build_command_index(
    spec: dict[str, Any], *, api_prefix: str = "/api/v1"
) -> dict[str, argparse.ArgumentParser]:
    """Map each ``paths`` entry in the spec to an ArgumentParser by dotted command."""
    index: dict[str, argparse.ArgumentParser] = {}
    for url, methods in spec.get("paths", {}).items():
        op = methods.get("get") or methods.get("post")
        if not op:
            continue
        index[url_to_command(url, api_prefix=api_prefix)] = build_parser_from_operation(
            op
        )
    return index


def build_router_map(
    spec: dict[str, Any], *, api_prefix: str = "/api/v1"
) -> dict[str, str]:
    """Classify every dotted path in ``spec`` as ``"menu"`` or ``"command"``.

    Mirrors ``cli_controller.PLATFORM_ROUTERS``. Every non-leaf prefix becomes
    a ``"menu"``; each leaf becomes a ``"command"``. ``commodity.price.spot``
    therefore yields ``commodity`` → menu, ``commodity.price`` → menu,
    ``commodity.price.spot`` → command.
    """
    out: dict[str, str] = {}
    for url, methods in spec.get("paths", {}).items():
        if not (methods.get("get") or methods.get("post")):
            continue
        cmd = url_to_command(url, api_prefix=api_prefix)
        if not cmd:
            continue
        parts = cmd.split(".")
        for i in range(1, len(parts)):
            out[".".join(parts[:i])] = "menu"
        out.setdefault(cmd, "command")
    return out


def build_reference(
    spec: dict[str, Any], *, api_prefix: str = "/api/v1"
) -> dict[str, Any]:
    """Mimic ``obb.reference`` — ``paths`` for commands, ``routers`` for menus.

    Keys are slash-style (``/equity/price/historical``, ``/equity/price/``)
    matching the in-process ``obb.reference`` layout that ``cli_controller``
    and ``base_platform_controller`` already index against.
    """
    prefix_parts = [p for p in api_prefix.strip("/").split("/") if p]
    tag_descriptions: dict[str, str] = {
        t["name"]: t.get("description", "")
        for t in spec.get("tags", [])
        if isinstance(t, dict) and t.get("name")
    }

    router_map = build_router_map(spec, api_prefix=api_prefix)

    paths_out: dict[str, dict[str, Any]] = {}
    routers_out: dict[str, dict[str, Any]] = {}
    for url, methods in spec.get("paths", {}).items():
        op = methods.get("get") or methods.get("post")
        if not op:
            continue
        parts = [p for p in url.strip("/").split("/") if p]
        if parts[: len(prefix_parts)] == prefix_parts:
            parts = parts[len(prefix_parts) :]
        non_template = [p for p in parts if not (p.startswith("{") and p.endswith("}"))]
        cli_path = "/" + "/".join(non_template)
        op_desc = (op.get("description") or op.get("summary") or "").strip()
        if cli_path not in paths_out or not paths_out[cli_path].get("description"):
            paths_out[cli_path] = {"description": op_desc}
        tags = op.get("tags") or []
        tag_desc = tag_descriptions.get(tags[0]) if tags else ""
        for i in range(1, len(non_template) + 1):
            dotted = ".".join(non_template[:i])
            if router_map.get(dotted) != "menu":
                continue
            menu_path = "/" + "/".join(non_template[:i]) + "/"
            if not routers_out.get(menu_path, {}).get("description"):
                routers_out[menu_path] = {"description": tag_desc or ""}
    return {"paths": paths_out, "routers": routers_out}


def _parse_spec_text(text: str, *, content_type: str = "") -> dict[str, Any]:
    """Parse a fetched spec body, choosing JSON or YAML by content sniff."""
    stripped = text.lstrip()
    if stripped.startswith(("{", "[")):
        return json.loads(text)
    if "yaml" in content_type or "yml" in content_type:
        return _yaml_load(text)
    if stripped[:8] in ("openapi:", "swagger:"):
        return _yaml_load(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return _yaml_load(text)


def _yaml_load(text: str) -> dict[str, Any]:
    """Parse a YAML document. ``pyyaml`` is a hard runtime dependency."""
    import yaml

    return yaml.safe_load(text)


_EMBEDDED_SPEC_MARKERS: tuple[str, ...] = (
    "var spec = ",
    "const spec = ",
    "let spec = ",
    "window.spec = ",
    '"spec":',
    "spec:",
)


def _find_matching_brace(text: str, start: int) -> int | None:
    """Return the index *after* the ``}`` that matches the ``{`` at ``start``.

    Skips braces inside double-quoted strings. Returns ``None`` if the brace
    is unbalanced.
    """
    if start >= len(text) or text[start] != "{":
        return None
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        c = text[i]
        if escape:
            escape = False
            continue
        if c == "\\":
            escape = True
            continue
        if c == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
    return None


def _extract_embedded_spec(html: str) -> dict[str, Any] | None:
    """Scan an HTML page for an embedded OpenAPI / Swagger spec.

    Many APIs (api.congress.gov, FastAPI's redoc, some Swagger UI bootstraps)
    don't expose a separate ``/openapi.json``: the spec is inlined into the
    landing page as a JS variable. Try several common markers, balanced-brace
    extract the JSON object, and verify it parses as an OpenAPI document.
    """
    for marker in _EMBEDDED_SPEC_MARKERS:
        idx = 0
        while True:
            i = html.find(marker, idx)
            if i < 0:
                break
            start = i + len(marker)
            while start < len(html) and html[start] in " \t\r\n":
                start += 1
            end = _find_matching_brace(html, start)
            if end is None:
                idx = i + 1
                continue
            try:
                obj = json.loads(html[start:end])
            except json.JSONDecodeError:
                idx = i + 1
                continue
            if isinstance(obj, dict) and ("openapi" in obj or "swagger" in obj):
                return obj
            idx = end
    return None


def fetch_openapi(
    base_url: str,
    *,
    timeout: float = 10.0,
    path: str | None = None,
    headers: dict[str, str] | None = None,
    query_params: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Fetch the OpenAPI spec at ``base_url`` and return the parsed dict.

    Resolution order:

    1. Explicit ``path`` (or default ``/openapi.json``). If it returns a
       parseable JSON/YAML body, use it.
    2. If the user did not pass ``path``, fall back to fetching the landing
       page at ``base_url`` and scraping for an embedded spec — many APIs
       (api.congress.gov, certain Swagger UI bootstraps) inline the spec as
       a JavaScript ``var spec = {...}`` variable instead of exposing a
       separate document.

    ``headers`` / ``query_params`` are sent on every fetch attempt — needed
    for servers that gate the spec itself behind auth (Congress.gov requires
    ``?api_key=...`` even on the landing page if scraped via the API host).
    """
    explicit_path = path is not None
    full_url = (
        path
        if path and (path.startswith("http://") or path.startswith("https://"))
        else f"{base_url.rstrip('/')}{path or '/openapi.json'}"
    )
    merged_headers = {"User-Agent": "openbb-cli/1.0"}
    if headers:
        merged_headers.update(headers)

    response = httpx.get(
        full_url,
        timeout=timeout,
        follow_redirects=True,
        headers=merged_headers,
        params=query_params or None,
    )
    if response.status_code < 400:
        try:
            return _parse_spec_text(
                response.text,
                content_type=response.headers.get("content-type", ""),
            )
        except (json.JSONDecodeError, ValueError):
            pass

    if explicit_path:
        response.raise_for_status()
        return _parse_spec_text(
            response.text,
            content_type=response.headers.get("content-type", ""),
        )

    landing_url = base_url.rstrip("/") + "/"
    landing = httpx.get(
        landing_url,
        timeout=timeout,
        follow_redirects=True,
        headers=merged_headers,
        params=query_params or None,
    )
    landing.raise_for_status()
    embedded = _extract_embedded_spec(landing.text)
    if embedded is not None:
        return embedded

    response.raise_for_status()
    return _parse_spec_text(
        response.text,
        content_type=response.headers.get("content-type", ""),
    )
