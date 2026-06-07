"""Generate ``QueryParams`` + ``Data`` + ``Fetcher`` modules for one spec command."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, cast

from openbb_cli.codegen.credentials import (
    credentials_from_command,
    filter_user_params,
)
from openbb_cli.codegen.pydantic_gen import (
    GeneratedClass,
    class_name_from,
    consolidate_imports,
    generate_class,
    render_function_docstring,
    safe_field_name,
)

_PATH_TEMPLATE_RE = re.compile(r"\{([^}]+)\}")


@dataclass
class FetcherCommandSpec:
    """Per-command inputs to the fetcher emitter.

    Parameters
    ----------
    name : str
        Dotted command path as it appears in ``spec_doc["commands"]``.
    cmd_spec : dict
        The spec entry.
    base_url : str
        The upstream API root.
    api_prefix : str
        Path prefix shared across every command in the spec.
    provider_name : str
        Snake-case provider name.
    """

    name: str
    cmd_spec: dict[str, Any]
    base_url: str
    api_prefix: str
    provider_name: str


@dataclass
class GeneratedFetcher:
    """The output of ``generate_fetcher_module``.

    Parameters
    ----------
    module_name : str
        Snake-case module filename (without ``.py``).
    model_name : str
        The Pydantic model name registered in the provider's ``fetcher_dict``.
    query_params_class : str
        Name of the emitted ``QueryParams`` subclass.
    data_class : str
        Name of the emitted ``Data`` subclass.
    fetcher_class : str
        Name of the emitted ``Fetcher`` subclass.
    source : str
        Full module source ready to write to disk.
    credentials_used : dict
        ``{canonical_name: {"name": wire_name, "in": "query"|"header"}}``.
    """

    module_name: str
    model_name: str
    query_params_class: str
    data_class: str
    fetcher_class: str
    source: str
    credentials_used: dict[str, dict[str, str]] = field(default_factory=dict)
    is_streaming: bool = False


def _command_is_streaming(cmd_spec: dict[str, Any]) -> bool:
    """Return whether a command's success response is a stream.

    Parameters
    ----------
    cmd_spec : dict
        The spec command entry.

    Returns
    -------
    bool
        True when a 2xx response advertises ``text/event-stream``.
    """
    for status, content in (cmd_spec.get("response_schemas") or {}).items():
        if (
            str(status).startswith("2")
            and isinstance(content, dict)
            and any("event-stream" in str(ct) for ct in content)
        ):
            return True
    return False


def _module_name_from_command(name: str) -> str:
    """Convert a dotted command path to a snake_case module identifier.

    Parameters
    ----------
    name : str
        Dotted command path.

    Returns
    -------
    str
        Snake-case identifier.
    """
    safe = re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_")
    if not safe:
        safe = "command"
    if safe[0].isdigit():
        safe = f"_{safe}"
    return safe.lower()


def _path_template_keys(url_path: str) -> list[str]:
    """Extract ``{placeholder}`` names from a URL template, in declaration order."""
    return [m.group(1) for m in _PATH_TEMPLATE_RE.finditer(url_path)]


def _query_params_schema(
    cmd_spec: dict[str, Any], provider_name: str
) -> dict[str, Any]:
    """Build a JSON-schema dict combining query, path, and body fields.

    Parameters
    ----------
    cmd_spec : dict
        The spec command entry.
    provider_name : str
        Provider this fetcher is being generated for.

    Returns
    -------
    dict
        A synthetic ``{"type": "object", "properties": {...}, "required": [...]}``.
    """
    properties: dict[str, Any] = {}
    required: list[str] = []
    for raw in filter_user_params(cmd_spec.get("parameters") or []):
        name = raw.get("name")
        if not name:
            continue
        if name == "provider":
            continue
        param_providers = raw.get("providers") or []
        if param_providers and provider_name not in param_providers:
            continue
        description = raw.get("help") or raw.get("description")
        if description:
            description = re.sub(r"\s*\(provider:[^)]*\)\s*$", "", description).strip()
        prop_schema: dict[str, Any] = {}
        for key in ("type", "default", "choices"):
            if key in raw and raw[key] is not None:
                prop_schema[key] = raw[key]
        if raw.get("in") == "path" and prop_schema.get("type") == "number":
            prop_schema["type"] = "integer"
        if description:
            prop_schema["description"] = description
        if raw.get("is_list"):
            inner = {"type": prop_schema.get("type", "string")}
            prop_schema = {"type": "array", "items": inner}
            if description:
                prop_schema["description"] = description
        if raw.get("choices"):
            prop_schema["enum"] = list(raw["choices"])
        properties[name] = prop_schema
        if raw.get("required"):
            required.append(name)
    body_schema = cmd_spec.get("request_body_schema") or {}
    body_props = body_schema.get("properties") or {}
    body_required = body_schema.get("required") or []
    for body_name, body_prop in body_props.items():
        if body_name not in properties:
            properties[body_name] = body_prop
            if body_name in body_required:
                required.append(body_name)
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def _column_metadata_from_data_schema(
    data_schema: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Pull per-column ``description`` / ``socrata_format`` out of the row schema."""
    properties = (data_schema or {}).get("properties") or {}
    out: dict[str, dict[str, Any]] = {}
    for field_name, schema in properties.items():
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
            out[field_name] = meta
    return out


