"""OpenBB Platform API.

Launch script and widgets builder for the OpenBB Workspace Custom Backend.

The launcher logic moved to ``openbb_platform_api.app.app`` in the V5
layout reorganization. This module is preserved as the canonical
entry point used by the ``openbb-api`` console script (declared in
``pyproject.toml``) and as the importable module path
``openbb_platform_api.main:app`` consumed by ``uvicorn.run``.

Every public name from ``app.app`` is re-exported here so legacy
imports (and tests that ``patch("openbb_platform_api.main.<name>", …)``)
keep working while new code imports from the V5 module directly.

Boot order — three short-circuits / hooks run BEFORE importing
``app.app`` so the launcher's heavy top-level imports stay
deferred until they're actually needed:

1. ``--help`` / ``-h`` — print the launcher's help text and exit
   without importing anything beyond ``args`` (stdlib-only at module
   scope).
2. Layered TOML config bootstrap — discover ``openbb.toml`` in the
   cascade (or ``--config-file <path>`` / ``$OPENBB_API_CONFIG``),
   apply the ``[env]`` table to ``os.environ``, and push the
   ``[system]`` / ``[user]`` sections onto the singleton services.
   Containers can ship one TOML and avoid shell exports entirely.
3. Re-export ``app.app``'s public names (``main``, ``app``,
   ``launch_api``, route handlers) so legacy
   ``openbb_platform_api.main:<name>`` patches still resolve.
"""

import sys


def _short_circuit_on_help() -> None:
    """Print help and exit when ``--help`` / ``-h`` is on argv.

    Must run before importing ``app.app`` — that module's top-level
    imports pull in the entire openbb-core stack, which is wasted work
    when the user just wants to read the flags.
    """
    argv = sys.argv[1:]
    if "--help" in argv or "-h" in argv:
        from openbb_platform_api.app.args import LAUNCH_SCRIPT_DESCRIPTION

        print(LAUNCH_SCRIPT_DESCRIPTION)  # noqa: T201
        sys.exit(0)


def _bootstrap_config() -> None:
    """Run the launcher TOML cascade BEFORE the launcher imports.

    Picks up ``--config-file <path>`` / ``$OPENBB_API_CONFIG`` /
    ``$OPENBB_CONFIG``, merges every layer (pyproject → user-global →
    project → explicit → ``.env`` → real env vars), and applies the
    ``[env]`` table to ``os.environ`` so the very first
    ``openbb_core.*`` module load sees the injected values. Also
    pushes the merged ``[system]`` / ``[user]`` sections onto the
    singleton services so any TOML-supplied OpenBB settings take
    effect for downstream code.

    Best-effort by design: if the TOML chain produces no overrides
    (no file present anywhere) the call is a no-op. Raises if a
    discovered file is malformed — silent corruption is worse than
    a clear startup error.
    """
    from openbb_platform_api.app.config import bootstrap_launcher_config

    bootstrap_launcher_config()


_short_circuit_on_help()
_bootstrap_config()


from openbb_platform_api.app import app as _app_module  # noqa: E402

# Re-export every non-dunder name from the launcher's module-level
# scope so legacy attribute-access patterns continue to resolve. The
# names point at the same objects ``app.app`` defines, so patches via
# the legacy or the V5 path target the same binding.
globals().update(
    {
        name: value
        for name, value in _app_module.__dict__.items()
        if not name.startswith("__")
    }
)


if __name__ == "__main__":  # pragma: no cover — manual launcher entry
    try:
        main()  # ty: ignore[unresolved-reference]  # noqa: F821 — provided via globals().update
    except KeyboardInterrupt:
        sys.exit(0)
