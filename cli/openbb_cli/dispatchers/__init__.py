"""Dispatcher subsystem for non-TTY (CI / agent) operation.

Two backends — both share the same Request/Response wire format and the same
async ``Dispatcher`` Protocol:

* ``LocalDispatcher`` — in-process, walks ``obb.<...>`` and dispatches commands.
  Single-tenant. Pays the heavy ``import openbb`` once at start-up.

* ``HttpDispatcher`` — thin client against an ``openbb-platform-api`` server.
  Multi-tenant. Heavy import lives on the server; CLI start-up stays light.

Two transports use these dispatchers:

* ``run_argv`` — degenerate one-shot: argv → single Request → exit.
* ``run_batch`` — NDJSON line-protocol: stdin lines → concurrent Tasks → stdout
  lines. Stateless because each request is its own asyncio Task scope.
"""

from openbb_cli.dispatchers.base import Dispatcher
from openbb_cli.dispatchers.http import HttpDispatcher
from openbb_cli.dispatchers.local import LocalDispatcher
from openbb_cli.dispatchers.protocol import Request, Response, ResponseError
from openbb_cli.dispatchers.runtime import run_argv, run_batch

__all__ = [
    "Dispatcher",
    "HttpDispatcher",
    "LocalDispatcher",
    "Request",
    "Response",
    "ResponseError",
    "run_argv",
    "run_batch",
]