def _data_schema(cmd_spec: dict[str, Any]) -> dict[str, Any]:
    """Pull the per-row data schema out of a response_schema.

    Parameters
    ----------
    cmd_spec : dict
        The spec command entry.

    Returns
    -------
    dict
        The schema that should drive the ``Data`` Pydantic class.
    """
    response = cmd_spec.get("response_schema") or {}
    if not isinstance(response, dict):
        return {}
    properties = response.get("properties") or {}
    results = properties.get("results")
    if isinstance(results, dict):
        non_null = [
            v
            for v in results.get("anyOf") or [results]
            if isinstance(v, dict) and v.get("type") != "null"
        ]
        if non_null:
            inner = non_null[0]
            if inner.get("type") == "array" and isinstance(inner.get("items"), dict):
                inner = inner["items"]
            if isinstance(inner.get("oneOf"), list):
                concrete = [c for c in inner["oneOf"] if isinstance(c, dict)]
                if concrete:
                    inner = concrete[0]
            return inner
    return _unwrap_schema_envelopes(response)


def _unwrap_schema_envelopes(schema: Any) -> dict[str, Any]:
    """Strip schema envelopes that ``unpack_response`` strips at runtime."""
    if not isinstance(schema, dict):
        return {}
    typed: dict[str, Any] = schema
    if typed.get("type") == "array":
        return _unwrap_schema_envelopes(typed.get("items"))
    combinator_target = _first_non_null_combinator_variant(typed)
    if combinator_target is not None:
        return _unwrap_schema_envelopes(combinator_target)
    if _is_scalar_schema(typed):
        return _wrap_scalar_as_value(typed)
    props = typed.get("properties")
    if not isinstance(props, dict) or not props:
        return typed
    inner = _envelope_inner_schema(typed, props)
    if inner is not None:
        return _unwrap_schema_envelopes(inner)
    return typed


def _first_non_null_combinator_variant(schema: dict[str, Any]) -> dict[str, Any] | None:
    """Return the first non-null variant of a top-level ``oneOf`` / ``anyOf``."""
    for combinator in ("oneOf", "anyOf"):
        variants = schema.get(combinator)
        if not isinstance(variants, list):
            continue
        for variant in variants:
            if isinstance(variant, dict) and variant.get("type") != "null":
                return cast(dict[str, Any], variant)
    return None


def _envelope_inner_schema(
    typed: dict[str, Any],  # noqa: ARG001
    props: dict[str, Any],
) -> dict[str, Any] | None:
    """Resolve the inner row schema when ``typed`` is a recognized envelope."""
    if len(props) == 1:
        only_value = next(iter(props.values()))
        if isinstance(only_value, dict):
            only_dict = cast(dict[str, Any], only_value)
            if only_dict.get("type") == "array":
                items = only_dict.get("items")
                return cast(dict[str, Any], items) if isinstance(items, dict) else None
            if (
                only_dict.get("properties")
                or only_dict.get("oneOf")
                or only_dict.get("anyOf")
            ):
                return only_dict
    array_keys = [
        k for k, v in props.items() if isinstance(v, dict) and v.get("type") == "array"
    ]
    if len(array_keys) == 1:
        items = props[array_keys[0]].get("items")
        if isinstance(items, dict):
            return cast(dict[str, Any], items)
    return None


