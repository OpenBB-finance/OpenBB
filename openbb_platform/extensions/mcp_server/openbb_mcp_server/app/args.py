"""Command-line argument parsing for ``openbb-mcp``.

Mirrors the platform-api launcher: ``parse_args`` reads
``sys.argv[1:]``, overlays any ``[mcp]`` table from the layered TOML
cascade as defaults (CLI always wins), and returns a dict the entry-
point in ``main.py`` consumes.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

_spec_headers_logger = logging.getLogger("openbb_mcp_server.spec.headers")


def _is_module_colon_notation(app_path: str) -> bool:
    r"""Tell colon-as-name from colon-as-Windows-drive.

    Mirrors the helper in ``app.bootstrap`` so ``parse_args`` doesn't
    treat the ``C:`` in a Windows absolute path as the start of
    ``module:attr`` notation. Without this, ``--app C:\\path\\app.py``
    splits on the drive-letter colon and clobbers ``--name`` with the
    path tail.
    """
    if ":" not in app_path:
        return False
    if len(app_path) >= 2 and app_path[1] == ":" and app_path[0].isalpha():
        # Drive-letter colon. Real ``module:attr`` after the path adds a
        # second colon, so ``len(parts) > 2`` is the disambiguator.
        return len(app_path.split(":")) > 2
    return True


def _collect_multi_spec_entries(spec_section: dict) -> dict[str, dict]:
    """Pick out ``[mcp.spec.NAME]`` subtables that look like spec entries.

    A subtable counts as a multi-spec entry only when its value is a
    dict carrying a ``path`` string — protects against single-spec
    sibling tables (``[mcp.spec.headers]``, ``[mcp.spec.auth]``,
    ``[mcp.spec.middleware]``) accidentally being treated as nested
    spec definitions.
    """
    out: dict[str, dict] = {}
    for name, value in spec_section.items():
        if isinstance(value, dict) and isinstance(value.get("path"), str):
            out[name] = value
    return out


def _expand_spec_headers(
    raw_headers: dict | None,
) -> dict[str, str]:
    """Expand ``$VAR`` / ``${VAR}`` refs in a ``[mcp.spec.headers]`` table.

    Same substitution logic as ``[env]`` (against the current
    ``os.environ``). Entries with unresolved references are SKIPPED
    with a warning.
    """
    from openbb_mcp_server.app.config import expand_env_refs

    if not raw_headers:
        return {}
    expanded: dict[str, str] = {}
    for header_name, header_value in raw_headers.items():
        if not isinstance(header_name, str):
            continue
        substituted, missing = expand_env_refs(str(header_value))
        if missing:
            _spec_headers_logger.warning(
                "Skipping [mcp.spec.headers] entry %s: references "
                "unresolved variable(s) %s",
                header_name,
                ", ".join(missing),
            )
            continue
        expanded[header_name] = substituted
    return expanded


LAUNCH_SCRIPT_DESCRIPTION = """
Serve the OpenBB Platform MCP Server.


Launcher specific arguments:

    --app                           Absolute/relative path to a Python file with the target FastAPI instance whose routes
                                    become MCP tools. Default is the installed openbb-core REST API.
    --name                          Name of the FastAPI instance in the app file. Default is 'app'.
    --factory                       Flag to indicate the app name is a factory function.
    --spec                          Absolute/relative path to an `openbb-cli` generated `.spec` file. Synthesizes a
                                    FastAPI app whose routes proxy to the spec's `base_url`; FastMCP exposes those
                                    routes as MCP tools. Mutually exclusive with --app.
    --config-file                   Absolute/relative path to a TOML config file. Highest-priority TOML layer in the cascade.
                                    Also honored via $OPENBB_MCP_CONFIG / $OPENBB_API_CONFIG / $OPENBB_CONFIG.
    --transport                     MCP transport: 'streamable-http' (default), 'sse', or 'stdio'.
    --host                          Host IP address for HTTP / SSE transports. Default is '127.0.0.1'.
    --port                          Port for HTTP / SSE transports. Default is 8000.
    --allowed-categories            Comma-separated list of tool categories to allow. Empty = all.
    --default-categories            Comma-separated list of tool categories enabled by default. Default is 'all'.
    --tool-discovery                Enable progressive tool discovery (admin tools to activate categories on demand).
    --system-prompt                 Path to a TXT file used as the server's system prompt.
    --server-prompts                Path to a JSON file with a list of server prompts.


Config file (`openbb.toml`) — runtime defaults + env injection:

The launcher reads the same layered TOML cascade openbb-core ships with
(pyproject → user-global → project → explicit → .env → real env vars).
MCP-specific tables:

    [mcp]
    # Default values for any of the CLI flags above. CLI wins over TOML.
    host = "0.0.0.0"
    port = 8005
    transport = "streamable-http"
    default-categories = "equity,crypto"
    tool-discovery = true

    [mcp.spec]
    # Single-spec mode: spec-driven MCP proxy with one upstream.
    path = "/etc/openbb/cli.spec"
    base_url = "https://upstream.example.com"  # optional override of the spec's recorded base_url
    # Optional pinned SHA-256. When set, the launcher recomputes the
    # spec's canonical-JSON hash and refuses to start unless it
    # matches.
    content_sha256 = "abc123..."

    [mcp.spec.headers]
    # Static headers injected on every proxied upstream request.
    # Same $VAR / ${VAR} substitution as [env].
    Authorization = "Bearer $OPENBB_UPSTREAM_TOKEN"
    X-API-Key     = "$OPENBB_UPSTREAM_KEY"

    # Multi-spec mode (alternative): each [mcp.spec.NAME] subtable
    # mounts an independent spec under its own prefix. FastMCP turns
    # the union of all mounted routes into MCP tools; per-spec hooks
    # fire on every tool dispatch into that spec's mount.
    [mcp.spec.equity]
    path = "/etc/openbb/equity.spec"
    mount = "/equity"                          # optional; defaults to "/<name>"
    content_sha256 = "abc..."
    [mcp.spec.equity.headers]
    Authorization = "Bearer $EQUITY_TOKEN"
    [mcp.spec.equity.auth]
    hooks = ["my_pkg.auth:equity_token_check"]
    [mcp.spec.equity.middleware]
    hooks = ["my_pkg.middleware:equity_rate_limit"]

    [mcp.spec.crypto]
    path = "/etc/openbb/crypto.spec"
    [mcp.spec.crypto.headers]
    X-API-Key = "$CRYPTO_KEY"

    [env]
    # Pushed into os.environ before any heavy import runs. Existing
    # shell env vars are NEVER clobbered. Useful in containers to
    # inject OPENBB_* keys without shell exports.
    OPENBB_MCP_HOST = "0.0.0.0"
    # Values support shell-style $VAR / ${VAR} substitution against
    # the current environment.
    OPENBB_GITHUB_TOKEN = "$GITHUB_TOKEN"

The cascade is container-friendly: every layer is optional, the
user-global layer is skipped when HOME is unset, and project-local
discovery walks up from CWD so a single openbb.toml at the container
root configures the whole stack.


