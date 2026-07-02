"""Launch the API from an ``openbb-cli`` generated ``.spec`` file.

A ``.spec`` is a digested OpenAPI snapshot — commands with their
``url_path``, ``parameters``, ``response_schema``, and a ``base_url``
pointing at the upstream that produced it. Feeding one to
``openbb-api`` synthesizes a Workspace-compatible backend that:

* exposes the same surface as the upstream (every command becomes a
  FastAPI route), and
* proxies every request to ``base_url + url_path``, replaying query
  string / body / headers verbatim.

The launcher's existing ``widgets.json`` builder runs against the
synthesized OpenAPI document, so widget generation, ``apps.json``
discovery, and the editable / SSRM flows all work without changes.
``apps.json`` is file-based and unaffected.

Use cases:

* Connect Workspace to a remote OpenBB Platform deployment without
  running the full backend locally — ship just ``openbb-platform-api``
  and the spec.
* Containerize a thin frontend that dispatches to a managed backend
  in another cluster / region.

Trade-offs:

* Latency doubles (proxy hop). Fine for dashboard-driven workloads,
  worth measuring for high-frequency endpoints.
* The spec doesn't carry credentials. Headers from the incoming
  request are forwarded as-is, so deploy the launcher behind whatever
  auth your upstream expects (mTLS, JWT, API gateway, …).
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

#: Trailing ``T00:00:00`` patterns we treat as "no real time-of-day"
#: when EVERY row in a response carries the same shape for a given
#: field. Matches ``T00:00:00``, ``T00:00:00.000``, ``T00:00:00Z``,
#: ``T00:00:00.000Z``, and ``T00:00:00+00:00``-style offsets. Does NOT
#: match ``T00:00:00.001`` (real ms), ``T00:00:01`` (real second), etc.
_ZERO_TIME_RE = re.compile(r"T00:00:00(?:\.0+)?(?:Z|[+-]\d{2}:?\d{2})?$")

#: Common envelope keys whose value is the row-list. Inspected when the
#: top-level payload is a dict — the trim recurses into the list under
#: any of these keys before bailing.
_ENVELOPE_KEYS: tuple[str, ...] = ("results", "data", "rows", "records")

from fastapi import FastAPI, Request
from fastapi.responses import Response

#: Spec versions this loader knows how to consume. Newer minor
#: revisions can extend the schema with optional fields without
#: bumping; ``SPEC_VERSION`` matches the openbb-cli generator.
SUPPORTED_SPEC_VERSIONS: frozenset[int] = frozenset({5})


# ---------------------------------------------------------------------------
# Spec provenance + structural compatibility models
# ---------------------------------------------------------------------------
#
# Mirrors ``openbb_cli.dispatchers.spec.SpecDocument``. Inlining the model
# (rather than importing from openbb-cli) keeps the launcher's runtime
# dep tree light — the CLI's spec module pulls argparse translators and
# openapi walkers that are pure deadweight here.


class _CommandParameterModel(BaseModel):
    """One parameter inside a command's ``parameters`` list."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    name: str
    type: str = "string"
    is_list: bool = False
    required: bool = False
    default: Any = None
    choices: list[Any] = Field(default_factory=list)


class _CommandSpecModel(BaseModel):
    """One entry in ``spec["commands"]`` keyed by dotted command path."""

    model_config = ConfigDict(extra="allow")

    url_path: str
    method: str
    parameters: list[_CommandParameterModel] = Field(default_factory=list)
    request_body_schema: dict[str, Any] | None = None
    response_schema: dict[str, Any] | None = None


class _SpecDocumentModel(BaseModel):
    """The on-disk shape of a ``.spec`` file.

    Validation is structural: every required field must be present
    with the declared type. ``content_sha256`` is required — every
    spec produced by ``openbb-cli`` stamps the field at generation
    time, so an absent value indicates either a corrupted file or
    a hand-rolled forgery; either way the launcher refuses to load
    it. Unknown fields are accepted so older launchers stay
    forward-compat with future spec generators that introduce
    optional metadata.
    """

    model_config = ConfigDict(extra="allow")

    version: int
    base_url: str
    api_prefix: str = ""
    commands: dict[str, _CommandSpecModel]
    content_sha256: str
    routers: dict[str, Any] = Field(default_factory=dict)
    reference: dict[str, Any] = Field(default_factory=dict)
    generated_at: str | None = None
    generator: str | None = None
    source_url: str | None = None
    api_version: str | None = None


