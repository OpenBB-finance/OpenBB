"""Pre-computed spec format for instant one-shot CLI startup.

The OpenAPI schema describes 280+ endpoints in 2+ MB of JSON. Parsing it on
every CLI invocation costs ~50ms even before the HTTP roundtrip. A ``.spec``
file is a normalized, denormalized snapshot of just the bits the CLI consumes:

* Per-command URL + method + parameter list (already digested types/choices).
* Router/menu classification.
* Reference descriptions for help text.

Loading a spec is a single ``json.loads`` and dictionary lookup — no schema
walk, no ``anyOf`` resolution, no provider-extension scanning. Generate once
when the server's surface changes, ship the file alongside whatever invokes
the CLI, and one-shot dispatches become near-instant.

Usage::

    openbb --generate-spec --server http://api:6900 -o cli.spec
    openbb --spec cli.spec equity.price.historical --symbol AAPL
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from importlib.metadata import (
    PackageNotFoundError,
    version as _pkg_version,
)
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from openbb_cli.dispatchers.openapi_schema import (
    _escape_help,
    _provider_choices,
    _resolve_schema,
    build_reference,
    build_router_map,
    deref_parameter,
    detect_api_prefix,
    extract_request_body_schema,
    extract_request_body_schemas,
    extract_response_schema,
    extract_response_schemas,
    param_provider_membership,
    url_to_command,
)

SPEC_VERSION = 5


_TYPE_TO_NAME: dict[type, str] = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
}
_NAME_TO_TYPE: dict[str, type] = {v: k for k, v in _TYPE_TO_NAME.items()}


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z?$")


def _coerce_iso_datetime(value: str) -> str:
    """Expand short date forms to RFC-3339 timestamps the upstream API expects.

    ``2025-01-01`` → ``2025-01-01T00:00:00Z``. Already-full timestamps get a
    trailing ``Z`` if missing. Anything else passes through unchanged so the
    upstream's own validator surfaces the error.
    """
    if _DATE_RE.match(value):
        return f"{value}T00:00:00Z"
    if _DATETIME_RE.match(value) and not value.endswith("Z"):
        return value + "Z"
    return value


def _looks_like_datetime_param(name: str, help_text: str | None) -> bool:
    """Heuristic: parameter is a datetime if name or help points at one.

    Matches names ending in ``DateTime``/``Datetime``/``_datetime`` (Congress
    uses ``fromDateTime``/``toDateTime``) and help text containing ``timestamp``
    or ``YYYY-MM-DD``.
    """
    n = name.lower()
    if n.endswith("datetime") or "_datetime" in n:
        return True
    return bool(
        help_text
        and ("timestamp" in help_text.lower() or "yyyy-mm-dd" in help_text.lower())
    )


def _operation_providers(op: dict[str, Any]) -> list[str]:
    """Return the OpenBB provider list for an operation, ordered as declared.

    OpenBB Platform encodes the discriminator as a ``provider`` parameter
    whose schema is either:

    * ``enum: [provider1, provider2, ...]`` — multi-provider endpoints
    * ``const: "providerX"`` — single-provider endpoints

    Other OpenAPI servers don't have this concept; they yield ``[]`` and
    the rest of the spec build / describe path falls back to the flat
    shape.
    """
    for raw in op.get("parameters", []) or []:
        if not isinstance(raw, dict):
            continue
        if raw.get("name") != "provider":
            continue
        schema = raw.get("schema") or {}
        enum = schema.get("enum")
        if isinstance(enum, list):
            return [str(e) for e in enum]
        const = schema.get("const")
        if const is not None:
            return [str(const)]
    return []


def _normalize_parameter(
    param: dict[str, Any], providers_set: set[str] | None = None
) -> dict[str, Any] | None:
    """Translate one OpenAPI parameter into the spec-file parameter form.

    Returns ``None`` for parameters the CLI does not surface (e.g. ``chart``).
    Records the ``in`` location (``query`` / ``path`` / ``header``) so the
    dispatcher knows whether to substitute the value into the URL template
    or send it as a query / body parameter. When ``providers_set`` is
    supplied (multi-provider OpenBB endpoint), records which providers each
    parameter belongs to so ``--describe`` can group them.
    """
    name = param.get("name")
    if not name or name == "chart":
        return None

    location = param.get("in", "query")
    schema = param.get("schema", {}) or {}
    py_type, enum_choices, is_list = _resolve_schema(schema)
    choices: list[Any] = list(enum_choices)
    for c in _provider_choices(schema):
        if c not in choices:
            choices.append(c)

    required = bool(param.get("required")) or location == "path"
    default = schema.get("default")
    lower_choices = {str(c).lower() for c in choices}
    if "json" in lower_choices and "xml" in lower_choices:
        default = "json"
    if default is not None:
        required = False

    description = param.get("description") or schema.get("description")
    providers: list[str] = (
        param_provider_membership(schema, description, providers_set)
        if providers_set and name != "provider"
        else []
    )

    # Capture the parameter's example value from either the OpenAPI 3.x
    # ``example``/``examples`` slots on the parameter object or its schema.
    # This is the strongest signal that a value will produce real data
    # against the live API — spec authors curate it specifically so docs
    # and Swagger UI render against a working call.
    example: Any = param.get("example")
    if example is None:
        examples_map = param.get("examples") or {}
        if isinstance(examples_map, dict):
            for entry in examples_map.values():
                if isinstance(entry, dict) and "value" in entry:
                    example = entry["value"]
                    break
    if example is None:
        example = schema.get("example")

    type_name = _TYPE_TO_NAME.get(py_type, "string")
    # Path parameters typed ``number`` in OpenAPI almost always carry whole
    # numbers (counts, IDs, "last N"). Without this promotion, ``--number 10``
    # gets type-cast to ``10.0`` (float) and the URL becomes
    # ``.../last/10.0.json`` which the API rejects.
    if location == "path" and type_name == "number":
        type_name = "integer"

    return {
        "name": name,
        "in": location,
        "type": type_name,
        "is_list": is_list,
        "required": required,
        "default": default,
        "choices": choices,
        "example": example,
        "help": param.get("description") or schema.get("description"),
        "providers": providers,
    }


def build_command_spec(
    spec: dict[str, Any], *, api_prefix: str = "/api/v1"
) -> dict[str, dict[str, Any]]:
    """Return ``{dotted_command: {url_path, method, description, parameters[]}}``.

    The output is the per-command portion of the on-disk spec file — already
    digested into argparse-ready primitives. Collisions (multiple URLs that
    strip to the same dotted name after dropping ``{path_params}``) are
    disambiguated by appending ``_2``, ``_3``, … in URL-iteration order.
    """
    out: dict[str, dict[str, Any]] = {}
    for url, methods in spec.get("paths", {}).items():
        method: str | None
        op: dict[str, Any] | None
        if "get" in methods:
            method, op = "get", methods["get"]
        elif "post" in methods:
            method, op = "post", methods["post"]
        else:
            continue
        base_cmd = url_to_command(url, api_prefix=api_prefix)
        if not base_cmd:
            continue
        cmd = base_cmd
        suffix = 2
        while cmd in out:
            cmd = f"{base_cmd}_{suffix}"
            suffix += 1
        providers = _operation_providers(op)
        providers_set = set(providers) if providers else None
        params: list[dict[str, Any]] = []
        for raw in op.get("parameters", []) or []:
            resolved = deref_parameter(spec, raw) if isinstance(raw, dict) else raw
            if not resolved:
                continue
            normalized = _normalize_parameter(resolved, providers_set)
            if normalized is not None:
                params.append(normalized)
        out[cmd] = {
            "url_path": url,
            "method": method,
            "description": (op.get("description") or op.get("summary") or "").strip(),
            "parameters": params,
            "providers": providers,
            "request_body_schema": extract_request_body_schema(spec, op),
            "request_body_schemas": extract_request_body_schemas(spec, op),
            "response_schema": extract_response_schema(spec, op),
            "response_schemas": extract_response_schemas(spec, op),
        }
    return out


def _resolve_base_url(openapi: dict[str, Any], user_base_url: str) -> str:
    """Honor the OpenAPI ``servers[0].url`` when it adds a path component.

    Many specs declare ``servers: [{"url": "https://api.example.com/v3"}]`` or
    ``servers: [{"url": "/v3"}]`` (Congress.gov). The user typically passes
    only the host (``--server https://api.congress.gov``) — without merging
    the server entry, every dispatch hits ``/bill`` instead of ``/v3/bill``.
    Strategy:

    * Absolute server URL (starts with ``http``) wins outright when the
      user only supplied a host with no path component.
    * Relative server URL (``/v3``) is appended to the user's base URL.
    * If the user already supplied the path themselves, leave it alone.
    """
    user_clean = user_base_url.rstrip("/")
    servers = openapi.get("servers") or []
    if not servers or not isinstance(servers[0], dict):
        return user_clean
    server_url = (servers[0].get("url") or "").strip()
    if not server_url:
        return user_clean
    if server_url.startswith(("http://", "https://")):
        from urllib.parse import urlsplit

        if urlsplit(user_clean).path in ("", "/"):
            return server_url.rstrip("/")
        return user_clean
    server_path = "/" + server_url.strip("/")
    if user_clean.endswith(server_path):
        return user_clean
    return user_clean + server_path


def _generator_identifier() -> str:
    """Return ``"openbb-cli==<version>"`` or just the name when unresolved."""
    try:
        return f"openbb-cli=={_pkg_version('openbb-cli')}"
    except PackageNotFoundError:
        return "openbb-cli"


def build_spec_document(
    openapi: dict[str, Any],
    *,
    base_url: str,
    api_prefix: str | None = None,
    source_url: str | None = None,
) -> dict[str, Any]:
    """Build the on-disk spec dict from a fetched OpenAPI document.

    ``base_url`` is reconciled against the OpenAPI ``servers`` array — see
    ``_resolve_base_url``. ``api_prefix`` defaults to the longest path-prefix
    shared by every URL in the spec — OpenBB Platform's ``/api/v1``, NY Fed's
    ``/api``, the empty prefix, etc. Pass an explicit value to override.
    ``source_url`` is the URL the OpenAPI document was fetched from — recorded
    so the spec carries enough provenance to be regenerated.
    """
    effective_prefix = (
        api_prefix if api_prefix is not None else detect_api_prefix(openapi)
    )
    return {
        "version": SPEC_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": _generator_identifier(),
        "source_url": source_url or "",
        "api_version": str(openapi.get("openapi") or openapi.get("swagger") or ""),
        "base_url": _resolve_base_url(openapi, base_url),
        "api_prefix": (("/" + effective_prefix.strip("/")) if effective_prefix else ""),
        "commands": build_command_spec(openapi, api_prefix=effective_prefix),
        "routers": build_router_map(openapi, api_prefix=effective_prefix),
        "reference": build_reference(openapi, api_prefix=effective_prefix),
    }


def _content_hash(spec_doc: dict[str, Any]) -> str:
    """Hash the spec doc deterministically, ignoring any existing hash field."""
    payload = {k: v for k, v in spec_doc.items() if k != "content_sha256"}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).hexdigest()


def write_spec(path: str | Path, spec_doc: dict[str, Any]) -> None:
    """Write the spec doc to ``path`` as compact JSON, stamped with its SHA-256.

    The hash covers the canonical JSON serialization of the doc with the
    ``content_sha256`` field excluded — so the value is reproducible from
    the written file alone. Mutates ``spec_doc`` in place to record it.
    """
    spec_doc["content_sha256"] = _content_hash(spec_doc)
    Path(path).write_text(json.dumps(spec_doc, separators=(",", ":")))


class _CommandParameter(BaseModel):
    """One parameter inside a command's ``parameters`` list."""

    model_config = ConfigDict(extra="allow")

    name: str
    in_: str = Field(default="query", alias="in")
    type: str = "string"
    is_list: bool = False
    required: bool = False
    default: Any = None
    choices: list[Any] = Field(default_factory=list)
    example: Any = None
    help: str | None = None
    providers: list[str] = Field(default_factory=list)


class _CommandSpec(BaseModel):
    """One entry in ``spec["commands"]`` keyed by dotted command path."""

    model_config = ConfigDict(extra="allow")

    url_path: str
    method: str
    description: str | None = None
    parameters: list[_CommandParameter] = Field(default_factory=list)
    providers: list[str] = Field(default_factory=list)
    request_body_schema: dict[str, Any] | None = None
    response_schema: dict[str, Any] | None = None


class SpecDocument(BaseModel):
    """The on-disk shape of a ``.spec`` file.

    Validation is structural: every required field must be present with the
    declared type. Unknown fields are accepted (forward-compat with future
    spec versions that introduce optional metadata).
    """

    model_config = ConfigDict(extra="allow")

    version: int
    base_url: str
    api_prefix: str = ""
    commands: dict[str, _CommandSpec]
    routers: dict[str, Any] = Field(default_factory=dict)
    reference: dict[str, Any] = Field(default_factory=dict)
    generated_at: str | None = None
    generator: str | None = None
    source_url: str | None = None
    # ``api_version`` is the upstream's own version label — OpenAPI's
    # ``"3.1.0"``, Socrata's ``"v2"`` — kept as an opaque string so spec
    # consumers can branch on it when needed without us baking in a
    # versioning scheme. Was ``openapi_version`` in earlier spec versions.
    api_version: str | None = None
    content_sha256: str | None = None


def load_spec(path: str | Path) -> dict[str, Any]:
    """Load and validate a spec doc; reject incompatible versions early.

    Three checks: the integer ``version`` must match ``SPEC_VERSION`` (hard
    floor for incompatible format changes), the document must conform to
    ``SpecDocument`` (required keys, declared types), and — when present —
    the recorded ``content_sha256`` must match the recomputed hash. Specs
    written by older generators predate the hash field and skip the third
    check.
    """
    spec_doc = json.loads(Path(path).read_text())
    version = spec_doc.get("version")
    if version != SPEC_VERSION:
        raise ValueError(
            f"Spec file at {path} has version {version!r}; expected {SPEC_VERSION}. "
            f"Regenerate with: openbb --server <URL> --generate-spec --output {path}"
        )
    try:
        SpecDocument.model_validate(spec_doc)
    except ValidationError as exc:
        raise ValueError(
            f"Spec file at {path} does not conform to the expected schema:\n{exc}"
        ) from exc
    recorded_hash = spec_doc.get("content_sha256")
    if recorded_hash is not None:
        actual_hash = _content_hash(spec_doc)
        if recorded_hash != actual_hash:
            raise ValueError(
                f"Spec file at {path} failed integrity check: "
                f"recorded SHA-256 {recorded_hash!r} does not match recomputed "
                f"{actual_hash!r}. The file has been modified since it was generated."
            )
    return spec_doc


def parser_from_command_spec(
    cmd_spec: dict[str, Any],
    prog: str | None = None,
    *,
    selected_provider: str | None = None,
) -> argparse.ArgumentParser:
    """Build an ArgumentParser from one entry in ``spec["commands"]``.

    ``prog`` overrides the program name shown in usage/help text — pass the
    dotted command name (``law``, ``bill.actions``) so the user sees that
    instead of the last URL segment, which can be a placeholder like
    ``{congress}`` for path-templated endpoints.

    ``selected_provider`` narrows the parser surface to flags valid for
    that provider — shared params (``providers == []``) plus provider-
    specific ones tagged with ``selected_provider``. Without this, an
    OpenBB multi-provider command would silently accept flags meant for
    a different provider and the upstream server would ignore them.

    ``add_help=False`` because the controller dispatch path always wraps the
    parser with ``parse_known_args_and_warn``, which adds its own ``-h``/
    ``--help`` action and would otherwise conflict on a duplicate flag.
    """
    fallback_prog = cmd_spec.get("url_path", "cmd").rsplit("/", 1)[-1] or "cmd"
    parser = argparse.ArgumentParser(
        prog=prog or fallback_prog,
        description=cmd_spec.get("description") or None,
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,
    )
    # Two argparse groups so help text shows required args separately from
    # optional ones — by default argparse lumps every ``--flag`` together
    # under "options" with no distinction.
    required_group = parser.add_argument_group("required arguments")
    optional_group = parser.add_argument_group("optional arguments")
    for p in cmd_spec.get("parameters", []) or []:
        if not _param_visible_for_provider(p, selected_provider):
            continue
        target = required_group if p.get("required") else optional_group
        try:
            _add_normalized_parameter(target, p)
        except argparse.ArgumentError:
            continue
    return parser


def _param_visible_for_provider(
    p: dict[str, Any], selected_provider: str | None
) -> bool:
    """Whether a normalized parameter belongs in the parser for ``selected_provider``.

    The ``provider`` discriminator itself is always visible. Other params
    are gated by the ``providers`` list recorded at spec-build time —
    empty list = shared across every provider, otherwise must include
    the chosen one.
    """
    if selected_provider is None or p.get("name") == "provider":
        return True
    tags = p.get("providers") or []
    return not tags or selected_provider in tags


def _add_normalized_parameter(
    parser: argparse._ActionsContainer, p: dict[str, Any]
) -> None:
    """Translate one normalized parameter dict into a parser argument."""
    flag = f"--{p['name']}"
    py_type = _NAME_TO_TYPE.get(p.get("type", "string"), str)
    kwargs: dict[str, Any] = {"dest": p["name"], "help": _escape_help(p.get("help"))}

    if py_type is bool:
        # ``BooleanOptionalAction`` registers both ``--flag`` and ``--no-flag``.
        # Required for params like ``use_cache`` whose default is ``True`` —
        # plain ``store_true`` would have no way to flip them off from the
        # command line.
        kwargs.update(
            action=argparse.BooleanOptionalAction,
            default=bool(p.get("default") or False),
        )
        parser.add_argument(flag, **kwargs)
        return

    # Socrata range-filter params (``start_date`` / ``end_date`` carry
    # ``_socrata_op``) need the raw ``YYYY-MM-DD`` string preserved —
    # the dispatcher folds them into a SoQL ``$where`` clause, and
    # Socrata's parser auto-coerces ISO-timestamp literals (``...T00:00:00Z``)
    # to a ``calendar_date`` type which fails ``op$>=`` against
    # text-stored date columns ("Type mismatch for op$>=, is text").
    is_socrata_range_param = p.get("_socrata_op") in {"date_min", "date_max"}
    if (
        py_type is str
        and not is_socrata_range_param
        and _looks_like_datetime_param(p["name"], p.get("help"))
    ):
        kwargs["type"] = _coerce_iso_datetime
    else:
        kwargs["type"] = py_type
    if p.get("default") is not None:
        kwargs["default"] = p["default"]
    if p.get("choices"):
        kwargs["choices"] = list(p["choices"])
    if p.get("is_list"):
        kwargs["nargs"] = "+"
    if p.get("required") and "default" not in kwargs:
        kwargs["required"] = True
    parser.add_argument(flag, **kwargs)


class SpecCommandError(KeyError):
    """Raised when a dotted command path is not present in the spec."""


def parse_command_argv(
    spec_doc: dict[str, Any], argv: list[str]
) -> tuple[str, dict[str, Any]]:
    """Resolve ``argv`` against ``spec_doc['commands']`` → (command, params).

    The first token is the dotted command path; everything after is parsed
    by the parser built from that command's normalized parameter list.

    Multi-provider OpenBB commands get a two-pass parse: first peek at
    ``--provider`` to learn which variant the user wants, then build the
    final parser containing only that provider's flags. This way
    ``equity.price.quote --provider intrinio --use_cache true`` errors
    out cleanly (``--use_cache`` is cboe-only) instead of silently being
    sent to the server and ignored.
    """
    if not argv:
        raise SpecCommandError(
            "missing command — usage: openbb --spec PATH <command.path> [--key value]"
        )
    command, rest = argv[0], list(argv[1:])
    cmd_spec = spec_doc.get("commands", {}).get(command)
    if cmd_spec is None:
        raise SpecCommandError(f"command not in spec: {command!r}")
    selected_provider = _peek_provider(cmd_spec, rest)
    parser = parser_from_command_spec(cmd_spec, selected_provider=selected_provider)
    ns = parser.parse_args(rest)
    params = {k: v for k, v in vars(ns).items() if v is not None}
    return command, params


def _peek_provider(cmd_spec: dict[str, Any], argv: list[str]) -> str | None:
    """Run a minimal first-pass parser to extract ``--provider`` from ``argv``.

    Returns ``None`` for non-multi-provider commands (no ``provider`` flag
    declared, or the user didn't pass one) so the caller falls back to the
    full parser. Uses ``parse_known_args`` so unknown flags don't trip the
    peek pass — they're surfaced by the real parser on the second pass.
    """
    providers = cmd_spec.get("providers") or []
    if not providers:
        return None
    peek = argparse.ArgumentParser(add_help=False)
    peek.add_argument("--provider", choices=list(providers))
    try:
        ns, _ = peek.parse_known_args(argv)
    except SystemExit:
        return None
    return getattr(ns, "provider", None)
