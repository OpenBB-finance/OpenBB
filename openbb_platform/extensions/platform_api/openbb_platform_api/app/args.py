"""Command-line argument parsing for ``openbb-api``.

Pulled out of ``utils/api.py`` so the CLI parsing path can be exercised
in isolation. ``parse_args`` reads ``sys.argv[1:]`` and returns a dict
of normalized kwargs; the entry-point in ``app/app.py`` consumes that
dict to wire up the FastAPI app and pass remaining flags through to
``uvicorn.run``.
"""

import json
import logging
import os
import sys
from pathlib import Path

_spec_headers_logger = logging.getLogger("openbb_platform_api.spec.headers")


def _collect_multi_spec_entries(spec_section: dict) -> dict[str, dict]:
    """Pick out the ``[spec.NAME]`` subtables that look like spec entries.

    Multi-spec form uses ``[spec.equity]`` / ``[spec.crypto]`` / ...
    subtables, each carrying its own ``path`` (and optional ``mount``,
    ``base_url``, ``content_sha256``, ``[spec.NAME.headers]``, etc.).

    A subtable counts as a multi-spec entry only when:

    * The value is a dict — protects against scalar reserved keys
      (``path``, ``base_url``, ``content_sha256``, ``mount``,
      ``headers`` are single-spec siblings, not entries).
    * The dict has a ``path`` key — keeps non-spec sibling tables
      (``[spec.headers]`` from the single-spec form, etc.) out of the
      multi-spec set.
    """
    out: dict[str, dict] = {}
    for name, value in spec_section.items():
        if isinstance(value, dict) and isinstance(value.get("path"), str):
            out[name] = value
    return out


def _expand_spec_headers(
    raw_headers: dict | None,
) -> dict[str, str]:
    """Expand ``$VAR`` / ``${VAR}`` refs in a ``[spec.headers]`` table.

    Each value goes through the same substitution logic ``[env]`` uses
    (against the current ``os.environ``), so credentials live in one
    place — the orchestrator-supplied env vars — and the launcher TOML
    just maps them to upstream header names. Entries with unresolved
    references are SKIPPED with a warning rather than shipped to the
    upstream as literal ``"$MISSING"`` values. Non-string keys (which
    real TOML can't produce, but defensive code keeps us honest) are
    silently dropped.
    """
    from openbb_platform_api.app.config import expand_env_refs

    if not raw_headers:
        return {}
    expanded: dict[str, str] = {}
    for header_name, header_value in raw_headers.items():
        if not isinstance(header_name, str):
            continue
        substituted, missing = expand_env_refs(str(header_value))
        if missing:
            _spec_headers_logger.warning(
                "Skipping [spec.headers] entry %s: references "
                "unresolved variable(s) %s",
                header_name,
                ", ".join(missing),
            )
            continue
        expanded[header_name] = substituted
    return expanded