def _content_hash(spec_doc: dict[str, Any]) -> str:
    """Hash the spec doc deterministically, ignoring ``content_sha256``.

    The hash covers the canonical JSON serialization of the doc with
    the ``content_sha256`` field excluded, so the value is reproducible
    from the written file alone — same algorithm openbb-cli uses when
    stamping the spec at generation time.
    """
    payload = {k: v for k, v in spec_doc.items() if k != "content_sha256"}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).hexdigest()


# ---------------------------------------------------------------------------
# Spec loading + provenance / integrity verification
# ---------------------------------------------------------------------------


def load_spec(
    path: str | Path,
    *,
    expected_content_sha256: str | None = None,
) -> dict[str, Any]:
    """Read, validate, and verify the integrity of a ``.spec`` file.

    Performs four checks before handing the spec to downstream
    consumers (the proxy builder, widgets generator, etc.):

    1. **File parseability** — must exist and contain valid JSON
       under a top-level object.
    2. **Version compatibility** — ``version`` must be one of
       ``SUPPORTED_SPEC_VERSIONS``. Mismatches raise with the
       regenerate hint.
    3. **Structural schema** — pydantic-validated against
       ``_SpecDocumentModel`` (required fields, declared types,
       command shape). Catches deeper malformations than the
       single-key sanity checks could.
    4. **Content integrity** — recompute SHA-256 over the canonical
       JSON serialization and verify against the spec's
       ``content_sha256``. The field is REQUIRED — every spec from
       ``openbb-cli`` carries one, and an absent or mismatched
       value indicates corruption or tampering. When
       ``expected_content_sha256`` is also supplied (typically from
       ``[spec].content_sha256`` in the deploy TOML), the recomputed
       hash must ALSO match the deploy pin so a remotely-distributed
       spec can be tied to a specific revision in the deployment
       manifest. Both checks raise distinct errors so the operator
       sees whether the failure is in-file tampering or version
       drift between the manifest and the deployed artifact.

    Returns the spec as a plain dict so callers don't pay the
    pydantic-model overhead on every read.

    Raises ``FileNotFoundError`` for missing paths, ``ValueError`` for
    every other failure. Each ValueError names the offending file path
    so multi-spec deployments can pinpoint the bad input.
    """
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Spec file not found: {path}")
    try:
        spec = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Spec file is not valid JSON: {path} — {exc}") from exc
    if not isinstance(spec, dict):
        raise ValueError(f"Spec file does not contain a top-level object: {path}")
    version = spec.get("version")
    if version not in SUPPORTED_SPEC_VERSIONS:
        raise ValueError(
            f"Unsupported spec version {version!r} at {path}. "
            f"This launcher knows versions {sorted(SUPPORTED_SPEC_VERSIONS)}. "
            "Regenerate with a matching ``openbb --generate-spec``."
        )
    base_url = spec.get("base_url")
    if not isinstance(base_url, str) or not base_url:
        raise ValueError(
            f"Spec missing required ``base_url`` field at {path}. "
            "Spec must point at the upstream the proxy will forward to."
        )
    if not isinstance(spec.get("commands"), dict):
        raise ValueError(f"Spec missing required ``commands`` table at {path}.")
    try:
        _SpecDocumentModel.model_validate(spec)
    except ValidationError as exc:
        raise ValueError(
            f"Spec file at {path} does not conform to the expected schema:\n{exc}"
        ) from exc

    # ``content_sha256`` is required by the pydantic schema, so we
    # know it's a non-empty string at this point.
    recorded_hash = spec["content_sha256"]
    actual_hash = _content_hash(spec)
    if recorded_hash != actual_hash:
        raise ValueError(
            f"Spec file at {path} failed integrity check: recorded SHA-256 "
            f"{recorded_hash!r} does not match recomputed {actual_hash!r}. "
            "The file has been modified since it was generated."
        )
    if expected_content_sha256 is not None and expected_content_sha256 != actual_hash:
        raise ValueError(
            f"Spec file at {path} failed deploy-config pin check: "
            f"expected SHA-256 {expected_content_sha256!r} (from deploy "
            f"config) does not match recomputed {actual_hash!r}. The "
            "deployed spec is not the version pinned by the operator."
        )
    return spec


