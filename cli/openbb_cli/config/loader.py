"""Layered configuration loader for openbb-cli.

Resolution order (highest priority last; later layers overwrite earlier ones):

1. Built-in defaults (the empty dict; argparse's own ``default=``)
2. ``[tool.openbb-cli]`` in the nearest ``pyproject.toml`` walking up from CWD
   — meant for libraries/services that depend on ``openbb-cli`` and want to
   ship a known-good baseline (``server`` URL, header file, etc.) with their
   distribution
3. ``~/.openbb_platform/openbb.toml`` — user-global config, in the same
   directory openbb-core uses for ``user_settings.json`` and ``.cli.env``
4. ``openbb.toml`` (or ``.openbb.toml``) in the nearest parent directory —
   project-local override that doesn't pollute ``pyproject.toml``
5. ``--config PATH`` (or ``OPENBB_CLI_CONFIG`` env var) — explicit pointer
   for swapping between setups (``congress.toml``, ``platform.toml``,
   ``staging.toml``, ...)
6. ``.env`` files (default ``~/.openbb_platform/.env`` plus
   ``--env-file PATH``) — loaded into ``os.environ`` so the env-var layer
   below picks them up
7. ``OPENBB_*`` environment variables (handled by the existing argparse
   ``default=os.environ.get(...)`` plumbing in ``runtime.build_parser``)
8. CLI flags

This module covers (1)-(4) and (6); the existing argparse layer covers (7)-(8).

Schema (all keys optional, all sections optional)::

    server = "https://api.congress.gov"
    spec = "./congress.spec"
    openapi-path = "/openapi.json"
    output-mode = "rich"

    [headers]
    "User-Agent" = "my-app/1.0"
    Authorization = "Bearer ..."

    [query]
    api_key = "..."

The ``[headers]`` and ``[query]`` tables are merged across layers (deep
merge); scalar settings overwrite. Both kebab-case and snake_case keys are
accepted at the top level.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):  # pragma: no cover — version-conditional import
    import tomllib
else:  # pragma: no cover — exercised only on the 3.10 backport path
    import tomli as tomllib  # ty: ignore[unresolved-import]

DEFAULT_CONFIG_NAMES: tuple[str, ...] = ("openbb.toml", ".openbb.toml")
PYPROJECT_NAME = "pyproject.toml"
PYPROJECT_TABLE: tuple[str, ...] = ("tool", "openbb-cli")
EXPLICIT_CONFIG_ENV = "OPENBB_CLI_CONFIG"
EXPLICIT_ENV_FILE_ENV = "OPENBB_CLI_ENV_FILE"

# The canonical openbb-platform user directory — same one openbb-core uses
# for ``user_settings.json`` / ``system_settings.json``, and the same one
# the CLI already uses for ``.cli.env`` and ``.cli.his``. Defining it here
# instead of importing from ``openbb_cli.config.constants`` keeps this
# module dependency-light (loader runs before settings are constructed).
USER_OPENBB_DIR = Path.home() / ".openbb_platform"
USER_OPENBB_TOML_NAMES: tuple[str, ...] = ("openbb.toml", ".openbb.toml")
USER_OPENBB_ENV_NAME = ".env"


def _walk_up(start: Path | None = None):
    cur = (start or Path.cwd()).resolve()
    yield cur
    yield from cur.parents


def _read_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def _find_first(start: Path | None, names: tuple[str, ...]) -> Path | None:
    for parent in _walk_up(start):
        for name in names:
            candidate = parent / name
            if candidate.is_file():
                return candidate
    return None


def _find_pyproject_section(start: Path | None = None) -> dict[str, Any]:
    """Find the nearest ancestor ``pyproject.toml`` with ``[tool.openbb-cli]``.

    Returns the section dict, or ``{}`` if no matching file is found.
    """
    py = _find_first(start, (PYPROJECT_NAME,))
    if py is None:
        return {}
    data = _read_toml(py)
    node: Any = data
    for key in PYPROJECT_TABLE:
        if not isinstance(node, dict) or key not in node:
            return {}
        node = node[key]
    return node if isinstance(node, dict) else {}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> None:
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


def _normalize_keys(d: dict[str, Any]) -> dict[str, Any]:
    """Normalize top-level kebab-case keys to snake_case for argparse ``dest`` matching.

    Nested ``[headers]`` / ``[query]`` tables keep their original keys —
    those are user-supplied strings (HTTP header names, query-param names)
    that must round-trip exactly.
    """
    return {k.replace("-", "_"): v for k, v in d.items()}


def _user_global_toml() -> Path | None:
    """Locate ``~/.openbb_platform/openbb.toml`` (or the dotted variant)."""
    if not USER_OPENBB_DIR.is_dir():
        return None
    for name in USER_OPENBB_TOML_NAMES:
        candidate = USER_OPENBB_DIR / name
        if candidate.is_file():
            return candidate
    return None


def load_config(
    explicit_path: str | os.PathLike[str] | None = None,
    *,
    start: Path | None = None,
) -> dict[str, Any]:
    """Resolve the layered openbb-cli configuration.

    Layers, lowest to highest priority:

    * ``[tool.openbb-cli]`` from the nearest ancestor ``pyproject.toml``
    * ``~/.openbb_platform/openbb.toml`` (or ``.openbb.toml``) — the user-
      global config in the same directory openbb-core uses for
      ``user_settings.json``
    * ``openbb.toml`` / ``.openbb.toml`` in the nearest ancestor directory
    * ``explicit_path`` if provided, otherwise ``$OPENBB_CLI_CONFIG``

    Returns a single merged dict with normalized top-level keys (kebab-case
    converted to snake_case). Nested header / query tables keep original
    casing. Returns ``{}`` when no layer is found — callers should fall
    back to env / argparse defaults.
    """
    layers: list[dict[str, Any]] = [_find_pyproject_section(start)]
    user_toml = _user_global_toml()
    if user_toml is not None:
        layers.append(_read_toml(user_toml))
    project_toml = _find_first(start, DEFAULT_CONFIG_NAMES)
    if project_toml is not None:
        layers.append(_read_toml(project_toml))
    explicit = explicit_path or os.environ.get(EXPLICIT_CONFIG_ENV)
    if explicit:
        path = Path(explicit).expanduser()
        if path.is_file():
            layers.append(_read_toml(path))
    merged: dict[str, Any] = {}
    for layer in layers:
        _deep_merge(merged, _normalize_keys(layer))
    return merged


def render_config_template(active: dict[str, Any] | None = None) -> str:
    """Render a documented TOML template covering every supported setting.

    Each key has a comment block describing what it does and which env var
    /CLI flag also sets it. Settings with no value resolved from any layer
    are emitted as commented-out lines so the file is valid TOML out of
    the box but the optional surface is visible.

    ``active`` (typically ``load_config()`` output) annotates each line
    with the currently-resolved value, so dropping the template into
    ``~/.openbb_platform/openbb.toml`` and tweaking it is straightforward.
    """
    a = active or {}
    headers = a.get("headers") or {}
    query = a.get("query") or {}

    def line(key: str, value: Any, doc: str, env: str, cli: str) -> str:
        commented = "# " if value in (None, "", []) else ""
        rendered = _toml_quote(value) if value not in (None, "", []) else '""'
        return (
            f"# {doc}\n"
            f"#   env: {env}\n"
            f"#   flag: {cli}\n"
            f"{commented}{key} = {rendered}\n\n"
        )

    parts: list[str] = [
        "# openbb-cli configuration template.\n"
        "#\n"
        "# Drop this file at any of the following discovery locations:\n"
        "#   * ~/.openbb_platform/openbb.toml          (user-global)\n"
        "#   * ./openbb.toml or ./.openbb.toml         (project-local; walks up from CWD)\n"
        "#   * [tool.openbb-cli] in pyproject.toml     (ships with a dev project)\n"
        "#   * --config PATH or $OPENBB_CLI_CONFIG     (explicit, swappable)\n"
        "#\n"
        "# Resolution order (lowest → highest priority):\n"
        "#   defaults -> pyproject -> ~/.openbb_platform/openbb.toml -> ./openbb.toml\n"
        "#   -> --config -> .env files -> OPENBB_* env vars -> CLI flags\n"
        "#\n"
        "# Lines starting with # are commented out. Either uncomment to set a value\n"
        "# (and the matching env/CLI override still wins), or leave commented to\n"
        "# fall through to the next layer.\n\n",
    ]

    parts.append(
        line(
            "server",
            a.get("server"),
            "HTTP backend URL. When set, dispatch goes via openbb-platform-api over HTTP\n"
            "# instead of the in-process LocalDispatcher.",
            "OPENBB_SERVER_URL",
            "--server",
        )
    )
    parts.append(
        line(
            "spec",
            a.get("spec"),
            "Path to a precomputed .spec file (built via --generate-spec). When set, dispatch\n"
            "# skips the OpenAPI fetch + parse on every call.",
            "OPENBB_SPEC_PATH",
            "--spec",
        )
    )
    parts.append(
        line(
            "openapi-path",
            a.get("openapi_path"),
            "Path (or full URL) to the OpenAPI document on the server. Defaults to\n"
            "# /openapi.json. Servers that publish under a different name (e.g. NY Fed at\n"
            "# /static/docs/markets-api.yml) need this.",
            "(none)",
            "--openapi-path",
        )
    )
    parts.append(
        line(
            "header-file",
            a.get("header_file"),
            "JSON object on disk supplying additional headers. --header flags and the\n"
            "# [headers] table below take precedence on conflicts.",
            "OPENBB_HEADER_FILE",
            "--header-file",
        )
    )
    parts.append(
        line(
            "query-param-file",
            a.get("query_param_file"),
            "JSON object on disk supplying additional query params. --query-param flags,\n"
            "# OPENBB_HTTP_QUERY_* env vars, and the [query] table below take precedence.",
            "OPENBB_QUERY_PARAM_FILE",
            "--query-param-file",
        )
    )
    parts.append(
        line(
            "output",
            a.get("output"),
            "Output spec path for --generate-spec. Default: openbb.spec",
            "(none)",
            "--output",
        )
    )
    parts.append(
        line(
            "batch-concurrency",
            a.get("batch_concurrency"),
            "Maximum number of concurrent in-flight dispatches in --batch mode.\n"
            "# Higher values raise throughput against fast servers; lower values give\n"
            "# back-pressure when an upstream rate-limits. Default: 8.",
            "OPENBB_CLI_BATCH_CONCURRENCY",
            "--batch-concurrency",
        )
    )
    parts.append(
        "# ── REPL display preferences (most-tweaked subset of [settings]) ─────────\n"
        "# These are the four interactive-output knobs users hit constantly. Setting\n"
        "# them at the top level overrides anything in the [settings] block below.\n"
        "# Every other Settings field is still available under [settings].\n\n"
    )
    parts.append(
        line(
            "output-mode",
            a.get("output_mode"),
            "Output display mode for command results: rich (terminal table with\n"
            "# colors), json (NDJSON-friendly), tsv (line-oriented plain text), or\n"
            "# html (browser viewer). Defaults to ``tsv`` for non-TTY shells and\n"
            "# auto-flips to ``rich`` when ``-i`` is used.",
            "OPENBB_OUTPUT_MODE",
            "(/settings/ output)",
        )
    )
    parts.append(
        line(
            "flair",
            a.get("flair"),
            "Emoji flair shown in the REPL prompt.",
            "OPENBB_FLAIR",
            "(/settings/ flair)",
        )
    )
    parts.append(
        line(
            "timezone",
            a.get("timezone"),
            "Time zone displayed in the REPL prompt and applied to date-typed\n"
            "# outputs.",
            "OPENBB_TIMEZONE",
            "(/settings/ timezone)",
        )
    )
    parts.append(
        line(
            "rich-style",
            a.get("rich_style"),
            "Rich theme name. Looks up ``<name>.richstyle.json`` from the styles\n"
            "# asset directory; ``dark`` and ``light`` ship out of the box.",
            "OPENBB_RICH_STYLE",
            "(/settings/ console_style)",
        )
    )

    parts.append(
        "# Custom HTTP headers sent on every dispatched request and on the OpenAPI fetch.\n"
        "# Repeat the table to add more entries. --header flags and --header-file still\n"
        "# override these on conflicts.\n"
    )
    if headers:
        parts.append("[headers]\n")
        for k, v in headers.items():
            parts.append(f"{_toml_quote(k)} = {_toml_quote(v)}\n")
        parts.append("\n")
    else:
        parts.append("# [headers]\n")
        parts.append('# Authorization = "Bearer ..."\n')
        parts.append('# "X-Tenant" = "acme"\n\n')

    parts.append(
        "# Query parameters injected on every request. Useful for APIs (e.g.\n"
        "# https://api.congress.gov) that authenticate via ?api_key=... on every call.\n"
        "# OPENBB_HTTP_QUERY_* env vars, --query-param flags, and --query-param-file\n"
        "# still override these on conflicts.\n"
    )
    if query:
        parts.append("[query]\n")
        for k, v in query.items():
            parts.append(f"{_toml_quote(k)} = {_toml_quote(v)}\n")
        parts.append("\n")
    else:
        parts.append("# [query]\n")
        parts.append('# api_key = "..."\n\n')

    parts.append(_render_settings_section(a.get("settings") or {}))

    return "".join(parts)


_SETTINGS_INTERNAL_FIELDS: frozenset[str] = frozenset(
    {
        # Set from package metadata at import time — not user-configurable
        "VERSION",
        # State the CLI flips itself; persisting it in config is meaningless
        "PREVIOUS_USE",
        # Vestige of the legacy in-process REPL's dev-vs-prod toggle; not
        # meaningful on the spec-driven dispatcher path
        "DEV_BACKEND",
    }
)
_SETTINGS_DEV_FIELDS: tuple[str, ...] = (
    "DEBUG_MODE",
    "TEST_MODE",
)


def _render_settings_section(active: dict[str, Any]) -> str:
    """Render the ``[settings]`` table from the live ``Settings`` model.

    Walks every Settings field (skipping internal-only ones like ``VERSION``
    that aren't user-configurable) and emits a comment block + commented-out
    line per field. Fields with ``json_schema_extra.command`` come from the
    documented user-facing surface; ``DEBUG_MODE`` / ``DEV_BACKEND`` /
    ``TEST_MODE`` lack that marker (they're set via ``--debug`` / ``--dev``
    CLI flags) but still belong here so the template surface is complete.
    Picks up overrides from ``active`` so values already set in any config
    layer surface uncommented.
    """
    from openbb_cli.models.settings import Settings

    out: list[str] = [
        "# Interactive REPL / display settings — applied via OPENBB_* env vars\n"
        "# under the hood. Real shell exports always win; --config / project /\n"
        "# user-global TOMLs cascade in the documented order.\n"
        "[settings]\n"
    ]
    field_items = sorted(
        Settings.model_fields.items(),
        key=lambda kv: kv[0],
    )
    for name, field in field_items:
        if name in _SETTINGS_INTERNAL_FIELDS:
            continue
        extra = field.json_schema_extra or {}
        is_documented = isinstance(extra, dict) and "command" in extra
        is_dev_flag = name in _SETTINGS_DEV_FIELDS
        if not is_documented and not is_dev_flag:
            continue
        kebab = name.lower().replace("_", "-")
        active_value = active.get(kebab) if isinstance(active, dict) else None
        if active_value is None and isinstance(active, dict):
            active_value = active.get(name.lower())
        env_key = f"OPENBB_{name}"
        rendered_default = (
            _toml_quote(field.default) if field.default is not None else '""'
        )
        rendered_active = (
            _toml_quote(active_value) if active_value is not None else None
        )
        commented = "# " if rendered_active is None else ""
        value = rendered_active if rendered_active is not None else rendered_default
        out.append(
            f"# {field.description or name}\n"
            f"#   env: {env_key}\n"
            f"#   default: {rendered_default}\n"
            f"{commented}{kebab} = {value}\n\n"
        )
    return "".join(out)


def _toml_quote(value: Any) -> str:
    """Render a Python value as a TOML literal."""
    if isinstance(value, str):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return '"' + str(value) + '"'


# Top-level config keys that map directly to a Settings ``OPENBB_*`` env var
# (i.e. don't go through argparse). Promoted out of ``[settings]`` for
# discoverability — having ``output-mode = "json"`` at the top of openbb.toml
# is far more obvious than digging through the alphabetized [settings] block.
_TOP_LEVEL_SETTINGS_PROMOTIONS: dict[str, str] = {
    "output_mode": "OPENBB_OUTPUT_MODE",
    "flair": "OPENBB_FLAIR",
    "timezone": "OPENBB_TIMEZONE",
    "rich_style": "OPENBB_RICH_STYLE",
}


def apply_settings_to_env(
    config: dict[str, Any] | None,
) -> list[str]:
    """Inject ``[settings]`` and promoted top-level keys into ``os.environ`` as ``OPENBB_*``.

    The Settings model already loads from ``OPENBB_*`` env vars (see
    ``Settings.from_env``), so converting each TOML key to its uppercase
    snake-case env equivalent and seeding ``os.environ`` (via ``setdefault``)
    makes the layered config reach Settings without coupling the loader to
    the model. Real shell exports stay authoritative.

    Top-level promoted keys (``output-mode``, ``flair``, ``timezone``,
    ``rich-style``) win over the ``[settings]`` table — they're explicit,
    user-promoted shortcuts, so a user who sets both clearly meant the
    top-level one.

    Returns the list of env var names actually set, so callers can log
    discovery if useful.
    """
    if not config:
        return []
    applied: list[str] = []

    def _set(env_key: str, value: Any) -> None:
        if env_key in os.environ:
            return
        if isinstance(value, bool):
            os.environ[env_key] = "True" if value else "False"
        else:
            os.environ[env_key] = str(value)
        applied.append(env_key)

    # [settings] table first — top-level shortcuts then override.
    for key, value in (config.get("settings") or {}).items():
        _set("OPENBB_" + key.replace("-", "_").upper(), value)

    for key, env_key in _TOP_LEVEL_SETTINGS_PROMOTIONS.items():
        if key in config:
            # Top-level wins: clear any [settings]-injected value.
            os.environ.pop(env_key, None)
            _set(env_key, config[key])

    return applied


def load_env_files(
    explicit_path: str | os.PathLike[str] | None = None,
) -> list[Path]:
    """Apply ``.env`` files into ``os.environ`` for subsequent env-var lookups.

    Argparse defaults, ``OPENBB_HTTP_QUERY_*`` scanning, etc. all read
    ``os.environ``, so the dotfile values must land before they run.

    Layers, applied in order so later files override earlier ones, and any
    pre-existing ``os.environ`` values still win (real shell exports always
    beat dotfiles):

    * ``~/.openbb_platform/.env`` — the canonical openbb-platform .env
    * ``explicit_path`` if provided, otherwise ``$OPENBB_CLI_ENV_FILE``

    Uses ``python-dotenv`` (already a CLI runtime dep). Silently skips
    missing files. Returns the list of files actually loaded so callers can
    log / surface the discovery if useful.
    """
    from dotenv import dotenv_values

    candidates: list[Path] = []
    user_env = USER_OPENBB_DIR / USER_OPENBB_ENV_NAME
    if user_env.is_file():
        candidates.append(user_env)
    explicit = explicit_path or os.environ.get(EXPLICIT_ENV_FILE_ENV)
    if explicit:
        path = Path(explicit).expanduser()
        if path.is_file():
            candidates.append(path)

    loaded: list[Path] = []
    for path in candidates:
        for k, v in dotenv_values(path).items():
            if v is None:
                continue
            os.environ.setdefault(k, v)
        loaded.append(path)
    return loaded