def _is_scalar_schema(schema: dict[str, Any]) -> bool:
    """Return True when the schema represents a primitive (string/number/etc.)."""
    return schema.get("type") in {
        "string",
        "integer",
        "number",
        "boolean",
    } and not schema.get("properties")


def _wrap_scalar_as_value(schema: dict[str, Any]) -> dict[str, Any]:
    """Promote a scalar schema to ``{type: object, properties: {value: scalar}}``."""
    return {
        "type": "object",
        "properties": {"value": schema},
        "required": ["value"],
    }


def _credential_lookup_lines(
    creds: dict[str, dict[str, str]], provider_name: str
) -> list[str]:
    """Render ``api_key = creds.get("<provider>_api_key", "")`` lines.

    Parameters
    ----------
    creds : dict
        Mapping returned by ``credentials_from_command``.
    provider_name : str
        Snake-case provider name used as the key prefix.

    Returns
    -------
    list of str
        One assignment per credential, in canonical-name order.
    """
    lines: list[str] = []
    for canonical in sorted(creds):
        var = f"_cred_{canonical}"
        full_key = f"{provider_name}_{canonical}"
        lines.append(f'        {var} = _creds.get("{full_key}", "")')
    return lines


def _query_dict_construction(
    cmd_spec: dict[str, Any],
    creds: dict[str, dict[str, str]],
    path_params: list[str],
    provider_name: str,
) -> str:
    """Compose the ``query_dict = {...}`` block emitted in ``aextract_data``.

    Parameters
    ----------
    cmd_spec : dict
        The spec command entry.
    creds : dict
        Credential entries.
    path_params : list of str
        URL-template placeholders.

    Returns
    -------
    str
        The Python source for the ``query_dict`` assignment.
    """
    body_props = (cmd_spec.get("request_body_schema") or {}).get("properties") or {}
    excluded = set(path_params) | set(body_props)
    range_params = [
        p
        for p in (cmd_spec.get("parameters") or [])
        if isinstance(p, dict) and p.get("_socrata_op") in {"date_min", "date_max"}
    ]
    excluded.update(p["name"] for p in range_params)
    if excluded:
        excluded_literal = (
            "{" + ", ".join(repr(name) for name in sorted(excluded)) + "}"
        )
        dump = (
            f"        _query_dict = query.model_dump("
            f"by_alias=True, exclude={excluded_literal}, exclude_none=True)"
        )
    else:
        dump = (
            "        _query_dict = query.model_dump(by_alias=True, exclude_none=True)"
        )
    lines = [dump]
    declares_provider = any(
        isinstance(p, dict) and p.get("name") == "provider"
        for p in (cmd_spec.get("parameters") or [])
    )
    if declares_provider:
        lines.append(f'        _query_dict["provider"] = {provider_name!r}')
    for canonical, info in creds.items():
        if info["in"] != "query":
            continue
        var = f"_cred_{canonical}"
        wire_name = info["name"]
        lines.append(f"        if {var}:")
        lines.append(f"            _query_dict[{wire_name!r}] = {var}")
    if range_params:
        lines.extend(_socrata_where_clause_lines(range_params))
        date_column = next(
            (p["_socrata_column"] for p in range_params if p.get("_socrata_column")),
            None,
        )
        if date_column:
            lines.append(
                f"        _query_dict.setdefault('$order', {date_column!r} + ' DESC')"
            )
    rename_pairs: list[tuple[str, str]] = []
    for param in cmd_spec.get("parameters") or []:
        if not isinstance(param, dict):
            continue
        wire_name = param.get("wire_name")
        if wire_name and wire_name != param.get("name"):
            rename_pairs.append((param["name"], wire_name))
    if rename_pairs:
        lines.append("        for _src, _dst in (")
        for src, dst in rename_pairs:
            lines.append(f"            ({src!r}, {dst!r}),")
        lines.append("        ):")
        lines.append("            if _src in _query_dict:")
        lines.append("                _query_dict[_dst] = _query_dict.pop(_src)")
    return "\n".join(lines)