# ---------------------------------------------------------------------------
# Spec → OpenAPI dict (so build_json keeps working unchanged)
# ---------------------------------------------------------------------------

#: Map ``spec.parameters[].type`` strings back to the JSON Schema types
#: the existing OpenAPI walker (``utils/openapi.py``) expects.
_SPEC_TYPE_TO_JSON_SCHEMA: dict[str, str] = {
    "string": "string",
    "integer": "integer",
    "number": "number",
    "boolean": "boolean",
}


def _spec_param_to_openapi(param: dict[str, Any]) -> dict[str, Any]:
    """Reverse ``cli.spec``'s ``_normalize_parameter`` so the param looks
    like the OpenAPI parameter object the launcher's widget builder
    consumes.

    The shapes are similar but not identical — spec params hoist
    ``type`` / ``default`` / ``choices`` to the top level; OpenAPI
    nests them under ``schema``. This re-nests them and recovers
    ``description`` from the spec's ``help`` slot.
    """
    schema: dict[str, Any] = {}
    type_name = param.get("type", "string")
    json_schema_type = _SPEC_TYPE_TO_JSON_SCHEMA.get(type_name, "string")
    if param.get("is_list"):
        schema["type"] = "array"
        schema["items"] = {"type": json_schema_type}
    else:
        schema["type"] = json_schema_type
    if (default := param.get("default")) is not None:
        schema["default"] = default
    if param.get("choices"):
        schema["enum"] = list(param["choices"])
    if (description := param.get("help")) is not None:
        schema["description"] = description

    out: dict[str, Any] = {
        "name": param["name"],
        "in": param.get("in", "query"),
        "required": bool(param.get("required")),
        "schema": schema,
    }
    if description is not None:
        out["description"] = description
    if (example := param.get("example")) is not None:
        out["example"] = example
    return out


def synthesize_openapi_from_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """Reconstruct an OpenAPI document from a spec's command list.

    The launcher's widget builder consumes raw OpenAPI dicts. Rather
    than fork that code path for spec-driven launches, we reverse the
    spec normalization and feed ``build_json`` an OpenAPI it already
    knows how to walk. Every command yields one path entry; the
    response_schema (when present) flows through unchanged so column
    auto-detection works the same as in a live-platform launch.
    """
    paths: dict[str, dict[str, Any]] = {}
    for cmd_name, cmd in spec.get("commands", {}).items():
        url = cmd.get("url_path")
        method = (cmd.get("method") or "get").lower()
        if not url or method not in {"get", "post"}:
            continue

        op: dict[str, Any] = {
            "operationId": cmd_name,
            "summary": cmd.get("description") or "",
            "description": cmd.get("description") or "",
            "parameters": [
                _spec_param_to_openapi(p) for p in (cmd.get("parameters") or [])
            ],
        }

        if response_schema := cmd.get("response_schema"):
            op["responses"] = {
                "200": {"content": {"application/json": {"schema": response_schema}}}
            }
        else:
            op["responses"] = {"200": {"content": {"application/json": {}}}}

        if method == "post" and (request_body_schema := cmd.get("request_body_schema")):
            op["requestBody"] = {
                "content": {"application/json": {"schema": request_body_schema}}
            }

        paths.setdefault(url, {})[method] = op

    return {
        "openapi": "3.1.0",
        "info": {
            "title": "OpenBB Platform API (spec-driven proxy)",
            "version": str(spec.get("api_version") or "1.0"),
        },
        "paths": paths,
        "components": {"schemas": {}},
    }


# ---------------------------------------------------------------------------
# Spec → FastAPI proxy app
# ---------------------------------------------------------------------------

#: Hop-by-hop headers that must NOT be forwarded across a proxy.
#: From RFC 7230 §6.1 plus a few practical extras (Workspace requests
#: tend to come through ``starlette``, which already handles these,
#: but we filter explicitly to be safe).
_HOP_BY_HOP_HEADERS: frozenset[str] = frozenset(
    {
        "connection",
        "content-encoding",
        "content-length",
        "host",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailer",
        "transfer-encoding",
        "upgrade",
    }
)


