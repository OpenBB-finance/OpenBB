"""Pluggable controller backend.

The CLI's controller graph (``cli_controller``, ``base_platform_controller``,
``platform_controller_factory``) historically reflected on an in-process
``obb`` namespace to discover routers, translators, and command callables.

This module replaces that hard-wired assumption with a ``Backend`` protocol —
controllers depend on the protocol, not on ``obb`` directly. Two
implementations:

* ``LocalBackend`` wraps in-process ``obb`` (the historical default; used when
  no spec / server flags are passed).
* ``SpecBackend`` reads a precomputed ``.spec`` document and dispatches every
  command via ``HttpDispatcher`` — no local ``openbb`` install required.

A ``Backend`` exposes everything the controller graph reads from ``obb`` today:
the top-level router/menu classification, the per-menu translator dict, the
sub-router map, and the reference description dicts. The ``Translator``
protocol mirrors what controllers consume from
``ArgparseTranslator``: a mutable ``_parser`` and a synchronous
``execute_func``.
"""

from __future__ import annotations

import argparse
import asyncio
from copy import deepcopy
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Translator(Protocol):
    """Per-command translator matching the ``ArgparseTranslator`` surface controllers touch."""

    _parser: argparse.ArgumentParser
    func: Any

    @property
    def parser(self) -> argparse.ArgumentParser: ...

    def execute_func(self, parsed_args: argparse.Namespace) -> Any: ...


class Backend(Protocol):
    """Source of truth for menu structure + command execution.

    Both implementations expose:

    * ``routers``: top-level ``{router_name: "menu" | "command"}``.
    * ``reference_paths`` / ``reference_routers``: description dicts used for
      help text. Same shape on both backends — see ``build_reference``.
    * ``get_translators_for_path(router_name)``: ``(translators, sub_paths)``
      pair. ``translators`` keys match the qualified-command-name format
      ``ArgparseClassProcessor`` already produces (``f"{router}_{cmd}"``).
      ``sub_paths`` is the same ``{name: "subpath" | "subsubpath"}`` shape.
    """

    @property
    def routers(self) -> dict[str, str]: ...

    @property
    def reference_paths(self) -> dict[str, dict[str, Any]]: ...

    @property
    def reference_routers(self) -> dict[str, dict[str, Any]]: ...

    def get_command_target(self, router: str) -> Any:
        """Resolve a top-level command-typed router target.

        Used when ``routers[name] == "command"``. ``LocalBackend`` returns
        ``getattr(obb, router)``; ``SpecBackend`` returns a stub exposing
        ``model_dump()`` over the command's response shape.
        """

    def get_translators_for_path(
        self, router: str
    ) -> tuple[dict[str, Translator], dict[str, str]]: ...


class LocalBackend:
    """Backend backed by in-process ``openbb``.

    Lazy: ``obb`` is imported on first access, so importing this module is
    cheap. Once a property is read, the ``obb`` namespace is walked once and
    cached.
    """

    def __init__(self) -> None:
        self._obb: Any = None
        self._routers: dict[str, str] | None = None

    def _ensure_obb(self) -> Any:
        if self._obb is None:
            from openbb import obb

            self._obb = obb
        return self._obb

    @property
    def routers(self) -> dict[str, str]:
        if self._routers is not None:
            return self._routers
        from pydantic import BaseModel

        obb = self._ensure_obb()
        self._routers = {
            d: ("menu" if not isinstance(getattr(obb, d), BaseModel) else "command")
            for d in dir(obb)
            if not d.startswith("_") and d not in ("user", "system", "account")
        }
        return self._routers

    @property
    def reference_paths(self) -> dict[str, dict[str, Any]]:
        return self._ensure_obb().reference.get("paths", {})

    @property
    def reference_routers(self) -> dict[str, dict[str, Any]]:
        return self._ensure_obb().reference.get("routers", {})

    def get_command_target(self, router: str) -> Any:
        return getattr(self._ensure_obb(), router)

    def get_translators_for_path(
        self, router: str
    ) -> tuple[dict[str, Translator], dict[str, str]]:
        from openbb_cli.argparse_translator.argparse_class_processor import (
            ArgparseClassProcessor,
        )

        target = getattr(self._ensure_obb(), router)
        processor = ArgparseClassProcessor(
            target_class=target, reference=self.reference_paths
        )
        return processor.translators, processor.paths  # ty: ignore[invalid-return-type]


