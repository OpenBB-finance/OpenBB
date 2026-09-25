"""HTTP middleware + auth hook entrypoints for ``openbb-mcp``."""

from __future__ import annotations

import importlib
import inspect
import logging
from collections.abc import Callable
from typing import Any, cast

from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("openbb_mcp_server.middleware")


def _resolve_entrypoint(path: str):
    """Import ``module:attr`` and return the resolved attribute."""
    if ":" not in path:
        raise ValueError(
            f"Hook entrypoint must be 'module:attr', got {path!r}. "
            "Example: 'my_pkg.middleware:auth_middleware'."
        )
    module_path, _, attr_path = path.partition(":")
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise ImportError(
            f"Failed to import hook module {module_path!r} (entrypoint {path!r}): {exc}"
        ) from exc

    target = module
    for part in attr_path.split("."):
        try:
            target = getattr(target, part)
        except AttributeError as exc:
            raise AttributeError(
                f"Hook module {module_path!r} has no attribute "
                f"{attr_path!r} (entrypoint {path!r})"
            ) from exc
    return target


def _validate_middleware_callable(fn, path: str) -> None:
    """Sanity-check the resolved callable so misconfigurations fail at startup rather than on the first incoming request."""
    if not callable(fn):
        raise TypeError(
            f"Hook entrypoint {path!r} resolved to a non-callable {type(fn).__name__}."
        )
    if not inspect.iscoroutinefunction(fn):
        raise TypeError(
            f"Hook entrypoint {path!r} must be an async function "
            "(``async def fn(request, call_next): ...``). Sync middleware "
            "silently breaks the Starlette middleware chain."
        )
    positional = [
        p
        for p in inspect.signature(fn).parameters.values()
        if p.kind
        in {
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        }
    ]
    if len(positional) < 2:
        raise TypeError(
            f"Hook entrypoint {path!r} must accept (request, call_next); "
            f"signature has only {len(positional)} positional parameter(s)."
        )


def _hook_to_middleware(fn: Callable[..., Any]) -> Middleware:
    """Wrap an async hook in a ``starlette.middleware.Middleware``."""
    return Middleware(BaseHTTPMiddleware, dispatch=fn)


def build_hook_middleware(
    auth_hooks: list[str] | None,
    middleware_hooks: list[str] | None,
) -> list[Middleware]:
    """Resolve both hook tables and return ordered Middleware instances."""
    resolved: list[Middleware] = []

    for label, hooks in (("auth", auth_hooks), ("middleware", middleware_hooks)):
        if not hooks:
            continue
        if not isinstance(hooks, list):
            raise TypeError(
                f"[mcp.{label}] hooks must be a list of 'module:attr' "
                f"strings; got {type(hooks).__name__}."
            )
        for hook_path in hooks:
            if not isinstance(hook_path, str):
                raise TypeError(
                    f"[mcp.{label}] hooks entries must be strings; got "
                    f"{type(hook_path).__name__} ({hook_path!r})."
                )
            fn = _resolve_entrypoint(hook_path)
            _validate_middleware_callable(fn, hook_path)
            resolved.append(_hook_to_middleware(cast("Callable[..., Any]", fn)))
            logger.info("Registered %s hook: %s", label, hook_path)

    return resolved
