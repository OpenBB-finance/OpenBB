"""Launcher TOML config bootstrap for ``openbb-mcp``.

Hooks the MCP server into the same layered TOML cascade
``openbb-core`` ships with (pyproject → user-global → project →
explicit → .env → real-shell env vars), and surfaces three extra
tables the core loader doesn't itself consume:

* ``[mcp]`` — defaults for the ``openbb-mcp`` CLI flags (``host``,
  ``port``, ``transport``, ``app``, ``spec``, ``allowed-categories``,
  ``default-categories``, etc.). CLI flags always win; the TOML
  provides fallbacks.
* ``[mcp.spec]`` — spec-driven backend table (``path``, ``base_url``,
  ``[mcp.spec.headers]`` for credential injection). Mirrors
  ``[spec]`` in ``openbb-platform-api`` so the same deployment shape
  works for both the REST and MCP surfaces.
* ``[env]`` — extra environment variables pushed into ``os.environ``
  before any heavy import runs. Lets containers inject API keys and
  other ``OPENBB_*`` knobs without shell exports. Real shell env vars
  always win (we never clobber a value the operator already set).

The ``--config-file <path>`` CLI flag and the ``OPENBB_MCP_CONFIG`` /
``OPENBB_API_CONFIG`` / ``OPENBB_CONFIG`` env vars all map to the
same explicit-path slot in the cascade — the highest-priority TOML
layer below real env vars.
"""

from __future__ import annotations

import logging
import os
import re
import sys
from collections.abc import Mapping, MutableMapping
from typing import Any

logger = logging.getLogger("openbb_mcp_server.config")

#: Match ``$VAR`` and ``${VAR}`` references in ``[env]`` /
#: ``[mcp.spec.headers]`` values. ``$`` not followed by a valid
#: identifier (e.g. ``$5``, ``$ ``, ``$@``) is left untouched, so
#: literal-dollar use cases still work.
_ENV_REF_PATTERN = re.compile(
    r"\$\{(?P<braced>[A-Za-z_][A-Za-z0-9_]*)\}"
    r"|\$(?P<bare>[A-Za-z_][A-Za-z0-9_]*)"
)

#: Env vars that, when set, point ``load_launcher_config`` at an
#: explicit TOML to use as the highest-priority layer in the cascade.
#: The MCP-specific name comes first; the API-server and core slots
#: are honored too so a single env var can configure the whole stack.
EXPLICIT_CONFIG_ENVS: tuple[str, ...] = (
    "OPENBB_MCP_CONFIG",
    "OPENBB_API_CONFIG",
    "OPENBB_CONFIG",
)

#: CLI flag that supplies an explicit config path. Detected by
#: ``extract_config_file_from_argv`` before the launcher's full
#: ``parse_args`` runs.
CONFIG_FILE_FLAG = "--config-file"


def extract_config_file_from_argv(argv: list[str] | None = None) -> str | None:
    """Sniff ``--config-file <path>`` out of argv WITHOUT importing args.

    Used in two places:

    1. ``main.py`` — to find the config before the launcher's heavy
       module body runs.
    2. ``args.parse_args`` — same flag, full parser; this helper just
       gives ``main.py`` a peek.

    Accepts both ``--config-file PATH`` and ``--config-file=PATH``.
    Returns ``None`` if the flag isn't present or has no value.
    """
    args = (argv if argv is not None else sys.argv[1:]).copy()
    for i, arg in enumerate(args):
        if arg == CONFIG_FILE_FLAG and i + 1 < len(args):
            value = args[i + 1]
            if value and not value.startswith("--"):
                return value
        elif arg.startswith(f"{CONFIG_FILE_FLAG}="):
            return arg.split("=", 1)[1] or None
    return None


def resolve_explicit_config_path(
    cli_path: str | None = None,
    env: Mapping[str, str] | None = None,
) -> str | None:
    """Pick the explicit-path slot for the cascade.

    Priority (highest first): ``--config-file`` CLI value → env vars in
    ``EXPLICIT_CONFIG_ENVS`` order. Returns the first non-empty value
    or ``None`` when nothing is set.
    """
    if cli_path:
        return cli_path
    env_map: Mapping[str, str] = env if env is not None else os.environ
    for key in EXPLICIT_CONFIG_ENVS:
        value = env_map.get(key)
        if value:
            return value
    return None


def _validate_explicit_toml(explicit_path: str) -> None:
    """Pre-parse the user-supplied config so malformed TOML fails loudly.

    The core cascade swallows TOML decode errors (every layer is
    best-effort by design). When the operator passes ``--config-file``
    or sets one of the env vars, a parse failure means the deployment
    is silently misconfigured and the launcher would boot with
    defaults the operator never asked for. Raise instead.

    Missing files are tolerated (cascade behavior) — only parse
    failures escalate.
    """
    import sys as _sys
    from pathlib import Path

    if _sys.version_info >= (3, 11):  # pragma: no cover — version-conditional
        import tomllib
    else:  # pragma: no cover — exercised only on the 3.10 backport path
        import tomli as tomllib

    p = Path(explicit_path)
    if not p.is_file():
        return
    try:
        with p.open("rb") as fh:
            tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(
            f"Malformed TOML at explicit config path '{explicit_path}': {exc}"
        ) from exc