def _filter_request_headers(headers: dict[str, str]) -> dict[str, str]:
    """Drop hop-by-hop headers before forwarding upstream."""
    return {k: v for k, v in headers.items() if k.lower() not in _HOP_BY_HOP_HEADERS}


def _filter_response_headers(headers: dict[str, str]) -> dict[str, str]:
    """Drop hop-by-hop headers on the response side — let the
    launcher's own response infrastructure (Content-Length,
    Content-Encoding) take over rather than echoing upstream's, which
    can mismatch after transcoding.
    """
    return {k: v for k, v in headers.items() if k.lower() not in _HOP_BY_HOP_HEADERS}


def build_app_from_spec(
    spec: dict[str, Any],
    *,
    base_url_override: str | None = None,
    extra_headers: dict[str, str] | None = None,
    spec_name: str | None = None,
) -> FastAPI:
    """Synthesize a FastAPI app whose routes proxy to ``spec.base_url``.

    Each command in ``spec["commands"]`` becomes one FastAPI route at
    its ``url_path``. The handler reads the incoming request, replays
    it against ``base_url + url_path`` with the same method / query /
    body / (filtered) headers, and streams the upstream response back.

    The route's OpenAPI metadata is populated from the spec via
    ``openapi_extra`` so the launcher's ``widgets.json`` builder sees
    the rich parameter / response_schema info the spec already
    digested. Falls back to ``synthesize_openapi_from_spec`` for the
    document-level fields that ``build_json`` reads.

    ``base_url_override`` swaps the spec's recorded ``base_url`` —
    useful when a single spec is shared across staging/prod or when
    the recorded URL points at an internal host the launcher needs
    to reroute.

    ``extra_headers`` injects static headers on every upstream
    request. Configured via ``[spec.headers]`` in the launcher TOML
    so deployments can ship credentials (``Authorization``,
    ``X-API-Key``, …) without baking them into the spec or relying on
    the incoming request to carry them. Config-supplied headers
    OVERRIDE matching incoming-request headers — the launcher's
    static auth is the source of truth.

    ``spec_name`` is the human-readable label that replaces the
    default ``["Custom"]`` source citation on every auto-generated
    widget. ``args.parse_args`` passes the spec file's full name
    (``Path(spec_path).name``) so dashboards built from
    ``/etc/openbb/fertilizer.spec`` cite ``fertilizer.spec`` instead
    of a generic ``Custom``. Stashed on
    ``app.state.openbb_spec_source`` where
    ``widgets_service.get_widgets_json`` reads it.
    """
    base_url = (base_url_override or spec["base_url"]).rstrip("/")
    api_title = "OpenBB Platform API (spec-driven proxy)"

    app = FastAPI(
        title=api_title,
        version=str(spec.get("api_version") or "1.0"),
    )

    # Stash on app.state so callers (the launcher's widgets builder,
    # tests, custom middleware) can introspect what the proxy was
    # built from. ``openbb_spec_source`` is the citation label
    # ``widgets_service`` reads to override the auto-generated
    # ``["Custom"]`` source on every spec-driven widget. The other
    # fields are provenance metadata captured at spec-generation time:
    # ``content_sha256`` (already integrity-verified by ``load_spec``)
    # is exposed so observability layers can fingerprint the active
    # spec, ``generator`` / ``generated_at`` / ``source_url`` give a
    # forensic trail back to the openbb-cli invocation that produced it.
    app.state.openbb_spec = spec
    app.state.openbb_spec_base_url = base_url
    app.state.openbb_spec_source = spec_name
    app.state.openbb_spec_extra_headers = dict(extra_headers or {})
    app.state.openbb_spec_version = spec.get("version")
    app.state.openbb_spec_generator = spec.get("generator")
    app.state.openbb_spec_generated_at = spec.get("generated_at")
    app.state.openbb_spec_source_url = spec.get("source_url")
    app.state.openbb_spec_content_sha256 = spec.get("content_sha256")
    app.state.openbb_spec_api_version = spec.get("api_version")

    def _make_handler(
        method: str,
        upstream_path: str,
        wire_name_map: dict[str, str],
    ):
        """Closure-bind ``method`` + ``upstream_path`` + ``wire_name_map``
        for the route.

        ``wire_name_map`` is per-route because each command can declare
        its own friendly→wire translations (Socrata datasets emit
        ``limit``/``offset`` but the upstream API actually expects
        ``$limit``/``$offset`` — the spec records the wire form on the
        parameter so the proxy can rewrite the query string before
        forwarding).

        The handler is intentionally untyped on its return — FastAPI's
        OpenAPI generator inspects return annotations to build a
        response model, and we don't want it to override the
        spec-supplied ``response_schema`` we attach via
        ``openapi_extra``. An un-annotated return + a typed ``Request``
        parameter gives FastAPI just enough to wire the route without
        overwriting the spec metadata.
        """

        async def handler(request: Request):
            # Substitute FastAPI path-parameter placeholders
            # (``{axis}`` etc.) with the resolved values from
            # ``request.path_params`` before forwarding upstream.
            # The spec records ``url_path`` in its template form
            # (``/breakdown/{axis}``), so without substitution the
            # upstream sees the literal ``{axis}`` and rejects the
            # request — caught against the BlackRock spec during
            # the live integration test.
            resolved_path = _substitute_path_params(upstream_path, request.path_params)
            return await _proxy_request(
                request,
                method=method,
                upstream_url=base_url + resolved_path,
                extra_headers=app.state.openbb_spec_extra_headers,
                wire_name_map=wire_name_map,
            )

        return handler

    for cmd_name, cmd in spec.get("commands", {}).items():
        url_path = cmd.get("url_path")
        method = (cmd.get("method") or "get").lower()
        if not url_path or method not in {"get", "post"}:
            continue

        # Filter out malformed (non-dict) parameter entries once so
        # both consumers below operate on a clean list — keeps the
        # launcher tolerant of partial/corrupt specs without
        # duplicating the type guard in two places.
        cmd_params: list[dict[str, Any]] = [
            p for p in (cmd.get("parameters") or []) if isinstance(p, dict)
        ]

        # Capture friendly→wire-name translations from this command's
        # parameters. Socrata-style specs emit e.g. ``name="limit"``,
        # ``wire_name="$limit"`` so the proxy can keep the friendly
        # name in the widget UI (and OpenAPI) but send the actual
        # upstream-expected name in the forwarded query string.
        # Without this rewrite, Socrata responds
        # ``Unrecognized arguments [limit]`` because it expects
        # ``$limit``.
        wire_name_map: dict[str, str] = {}
        for p in cmd_params:
            wire = p.get("wire_name")
            friendly = p.get("name")
            if wire and friendly and wire != friendly:
                wire_name_map[friendly] = wire

        # Build the OpenAPI ``operation`` for this route. We pass it
        # through ``openapi_extra`` so FastAPI doesn't strip the
        # spec-supplied ``parameters`` / ``responses`` blocks.
        operation_extra: dict[str, Any] = {
            "parameters": [_spec_param_to_openapi(p) for p in cmd_params],
        }
        if response_schema := cmd.get("response_schema"):
            operation_extra["responses"] = {
                "200": {"content": {"application/json": {"schema": response_schema}}}
            }
        if method == "post" and (request_body_schema := cmd.get("request_body_schema")):
            operation_extra["requestBody"] = {
                "content": {"application/json": {"schema": request_body_schema}}
            }

        app.add_api_route(
            path=url_path,
            endpoint=_make_handler(method, url_path, wire_name_map),
            methods=[method.upper()],
            name=cmd_name,
            description=cmd.get("description") or "",
            openapi_extra=operation_extra,
        )

    return app