All other arguments are passed through as MCPSettings overrides.
"""


def parse_args() -> dict:  # noqa: PLR0912
    """Parse ``sys.argv[1:]`` into the launcher's keyword-arg dict.

    Returns a dict with:

    * ``app`` — the FastAPI instance whose routes will be exposed as MCP
      tools. Either imported from ``--app`` or synthesized from
      ``--spec`` / ``[mcp.spec]``. Absent when neither is supplied
      (``main.py`` falls back to the default ``openbb_core.api.rest_api``
      app).
    * ``transport`` — one of ``streamable-http`` / ``sse`` / ``stdio``.
    * ``mcp_overrides`` — dict of MCP-specific overrides
      (``allowed_categories``, ``default_categories`` etc.) destined for
      ``MCPService.load_with_overrides``.
    * ``uvicorn_overrides`` — remaining flags (host / port /
      ssl-* / etc.) destined for the same overrides dict
      (``MCPService`` separates uvicorn vs MCP fields).
    """

    from openbb_mcp_server.app.bootstrap import import_app  # noqa
    from openbb_mcp_server.app.config import (
        load_launcher_config,
        merge_launcher_kwargs,
        resolve_explicit_config_path,
    )

    args = sys.argv[1:].copy()
    cwd = Path.cwd()
    _kwargs: dict = {}
    for i, arg in enumerate(args):
        if arg == "--help":
            print(LAUNCH_SCRIPT_DESCRIPTION)  # noqa: T201
            sys.exit(0)
        if arg.startswith("--"):
            key = arg[2:]
            if key in ["no-use-colors", "use-colors"]:
                _kwargs["use_colors"] = key == "use-colors"
            elif i + 1 < len(args) and not args[i + 1].startswith("--"):
                value = args[i + 1]
                if isinstance(value, str) and value.lower() in ["false", "true"]:
                    _kwargs[key] = value.lower() == "true"
                else:
                    try:
                        if (value.startswith("{") and value.endswith("}")) or (
                            value.startswith("[") and value.endswith("]")
                        ):
                            _kwargs[key] = json.loads(value)
                        else:
                            _kwargs[key] = value
                    except (json.JSONDecodeError, ValueError):
                        _kwargs[key] = value
            else:
                _kwargs[key] = True

    cli_config_path = _kwargs.pop("config-file", None)
    explicit_path = resolve_explicit_config_path(cli_config_path)
    layered = load_launcher_config(
        explicit_path=explicit_path,
        apply_to_services=False,
        apply_to_env=False,
    )
    _kwargs = merge_launcher_kwargs(_kwargs, layered.get("mcp"))

    # ``--spec`` / ``[mcp.spec].path`` and ``--app`` are mutually exclusive.
    spec_section: dict = (
        (layered.get("mcp") or {}).get("spec") or layered.get("spec") or {}
    )
    multi_specs = _collect_multi_spec_entries(spec_section)
    single_spec_path = spec_section.get("path") or _kwargs.pop("spec", None)
    if (single_spec_path or multi_specs) and _kwargs.get("app"):
        raise ValueError(
            "Error: --spec and --app are mutually exclusive. "
            "--spec synthesizes a proxy app from the spec's commands; "
            "--app imports a user-supplied app. Pick one."
        )

    imported_app = None

    if multi_specs:
        # Multi-spec mode — each ``[mcp.spec.NAME]`` subtable mounts an
        # independent spec under its own prefix. FastMCP walks the
        # parent's union of routes and turns each one into an MCP tool;
        # tool dispatches go through the sub-app's ASGI stack so per-
        # spec hooks (auth, middleware) fire on every tool call.
        from openbb_mcp_server.app.spec import build_apps_from_specs, load_spec

        specs_config: dict[str, dict] = {}
        for name, sub in multi_specs.items():
            sub_path = sub["path"]
            if not Path(sub_path).is_absolute():
                sub_path = str(cwd.joinpath(sub_path).resolve())
            specs_config[name] = {
                "spec": load_spec(
                    sub_path,
                    expected_content_sha256=sub.get("content_sha256"),
                ),
                "mount": sub.get("mount"),
                "base_url_override": sub.get("base_url"),
                "extra_headers": _expand_spec_headers(sub.get("headers")),
                "spec_name": Path(sub_path).name,
                "auth_hooks": (sub.get("auth") or {}).get("hooks"),
                "middleware_hooks": (sub.get("middleware") or {}).get("hooks"),
            }
        imported_app = build_apps_from_specs(specs_config)

    elif single_spec_path:
        from openbb_mcp_server.app.spec import build_app_from_spec, load_spec

        if not Path(single_spec_path).is_absolute():
            single_spec_path = str(cwd.joinpath(single_spec_path).resolve())

        # Optional ``[mcp.spec].content_sha256`` lets ops version-
        # control the expected hash separately from the spec file
        # itself — important for remote distribution where the
        # operator's deployment manifest is the source of truth and
        # the file at ``path`` is just a fetched artifact.
        imported_app = build_app_from_spec(
            load_spec(
                single_spec_path,
                expected_content_sha256=spec_section.get("content_sha256"),
            ),
            base_url_override=spec_section.get("base_url"),
            extra_headers=_expand_spec_headers(spec_section.get("headers")),
            spec_name=Path(single_spec_path).name,
        )

    elif _kwargs.get("app"):
        _app_path = _kwargs.pop("app", None)
        _name = _kwargs.pop("name", "app")
        _factory = _kwargs.pop("factory", False)

        if _is_module_colon_notation(_app_path):
            _app_instance_name = _app_path.rsplit(":", 1)[-1]
            _name = _app_instance_name if _app_instance_name else _name

        if _factory and not _name:
            raise ValueError(
                "Error: The factory function name must be provided to the --name parameter when the factory flag is set."
            )
        imported_app = import_app(_app_path, _name, _factory)

    transport = _kwargs.pop("transport", "streamable-http")

    # MCP-specific knobs that map to MCPSettings overrides.
    _mcp_keys = {
        "allowed-categories",
        "allowed_categories",
        "default-categories",
        "default_categories",
        "tool-discovery",
        "tool_discovery",
        "system-prompt",
        "system_prompt",
        "server-prompts",
        "server_prompts",
    }
    mcp_overrides: dict = {}
    for key in list(_kwargs.keys()):
        if key in _mcp_keys:
            mcp_overrides[key.replace("-", "_")] = _kwargs.pop(key)

    # Anything left is uvicorn / generic settings.
    uvicorn_overrides: dict = {
        key.replace("-", "_"): value for key, value in _kwargs.items()
    }

    return {
        "app": imported_app,
        "transport": transport,
        "mcp_overrides": mcp_overrides,
        "uvicorn_overrides": uvicorn_overrides,
    }
