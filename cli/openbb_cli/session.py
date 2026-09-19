"""CLI Session singleton holding settings, console, registry."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from openbb_core.app.model.abstract.singleton import SingletonMeta
from openbb_core.app.model.user_settings import UserSettings as User

from openbb_cli.argparse_translator.obbject_registry import Registry
from openbb_cli.config.console import Console
from openbb_cli.config.style import Style
from openbb_cli.models.settings import Settings


class Session(metaclass=SingletonMeta):
    """Session class."""

    def __init__(self) -> None:
        self._obb_cached: Any = None
        self._settings = Settings()
        self._style = Style(style=self._settings.RICH_STYLE, directory=None)
        self._console = Console(
            settings=self._settings, style=self._style.console_style
        )
        self._obbject_registry = Registry()
        self._prompt_session: Any = _UNSET
        self._backend: Any = _UNSET
        self._output_adapter: Any = _UNSET

    @property
    def _obb(self) -> Any:
        """Lazy ``obb`` accessor; cached after first call."""
        if self._obb_cached is None:
            from openbb import obb

            self._obb_cached = obb
            try:
                directory = Path(obb.user.preferences.user_styles_directory)  # ty: ignore[unresolved-attribute]
                self._style.apply(self._settings.RICH_STYLE, directory)
            except Exception:  # noqa: BLE001, S110
                pass
        return self._obb_cached

    @property
    def user(self) -> User:
        """Get platform user."""
        return self._obb.user

    @property
    def settings(self) -> Settings:
        """Get CLI settings."""
        return self._settings

    @property
    def style(self) -> Style:
        """Get CLI style."""
        return self._style

    @property
    def console(self) -> Console:
        """Get console."""
        return self._console

    @property
    def obbject_registry(self) -> Registry:
        """Get obbject registry."""
        return self._obbject_registry

    @property
    def is_interactive(self) -> bool:
        """Whether stdin is attached to a TTY (controls REPL-only behaviors)."""
        try:
            return bool(sys.stdin.isatty())
        except (AttributeError, ValueError):
            return False

    @property
    def prompt_session(self) -> Any:
        """Lazy prompt-toolkit PromptSession; ``None`` when stdin is not a TTY."""
        if self._prompt_session is _UNSET:
            self._prompt_session = self._build_prompt_session()
        return self._prompt_session

    @property
    def backend(self) -> Any:
        """Lazy charting backend."""
        if self._backend is _UNSET:
            self._backend = self._build_backend()
        return self._backend

    @property
    def output_adapter(self) -> Any:
        """Output adapter selected by ``settings.OUTPUT_MODE``."""
        mode = getattr(self._settings, "OUTPUT_MODE", "tsv")
        if (
            self._output_adapter is _UNSET
            or getattr(self._output_adapter, "_mode", None) != mode
        ):
            self._output_adapter = self._build_output_adapter()
            self._output_adapter._mode = mode
        return self._output_adapter

    def _build_output_adapter(self) -> Any:
        mode = getattr(self._settings, "OUTPUT_MODE", "tsv")
        if mode == "rich":
            from openbb_cli.outputs.rich import RichTableOutput

            return RichTableOutput()
        if mode == "json":
            from openbb_cli.outputs.json import JsonOutput

            return JsonOutput()
        if mode == "html":
            from openbb_cli.outputs.html import HtmlOutput

            return HtmlOutput()
        from openbb_cli.outputs.tsv import TsvOutput

        return TsvOutput()

    def _build_prompt_session(self) -> Any:
        try:
            if not self.is_interactive:
                return None
            from prompt_toolkit import PromptSession

            from openbb_cli.config.completer import CustomFileHistory
            from openbb_cli.config.constants import HIST_FILE_PROMPT

            return PromptSession(
                history=CustomFileHistory(str(HIST_FILE_PROMPT)),
                complete_while_typing=True,
            )
        except Exception:
            return None

    @staticmethod
    def _resolve_backend_class() -> Any:
        """Resolve the charting backend class, honoring overrides and the engine.

        Prefers a backend registered under the ``openbb_charting_backend``
        entry-point group, otherwise asks the resolved charting engine for its
        built-in backend, so the CLI never depends on ``openbb_charting`` by name.
        """
        from openbb_core.app.charting import (
            ChartingManager,
            get_charting_backend_class,
        )

        backend_class = get_charting_backend_class()
        if backend_class is not None:
            return backend_class

        engine = ChartingManager.get_charting_class()
        getter = getattr(engine, "get_backend_class", None) if engine else None
        return getter() if callable(getter) else None

    def _build_backend(self) -> Any:
        try:
            from openbb_core.app.model.charts.charting_settings import ChartingSettings

            backend_class = self._resolve_backend_class()
            if backend_class is None:
                return None

            return backend_class(
                ChartingSettings(
                    system_settings=self._obb.system,
                    user_settings=self._obb.user,
                )
            )
        except Exception:
            return None

    def max_obbjects_exceeded(self) -> bool:
        """Check if max obbjects exceeded."""
        return (
            len(self.obbject_registry.all) >= self.settings.N_TO_KEEP_OBBJECT_REGISTRY
        )


_UNSET: Any = object()