def build_apps_from_specs(
    specs_config: dict[str, dict[str, Any]],
) -> FastAPI:
    """Build a parent FastAPI app that mounts each spec at its prefix.

    ``specs_config`` is a dict of ``{name: per_spec_kwargs}`` where each
    per-spec entry carries:

    * ``spec`` — the loaded spec dict (already validated by
      ``load_spec``).
    * ``mount`` — the path prefix to mount the spec's app at, e.g.
      ``/equity``. Defaults to ``"/" + name`` when not supplied.
    * ``base_url_override`` / ``extra_headers`` / ``spec_name`` — same
      semantics as the single-spec ``build_app_from_spec`` kwargs;
      passed through verbatim so each spec keeps its own upstream
      target, credential headers, and citation label.
    * ``auth_hooks`` / ``middleware_hooks`` — optional lists of
      ``module:async_callable`` references applied as
      ``BaseHTTPMiddleware`` to that spec's sub-app. Auth runs as
      the outermost layer, then the middleware list. The hooks are
      naturally scoped to the sub-app's mount prefix because they're
      registered on that sub-app instance, not the parent.

    Returns a parent ``FastAPI`` whose ``app.state.openbb_specs`` is
    a dict of ``{mount: sub_app_state_snapshot}`` — gives the widgets
    builder, telemetry layers, and tests a single attachment point
    to introspect every mounted spec.

    Mount prefix collisions raise ``ValueError`` immediately so a
    misconfigured deployment fails at startup, not on the first
    routing miss.
    """
    if not specs_config:
        raise ValueError("build_apps_from_specs requires at least one spec entry.")

    parent = FastAPI(title="OpenBB Platform API (multi-spec proxy)")

    used_mounts: dict[str, str] = {}
    state_by_mount: dict[str, dict[str, Any]] = {}

    for name, entry in specs_config.items():
        if not isinstance(entry, dict):
            raise TypeError(
                f"Spec entry {name!r} must be a dict; got {type(entry).__name__}."
            )
        if "spec" not in entry:
            raise ValueError(
                f"Spec entry {name!r} is missing the required 'spec' field "
                "(the loaded spec dict)."
            )

        # Mount prefix: explicit ``mount`` wins, otherwise derive from
        # the dict key. Always forced to start with ``/``.
        mount = entry.get("mount") or f"/{name}"
        if not mount.startswith("/"):
            mount = "/" + mount
        # Normalize trailing slash off (FastAPI mount eats the trailing
        # slash on its own when forming sub-app paths).
        normalized_mount = mount.rstrip("/") or "/"

        if normalized_mount in used_mounts:
            other = used_mounts[normalized_mount]
            raise ValueError(
                f"Spec mount collision: {name!r} and {other!r} both target "
                f"{normalized_mount!r}. Each spec must mount at a distinct "
                "prefix (set ``mount = ...`` to disambiguate)."
            )
        used_mounts[normalized_mount] = name

        sub_app = build_app_from_spec(
            entry["spec"],
            base_url_override=entry.get("base_url_override"),
            extra_headers=entry.get("extra_headers"),
            spec_name=entry.get("spec_name") or name,
        )

        # Apply per-spec auth + middleware hooks. Auth runs as the
        # outermost layer. ``BaseHTTPMiddleware(dispatch=fn)`` adapts
        # the ``async def fn(request, call_next)`` shape into a
        # Starlette middleware class without subclassing.
        from starlette.middleware.base import BaseHTTPMiddleware

        from openbb_platform_api.app.middleware import (
            _resolve_entrypoint,
            _validate_middleware_callable,
        )

        for label, hooks in (
            ("middleware", entry.get("middleware_hooks")),
            ("auth", entry.get("auth_hooks")),
        ):
            # Reverse so the FIRST entry of each list ends up
            # OUTERMOST after Starlette's stack-build (add_middleware
            # inserts at index 0). Auth registered LAST = outermost
            # overall, so it sees the request before any middleware
            # hook does.
            if not hooks:
                continue
            if not isinstance(hooks, list):
                raise TypeError(
                    f"[spec.{name}.{label}] hooks must be a list of "
                    f"'module:attr' strings; got {type(hooks).__name__}."
                )
            for hook_path in reversed(hooks):
                if not isinstance(hook_path, str):
                    raise TypeError(
                        f"[spec.{name}.{label}] hook entries must be "
                        f"strings; got {type(hook_path).__name__} "
                        f"({hook_path!r})."
                    )
                fn = _resolve_entrypoint(hook_path)
                _validate_middleware_callable(fn, hook_path)
                sub_app.add_middleware(BaseHTTPMiddleware, dispatch=fn)

        parent.mount(normalized_mount, sub_app, name=name)

        # Snapshot the sub-app's ``app.state`` provenance for the
        # parent's introspection dict — saves consumers from walking
        # ``parent.routes`` to find each Mount and reach into its
        # nested app.state.
        state_by_mount[normalized_mount] = {
            "name": name,
            "spec_name": sub_app.state.openbb_spec_source,
            "base_url": sub_app.state.openbb_spec_base_url,
            "version": sub_app.state.openbb_spec_version,
            "generator": sub_app.state.openbb_spec_generator,
            "generated_at": sub_app.state.openbb_spec_generated_at,
            "source_url": sub_app.state.openbb_spec_source_url,
            "content_sha256": sub_app.state.openbb_spec_content_sha256,
            "api_version": sub_app.state.openbb_spec_api_version,
        }

    parent.state.openbb_specs = state_by_mount
    return parent