def _socrata_where_clause_lines(range_params: list[dict[str, Any]]) -> list[str]:
    """Compose runtime lines that fold Socrata range params into ``$where``."""
    field_lookups: list[str] = []
    for param in range_params:
        wire_name = param["name"]
        column = param["_socrata_column"]
        op = ">=" if param["_socrata_op"] == "date_min" else "<="
        py_field, _ = safe_field_name(wire_name)
        var = f"_range_{py_field}"
        field_lookups.append(
            f"        {var} = getattr(query, {py_field!r}, None)\n"
            f"        if {var} is not None:\n"
            f"            _socrata_where_parts.append("
            f'f"{column} {op} \'" + str({var}) + "\'")'
        )
    out: list[str] = ["        _socrata_where_parts: list[str] = []"]
    out.extend(field_lookups)
    out.append("        if _socrata_where_parts:")
    out.append("            _existing_where = _query_dict.pop('$where', None)")
    out.append("            _socrata_where = ' AND '.join(_socrata_where_parts)")
    out.append("            if _existing_where:")
    out.append(
        "                _socrata_where = f'({_existing_where}) AND ({_socrata_where})'"
    )
    out.append("            _query_dict['$where'] = _socrata_where")
    return out


def _header_dict_construction(creds: dict[str, dict[str, str]]) -> str:
    """Compose the ``_headers = {...}`` block for credential headers.

    Parameters
    ----------
    creds : dict
        Credential entries.

    Returns
    -------
    str
        Python source for the headers dict.
    """
    lines = ["        _headers: dict[str, str] = {}"]
    for canonical, info in creds.items():
        if info["in"] != "header":
            continue
        var = f"_cred_{canonical}"
        wire_name = info["name"]
        lines.append(f"        if {var}:")
        lines.append(f"            _headers[{wire_name!r}] = {var}")
    return "\n".join(lines)


def _resolve_url_path(api_prefix: str, url_path: str) -> str:
    """Combine api_prefix with url_path; the prefix is dropped if already present."""
    prefix = ("/" + api_prefix.strip("/")) if api_prefix.strip("/") else ""
    path = url_path if url_path.startswith("/") else "/" + url_path
    if prefix and path.startswith(prefix + "/"):
        return path
    if prefix:
        return prefix + path if not path.startswith(prefix) else path
    return path


def generate_fetcher_module(spec: FetcherCommandSpec) -> GeneratedFetcher:
    """Render the full three-class fetcher module for one spec command.

    Parameters
    ----------
    spec : FetcherCommandSpec
        The command-level inputs (see ``FetcherCommandSpec``).

    Returns
    -------
    GeneratedFetcher
        The emitted source plus metadata the package builder needs to
        register the fetcher in the provider's ``fetcher_dict``.
    """
    module_name = _module_name_from_command(spec.name)
    model_name = class_name_from(spec.name)
    qp_class = f"{model_name}QueryParams"
    data_class = f"{model_name}Data"
    fetcher_class = f"{model_name}Fetcher"

    qp_schema = _query_params_schema(spec.cmd_spec, spec.provider_name)
    data_schema = _data_schema(spec.cmd_spec) or {"type": "object"}

    qp_generated = generate_class(
        qp_schema,
        class_name=qp_class,
        base_class="QueryParams",
        docstring=f"Query parameters for {spec.name}.",
    )
    data_generated = generate_class(
        data_schema,
        class_name=data_class,
        base_class="Data",
        docstring=f"Response row for {spec.name}.",
    )

    creds = credentials_from_command(spec.cmd_spec)
    path_params = _path_template_keys(spec.cmd_spec.get("url_path") or "")

    imports = {
        "from typing import Any",
        "from openbb_core.app.model.abstract.error import OpenBBError",
        "from openbb_core.provider.abstract.annotated_result import AnnotatedResult",
        "from openbb_core.provider.abstract.data import Data",
        "from openbb_core.provider.abstract.fetcher import Fetcher",
        "from openbb_core.provider.abstract.query_params import QueryParams",
        "from openbb_core.provider.utils.helpers import "
        "get_async_requests_session, get_querystring",
        "from pydantic import BaseModel, Field",
        "from ....utils import safe_json_loads, unpack_response",
    }
    imports.update(qp_generated.collect_imports())
    imports.update(data_generated.collect_imports())

    method = (spec.cmd_spec.get("method") or "get").lower()
    full_url_path = _resolve_url_path(
        spec.api_prefix, spec.cmd_spec.get("url_path") or ""
    )
    base_url = spec.base_url.rstrip("/")
    description = (spec.cmd_spec.get("description") or f"Fetch {spec.name}.").strip()

    cred_lines = _credential_lookup_lines(creds, spec.provider_name)
    query_block = _query_dict_construction(
        spec.cmd_spec, creds, path_params, spec.provider_name
    )
    header_block = _header_dict_construction(creds)

    if _command_is_streaming(spec.cmd_spec):
        source = _render_streaming_fetcher_source(
            spec=spec,
            qp_class=qp_class,
            qp_classes=qp_generated.flatten(),
            data_class=data_class,
            fetcher_class=fetcher_class,
            method=method,
            url_path_template=full_url_path,
            base_url=base_url,
            cred_lines=cred_lines,
            query_block=query_block,
            header_block=header_block,
            description=description,
        )
        return GeneratedFetcher(
            module_name=module_name,
            model_name=model_name,
            query_params_class=qp_class,
            data_class=data_class,
            fetcher_class=fetcher_class,
            source=source,
            credentials_used=creds,
            is_streaming=True,
        )

    source = _render_fetcher_source(
        spec=spec,
        qp_class=qp_class,
        qp_classes=qp_generated.flatten(),
        data_class=data_class,
        data_classes=data_generated.flatten(),
        fetcher_class=fetcher_class,
        model_name=model_name,
        method=method,
        url_path_template=full_url_path,
        base_url=base_url,
        path_params=path_params,
        cred_lines=cred_lines,
        query_block=query_block,
        header_block=header_block,
        creds=creds,
        description=description,
        imports=consolidate_imports(imports),
        column_metadata=_column_metadata_from_data_schema(data_schema),
    )

    return GeneratedFetcher(
        module_name=module_name,
        model_name=model_name,
        query_params_class=qp_class,
        data_class=data_class,
        fetcher_class=fetcher_class,
        source=source,
        credentials_used=creds,
    )