LAUNCH_SCRIPT_DESCRIPTION = """
Serve the OpenBB Platform API.


Launcher specific arguments:

    --app                           Absolute path to the Python file with the target FastAPI instance. Default is the installed OpenBB Platform API.
    --name                          Name of the FastAPI instance in the app file. Default is 'app'.
    --factory                       Flag to indicate if the app name is a factory function. Default is 'false'.
    --editable                      Flag to make widgets.json an editable file that can be modified during runtime. Default is 'false'.
    --build                         If the file already exists, changes prompt action to overwrite/append/ignore. Only valid when --editable true.
    --no-build                      Do not build the widgets.json file. Use this flag to load an existing widgets.json file without checking for updates.
    --exclude                       JSON encoded list of API paths to exclude from widgets.json. Disable entire routes with '*' - e.g. '["/api/v1/*"]'.
    --no-filter                     Do not filter out widgets in widget_settings.json file.
    --widgets-json                  Absolute/relative path to use as the widgets.json file. Default is ~/envs/{env}/assets/widgets.json, when --editable is 'true'.
    --apps-json                     Absolute/relative path to use as the apps.json file. Default is ~/OpenBBUserData/workspace_apps.json.
    --agents-json                   Absolute/relative path to use as the agents.json file. Including this will add the /agents endpoint to the API.
    --config-file                   Absolute/relative path to a TOML config file. Highest-priority TOML layer in the cascade.
                                    Also honored via $OPENBB_API_CONFIG or $OPENBB_CONFIG. CLI flags still override TOML values.
    --spec                          Absolute/relative path to an `openbb-cli` generated `.spec` file. Synthesizes a Workspace-compatible
                                    backend that proxies every command in the spec to its `base_url`. widgets.json / apps.json are
                                    generated from the spec's metadata. Mutually exclusive with --app.


Config file (`openbb.toml`) — runtime defaults + env injection:

The launcher reads the same layered TOML cascade openbb-core ships with
(pyproject → user-global → project → explicit → .env → real env vars).
Two extra tables are launcher-specific:

    [launcher]
    # Default values for any of the CLI flags above. Use the same
    # names (TOML accepts hyphens). CLI flags ALWAYS win over TOML.
    host = "0.0.0.0"
    port = 6900
    agents-json = "/etc/openbb/agents.json"
    exclude = ["/api/v1/admin/*"]

    [env]
    # Pushed into os.environ before any heavy import runs. Existing
    # shell env vars are NEVER clobbered. Useful in containers to
    # inject OPENBB_* keys without shell exports.
    OPENBB_API_HOST = "0.0.0.0"
    OPENBB_API_PORT = "6900"
    # Values support shell-style $VAR / ${VAR} substitution against
    # the current environment, so you can map orchestrator-injected
    # secrets (Kubernetes, docker run -e, CI tokens) to the names the
    # application expects. Entries with unresolved references are
    # SKIPPED with a warning rather than set to a literal "$MISSING".
    OPENBB_GITHUB_TOKEN = "$GITHUB_TOKEN"
    OPENBB_API_URL      = "https://${HOST}:${PORT}/v1"

    [spec]
    # Single-spec mode: spec-driven proxy with one upstream target.
    # The path can also be supplied via --spec on the CLI; the rest
    # of the per-spec config (``base_url``, ``content_sha256``,
    # ``headers``) ONLY lives here.
    path = "/etc/openbb/cli.spec"
    base_url = "https://upstream.example.com"  # optional override of the spec's recorded base_url
    # Optional pinned SHA-256. When set, the launcher recomputes the
    # spec's canonical-JSON hash and refuses to start unless it
    # matches. Lets ops version-control the expected hash separately
    # from the spec file itself — useful for remote-distributed
    # specs whose payload is fetched at boot but whose version is
    # pinned by the deployment manifest.
    content_sha256 = "abc123..."

    [spec.headers]
    # Static headers injected on every proxied upstream request.
    # Override matching incoming-request headers — credential
    # injection point. Same $VAR / ${VAR} substitution as [env].
    Authorization = "Bearer $OPENBB_UPSTREAM_TOKEN"
    X-API-Key     = "$OPENBB_UPSTREAM_KEY"

    # Multi-spec mode (alternative to single-spec): each [spec.NAME]
    # subtable mounts an independent spec under its own prefix. The
    # launcher serves a parent FastAPI whose routes union all mounts.
    # Every per-spec key (base_url, content_sha256, headers, auth,
    # middleware) is scoped to that subtable.
    [spec.equity]
    path = "/etc/openbb/equity.spec"
    mount = "/equity"                          # optional; defaults to "/<name>"
    base_url = "https://equity.example.com"
    content_sha256 = "abc..."
    [spec.equity.headers]
    Authorization = "Bearer $EQUITY_TOKEN"
    [spec.equity.auth]
    hooks = ["my_pkg.auth:equity_token_check"]
    [spec.equity.middleware]
    hooks = ["my_pkg.middleware:equity_rate_limit"]

    [spec.crypto]
    path = "/etc/openbb/crypto.spec"
    [spec.crypto.headers]
    X-API-Key = "$CRYPTO_KEY"

    [middleware]
    # HTTP middleware applied to every inbound server request.
    # Each entry is a "module:async_callable" reference resolved via
    # the standard import system. The callable signature must be
    # ``async def fn(request, call_next): ...``. List order is
    # outermost-to-innermost: the first entry sees the request first
    # on the way in and the response last on the way out.
    hooks = [
        "my_pkg.middleware:auth_middleware",
        "my_pkg.middleware:request_logger",
    ]

The cascade is container-friendly: every layer is optional, the
user-global layer is skipped when HOME is unset, and project-local
discovery walks up from CWD so a single openbb.toml at the container
root configures the whole stack.


The FastAPI app instance can be imported to another script, modified, and launched by using the --app argument.

If the path to the app file is not absolute, it will be resolved relative to the current working directory.

Imported with:

>>> from openbb_platform_api.main import app
>>>
>>> @app.get()
>>> async def hello(input: str = "Hello") -> str:
>>>     '''Widget description created by doctring.'''
>>>     return f"You entered: {input}"

Launched with:

>>> openbb-api --app /path/to/some_file.py

The app instance name can be defined by either the --name argument, or by referencing the module name, for example:

>>> openbb-api --app some_file.py:main --factory

A name must be set when using the factory flag.

All other arguments will be passed to uvicorn. Here are the most common ones:

    --host TEXT                     Host IP address or hostname.
                                      [default: 127.0.0.1]
    --port INTEGER                  Port number.
                                      [default: 6900]
    --ssl-keyfile TEXT              SSL key file.
    --ssl-certfile TEXT             SSL certificate file.
    --ssl-keyfile-password TEXT     SSL keyfile password.
    --ssl-version INTEGER           SSL version to use.
                                      (see stdlib ssl module's)
                                      [default: 17]
    --ssl-cert-reqs INTEGER         Whether client certificate is required.
                                      (see stdlib ssl module's)
                                      [default: 0]
    --ssl-ca-certs TEXT             CA certificates file.
    --ssl-ciphers TEXT              Ciphers to use.
                                      (see stdlib ssl module's)
                                      [default: TLSv1]

Run `uvicorn --help` to get the full list of arguments.
"""  # noqa: E501