class SpecBackend:
    """Backend backed by a loaded ``.spec`` document and an HTTP dispatcher.

    Every command resolution, parser build, and execution goes through the
    spec — no ``import openbb``. Sub-router and translator dicts are derived
    on demand, mirroring the shape ``ArgparseClassProcessor`` produces so the
    rest of the controller graph stays unchanged.
    """

    def __init__(self, spec_doc: dict[str, Any], dispatcher: Any) -> None:
        self._spec = spec_doc
        self._dispatcher = dispatcher
        self._top_level_routers: dict[str, str] = {
            name: kind
            for name, kind in spec_doc.get("routers", {}).items()
            if "." not in name
        }

    @property
    def routers(self) -> dict[str, str]:
        return self._top_level_routers

    @property
    def reference_paths(self) -> dict[str, dict[str, Any]]:
        return self._spec.get("reference", {}).get("paths", {})

    @property
    def reference_routers(self) -> dict[str, dict[str, Any]]:
        return self._spec.get("reference", {}).get("routers", {})

    def get_command_target(self, router: str) -> Any:
        """Stub exposing ``model_dump()`` for top-level command-typed routers.

        Mirrors the surface ``cli_controller._generate_platform_commands`` reads
        when a router is classified as a command rather than a menu — it calls
        ``getattr(obb, router).model_dump()``.
        """
        commands = self._spec.get("commands", {})
        meta = commands.get(router)
        if meta is None:
            return _CommandStub(router, {})
        return _CommandStub(router, meta)

    def get_translators_for_path(
        self, router: str
    ) -> tuple[dict[str, Translator], dict[str, str]]:
        """Get translators for ``router.*`` commands and the direct sub-namespace list.

        Sub-paths are *direct* children only — grandchildren collapse into the
        flattened command names (``rates.secured.all.latest`` becomes the
        translator key ``nyfed_rates_secured_all_latest`` under the
        ``rates`` direct child). Surfacing intermediate segments like
        ``secured`` / ``all`` at the root would create empty menus with no
        translators routing to them.
        """
        prefix = router + "."
        translators: dict[str, Translator] = {}
        direct_subs: set[str] = set()

        for cmd_name, cmd_spec in self._spec.get("commands", {}).items():
            if not cmd_name.startswith(prefix):
                continue
            tail = cmd_name[len(prefix) :]
            key = f"{router}_{tail.replace('.', '_')}"
            translators[key] = SpecTranslator(cmd_name, cmd_spec, self._dispatcher)
            parts = tail.split(".")
            if len(parts) > 1:
                direct_subs.add(parts[0])

        sub_paths: dict[str, str] = {name: "subpath" for name in direct_subs}
        return translators, sub_paths


class _CommandStub:
    """Minimal object exposing ``model_dump`` for command-typed top-level routers."""

    def __init__(self, command: str, meta: dict[str, Any]) -> None:
        self._command = command
        self._meta = meta

    def model_dump(self) -> dict[str, Any]:
        return {"command": self._command, **self._meta}


class SpecTranslator:
    """ArgparseTranslator-shaped facade over a spec command + HTTP dispatcher.

    Exposes the two things controllers actually consume from a translator:

    * ``parser`` — fresh deep copy each access (matches ``ArgparseTranslator``
      semantics, important because controllers mutate parser actions).
    * ``execute_func(parsed_args)`` — synchronously bridges to async dispatch.
    """

    def __init__(self, command: str, cmd_spec: dict[str, Any], dispatcher: Any) -> None:
        from openbb_cli.dispatchers.spec import parser_from_command_spec

        self._command = command
        self._spec = cmd_spec
        self._dispatcher = dispatcher
        self._parser = parser_from_command_spec(cmd_spec, prog=command)
        self._param_names = {
            p["name"] for p in (cmd_spec.get("parameters") or []) if p.get("name")
        }
        # Per-provider whitelist for multi-provider OpenBB commands. Used at
        # ``execute_func`` time to drop flags that don't apply to the chosen
        # provider — the eagerly-built ``self._parser`` accepts every flag so
        # tab-completion and ``--help`` keep working without knowing which
        # provider the user will pick.
        self._params_by_provider: dict[str, set[str]] = {}
        providers: list[str] = cmd_spec.get("providers") or []
        for provider in providers:
            self._params_by_provider[provider] = {
                p["name"]
                for p in (cmd_spec.get("parameters") or [])
                if p.get("name")
                and (not p.get("providers") or provider in p["providers"])
            }
        self.func = _NamedStub(command.replace(".", "_"))

    @property
    def parser(self) -> argparse.ArgumentParser:
        return deepcopy(self._parser)

    def execute_func(self, parsed_args: argparse.Namespace) -> Any:
        from openbb_cli.dispatchers.protocol import Request

        # Only forward params declared in the spec. ``parse_known_args_and_warn``
        # injects CLI-internal flags (``export``, ``help``, ``is_image``,
        # ``register_key``, ``register_obbject``) onto the namespace; without
        # this filter they leak onto the upstream URL as query params.
        params = {
            k: v
            for k, v in vars(parsed_args).items()
            if v is not None and k in self._param_names
        }
        # Multi-provider commands: reject flags that don't apply to the
        # chosen provider. Without this, ``equity.price.quote --provider
        # intrinio --use_cache true`` would silently send ``use_cache`` to
        # an upstream that doesn't take it.
        provider = params.get("provider")
        if provider and provider in self._params_by_provider:
            allowed = self._params_by_provider[provider]
            stray = [k for k in params if k not in allowed and k != "provider"]
            if stray:
                raise RuntimeError(
                    f"flags not valid for provider={provider!r}: "
                    f"{', '.join('--' + s for s in stray)}"
                )
        request = Request(command=self._command, params=params)

        async def _dispatch_and_close() -> Any:
            try:
                return await self._dispatcher.dispatch(request)
            finally:
                pass

        response = asyncio.run(_dispatch_and_close())
        if not response.ok:
            raise RuntimeError(
                response.error.message if response.error else "dispatch failed"
            )
        return response.result


class _NamedStub:
    """Callable carrying a ``__name__`` attribute used by export-filename generation.

    Body never runs — controllers only ever introspect ``__name__``.
    """

    def __init__(self, name: str) -> None:
        self.__name__ = name

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError(
            "SpecTranslator stub called directly; use execute_func instead."
        )