def _render_streaming_fetcher_source(
    *,
    spec: FetcherCommandSpec,
    qp_class: str,
    qp_classes: list[GeneratedClass],
    data_class: str,
    fetcher_class: str,
    method: str,
    url_path_template: str,
    base_url: str,
    cred_lines: list[str],
    query_block: str,
    header_block: str,
    description: str,
) -> str:
    """Format a streaming fetcher module source.

    Parameters
    ----------
    spec : FetcherCommandSpec
        Original command input.
    qp_class : str
        Query parameters class name.
    qp_classes : list of GeneratedClass
        Pre-flattened query parameter classes.
    data_class : str
        Streamed row class name.
    fetcher_class : str
        Fetcher class name.
    method : str
        HTTP verb.
    url_path_template : str
        URL path with placeholders intact.
    base_url : str
        Upstream API root, no trailing slash.
    cred_lines : list of str
        Credential-extraction source lines.
    query_block : str
        Pre-rendered query-dict source.
    header_block : str
        Pre-rendered headers-dict source.
    description : str
        First paragraph of the spec command's description.

    Returns
    -------
    str
        The full streaming fetcher module source.
    """
    transform_query_doc = render_function_docstring(
        "Validate raw input into typed query parameters.",
        parameters=[("params", "dict[str, Any]", "Raw user input.")],
        returns=(qp_class, "Validated query parameters."),
        indent="        ",
    )
    aextract_doc = render_function_docstring(
        f"Open the stream at {base_url}{url_path_template}.",
        parameters=[
            ("query", qp_class, "Validated query parameters."),
            ("credentials", "dict | None", "Provider credentials."),
            ("**kwargs", "Any", "Forwarded by the provider runtime."),
        ],
        returns=("AsyncIterator[str]", "Async iterator of raw stream lines."),
        indent="        ",
    )
    stream_data_doc = render_function_docstring(
        f"Type each stream line as {data_class}.",
        parameters=[
            ("query", qp_class, "Validated query parameters."),
            ("data", "Any", "Async iterator of raw stream lines."),
            ("**kwargs", "Any", "Forwarded by the provider runtime."),
        ],
        returns=(f"AsyncIterator[{data_class}]", "Async iterator of typed rows."),
        indent="        ",
    )

    parts: list[str] = []
    parts.append(f'"""Streaming fetcher for {spec.name} — generated from spec."""')
    parts.append("")
    parts.append("from collections.abc import AsyncIterator")
    parts.append("from typing import Any")
    parts.append("")
    parts.append("import httpx")
    parts.append("")
    parts.append("from openbb_core.provider.abstract.data import Data")
    parts.append("from openbb_core.provider.abstract.fetcher import Fetcher")
    parts.append("from openbb_core.provider.abstract.query_params import QueryParams")
    parts.append("from openbb_core.provider.utils.helpers import get_querystring")
    parts.append("")
    parts.append("")
    for cls in qp_classes:
        parts.append(cls.source)
    parts.append(f"class {data_class}(Data):")
    parts.append(f'    """Streamed row for {spec.name}."""')
    parts.append("")
    parts.append("    data: str")
    parts.append("")
    parts.append("")
    parts.append(
        f"class {fetcher_class}(Fetcher[{qp_class}, AsyncIterator[{data_class}]]):"
    )
    parts.append(f'    """Streaming fetcher for {spec.name}."""')
    parts.append("")
    parts.append("    @staticmethod")
    parts.append(f"    def transform_query(params: dict) -> {qp_class}:")
    parts.append(transform_query_doc)
    parts.append(f"        return {qp_class}(**params)")
    parts.append("")
    parts.append("    @staticmethod")
    parts.append(
        f"    async def aextract_data(query: {qp_class}, "
        "credentials: dict | None, **kwargs) -> AsyncIterator[str]:"
    )
    parts.append(aextract_doc)
    parts.extend(cred_lines)
    parts.append(query_block)
    parts.append("        _query_string = get_querystring(_query_dict, [])")
    parts.append(
        f'        _url = f"{base_url}{url_path_template}"'
        ' + ("?" + _query_string if _query_string else "")'
    )
    parts.append(header_block)
    parts.append("")
    parts.append("        async def _stream() -> AsyncIterator[str]:")
    parts.append(
        "            async with httpx.AsyncClient(timeout=None) as _client:  # noqa: S113"
    )
    parts.append(
        f'                async with _client.stream("{method.upper()}", '
        "_url, headers=_headers) as _resp:"
    )
    parts.append("                    _resp.raise_for_status()")
    parts.append("                    async for _line in _resp.aiter_lines():")
    parts.append("                        if _line:")
    parts.append("                            yield _line")
    parts.append("")
    parts.append("        return _stream()")
    parts.append("")
    parts.append("    @staticmethod")
    parts.append(
        f"    async def stream_data(query: {qp_class}, data: Any, **kwargs)"
        f" -> AsyncIterator[{data_class}]:"
    )
    parts.append(stream_data_doc)
    parts.append("        async for _line in data:")
    parts.append(f"            yield {data_class}(data=_line)")
    return "\n".join(parts).rstrip() + "\n"


