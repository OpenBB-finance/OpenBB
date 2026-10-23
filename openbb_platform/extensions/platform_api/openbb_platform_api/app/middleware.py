"""HTTP middleware hook entrypoints for ``openbb-api``.

Lets a deployment attach Starlette-style HTTP middleware functions to
the launcher's FastAPI app from a config-supplied entrypoint, with no
launcher source changes. Useful for:

* request authentication / authorization (API keys, JWT validation,
  mTLS client cert checks)
* request logging, tracing, metric collection
* IP allow-listing / rate limiting
* response transformation (CORS overrides, custom headers)

Configured via the ``[middleware]`` table in the launcher TOML::

    [middleware]
    hooks = [
        "my_pkg.middleware:auth_middleware",
        "my_pkg.middleware:request_logger",
    ]

Each entry is a ``"module:callable"`` reference resolved through the
standard import system. The callable must be an async function with
the Starlette HTTP middleware signature::

    async def auth_middleware(request, call_next):
        # pre-process — short-circuit by returning a Response
        if not request.headers.get("X-API-Key"):
            return JSONResponse({"error": "unauthorized"}, status_code=401)

        response = await call_next(request)

        # post-process — inspect or mutate the response
        response.headers["X-Custom"] = "value"
        return response

Order matters. Hooks are registered so the FIRST entry in the TOML
list is the OUTERMOST layer — it sees the request first on the way in
and the response last on the way out. This matches the natural
"outside in" reading of the config file.

Failures during hook resolution / registration raise loudly at
startup. A misconfigured middleware reference is a deployment bug
that needs to surface immediately, not a silent passthrough.
"""

from __future__ import annotations

import importlib
import inspect
import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = logging.getLogger("openbb_platform_api.middleware")


def _resolve_entrypoint(path: str):
    """Import ``module:attr`` and return the resolved attribute.

    Splits on the first ``:`` so attribute names with dots
    (``MyClass.method``) work. Errors are re-raised with a message
    that names the offending entrypoint string for fast debugging.
    """
    if ":" not in path:
        raise ValueError(
            f"Middleware entrypoint must be 'module:attr', got {path!r}. "
            "Example: 'my_pkg.middleware:auth_middleware'."
        )
    module_path, _, attr_path = path.partition(":")
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise ImportError(
            f"Failed to import middleware module {module_path!r} "
            f"(entrypoint {path!r}): {exc}"
        ) from exc

    target = module
    for part in attr_path.split("."):
        try:
            target = getattr(target, part)
        except AttributeError as exc:
            raise AttributeError(
                f"Middleware module {module_path!r} has no attribute "
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
            f"Middleware entrypoint {path!r} resolved to a non-callable "
            f"{type(fn).__name__}."
        )
    if not inspect.iscoroutinefunction(fn):
        raise TypeError(
            f"Middleware entrypoint {path!r} must be an async function "
            "(``async def fn(request, call_next): ...``). Sync middleware "
            "silently breaks the Starlette middleware chain."
        )
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):  # pragma: no cover — rare builtins
        # Some builtins / C-implemented callables don't expose a
        # signature — let those through; FastAPI will surface any
        # arity mismatch when the middleware is invoked. Pragma'd
        # because constructing such a callable in a test is brittle
        # and the branch is purely defensive.
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
            f"Middleware entrypoint {path!r} must accept (request, "
            f"call_next); signature has only {len(positional)} positional "
            "parameter(s)."
        )


def apply_http_middleware_hooks(
    app: FastAPI,
    hooks: list[str] | None,
) -> list[str]:
    """Register each entrypoint as HTTP middleware on ``app``.

    Hooks run in the order ``[middleware] hooks`` lists them — the
    first entry is the outermost layer. Returns the list of resolved
    entrypoint paths, in registration order, for logging / tests.

    Raises immediately on resolution / signature-validation failures
    so a deployment with a bad reference fails at startup, not
    on the first inbound request.
    """
    if not hooks:
        return []
    if not isinstance(hooks, list):
        raise TypeError(
            "[middleware] hooks must be a list of 'module:attr' strings; "
            f"got {type(hooks).__name__}."
        )

    resolved: list[tuple[str, object]] = []
    for hook_path in hooks:
        if not isinstance(hook_path, str):
            raise TypeError(
                f"[middleware] hooks entries must be strings; got "
                f"{type(hook_path).__name__} ({hook_path!r})."
            )
        fn = _resolve_entrypoint(hook_path)
        _validate_middleware_callable(fn, hook_path)
        resolved.append((hook_path, fn))

    # Starlette's middleware stack is built bottom-up: ``add_middleware``
    # inserts at index 0, so the LAST registered entry runs FIRST on
    # the way in. To make the TOML list read top-to-bottom as
    # outermost-to-innermost (the natural reading order), we register
    # in REVERSE — the first hook ends up at the top of the stack.
    for hook_path, fn in reversed(resolved):
        # ``fn`` was just validated to be an async callable with the
        # right arity by ``_validate_middleware_callable``, but it's
        # statically typed as ``object`` because ``_resolve_entrypoint``
        # returns the raw imported attribute. Cast for the decorator's
        # benefit so ty doesn't trip on the ``DecoratedCallable`` bound.
        app.middleware("http")(cast("Callable[..., Any]", fn))
        logger.info("Registered HTTP middleware: %s", hook_path)

    return [path for path, _ in resolved]
