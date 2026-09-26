"""Auth hooks for pluggable per-request authentication."""

from __future__ import annotations

import importlib
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, Union


@dataclass(frozen=True)
class AuthContext:
    """Read-only context handed to an auth hook for one request."""

    namespace: str | None
    command: str
    params: dict[str, Any] = field(default_factory=dict)
    method: str = "post"


@dataclass(frozen=True)
class AuthDecision:
    """Hook output: extra credentials to add and / or an RBAC deny."""

    headers: dict[str, str] | None = None
    query_params: dict[str, str] | None = None
    allow: bool = True
    deny_reason: str | None = None


AuthHook = Callable[[AuthContext], Union["AuthDecision", Awaitable["AuthDecision"]]]


def resolve_auth_hook(spec: str) -> AuthHook:
    """Import an auth hook from its ``module.path:attribute`` spec."""
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
