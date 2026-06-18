"""HTTP middleware + auth hook entrypoints for ``openbb-mcp``.

Lets a deployment attach Starlette-style HTTP middleware to the MCP
server's transport (``streamable-http`` / ``sse``) without modifying
launcher source. Useful for:

* request authentication / authorization (API keys, JWT validation,
  mTLS client cert checks)
* request logging, tracing, metric collection
* IP allow-listing / rate limiting
* response transformation (CORS overrides, custom headers)

Configured via two TOML tables. Both accept the same
``module:async_callable`` reference syntax — auth hooks just run as
the outermost layer so unauthenticated requests are rejected before
any other middleware spends cycles on them::

    [mcp.auth]
    # Authentication / authorization hooks — outermost layer.
    hooks = [
        "my_pkg.auth:bearer_token_validator",
    ]

    [mcp.middleware]
    # General-purpose HTTP middleware — runs after auth.
    hooks = [
        "my_pkg.middleware:request_logger",
        "my_pkg.middleware:rate_limiter",
    ]

Each entry is a ``"module:callable"`` reference resolved through the
standard import system. The callable must be an async function with
the Starlette HTTP middleware signature::

    async def bearer_token_validator(request, call_next):
        if request.headers.get("Authorization") != "Bearer s3cret":
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        return await call_next(request)

Order within each list matters. Hooks are registered so the FIRST
entry is the OUTERMOST layer — sees the request first on the way in,
the response last on the way out. Across the two tables the order
is: ``[mcp.auth].hooks[0]`` (outermost) → ... →
``[mcp.middleware].hooks[-1]`` (innermost).

Failures during hook resolution / signature validation raise loudly
at startup. A misconfigured reference is a deployment bug that
needs to surface immediately, not a silent passthrough.
"""

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
    """Import ``module:attr`` and return the resolved attribute.

    Splits on the first ``:`` so attribute names with dots
    (``MyClass.method``) work. Errors are re-raised with a message
    that names the offending entrypoint string for fast debugging.
    """
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
    """Sanity-check the resolved callable so misconfigurations fail at
    startup rather than on the first incoming request.

    Verifies it's callable, takes at least two positional parameters,
    and is an async function (Starlette HTTP middleware must be
    coroutines — sync functions silently break the middleware chain).
    """
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
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):  # pragma: no cover — rare builtins
        return
    positional = [
        p
        for p in sig.parameters.values()
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
    """Wrap an async hook in a ``starlette.middleware.Middleware``.

    FastMCP's ``run(middleware=...)`` expects a list of
    ``Middleware(cls, **kwargs)`` instances, not bare callables.
    ``BaseHTTPMiddleware`` adapts the ``async def fn(request,
    call_next)`` shape into a Starlette middleware class, and the
    ``dispatch`` kwarg lets us bind the user's function as that
    class's request handler without subclassing.
    """
    return Middleware(BaseHTTPMiddleware, dispatch=fn)


def build_hook_middleware(
    auth_hooks: list[str] | None,
    middleware_hooks: list[str] | None,
) -> list[Middleware]:
    """Resolve both hook tables and return ordered Middleware instances.

    Returns the list in OUTERMOST-FIRST order so the caller can
    splice it into the FastMCP ``middleware=`` list at the right
    position (typically just after CORS, just before the SSE
    shutdown wrapper).

    Within each list, the first TOML entry is the outermost layer.
    Across the two tables: every auth hook wraps every middleware
    hook (auth runs first on the way in, last on the way out).

    Raises immediately on resolution / signature validation failures
    so a deployment with a bad reference fails at startup, not on
    the first inbound request.
    """
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
