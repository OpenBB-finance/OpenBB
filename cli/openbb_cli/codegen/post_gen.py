"""Generate free-form router modules for POST endpoints with request bodies.

OpenBB POST commands are emitted with the same pattern the platform's
own econometrics / quantitative routers use: a regular ``async def``
body that takes Pydantic-typed body params and scalar query params, and
makes the upstream HTTP call inline. The provider-backed
``@router.command(model=...)`` machinery doesn't apply here because
FastAPI would otherwise treat ``data: list[BodyData]`` as a query
parameter and reject it.

Each generated module exposes:

* A ``<Cmd>BodyItem`` Pydantic class (from ``request_body_schema.properties``
  array-element shape) — the row type for ``data: list[<Cmd>BodyItem]``.
* A ``<Cmd>Data`` Pydantic class (from ``response_schema``) — the row
  type for the ``OBBject[list[<Cmd>Data]]`` return.
* A ``<cmd_name>`` async function decorated with
  ``@router.command(methods=["POST"])`` that the router module imports
  and re-exports.
"""

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
    safe_field_name,
)


@dataclass
class PostCommandSpec:
    """Per-command inputs for a POST router emitter.

    Parameters
    ----------
    name : str
        Dotted command path from the spec.
    cmd_spec : dict
        The command's spec entry — ``url_path``, ``parameters``,
        ``request_body_schema``, ``response_schema``, ``description``.
    base_url : str
        Upstream API root, no trailing slash.
    api_prefix : str
        Path prefix shared across every command in the spec.
    provider_name : str
        Snake-case provider identifier; drives credential lookup keys.
    """

    name: str
    cmd_spec: dict[str, Any]
    base_url: str
    api_prefix: str
    provider_name: str


@dataclass
class GeneratedPostCommand:
    """Output of ``generate_post_command_module``.

    Parameters
    ----------
    module_name : str
        Snake-case module filename (without ``.py``) — the function name
        is the same identifier.
    function_name : str
        The router function name (e.g. ``"econometrics_ols_regression"``).
    body_class : str, optional
        Name of the emitted body element class, if a body is present.
    data_class : str
        Name of the emitted response-row class.
    source : str
        Full module source ready to write to disk.
    credentials_used : dict
        Same shape as ``GeneratedFetcher.credentials_used`` — drives
        provider credential registration.
    """

    module_name: str
    function_name: str
    data_class: str
    source: str
    body_class: str | None = None
    credentials_used: dict[str, dict[str, str]] = field(default_factory=dict)


_PATH_TEMPLATE_RE = re.compile(r"\{([^}]+)\}")


def _module_name_from_command(name: str) -> str:
    """Convert a dotted command path to a snake_case module identifier."""
    safe = re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_")
    if not safe:
        safe = "command"
    if safe[0].isdigit():
        safe = f"_{safe}"
    return safe.lower()


def _path_template_keys(url_path: str) -> list[str]:
    """Extract ``{placeholder}`` names from a URL template, in declaration order."""
    return [m.group(1) for m in _PATH_TEMPLATE_RE.finditer(url_path)]


def _resolve_url_path(api_prefix: str, url_path: str) -> str:
    """Combine api_prefix with url_path; the prefix is dropped if already present."""
    prefix = ("/" + api_prefix.strip("/")) if api_prefix.strip("/") else ""
    path = url_path if url_path.startswith("/") else "/" + url_path
    if prefix and path.startswith(prefix + "/"):
        return path
    if prefix:
        return prefix + path if not path.startswith(prefix) else path
    return path


def _python_type_from_param(param: dict[str, Any]) -> str:
    """Render a Python type annotation for a normalized parameter entry.

    Parameters
    ----------
    param : dict
        Spec parameter entry with ``type`` / ``is_list`` / ``choices``.

    Returns
    -------
    str
        Annotation text suitable for the generated function signature.
    """
    base_type = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
    }.get(param.get("type", "string"), "str")
    if param.get("choices"):
        rendered = ", ".join(repr(c) for c in param["choices"])
        base_type = f"Literal[{rendered}]"
    if param.get("is_list"):
        return f"list[{base_type}]"
    return base_type


