"""CLI Session — singleton holding settings, console, registry.

Lazy-construct heavy dependencies (prompt-toolkit, charting backend) so that
non-interactive paths (`openbb economy.gdp ...`) do not spawn a browser process
or initialize a TTY-only PromptSession just to dispatch one command.
"""

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
    """Session class.

    Heavy attributes (prompt session, charting backend, output adapter, the
    ``obb`` namespace itself) are materialized on first access. Constructing
    ``Session()`` is cheap and side-effect-free — the spec-driven REPL path
    can run without ever importing ``openbb``.
    """

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
        """Lazy ``obb`` accessor; cached after first call.

        Spec-driven REPL flows never touch this — they get menu/parser data
        from a ``Backend`` instead. Local-mode flows (and any code path that
        actually needs ``obb.user``/``obb.system``) trigger the real import
        on first access.
        """
        if self._obb_cached is None:
            from openbb import obb

            self._obb_cached = obb
            try:
                directory = Path(obb.user.preferences.user_styles_directory)  # ty: ignore[unresolved-attribute]
                self._style.apply(self._settings.RICH_STYLE, directory)
            except Exception:  # noqa: BLE001, S110 — best-effort styling, intentional
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
        """Lazy charting backend.

        Importing ``openbb_charting`` is expensive and starts a browser process
        when used. Only build it when something actually requests a chart.
        """
        if self._backend is _UNSET:
            self._backend = self._build_backend()
        return self._backend

    @property
    def output_adapter(self) -> Any:
        """Output adapter selected by ``settings.OUTPUT_MODE``.

        Rebuilt whenever ``OUTPUT_MODE`` changes so ``/settings/ output json``
        takes effect immediately — caching froze the adapter to whatever was
        active at first access. Adapter construction is cheap (a single
        class instantiation), so re-checking the mode on every access is
        a good tradeoff for live-updateable settings.
        """
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

    def _build_backend(self) -> Any:
        try:
            from openbb_charting.core.backend import (  # ty: ignore[unresolved-import]
                Backend,
            )
            from openbb_core.app.model.charts.charting_settings import ChartingSettings

            return Backend(
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