def _substitute_path_params(template: str, params: dict[str, Any]) -> str:
    """Replace FastAPI ``{name}`` path-param placeholders with resolved values.

    The spec records URL paths in their template form
    (``/breakdown/{axis}``). FastAPI parses path-params from incoming
    requests into ``request.path_params``; we splice them back into
    the template so the upstream URL is fully resolved before the
    proxy hop. Each value is URL-quoted with ``safe=""`` so segments
    containing slashes, spaces, or other special characters don't
    corrupt the path. Templates without ``{...}`` placeholders flow
    through unchanged.
    """
    from urllib.parse import quote

    resolved = template
    for name, value in params.items():
        placeholder = "{" + str(name) + "}"
        if placeholder in resolved:
            resolved = resolved.replace(placeholder, quote(str(value), safe=""))
    return resolved


def _rewrite_query_string(
    query_string: str, wire_name_map: dict[str, str] | None
) -> str:
    """Rewrite query-string param names per ``wire_name_map``.

    Preserves ordering and value encoding; only the keys are swapped.
    Unmapped keys flow through verbatim. Returns the original string
    when no map is given (or it's empty) so the common no-rewrite
    path stays a single dict-emptiness check.

    Implemented over ``parse_qsl(keep_blank_values=True)`` so an empty
    ``?foo=`` round-trips correctly.
    """
    if not wire_name_map or not query_string:
        return query_string
    from urllib.parse import parse_qsl, urlencode

    pairs = parse_qsl(query_string, keep_blank_values=True)
    rewritten = [(wire_name_map.get(k, k), v) for k, v in pairs]
    return urlencode(rewritten)