def _render_fetcher_source(
    *,
    spec: FetcherCommandSpec,
    qp_class: str,
    qp_classes: list[GeneratedClass],
    data_class: str,
    data_classes: list[GeneratedClass],
    fetcher_class: str,
    model_name: str,
    method: str,
    url_path_template: str,
    base_url: str,
    path_params: list[str],
    cred_lines: list[str],
    query_block: str,
    header_block: str,
    creds: dict[str, dict[str, str]],
    description: str,
    imports: list[str],
    column_metadata: dict[str, dict[str, Any]] | None = None,
) -> str:
    """Format the final fetcher module source.

    Parameters
    ----------
    spec : FetcherCommandSpec
        Original command input.
    qp_class, data_class, fetcher_class : str
        Class names emitted in the module.
    qp_classes, data_classes : list of GeneratedClass
        Pre-flattened lists of emitted classes.
    model_name : str
        The Pydantic model key referenced by ``@router.command(model=...)``.
    method : str
        HTTP verb.
    url_path_template : str
        URL path with placeholders intact.
    base_url : str
        Upstream API root, no trailing slash.
    path_params : list of str
        Names of placeholders in ``url_path_template``.
    cred_lines : list of str
        Credential-extraction source lines.
    query_block, header_block : str
        Pre-rendered query-dict and headers-dict source.
    creds : dict
        Credential entries.
    description : str
        First paragraph of the spec command's description.
    imports : list of str
        All imports the module needs, already sorted.

    Returns
    -------
    str
        The full module source text.
    """
    stdlib_imports = [
        i
        for i in imports
        if i.startswith(
            ("from typing", "from datetime", "import typing", "import datetime")
        )
    ]
    third_party_imports = [i for i in imports if i not in stdlib_imports]

    parts: list[str] = []
    parts.append(
        f'"""Fetcher for {spec.name} — generated from spec.\n\n'
        f"Hits ``{base_url}{url_path_template}`` via HTTP "
        f'{method.upper()}.\n"""'
    )
    parts.append("")
    if stdlib_imports:
        parts.extend(stdlib_imports)
        parts.append("")
    if third_party_imports:
        parts.extend(third_party_imports)
        parts.append("")
    parts.append("")

    for cls in qp_classes:
        parts.append(cls.source)
    for cls in data_classes:
        parts.append(cls.source)

    fetcher_doc = render_function_docstring(
        description.split("\n", 1)[0],
    )

    transform_query_doc = render_function_docstring(
        "Validate raw input into typed query parameters.",
        parameters=[
            ("params", "dict[str, Any]", "Raw user input (CLI flags / API body)."),
        ],
        returns=(qp_class, "Validated query parameters."),
        indent="        ",
    )

    aextract_doc_params: list[tuple[str, str, str | None]] = [
        ("query", qp_class, "Validated query parameters."),
        (
            "credentials",
            "dict[str, str] | None",
            "Provider credentials registered on the ``Provider`` instance.",
        ),
        ("**kwargs", "Any", "Forwarded by the provider runtime; unused."),
    ]
    aextract_doc = render_function_docstring(
        f"Fetch from {base_url}{url_path_template} and split rows from metadata.",
        parameters=aextract_doc_params,
        returns=(
            "dict[str, Any]",
            (
                "``{'rows': [...], 'metadata': {...}}`` — single-element list "
                "and single-key envelope wrappers are stripped at the response "
                "boundary, scalar fields beside the data array become metadata."
            ),
        ),
        indent="        ",
    )

    transform_data_doc = render_function_docstring(
        f"Type the unpacked rows as {data_class}; surface metadata via AnnotatedResult.",
        parameters=[
            ("query", qp_class, "The validated query (unused but provided)."),
            ("data", "dict[str, Any]", "Output of ``aextract_data``."),
            ("**kwargs", "Any", "Forwarded by the provider runtime; unused."),
        ],
        returns=(
            f"list[{data_class}] | AnnotatedResult[list[{data_class}]]",
            (
                "Typed rows; wrapped in ``AnnotatedResult`` when the response "
                "carried metadata alongside the data array."
            ),
        ),
        indent="        ",
    )

    has_path_params = bool(path_params)
    has_query_creds = any(info["in"] == "query" for info in creds.values())

    body_construction = _aextract_body(
        method=method,
        base_url=base_url,
        url_path_template=url_path_template,
        path_params=path_params,
        cred_lines=cred_lines,
        query_block=query_block,
        header_block=header_block,
        body_field_names=list(
            (spec.cmd_spec.get("request_body_schema") or {}).get("properties") or {}
        ),
        has_path_params=has_path_params,
        has_query_creds=has_query_creds,
    )

    fetcher_source_lines = [
        f"class {fetcher_class}(Fetcher[{qp_class}, list[{data_class}]]):",
        fetcher_doc,
        "",
        "    @staticmethod",
        f"    def transform_query(params: dict[str, Any]) -> {qp_class}:",
        transform_query_doc,
        f"        return {qp_class}(**params)",
        "",
        "    @staticmethod",
        "    async def aextract_data(",
        f"        query: {qp_class},",
        "        credentials: dict[str, str] | None,",
        "        **kwargs: Any,",
        "    ) -> dict[str, Any]:",
        aextract_doc,
        "        _creds = credentials or {}",
    ]
    fetcher_source_lines.extend(body_construction)
    column_meta_literal = repr(column_metadata) if column_metadata else None
    transform_data_lines = [
        "",
        "    @staticmethod",
        "    def transform_data(",
        f"        query: {qp_class},",
        "        data: dict[str, Any],",
        "        **kwargs: Any,",
        f"    ) -> list[{data_class}] | AnnotatedResult[list[{data_class}]]:",
        transform_data_doc,
        f"        _typed = [{data_class}(**row) for row in data['rows']]",
        "        _metadata = dict(data.get('metadata') or {})",
    ]
    if column_meta_literal:
        transform_data_lines.append(f"        _column_metadata = {column_meta_literal}")
        transform_data_lines.append(
            "        _metadata.setdefault('columns', _column_metadata)"
        )
    transform_data_lines.extend(
        [
            "        if _metadata:",
            "            return AnnotatedResult(result=_typed, metadata=_metadata)",
            "        return _typed",
            "",
        ]
    )
    fetcher_source_lines.extend(transform_data_lines)
    parts.append("\n".join(fetcher_source_lines))

    return "\n".join(parts).rstrip() + "\n"