def _array_item_class(
    body_schema: dict[str, Any],
    *,
    parent_class_name: str,
) -> tuple[str | None, GeneratedClass | None, str | None]:
    """Detect a body's array-of-objects field and emit its item class.

    Two body shapes get the array-item treatment:

    * ``{type: "object", properties: {data: {type: "array", items: {...}}}}``
      — the standard "wrapped" body where ``data`` is one named field.
    * ``{type: "array", items: {...}}`` — the body is the array itself,
      with no enclosing object. The function signature uses ``data`` as
      the parameter name to match OpenBB convention.

    Parameters
    ----------
    body_schema : dict
        The request_body_schema.
    parent_class_name : str
        Camel-case base for the generated item class name.

    Returns
    -------
    tuple
        ``(field_name, item_class, type_annotation)``. ``(None, None,
        None)`` when no array-of-objects body is present.
    """
    # Top-level array body: ``request body IS the array`` (no wrapper).
    if body_schema.get("type") == "array":
        items = body_schema.get("items")
        if isinstance(items, dict):
            item_class_name = class_name_from(parent_class_name, "BodyItem")
            # ``Data`` (with ``additionalProperties: true``) is the OpenBB
            # standardized open-row base. Subclassing it means callers can
            # pass any other endpoint's result rows in unchanged — Pydantic
            # accepts subclass instances of an open ``Data`` parent.
            item_class = generate_class(
                items,
                class_name=item_class_name,
                base_class="Data",
                docstring=f"Body item for {parent_class_name}.",
            )
            return ("data", item_class, f"list[{item_class_name}]")
        return (None, None, None)

    # Object body with one or more array-of-objects fields.
    properties = body_schema.get("properties") or {}
    for name, schema in properties.items():
        if not isinstance(schema, dict):
            continue
        if schema.get("type") != "array":
            continue
        items = schema.get("items")
        if not isinstance(items, dict):
            continue
        if items.get("type") != "object" and "properties" not in items:
            continue
        item_class_name = class_name_from(parent_class_name, "BodyItem")
        item_class = generate_class(
            items,
            class_name=item_class_name,
            base_class="Data",
            docstring=f"Body item for {parent_class_name}.",
        )
        return (name, item_class, f"list[{item_class_name}]")
    return (None, None, None)


def _data_schema(cmd_spec: dict[str, Any]) -> dict[str, Any]:
    """Pull the per-row data schema out of a response_schema (same logic as fetcher_gen)."""
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
    typed: dict[str, Any],  # noqa: ARG001 — kept for symmetry with caller signature
    props: dict[str, Any],
) -> dict[str, Any] | None:
    """Resolve the inner row schema when ``typed`` is a recognized envelope.

    Returns ``None`` when the schema isn't an envelope (i.e. it IS the row,
    OR the would-be inner schema is too malformed to descend into safely).
    Mirrors ``unpack_response``: pure single-property wrappers descend, and
    multi-property objects with exactly one array property treat the
    array's items as the row shape.
    """
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
    """Render the credential extraction block for the POST router body.

    Parameters
    ----------
    creds : dict
        Mapping from canonical credential names to ``{name, in}`` info.
    provider_name : str
        Snake-case provider name; used as the credentials-attribute prefix.

    Returns
    -------
    list of str
        Indented lines that pull each credential off
        ``cc.user_settings.credentials`` into ``_cred_<canonical>`` locals.
    """
    if not creds:
        return []
    lines: list[str] = ["    _user_creds = cc.user_settings.credentials"]
    for canonical in sorted(creds):
        var = f"_cred_{canonical}"
        attr = f"{provider_name}_{canonical}"
        lines.append(f'    {var} = (getattr(_user_creds, "{attr}", "") or "")')
    return lines