def _trim_uniform_zero_time_columns(payload: Any) -> Any:
    """Strip ``T00:00:00*`` from columns that are uniformly all-zero-time.

    Data-driven, not schema-driven: walks the actual response and
    decides per-column based on what every row carries.

    * For each field across every row, if EVERY string value matches
      ``T00:00:00*``, the time portion carries no information for that
      column — strip it.
    * If even one row has a real time-of-day for that field
      (``T00:00:01``, ``T13:45:00``, anything with non-zero
      hours/minutes/seconds/sub-seconds), the whole column is left
      alone — midnight IS a legitimate time when the upstream actually
      records it.

    Handles two payload shapes:

    * Top-level list of dicts (Socrata's typical format).
    * Top-level dict with a list under one of ``_ENVELOPE_KEYS``
      (``results``, ``data``, ``rows``, ``records``) — the OBBject
      envelope and similar wrapper shapes.

    Single records / unwrapped scalars pass through unchanged: with
    only one row there's no cross-row signal, and per the contract
    above, midnight on a lone record could be meaningful.
    """
    if isinstance(payload, list):
        return _trim_uniform_zero_time_in_records(payload)
    if isinstance(payload, dict):
        for key in _ENVELOPE_KEYS:
            inner = payload.get(key)
            if isinstance(inner, list):
                trimmed = _trim_uniform_zero_time_in_records(inner)
                if trimmed is inner:
                    return payload
                return {**payload, key: trimmed}
    return payload