def _aextract_body(
    *,
    method: str,
    base_url: str,
    url_path_template: str,
    path_params: list[str],
    cred_lines: list[str],
    query_block: str,
    header_block: str,
    body_field_names: list[str],
    has_path_params: bool,
    has_query_creds: bool,
) -> list[str]:
    """Render the body of ``aextract_data`` as a list of source lines.

    Parameters
    ----------
    method : str
        ``"get"`` or ``"post"``.
    base_url : str
        Upstream API root, no trailing slash.
    url_path_template : str
        URL path with ``{placeholder}`` substitutions intact.
    path_params : list of str
        Placeholder names in ``url_path_template``.
    cred_lines : list of str
        Credential-extraction source lines.
    query_block : str
        Pre-rendered query-dict construction block.
    header_block : str
        Pre-rendered headers-dict construction block.
    body_field_names : list of str
        Names of fields that should travel in the JSON request body.
    has_path_params : bool
        Whether the URL has placeholders to substitute.
    has_query_creds : bool
        Whether any credential lives in the query string.

    Returns
    -------
    list of str
        Indented lines forming the body of ``aextract_data``.
    """
    lines: list[str] = list(cred_lines)
    if has_path_params:
        sub_args = ", ".join(f"{p}=getattr(query, {p!r})" for p in path_params)
        lines.append(f"        _path = {url_path_template!r}.format({sub_args})")
    else:
        lines.append(f"        _path = {url_path_template!r}")
    lines.append("")
    lines.append(query_block)
    lines.append("        _query_string = get_querystring(_query_dict, [])")
    lines.append(
        f'        _url = f"{base_url}{{_path}}" + ("?" + _query_string if _query_string else "")'
    )
    lines.append("")
    lines.append(header_block)
    lines.append("")
    if method == "post":
        body_literal = (
            "{"
            + ", ".join(
                f"{name!r}: getattr(query, {safe_field_name(name)[0]!r}, None)"
                for name in body_field_names
            )
            + "}"
        )
        lines.append(f"        _body = {body_literal}")
        lines.append('        _method = "POST"')
        lines.append('        _request_kwargs: dict[str, Any] = {"json": _body}')
    else:
        lines.append('        _method = "GET"')
        lines.append("        _request_kwargs: dict[str, Any] = {}")
    lines.append("        async with await get_async_requests_session() as _session:")
    lines.append(
        "            async with await _session.request("
        "_method, _url, headers=_headers, **_request_kwargs) as _resp:"
    )
    lines.append(
        "                _ct = (_resp.headers.get('Content-Type') or '').lower()"
    )
    lines.append("                _text = await _resp.text()")
    lines.append("                if _resp.status >= 400:")
    lines.append(
        "                    raise OpenBBError("
        "f'HTTP {_resp.status} from {_url}: {_text[:500]}')"
    )
    lines.append(
        "                if 'json' in _ct or _text.lstrip().startswith(('{', '[')):"
    )
    lines.append("                    try:")
    lines.append("                        _payload = safe_json_loads(_text)")
    lines.append("                    except ValueError as _exc:")
    lines.append(
        "                        raise OpenBBError("
        "f'Upstream {_url} returned malformed JSON: {_exc}') from _exc"
    )
    lines.append("                else:")
    lines.append(
        "                    return {'rows': [{'content': _text, "
        "'content_type': _ct}], 'metadata': {}}"
    )
    lines.append("        _rows, _metadata = unpack_response(_payload)")
    lines.append("        return {'rows': _rows, 'metadata': _metadata}")
    return lines
