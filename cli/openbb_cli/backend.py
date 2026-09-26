"""Pluggable controller backend."""

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
    """Source of truth for menu structure and command execution."""

    @property
    def routers(self) -> dict[str, str]: ...

    @property
    def reference_paths(self) -> dict[str, dict[str, Any]]: ...

    @property
    def reference_routers(self) -> dict[str, dict[str, Any]]: ...

    def get_command_target(self, router: str) -> Any:
        """Resolve a top-level command-typed router target."""

    def get_translators_for_path(
        self, router: str
    ) -> tuple[dict[str, Translator], dict[str, str]]: ...


class LocalBackend:
    """Backend backed by in-process ``openbb``."""

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
    """Backend backed by a loaded ``.spec`` document and an HTTP dispatcher."""

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
        """Stub exposing ``model_dump()`` for top-level command-typed routers."""
        commands = self._spec.get("commands", {})
        meta = commands.get(router)
        if meta is None:
            return _CommandStub(router, {})
        return _CommandStub(router, meta)

    def get_translators_for_path(
        self, router: str
    ) -> tuple[dict[str, Translator], dict[str, str]]:
        """Get translators for ``router.*`` commands and the direct sub-namespace list."""
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
    """ArgparseTranslator-shaped facade over a spec command and HTTP dispatcher."""

    def __init__(self, command: str, cmd_spec: dict[str, Any], dispatcher: Any) -> None:
        from openbb_cli.dispatchers.spec import (
            command_parameters,
            parser_from_command_spec,
        )

        self._command = command
        self._spec = cmd_spec
        self._dispatcher = dispatcher
        self._parser = parser_from_command_spec(cmd_spec, prog=command)
        all_params = command_parameters(cmd_spec)
        self._param_names = {p["name"] for p in all_params if p.get("name")}
        self._params_by_provider: dict[str, set[str]] = {}
        providers: list[str] = cmd_spec.get("providers") or []
        for provider in providers:
            self._params_by_provider[provider] = {
                p["name"]
                for p in all_params
                if p.get("name")
                and (not p.get("providers") or provider in p["providers"])
            }
        self.func = _NamedStub(command.replace(".", "_"))

    @property
    def parser(self) -> argparse.ArgumentParser:
        return deepcopy(self._parser)

    def execute_func(self, parsed_args: argparse.Namespace) -> Any:
        from openbb_cli.dispatchers.protocol import Request

        params = {
            k: v
            for k, v in vars(parsed_args).items()
            if v is not None and k in self._param_names
        }
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
    """Callable carrying a ``__name__`` attribute used by export-filename generation."""

    def __init__(self, name: str) -> None:
        self.__name__ = name

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError(
            "SpecTranslator stub called directly; use execute_func instead."
        )
