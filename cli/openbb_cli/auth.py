"""Auth hooks — pluggable per-request authentication for the HTTP dispatcher.

Static headers and query params (``-H``, ``-Q``, ``[headers]``, ``[query]``)
cover the common case where credentials don't change between calls. RBAC
flows need more: tokens that expire, per-user credentials sourced from a
vault, role-aware allow/deny decisions made before the request goes out.

A hook is any importable callable matching::

    Callable[[AuthContext], AuthDecision | Awaitable[AuthDecision]]

Configured in TOML by dotted ``module:attribute`` path::

    auth-hook = "myapp.auth:rbac_hook"          # global, applies to every backend

    [specs.congress]
    path = "..."
    auth-hook = "myapp.auth:congress_hook"     # per-namespace, replaces the global

Each invocation receives the request's ``AuthContext`` and returns an
``AuthDecision``. The returned headers / query params are merged on top of
the dispatcher's static auth (right-biased — the hook wins). ``allow=False``
short-circuits dispatch with a structured ``AccessDenied`` response.

Hooks fire only for command dispatches that go over the network. The
introspection short-circuits (``__commands__``, ``__schema__``) read directly
from the spec doc and skip the hook so RBAC never accidentally hides the
listing the user needs to discover what they're allowed to call.
"""

from __future__ import annotations

import importlib
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, Union


@dataclass(frozen=True)
class AuthContext:
    """Read-only context handed to an auth hook for one request.

    ``namespace`` is the spec namespace (``"congress"``, ``"nyfed"``, …) or
    ``None`` when the dispatcher was built from a single unnamed spec.
    ``command`` is the dotted name *as the upstream backend will see it* —
    namespace prefix stripped. Hooks that key on the user's intended
    command should join ``namespace`` and ``command`` themselves.
    """

    namespace: str | None
    command: str
    params: dict[str, Any] = field(default_factory=dict)
    method: str = "post"


@dataclass(frozen=True)
class AuthDecision:
    """Hook output: extra credentials to add and / or an RBAC deny.

    A hook that wants to inject a token returns ``AuthDecision(headers={...})``.
    A hook that wants to deny a request returns
    ``AuthDecision(allow=False, deny_reason="...")``. Default is allow with
    no extra material — equivalent to no hook at all.
    """

    headers: dict[str, str] | None = None
    query_params: dict[str, str] | None = None
    allow: bool = True
    deny_reason: str | None = None


AuthHook = Callable[[AuthContext], Union["AuthDecision", Awaitable["AuthDecision"]]]


def resolve_auth_hook(spec: str) -> AuthHook:
    """Import an auth hook from its ``module.path:attribute`` spec.

    Raises ``ValueError`` for malformed specs and ``ImportError`` when the
    module or attribute can't be located. The resolved object must be
    callable; classes are accepted too (their instances are the hook).
    """
    if not isinstance(spec, str) or ":" not in spec:
        raise ValueError(
            f"auth-hook must be of the form 'module.path:attribute'; got {spec!r}"
        )
    module_name, _, attr = spec.partition(":")
    module_name = module_name.strip()
    attr = attr.strip()
    if not module_name or not attr:
        raise ValueError(f"auth-hook spec missing module or attribute: {spec!r}")
    module = importlib.import_module(module_name)
    target = getattr(module, attr, None)
    if target is None:
        raise ImportError(f"auth-hook {spec!r}: {attr!r} not found in {module_name!r}")
    if not callable(target):
        raise TypeError(f"auth-hook {spec!r}: {target!r} is not callable")
    return target