def _trim_uniform_zero_time_in_records(records: list[Any]) -> list[Any]:
    """Per-column unanimity check + strip on a list of dict records.

    Returns the input list unchanged (same identity) when no column
    needs trimming so callers can detect no-op cheaply.
    """
    dict_records = [r for r in records if isinstance(r, dict)]
    if not dict_records:
        return records

    # Pass 1: find columns where every present string value matches the
    # zero-time pattern. ``None`` values don't disqualify a column —
    # they just don't contribute. A column with ZERO matching values
    # (e.g. all-None, or all numbers) is also excluded since there's
    # nothing to trim.
    all_keys: set[str] = set()
    for r in dict_records:
        all_keys.update(r.keys())

    zero_time_columns: set[str] = set()
    for key in all_keys:
        present_values = []
        for r in dict_records:
            v = r.get(key)
            if v is None:
                continue
            present_values.append(v)
        if not present_values:
            continue
        if all(isinstance(v, str) and _ZERO_TIME_RE.search(v) for v in present_values):
            zero_time_columns.add(key)

    if not zero_time_columns:
        return records

    # Pass 2: rebuild records, stripping the time suffix only on the
    # identified columns. Non-dict entries (rare, but possible in
    # heterogeneous responses) flow through untouched.
    out: list[Any] = []
    for r in records:
        if not isinstance(r, dict):
            out.append(r)
            continue
        rewritten = {
            k: (
                _ZERO_TIME_RE.sub("", v)
                if k in zero_time_columns and isinstance(v, str)
                else v
            )
            for k, v in r.items()
        }
        out.append(rewritten)
    return out


async def _proxy_request(
    request: Request,
    *,
    method: str,
    upstream_url: str,
    extra_headers: dict[str, str] | None = None,
    wire_name_map: dict[str, str] | None = None,
) -> Response:
    """Forward ``request`` to ``upstream_url`` and stream the response.

    Uses ``aiohttp`` because it's already a runtime dep of
    ``openbb-core`` (no new transitive deps for the launcher). One
    ``ClientSession`` is created per request — fine for dashboard
    traffic; revisit with a shared session pool if proxying becomes
    high-frequency.

    ``extra_headers`` are merged in AFTER hop-by-hop filtering and
    OVERRIDE any matching incoming-request header. This is the slot
    the ``[spec.headers]`` TOML table fills, so deployments can inject
    auth credentials regardless of what the dashboard widget sent.

    ``wire_name_map`` rewrites query-string param names from the
    user-facing form to whatever the upstream expects. The Socrata
    case — friendly ``limit``/``offset``, wire ``$limit``/``$offset`` —
    is the motivating example; without the rewrite the upstream
    responds ``Unrecognized arguments [limit]``.

    JSON responses are run through ``_trim_uniform_zero_time_columns``
    before being relayed — that's data-driven, not schema-driven: a
    column whose every row carries ``T00:00:00*`` (across the whole
    response) loses the meaningless time portion. Columns where ANY
    row has a real time-of-day are left intact.
    """
    import aiohttp

    body = await request.body() if method in {"post", "put", "patch"} else None
    forwarded_headers = _filter_request_headers(dict(request.headers))
    if extra_headers:
        # Static headers from config are the source of truth — they
        # override matching incoming-request headers. Reasoning:
        # ``[spec.headers]`` exists for credential injection, and
        # we don't want a misbehaving client to leak its own auth
        # value upstream by accident.
        forwarded_headers.update(extra_headers)
    query_string = _rewrite_query_string(request.url.query, wire_name_map)

    target = upstream_url + ("?" + query_string if query_string else "")

    timeout = aiohttp.ClientTimeout(total=60)
    async with (
        aiohttp.ClientSession(timeout=timeout) as session,
        session.request(
            method.upper(),
            target,
            data=body,
            headers=forwarded_headers,
        ) as upstream,
    ):
        content = await upstream.read()
        response_headers = _filter_response_headers(dict(upstream.headers))

        # JSON responses get the per-column unanimity trim. The
        # function returns the original payload (same identity) when
        # nothing needs trimming, so we only re-encode + drop the
        # upstream Content-Length when we actually mutated something.
        if "application/json" in (upstream.headers.get("Content-Type") or ""):
            try:
                payload = json.loads(content)
            except (json.JSONDecodeError, UnicodeDecodeError):
                payload = None
            if payload is not None:
                trimmed = _trim_uniform_zero_time_columns(payload)
                if trimmed is not payload:
                    content = json.dumps(trimmed).encode("utf-8")
                    response_headers.pop("Content-Length", None)
                    response_headers.pop("content-length", None)

        return Response(
            content=content,
            status_code=upstream.status,
            headers=response_headers,
            media_type=upstream.headers.get("Content-Type"),
        )