def _signature_params(
    cmd_spec: dict[str, Any],
    array_field: str | None,
    array_annotation: str | None,
    has_credentials: bool,
) -> list[tuple[str, str, str | None, bool, Any]]:
    """Build the function parameter list (name, annotation, description, required, default).

    Parameters
    ----------
    cmd_spec : dict
        Spec command entry.
    array_field : str, optional
        Name of the body's array-of-objects field (e.g. ``"data"``).
    array_annotation : str, optional
        The Python annotation for that field (e.g. ``"list[OlsBodyItem]"``).
    has_credentials : bool
        Whether the command needs credentials — when ``True`` a
        ``cc: CommandContext`` parameter is prepended so the generated
        body can read ``cc.user_settings.credentials``.

    Returns
    -------
    list of tuple
        Per-parameter tuples in declaration order — required first, then
        optional. ``cc`` (when present) always comes first.
    """
    out: list[tuple[str, str, str | None, bool, Any]] = []
    if has_credentials:
        out.append(
            (
                "cc",
                "CommandContext",
                "Provides access to user-configured credentials.",
                True,
                None,
            )
        )
    if array_field and array_annotation:
        out.append((array_field, array_annotation, "Body data rows.", True, None))
    body_props = (cmd_spec.get("request_body_schema") or {}).get("properties") or {}
    body_required = set(
        (cmd_spec.get("request_body_schema") or {}).get("required") or []
    )
    for name, schema in body_props.items():
        if name == array_field:
            continue
        if not isinstance(schema, dict):
            continue
        ann = _python_type_from_param(
            {
                "type": schema.get("type"),
                "is_list": schema.get("type") == "array",
                "choices": schema.get("enum"),
            }
        )
        out.append(
            (
                name,
                ann,
                schema.get("description") or schema.get("title"),
                name in body_required,
                schema.get("default"),
            )
        )
    for raw in filter_user_params(cmd_spec.get("parameters") or []):
        name = raw.get("name")
        if not name:
            continue
        ann = _python_type_from_param(raw)
        out.append(
            (
                name,
                ann,
                raw.get("help"),
                bool(raw.get("required")),
                raw.get("default"),
            )
        )
    # Stable sort: cc first, then required, then optional.
    out.sort(key=lambda entry: (0 if entry[0] == "cc" else 1, 0 if entry[3] else 1))
    return out


def _render_signature(
    func_name: str,
    params: list[tuple[str, str, str | None, bool, Any]],
    return_annotation: str,
) -> str:
    """Render ``async def func_name(...) -> return_annotation:`` lines.

    Parameters
    ----------
    func_name : str
        Generated function identifier.
    params : list of tuple
        Output of ``_signature_params``.
    return_annotation : str
        The return type annotation text.

    Returns
    -------
    str
        Multi-line signature ready for the function body to follow.
    """
    if not params:
        return f"async def {func_name}() -> {return_annotation}:"
    lines = [f"async def {func_name}("]
    for name, annotation, _, required, default in params:
        if required:
            lines.append(f"    {name}: {annotation},")
        else:
            default_repr = render_default(default)
            lines.append(f"    {name}: {annotation} = {default_repr},")
    lines.append(f") -> {return_annotation}:")
    return "\n".join(lines)


def render_default(default: Any) -> str:
    """Render a Python literal for a default value.

    Parameters
    ----------
    default : Any
        The literal default — primitives and lists/dicts pass through repr.

    Returns
    -------
    str
        The literal text usable on the right-hand side of ``= default``.
    """
    if default is None:
        return "None"
    if isinstance(default, bool):
        return "True" if default else "False"
    return repr(default)


