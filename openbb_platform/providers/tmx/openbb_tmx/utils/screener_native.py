"""The screener builder in a native window or a notebook, powered by PyWry."""

import logging
from typing import Any

_logger = logging.getLogger(__name__)


def _run_screen(config: dict, limit: int | None) -> list[dict]:
    """Run the screen for a builder configuration on a private event loop.

    Parameters
    ----------
    config : dict
        The configuration the builder emitted.
    limit : int or None
        The maximum number of rows, or None for the screener's own ceiling.

    Returns
    -------
    list[dict]
        One entry per matched instrument.
    """
    import asyncio

    from openbb_core.provider.utils.errors import EmptyDataError

    from openbb_tmx.models.equity_screener import (
        TmxEquityScreenerData,
        TmxEquityScreenerFetcher,
    )
    from openbb_tmx.utils.screener_catalog import query_from_config

    params = query_from_config(config)

    if limit:
        params["limit"] = limit

    loop = asyncio.new_event_loop()

    try:
        results = loop.run_until_complete(
            TmxEquityScreenerFetcher.fetch_data(params, {})
        )
    except EmptyDataError:
        return []
    finally:
        loop.close()

    return [
        row.model_dump(mode="json", exclude_none=True)
        for row in results
        if isinstance(row, TmxEquityScreenerData)
    ]


def make_screener_callbacks(app: Any) -> dict:
    """Build the callbacks that serve the builder over the PyWry bridge.

    Parameters
    ----------
    app : Any
        The PyWry application the window belongs to.

    Returns
    -------
    dict
        The event name to handler mapping.
    """
    import json

    from openbb_tmx.utils.screener_iframe import columns_for, prune_empty_columns

    def on_run(data: dict[str, Any], *_: Any) -> None:
        """Screen for the configuration and reply with rows and columns."""
        try:
            config = json.loads(data.get("config") or "{}")
        except (TypeError, ValueError):
            config = {}

        requested = int(data.get("limit") or 0)

        try:
            rows = _run_screen(config, None if requested <= 0 else requested)
        except Exception:  # noqa: BLE001
            _logger.exception("The screen could not be run")
            app.emit(
                "screener:results",
                {"rows": [], "error": "The screen could not be run."},
            )
            return

        columns = columns_for(str(config.get("asset_type") or "Equity"))
        app.emit(
            "screener:results",
            {"rows": rows, "columns": prune_empty_columns(rows, columns)},
        )

    def on_theme(data: dict[str, Any], *_: Any) -> None:
        """Follow the theme the window switched to."""
        from pywry import ThemeMode

        app.theme = (
            ThemeMode.LIGHT
            if str(data.get("theme") or "dark").lower() == "light"
            else ThemeMode.DARK
        )

    def on_presets_list(_data: dict[str, Any], *_: Any) -> None:
        """Reply with every saved configuration."""
        from openbb_tmx.utils.screener_presets import list_presets

        app.emit("screener:presets", {"presets": list_presets()})

    def on_preset_load(data: dict[str, Any], *_: Any) -> None:
        """Reply with one saved configuration."""
        from openbb_tmx.utils.screener_presets import load_preset

        name = str(data.get("name") or "")

        try:
            app.emit(
                "screener:preset-loaded", {"config": load_preset(name), "name": name}
            )
        except FileNotFoundError:
            app.emit("screener:preset-loaded", {"error": "Preset not found."})

    def on_preset_save(data: dict[str, Any], *_: Any) -> None:
        """Save the configuration and reply with the refreshed list."""
        from openbb_tmx.utils.screener_presets import save_preset

        try:
            config = json.loads(data.get("config") or "{}")
            presets = save_preset(str(data.get("name") or ""), config)
        except (TypeError, ValueError, OSError):
            app.emit("screener:presets", {"error": "The preset could not be saved."})
            return

        app.emit("screener:presets", {"presets": presets})

    def on_preset_delete(data: dict[str, Any], *_: Any) -> None:
        """Delete one saved configuration and reply with the refreshed list."""
        from openbb_tmx.utils.screener_presets import delete_preset

        app.emit(
            "screener:presets", {"presets": delete_preset(str(data.get("name") or ""))}
        )

    return {
        "screener:run": on_run,
        "pywry:update-theme": on_theme,
        "screener:presets-list": on_presets_list,
        "screener:preset-load": on_preset_load,
        "screener:preset-save": on_preset_save,
        "screener:preset-delete": on_preset_delete,
    }


_APP: Any = None


def _get_app(theme_mode: Any) -> Any:
    """Return the process-wide PyWry application, creating it once."""
    global _APP  # noqa: PLW0603
    from pywry import PyWry

    if _APP is None:
        _APP = PyWry(theme=theme_mode)
    else:
        _APP.theme = theme_mode

    return _APP


def launch_screener_builder(
    theme: str = "dark", width: int = 1320, height: int = 880
) -> Any:
    """Open the builder and return the window handle without blocking.

    Parameters
    ----------
    theme : str
        Either 'dark' or 'light'.
    width : int
        The window width.
    height : int
        The window height.

    Returns
    -------
    Any
        The PyWry window handle, or the inline widget in a notebook.
    """
    from pywry import ThemeMode

    from openbb_tmx.utils.screener_iframe import build_screener_content

    theme_mode = ThemeMode.LIGHT if str(theme).lower() == "light" else ThemeMode.DARK
    app = _get_app(theme_mode)
    content, toolbars, modals, _ = build_screener_content(theme, transport="bridge")

    return app.show(
        content,
        title="OpenBB - TMX Screener Builder",
        width=width,
        height=height,
        include_aggrid=True,
        aggrid_theme="balham",
        toolbars=toolbars,
        modals=modals,
        callbacks=make_screener_callbacks(app),
    )