def parse_args() -> dict:  # noqa: PLR0912
    """Parse ``sys.argv[1:]`` into the launcher's keyword-arg dict.

    Recognized launcher flags get normalized (booleans, JSON-encoded
    lists, ``app`` → imported FastAPI instance, ``agents-json`` /
    ``widgets-json`` / ``apps-json`` paths resolved relative to ``cwd``).
    Anything else passes through verbatim and ultimately reaches
    ``uvicorn.run`` as keyword arguments.
    """

    from openbb_platform_api.app.bootstrap import import_app  # noqa
    from openbb_platform_api.app.config import (
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
                elif key == "exclude":
                    _kwargs[key] = json.loads(value)
                else:
                    _kwargs[key] = value
            else:
                _kwargs[key] = True

    # Layered TOML config — overlay ``[launcher]`` defaults under the
    # CLI kwargs (CLI always wins). The explicit-path slot is fed by
    # ``--config-file`` here, or falls back to ``$OPENBB_API_CONFIG``
    # / ``$OPENBB_CONFIG`` when the flag isn't supplied.
    cli_config_path = _kwargs.pop("config-file", None)
    explicit_path = resolve_explicit_config_path(cli_config_path)
    # ``apply_to_*=False`` here — ``main.py`` already ran the bootstrap
    # and applied env / services. We just want the merged dict to
    # extract the ``[launcher]`` defaults from.
    layered = load_launcher_config(
        explicit_path=explicit_path,
        apply_to_services=False,
        apply_to_env=False,
    )
    _kwargs = merge_launcher_kwargs(_kwargs, layered.get("launcher"))

    # ``--spec`` (or ``[spec] path``) and ``--app`` are mutually
    # exclusive — both supply the FastAPI ``app`` instance the
    # launcher serves. ``--spec`` synthesizes one from a digested
    # OpenAPI snapshot; ``--app`` imports a user-written one. Reject
    # combinations early so the failure mode is a clear startup error.
    spec_section: dict = layered.get("spec") or {}
    multi_specs = _collect_multi_spec_entries(spec_section)
    single_spec_path = spec_section.get("path") or _kwargs.pop("spec", None)
    if (single_spec_path or multi_specs) and _kwargs.get("app"):
        raise ValueError(
            "Error: --spec and --app are mutually exclusive. "
            "--spec synthesizes a proxy app from the spec's commands; "
            "--app imports a user-supplied app. Pick one."
        )

    if multi_specs:
        # Multi-spec mode — every ``[spec.NAME]`` subtable becomes a
        # mounted sub-app. The launcher serves a single parent FastAPI
        # whose routes are union-ed from all mounts.
        from typing import Any

        from openbb_platform_api.app.spec import build_apps_from_specs, load_spec

        specs_config: dict[str, dict[str, Any]] = {}
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
        _kwargs["app"] = build_apps_from_specs(specs_config)

    elif single_spec_path:
        from openbb_platform_api.app.spec import build_app_from_spec, load_spec

        if not Path(single_spec_path).is_absolute():
            single_spec_path = str(cwd.joinpath(single_spec_path).resolve())

        # Optional ``[spec].content_sha256`` lets ops version-control
        # the expected hash separately from the spec file itself —
        # important for remote distribution where the operator's
        # deployment manifest is the source of truth and the file in
        # ``[spec].path`` is just a fetched artifact.
        _kwargs["app"] = build_app_from_spec(
            load_spec(
                single_spec_path,
                expected_content_sha256=spec_section.get("content_sha256"),
            ),
            base_url_override=spec_section.get("base_url"),
            extra_headers=_expand_spec_headers(spec_section.get("headers")),
            # Full filename ("fertilizer.spec" for
            # "/etc/openbb/fertilizer.spec") — used as the source
            # citation on every auto-generated widget so dashboards
            # don't display a generic "Custom" label for every column.
            spec_name=Path(single_spec_path).name,
        )

    elif _kwargs.get("app"):
        _app_path = _kwargs.pop("app", None)
        _name = _kwargs.pop("name", "app")
        _factory = _kwargs.pop("factory", False)

        def _is_module_colon_notation(path: str) -> bool:
            if ":" not in path:
                return False
            if len(path) >= 2 and path[1] == ":" and path[0].isalpha():
                return path.count(":") > 1
            return True

        if _is_module_colon_notation(_app_path):
            _app_instance_name = _app_path.split(":")[-1]
            _name = _app_instance_name if _app_instance_name else _name

        if _factory and not _name:
            raise ValueError(
                "Error: The factory function name must be provided to the --name parameter when the factory flag is set."
            )
        _kwargs["app"] = import_app(_app_path, _name, _factory)

    if isinstance(_kwargs.get("exclude"), str):
        _kwargs["exclude"] = [_kwargs["exclude"]]

    if _kwargs.get("agents-json") or _kwargs.get("copilots-path"):
        _agents_path = _kwargs.pop("agents-json", None) or _kwargs.pop(
            "copilots-path", None
        )

        if not str(_agents_path).endswith(".json"):
            # ``os.path.join`` produces platform-native separators so the
            # path round-trips cleanly through ``Path``/``str`` on
            # Windows — the prior f-string with a literal ``/`` produced
            # mixed ``C:\dir/agents.json`` on Windows.
            _agents_path = os.path.join(str(_agents_path), "agents.json")

        if str(_agents_path).startswith("./"):
            _agents_path = str(cwd.joinpath(_agents_path).resolve())

        _kwargs["agents-json"] = _agents_path

    if _kwargs.get("widgets-json") or _kwargs.get("widgets-path"):
        _widgets_path = _kwargs.pop("widgets-json", None) or _kwargs.pop(
            "widgets-path", None
        )

        # If it's a file (endswith .json), use as is; else treat as directory and append widgets.json
        if str(_widgets_path).endswith(".json"):
            widgets_file_path = _widgets_path
        else:
            # Platform-native join — see ``apps-json`` branch above for
            # rationale (avoids mixed ``C:\dir/widgets.json`` on Windows).
            widgets_file_path = os.path.join(str(_widgets_path), "widgets.json")

        # Resolve relative paths to absolute
        if str(widgets_file_path).startswith("./"):
            widgets_file_path = str(cwd.joinpath(widgets_file_path).resolve())

        _kwargs["widgets-json"] = widgets_file_path

    if _kwargs.get("widgets-json"):
        _kwargs["editable"] = True
        # If the file already exists, we assume that it is already built.
        if os.path.exists(_kwargs["widgets-json"]):
            _kwargs["no-build"] = True

    # Handle apps-json and templates-path in the same way as widgets-path
    if _kwargs.get("apps-json") or _kwargs.get("templates-path"):
        _apps_path = _kwargs.pop("apps-json", None) or _kwargs.pop(
            "templates-path", None
        )

        # If it's a file (endswith .json), use as is; else treat as directory and append apps.json
        if str(_apps_path).endswith(".json"):
            apps_file_path = _apps_path
        else:
            # ``os.path.join`` gives platform-native separators (``\`` on
            # Windows, ``/`` elsewhere), so the produced string round-trips
            # through ``str(Path(...))`` cleanly on every OS — the previous
            # f-string concatenation hard-coded ``/`` and produced mixed
            # separators on Windows like ``C:\tmp\dir/apps.json``.
            possible_workspace_file = os.path.join(
                str(_apps_path), "workspace_apps.json"
            )
            if os.path.isfile(possible_workspace_file):
                apps_file_path = possible_workspace_file
            else:
                apps_file_path = os.path.join(str(_apps_path), "apps.json")

        # Resolve relative paths to absolute
        if str(apps_file_path).startswith("./"):
            apps_file_path = str(cwd.joinpath(apps_file_path).resolve())

        _kwargs["apps-json"] = apps_file_path

    return _kwargs