def load_launcher_config(
    explicit_path: str | None = None,
    *,
    apply_to_services: bool = True,
    apply_to_env: bool = True,
) -> dict[str, Any]:
    """Run the layered TOML cascade and return the merged config.

    Thin wrapper around ``openbb_core.app.config.loader.load_layered_config``.
    Defaults preserve the core loader's behavior — push system/user
    sections onto the singleton services and emit ``OPENBB_*`` env vars
    for the promoted top-level flags. Pass ``apply_to_services=False``
    if you only want the dict for inspection (e.g., in tests).

    The returned dict includes the ``[mcp]`` and ``[env]`` tables
    raw — callers must run ``apply_launcher_env`` / merge launcher
    kwargs themselves; the core loader doesn't know about those.
    """
    from openbb_core.app.config.loader import load_layered_config

    if explicit_path:
        _validate_explicit_toml(explicit_path)

    return load_layered_config(
        explicit_path=explicit_path,
        apply_to_services=apply_to_services,
        apply_to_env=apply_to_env,
    )


def expand_env_refs(
    value: str, env: Mapping[str, str] | None = None
) -> tuple[str, list[str]]:
    """Public entry point for ``$VAR`` / ``${VAR}`` substitution.

    Used by ``apply_launcher_env`` for the ``[env]`` table and by
    ``[mcp.spec.headers]`` parsing for credential injection on the
    spec proxy.
    """
    return _expand_env_refs(value, env if env is not None else os.environ)


def _expand_env_refs(value: str, env: Mapping[str, str]) -> tuple[str, list[str]]:
    """Substitute ``$VAR`` / ``${VAR}`` references against ``env``.

    Returns ``(expanded_value, missing_refs)``. Missing references stay
    as their literal ``$VAR`` form in the expanded value so a caller
    that wants to skip the entry has the original spelling for the
    error message. Each missing name is reported only once even if it
    appears multiple times in the same value.
    """
    missing: list[str] = []

    def replace(match: re.Match[str]) -> str:
        name = match.group("braced") or match.group("bare")
        if name and name in env:
            return env[name]
        if name and name not in missing:
            missing.append(name)
        return match.group(0)

    return _ENV_REF_PATTERN.sub(replace, value), missing


def apply_launcher_env(
    env_section: dict[str, Any] | None,
    *,
    env: MutableMapping[str, str] | None = None,
) -> list[str]:
    """Push ``[env]`` table entries into ``os.environ`` (no clobber).

    Real shell env vars always win — if a key is already set, we leave
    it alone. Values support shell-style ``$VAR`` / ``${VAR}``
    substitution against the current environment.

    Entries whose value references an unresolved variable are SKIPPED
    (a warning is logged) — silently setting a value of literal
    ``"$MISSING"`` would let the application boot with bogus
    credentials.

    Returns the list of keys actually applied so callers can
    log/observe what came from TOML versus the shell.
    """
    if not env_section:
        return []
    target: MutableMapping[str, str] = env if env is not None else os.environ
    applied: list[str] = []
    for key, value in env_section.items():
        if not isinstance(key, str):
            continue
        if key in target:
            continue
        expanded, missing = _expand_env_refs(str(value), target)
        if missing:
            logger.warning(
                "Skipping [env] entry %s: references unresolved variable(s) %s",
                key,
                ", ".join(missing),
            )
            continue
        target[key] = expanded
        applied.append(key)
    return applied


def merge_launcher_kwargs(
    cli_kwargs: dict[str, Any],
    launcher_section: dict[str, Any] | None,
) -> dict[str, Any]:
    """Overlay ``[mcp]`` section under CLI kwargs (CLI wins).

    The launcher section is treated as a defaults dict — every key it
    provides is filled into ``cli_kwargs`` only when the CLI didn't
    already set it.
    """
    if not launcher_section:
        return cli_kwargs
    merged = dict(launcher_section)
    merged.update(cli_kwargs)
    return merged


#: Stashed result of the most recent ``bootstrap_launcher_config``.
_BOOTSTRAPPED_CONFIG: dict[str, Any] | None = None


def bootstrap_launcher_config(
    argv: list[str] | None = None,
) -> dict[str, Any]:
    """One-call bootstrap for ``main.py``.

    Resolves the explicit config path from ``--config-file``/env vars,
    runs the layered cascade, and applies the ``[env]`` table. The
    merged result is stashed in ``_BOOTSTRAPPED_CONFIG`` so later boot
    phases can reuse it via ``get_bootstrapped_config()``.

    Safe to call before any ``openbb-core`` import — the only modules
    touched are stdlib + the core's lightweight loader module.
    """
    global _BOOTSTRAPPED_CONFIG  # noqa: PLW0603

    cli_path = extract_config_file_from_argv(argv)
    explicit_path = resolve_explicit_config_path(cli_path)
    config = load_launcher_config(explicit_path=explicit_path)
    apply_launcher_env(config.get("env"))
    _BOOTSTRAPPED_CONFIG = config
    return config


def get_bootstrapped_config() -> dict[str, Any]:
    """Return the config loaded by the most recent ``bootstrap_launcher_config``.

    Returns an empty dict when bootstrap hasn't run.
    """
    return _BOOTSTRAPPED_CONFIG or {}


def reset_bootstrapped_config() -> None:
    """Clear the stashed bootstrap config. For tests only."""
    global _BOOTSTRAPPED_CONFIG  # noqa: PLW0603

    _BOOTSTRAPPED_CONFIG = None