def generate_post_command_module(spec: PostCommandSpec) -> GeneratedPostCommand:
    """Render a POST command module for one spec command.

    Parameters
    ----------
    spec : PostCommandSpec
        Per-command inputs (see ``PostCommandSpec``).

    Returns
    -------
    GeneratedPostCommand
        The emitted module source plus metadata the package builder
        needs to register the command in the router.
    """
    module_name = _module_name_from_command(spec.name)
    base_class_name = class_name_from(spec.name)
    function_name = module_name
    data_class = f"{base_class_name}Data"

    # 1) Body item class (when the body declares ``data: list[<obj>]``).
    body_field, body_item_class, body_annotation = _array_item_class(
        spec.cmd_spec.get("request_body_schema") or {},
        parent_class_name=base_class_name,
    )

    # 2) Response data class.
    data_schema = _data_schema(spec.cmd_spec) or {"type": "object"}
    data_generated = generate_class(
        data_schema,
        class_name=data_class,
        base_class="BaseModel",
        docstring=f"Response row for {spec.name}.",
    )

    # 3) Credentials: same as fetcher_gen so POST endpoints honor the
    #    provider's registered credentials registry.
    creds = credentials_from_command(spec.cmd_spec)
    cred_lines = _credential_lookup_lines(creds, spec.provider_name)

    # 4) Function signature: cc first (when creds), body-array, then scalar query.
    params = _signature_params(
        spec.cmd_spec, body_field, body_annotation, has_credentials=bool(creds)
    )
    return_annotation = f"OBBject[list[{data_class}]]"
    signature = _render_signature(function_name, params, return_annotation)

    # 5) Function body: build URL, body payload, headers; call amake_request.
    path_params = _path_template_keys(spec.cmd_spec.get("url_path") or "")
    full_url_path = _resolve_url_path(
        spec.api_prefix, spec.cmd_spec.get("url_path") or ""
    )
    body_block = _render_body_block(
        cmd_spec=spec.cmd_spec,
        body_field=body_field,
        creds=creds,
        path_params=path_params,
        url_path_template=full_url_path,
        base_url=spec.base_url.rstrip("/"),
        cred_lines=cred_lines,
        data_class=data_class,
        params=params,
    )

    # 6) Imports. The module exposes the function bare — no
    #    ``Router(...)`` instance and no ``@router.command`` decoration —
    #    so the main router module can import it and decorate it once.
    imports = {
        "import json as _json",
        "from typing import Any",
        "from openbb_core.app.model.abstract.error import OpenBBError",
        "from openbb_core.app.model.obbject import OBBject",
        "from openbb_core.provider.abstract.data import Data",
        "from openbb_core.provider.utils.helpers import "
        "get_async_requests_session, get_querystring",
        "from pydantic import BaseModel, Field",
        "from ....utils import unpack_response",
    }
    if creds:
        imports.add("from openbb_core.app.model.command_context import CommandContext")
    imports.update(data_generated.collect_imports())
    if body_item_class:
        imports.update(body_item_class.collect_imports())
    if any(p[1].startswith("Literal[") for p in params):
        imports.add("from typing import Literal")

    sorted_imports = consolidate_imports(imports)

    # 7) Assemble the module source.
    description = (spec.cmd_spec.get("description") or f"POST {spec.name}.").strip()
    summary = description.split("\n", 1)[0]
    parts: list[str] = [
        f'"""POST router function for {spec.name} — generated from spec.\n\n'
        f"Hits ``{spec.base_url.rstrip('/')}{full_url_path}`` via HTTP POST.\n"
        f'"""',
        "",
    ]
    stdlib = [
        i
        for i in sorted_imports
        if i.startswith(
            ("from typing", "from datetime", "import typing", "import datetime")
        )
    ]
    third_party = [i for i in sorted_imports if i not in stdlib]
    if stdlib:
        parts.extend(stdlib)
        parts.append("")
    if third_party:
        parts.extend(third_party)
        parts.append("")
    parts.append("")

    if body_item_class:
        for cls in body_item_class.flatten():
            parts.append(cls.source)
    for cls in data_generated.flatten():
        parts.append(cls.source)

    # Summary-only docstring built from the spec's actual description —
    # OpenBB's ``DocstringGenerator`` injects the Parameters / Returns
    # blocks at static-stub-build time, so we don't repeat them here.
    cleaned_summary = (description or summary).strip()
    if not cleaned_summary:
        cleaned_summary = summary
    if not cleaned_summary.endswith((".", "!", "?")):
        cleaned_summary += "."
    if "\n" in cleaned_summary:
        first, _, rest = cleaned_summary.partition("\n")
        rest_indented = "\n".join(
            f"    {line}" if line.strip() else "" for line in rest.split("\n")
        )
        func_doc = f'    """{first}\n\n{rest_indented}\n    """'
    else:
        func_doc = f'    """{cleaned_summary}"""'
    parts.append(f"{signature}\n{func_doc}\n{body_block}\n")

    return GeneratedPostCommand(
        module_name=module_name,
        function_name=function_name,
        body_class=body_item_class.name if body_item_class else None,
        data_class=data_class,
        source="\n".join(parts).rstrip() + "\n",
        credentials_used=creds,
    )


