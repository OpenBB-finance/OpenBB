# OpenBB Charting

Plotly-based charting for the OpenBB Platform. Installing this package registers a `charting` accessor on every `OBBject` command result and enables the `chart=True` argument on Platform endpoints that have a chart.

## Installation

```bash
pip install openbb-charting
```

To display charts in a native desktop window, install the PyWry extra:

```bash
pip install "openbb-charting[pywry]"
```

On Linux, PyWry requires system WebKit/GTK libraries:

- Debian / Ubuntu / Mint: `sudo apt install libwebkit2gtk-4.1-dev libgtk-3-dev`
- Arch / Manjaro: `sudo pacman -S webkit2gtk`
- Fedora: `sudo dnf install gtk3-devel webkit2gtk3-devel`

## Usage

Pass `chart=True` to an endpoint that has a chart, then call `show()` on the result:

```python
from openbb import obb

data = obb.equity.price.historical("AAPL", provider="yfinance", chart=True)
data.show()
```

The same chart is reachable through the `charting` accessor on any result, without `chart=True`:

```python
res = obb.equity.price.historical("AAPL", provider="yfinance")
res.charting.show()
```

### Which commands have a chart

Charts are contributed by the installed extensions. List the registered routes:

```python
from openbb_charting import Charting

Charting.functions()
```

### Technical-analysis overlays — `to_chart`

`to_chart` rebuilds the chart of a time-series (OHLCV) result with indicator overlays. Indicators and their parameters are passed through the `indicators` argument:

```python
res = obb.equity.price.historical("AAPL", provider="yfinance")
res.charting.to_chart(
    indicators=dict(
        sma=dict(length=[20, 50]),
        rsi=dict(length=14),
        macd=dict(fast=12, slow=26, signal=9),
    )
)
res.show()
```

List every available indicator and its parameters:

```python
res.charting.indicators()    # from a result
Charting.indicators()        # standalone
```

## Building charts directly from data

The accessor exposes builders that accept a DataFrame or a list of `Data` (such as `OBBject.results`) and return an `OpenBBFigure`. Their input signatures differ; `create_line_chart` and `create_bar_chart` also display the chart by default — pass `render=False` to build it without displaying.

```python
res = obb.equity.price.historical("AAPL", provider="yfinance")
df = res.to_dataframe()

fig = res.charting.create_line_chart(data=res.results, target="close", render=False)
fig = res.charting.create_bar_chart(data=res.results, x="date", y="volume", render=False)
fig = res.charting.create_correlation_matrix(data=res.results, method="pearson")
fig = res.charting.create_3d_surface(X=df["open"], Y=df["high"], Z=df["close"])
fig.show()
```

## Adding a chart to a command

Register a charting-view class through the `openbb_charting_extension` entry-point group in your `pyproject.toml`:

```toml
[project.entry-points."openbb_charting_extension"]
my_extension = "openbb_my_extension.my_extension_views:MyExtensionViews"
```

A view method is matched to an endpoint by replacing the route's slashes with underscores: `/equity/price/historical` → `equity_price_historical`, `/technical/ema` → `technical_ema`. Each method receives the command output as `**kwargs` and returns a `tuple[OpenBBFigure, dict[str, Any]]` — the interactive figure plus the JSON content the API serializes.

```python
"""Views for MyExtension."""

from typing import Any

from openbb_charting.charts.price_historical import price_historical
from openbb_charting.core.openbb_figure import OpenBBFigure


class MyExtensionViews:
    """MyExtension Views."""

    @staticmethod
    def my_extension_price_historical(**kwargs) -> tuple[OpenBBFigure, dict[str, Any]]:
        """My Extension Price Historical Chart."""
        return price_historical(**kwargs)
```

The chart is then produced by setting `chart=True` on the command, or via `result.charting.show()`.

## Replacing the engine, hooks, and backend

The Platform interfaces (Python, API, CLI, MCP) do not depend on `openbb-charting` by name; they resolve the active engine from whichever OBBject extension registers the `charting` accessor. Three things are pluggable through entry points alone.

### Replace the engine

Ship an OBBject extension that registers the `charting` accessor:

```toml
[project.entry-points."openbb_obbject_extension"]
my_charting = "openbb_my_charting:ext"   # ext = Extension(name="charting")
```

If `openbb-charting` is uninstalled, your engine is used automatically. When both are installed, select one with `system_settings.charting_extension` (or the `OPENBB_CHARTING_EXTENSION` environment variable). An engine must expose the `functions()` classmethod, and `get_backend_class()` to be usable from the CLI.

### Chart lifecycle hooks

Register a `ChartingHook` subclass under the `openbb_charting_hooks` group. Hooks run inside chart creation, so they fire for every interface:

```toml
[project.entry-points."openbb_charting_hooks"]
my_hook = "openbb_my_pkg.hooks:MyHook"
```

```python
from openbb_core.app.charting import ChartingHook


class MyHook(ChartingHook):
    """Watermark every figure after it is built."""

    routes = ()        # empty matches all routes
    priority = 100     # lower runs first

    def post_figure(self, context):
        context.figure.add_annotation(text="INTERNAL", opacity=0.1)
        return context
```

Stages: `resolve_data`, `pre_figure`, `post_figure`, `pre_render`, `post_render`. A hook mutates `context` in place and/or returns a new one.

### Backend override

Swap the rendering backend (PyWry / browser / custom) without replacing the engine, via the `openbb_charting_backend` group:

```toml
[project.entry-points."openbb_charting_backend"]
my_backend = "openbb_my_pkg.backend:MyBackend"
```

A backend is constructed with a single `charting_settings` argument. The override is opt-in: set `system_settings.charting_backend` (or `OPENBB_CHARTING_BACKEND`) to the registered name. Without a selection, the engine keeps its built-in backend.
