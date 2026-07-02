"""FastAPI app boot subpackage.

* ``args`` — command-line argument parsing for the ``openbb-api``
  launcher.
* ``bootstrap`` — pluggable FastAPI app loading
  (``import_app``) and platform-extension detection.
* ``app`` — the launcher entry point. Holds the FastAPI app instance,
  registers route handlers, exposes ``main`` / ``launch_api``.
"""

from openbb_platform_api.app import args, bootstrap
from openbb_platform_api.app.args import LAUNCH_SCRIPT_DESCRIPTION, parse_args
from openbb_platform_api.app.bootstrap import (
    check_for_platform_extensions,
    import_app,
)

__all__ = [
    "LAUNCH_SCRIPT_DESCRIPTION",
    "args",
    "bootstrap",
    "check_for_platform_extensions",
    "import_app",
    "parse_args",
]