def _render_body_block(
    *,
    cmd_spec: dict[str, Any],
    body_field: str | None,
    creds: dict[str, dict[str, str]],
    path_params: list[str],
    url_path_template: str,
    base_url: str,
    cred_lines: list[str],
    data_class: str,
    params: list[tuple[str, str, str | None, bool, Any]],
) -> str:
    """Render the function body for a POST command.

    Parameters
    ----------
    cmd_spec : dict
        The spec command entry.
    body_field : str, optional
        Name of the array-of-objects body field, if any.
    creds : dict
        Credential entries from ``credentials_from_command``.
    path_params : list of str
        URL-template placeholders to substitute.
    url_path_template : str
        URL path with placeholders intact.
    base_url : str
        Upstream API root, no trailing slash.
    cred_lines : list of str
        Credential-extraction source lines.
    data_class : str
        Name of the response Data class — used to construct the OBBject.
    params : list of tuple
        Function parameters (used to build query/body payload).

    Returns
    -------
    str
        Full function body (every line indented by four spaces).
    """
    body_props = (cmd_spec.get("request_body_schema") or {}).get("properties") or {}
    body_field_names = list(body_props)
    query_field_names = [
        n for n, _, _, _, _ in params if n != "cc" and n not in body_field_names
    ]

    lines: list[str] = []
    lines.extend(cred_lines)

    if path_params:
        sub_args = ", ".join(f"{p}={p}" for p in path_params)
        lines.append(f"    _path = {url_path_template!r}.format({sub_args})")
    else:
        lines.append(f"    _path = {url_path_template!r}")

    # Query string from non-body, non-path params + query credentials
    lines.append("    _query_dict: dict[str, Any] = {}")
    for name in query_field_names:
        if name in path_params:
            continue
        lines.append(f"    if {name} is not None:")
        lines.append(f"        _query_dict[{name!r}] = {name}")
    for canonical, info in creds.items():
        if info["in"] != "query":
            continue
        wire_name = info["name"]
        var = f"_cred_{canonical}"
        lines.append(f"    if {var}:")
        lines.append(f"        _query_dict[{wire_name!r}] = {var}")
    lines.append("    _query_string = get_querystring(_query_dict, [])")
    lines.append(
        f'    _url = f"{base_url}{{_path}}" + ("?" + _query_string if _query_string else "")'
    )

    # Headers
    lines.append("    _headers: dict[str, str] = {}")
    for canonical, info in creds.items():
        if info["in"] != "header":
            continue
        wire_name = info["name"]
        var = f"_cred_{canonical}"
        lines.append(f"    if {var}:")
        lines.append(f"        _headers[{wire_name!r}] = {var}")

    # Body payload. Top-level array bodies serialize the array directly;
    # object bodies wrap each named field into a dict.
    body_top_is_array = (cmd_spec.get("request_body_schema") or {}).get(
        "type"
    ) == "array"
    if body_top_is_array and body_field:
        safe = safe_field_name(body_field)[0]
        lines.append(
            "    _body: list[dict[str, Any]] = "
            f'[_item.model_dump(mode="json") for _item in {safe}]'
        )
    else:
        body_entries: list[str] = []
        for name in body_field_names:
            safe = safe_field_name(name)[0]
            if name == body_field:
                body_entries.append(
                    f'        {name!r}: [_item.model_dump(mode="json") for _item in {safe}],'
                )
            else:
                body_entries.append(f"        {name!r}: {safe},")
        if body_entries:
            body_lines = "\n".join(body_entries)
            lines.append(f"    _body: dict[str, Any] = {{\n{body_lines}\n    }}")
        else:
            lines.append("    _body: dict[str, Any] = {}")

    lines.append("    _rows: list[dict[str, Any]] = []")
    lines.append("    _metadata: dict[str, Any] = {}")
    lines.append("    async with await get_async_requests_session() as _session:")
    lines.append(
        "        async with await _session.request("
        '"POST", _url, headers=_headers, json=_body) as _resp:'
    )
    lines.append("            _ct = (_resp.headers.get('Content-Type') or '').lower()")
    lines.append("            _text = await _resp.text()")
    lines.append("            if _resp.status >= 400:")
    lines.append(
        "                raise OpenBBError("
        "f'HTTP {_resp.status} from {_url}: {_text[:500]}')"
    )
    lines.append(
        "            if 'json' in _ct or _text.lstrip().startswith(('{', '[')):"
    )
    lines.append("                try:")
    lines.append("                    _payload = _json.loads(_text)")
    lines.append("                except ValueError as _exc:")
    lines.append(
        "                    raise OpenBBError("
        "f'Upstream {_url} returned malformed JSON: {_exc}') from _exc"
    )
    lines.append("                _rows, _metadata = unpack_response(_payload)")
    lines.append("            else:")
    lines.append("                _rows = [{'content': _text, 'content_type': _ct}]")
    lines.append(f"    _typed = [{data_class}(**row) for row in _rows]")
    lines.append("    if _metadata:")
    lines.append(
        '        return OBBject(results=_typed, extra={"results_metadata": _metadata})'
    )
    lines.append("    return OBBject(results=_typed)")
    return "\n".join(lines)
