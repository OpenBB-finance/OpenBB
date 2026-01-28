# AGENTS.md - PyWry Library Guide for AI Coding Agents

> **Purpose**: This document provides AI coding agents with comprehensive context to understand, develop with, and contribute to the PyWry library.

---

## Quick Reference

| Aspect | Details |
|--------|---------|
| **Language** | Python 3.10+ |
| **Type System** | Strict typing with Pydantic v2 models |
| **Style** | Ruff (line length 100), NumPy docstrings |
| **Testing** | pytest with fixtures, `PYWRY_HEADLESS=1` for CI |
| **Architecture** | Subprocess IPC (desktop) + FastAPI inline server (notebooks) |
| **Scaling** | Deploy mode with Redis-backed state for multi-worker deployments |

---

## Project Overview

**PyWry** is a blazingly fast rendering library for generating and managing native desktop windows, iFrames, and Jupyter widgets — with full bidirectional Python ↔ JavaScript communication.

Unlike dashboard libraries that only render output, PyWry provides a complete event system where Python can send events to JavaScript and JavaScript can invoke Python callbacks, enabling truly interactive applications.

Built on [PyTauri](https://pypi.org/project/pytauri/) (which uses Rust's [Tauri](https://tauri.app/) framework), it leverages the OS webview instead of bundling a browser engine—resulting in binaries under 3MB compared to Electron's 150MB+ overhead.

### Core Capabilities

- **Five Window Modes**: `NEW_WINDOW`, `SINGLE_WINDOW`, `MULTI_WINDOW`, `NOTEBOOK`, `BROWSER`
- **Notebook Support**: Automatic inline rendering via anywidget or IFrame in Jupyter/Colab
- **Toolbar System**: 18 declarative Pydantic components with 7 layout positions — automatic nested flexbox structure
- **Two-Way Events**: Python ↔ JavaScript communication with pre-wired Plotly/AgGrid events and utility events for DOM manipulation
- **Theming & CSS**: Light/dark modes, 60+ CSS variables, component ID targeting, and dynamic styling via events (`pywry:set-style`, `pywry:inject-css`)
- **Security**: Scoped token auth enabled by default, CSP headers, internal API protection, production presets available
- **AgGrid Tables**: Best-in-class Pandas → AgGrid conversion with pre-wired events, context menus, and practical defaults
- **Plotly Charts**: Plotly rendering with pre-wired plot events for Dash-like interactivity
- **Toast Notifications**: Built-in alert system with positioning (info, success, warning, error, confirm)
- **Marquee Ticker**: Scrolling text/content with dynamic updates
- **Secrets Handling**: Secure password inputs — values stored server-side, never rendered in HTML
- **Hot Reload**: CSS injection and JS refresh with scroll preservation
- **Bundled Libraries**: Plotly.js 3.3.1 and AgGrid 35.0.0 (offline capable)
- **Native File Dialogs**: Tauri-powered save/open dialogs and filesystem access
- **Configuration System**: TOML files, pyproject.toml, and environment variables
- **CLI Tools**: Configuration management and project initialization
- **Deploy Mode**: Horizontal scaling with Redis-backed state for multi-worker deployments
- **Authentication & RBAC**: JWT-based authentication with role-based access control

### Dependencies

```
Python 3.10+
pytauri >= 0.8.0
pytauri-wheel >= 0.8.0
pydantic >= 2.0.0
pydantic-settings >= 2.0.0
anyio >= 4.0.0
fastapi >= 0.128.0
uvicorn >= 0.40.0
watchdog >= 3.0.0
websockets >= 15.0.1
requests >= 2.32.5
pandas >= 1.5.3
anywidget >= 0.9.0 (optional, recommended)
redis >= 5.0.0 (optional, for deploy mode)
```

---

## Architecture Overview

### Rendering Paths

PyWry automatically selects the appropriate rendering path based on environment:

| Environment | Rendering Path | Module | Return Type |
|-------------|----------------|--------|-------------|
| Desktop (script/terminal) | Native Window | `pywry.app.PyWry` | `NativeWindowHandle` |
| Jupyter/VS Code with anywidget | Notebook Widget | `pywry.widget` | `PyWryWidget` |
| Jupyter/VS Code without anywidget | Inline IFrame | `pywry.inline` | `InlineWidget` |
| Headless / Server / SSH | Browser Mode | `pywry.window_manager.modes.browser` | `InlineWidget` |

### Window Modes

| Mode | Behavior |
|------|----------|
| `NEW_WINDOW` | Creates new window for each `show()` call |
| `SINGLE_WINDOW` | Reuses one window, replaces content |
| `MULTI_WINDOW` | Multiple labeled windows, update by label |
| `NOTEBOOK` | Inline rendering in Jupyter notebooks (auto-detected) |
| `BROWSER` | Opens in system browser, uses FastAPI server (headless/SSH) |

### Key Architectural Points

1. **Desktop Mode**: Python manages high-level API via `PyWry` class; PyTauri subprocess handles window creation and OS webview; JSON IPC over stdin/stdout; subprocess starts lazily on first `show()` call

2. **Notebook Mode**: Auto-detected via `notebook.py`; FastAPI server starts on first render; IFrame displays content; bidirectional events via WebSocket

3. **anywidget Mode**: Uses anywidget/traitlets for Jupyter widget protocol; bundles Plotly.js and AgGrid as ESM modules

4. **Browser Mode**: Same FastAPI server as Notebook mode; opens URL in system default browser; ideal for headless/SSH/server environments

---

## Directory Structure

```
pywry/
├── __init__.py          # Public API exports
├── __main__.py          # PyTauri subprocess entry point
├── app.py               # Main PyWry class - user entry point
├── runtime.py           # PyTauri subprocess management (stdin/stdout IPC)
├── inline.py            # FastAPI-based inline rendering + InlineWidget class
├── notebook.py          # Notebook environment detection (NotebookEnvironment enum)
├── widget.py            # anywidget-based widgets (PyWryWidget, PyWryPlotlyWidget, PyWryAgGridWidget)
├── widget_protocol.py   # BaseWidget protocol and NativeWindowHandle class
├── config.py            # Layered configuration system (pydantic-settings)
├── models.py            # Pydantic models (WindowConfig, HtmlContent, ThemeMode, WindowMode)
├── templates.py         # HTML template builder with CSP, themes, scripts, toolbar
├── scripts.py           # JavaScript bridge code injected into windows
├── callbacks.py         # Event callback registry (singleton)
├── assets.py            # Bundled asset loading (Plotly.js, AgGrid, CSS)
├── asset_loader.py      # CSS/JS file loading with caching
├── grid.py              # AgGrid Pydantic models (ColDef, GridOptions, etc.)
├── plotly_config.py     # Plotly configuration models (PlotlyConfig, ModeBarButton, etc.)
├── toolbar.py           # Toolbar component models (Button, Select, etc.)
├── state_mixins.py      # Widget state management mixins
├── hot_reload.py        # Hot reload manager
├── watcher.py           # File system watcher (watchdog-based)
├── log.py               # Logging utilities
├── cli.py               # CLI commands (config, init)
├── Tauri.toml           # Tauri configuration
├── capabilities/        # Tauri capability permissions
│   └── default.toml
├── commands/            # IPC command handlers
│   └── window_commands.py
├── frontend/            # Frontend HTML and bundled assets
│   ├── index.html
│   ├── assets/          # Compressed libraries (plotly, ag-grid, icons)
│   ├── src/             # JavaScript files (main.js, aggrid-defaults.js, plotly-defaults.js)
│   └── style/           # CSS files (pywry.css)
├── state/               # Pluggable state management for deploy mode
│   ├── __init__.py      # Public exports (stores, factory functions, types)
│   ├── _factory.py      # Factory functions for store instantiation
│   ├── memory.py        # In-memory state backends (default)
│   ├── redis.py         # Redis-backed state backends
│   ├── types.py         # Type definitions (StateBackend, WidgetData, etc.)
│   └── auth.py          # Authentication and RBAC utilities
├── utils/               # Utility helpers
└── window_manager/      # Window mode implementations
    ├── controller.py
    ├── lifecycle.py
    └── modes/           # base.py, new_window.py, single_window.py, multi_window.py, browser.py
```

---

## Core API

### Imports

```python
# Main class
from pywry import PyWry

# Enums
from pywry import WindowMode, ThemeMode

# Models
from pywry import HtmlContent, WindowConfig

# Toolbar components
from pywry import (
    Toolbar, Button, Select, MultiSelect, TextInput, TextArea, SearchInput,
    SecretInput, NumberInput, DateInput, SliderInput, RangeInput, Toggle,
    Checkbox, RadioGroup, TabGroup, Div, Marquee, TickerItem, Option, ToolbarItem
)

# Plotly configuration (for customizing modebar, icons, buttons)
from pywry import PlotlyConfig, PlotlyIconName, ModeBarButton, ModeBarConfig, SvgIcon, StandardButton

# Grid models (for AgGrid customization)
from pywry.grid import ColDef, ColGroupDef, DefaultColDef, RowSelection, GridOptions, GridConfig, GridData, build_grid_config, to_js_grid_config

# State mixins (for extending custom widgets)
from pywry import GridStateMixin, PlotlyStateMixin, ToolbarStateMixin

# Inline functions (for notebooks)
from pywry.inline import show_plotly, show_dataframe, block, stop_server

# Notebook detection
from pywry import NotebookEnvironment, detect_notebook_environment, is_anywidget_available, should_use_inline_rendering

# Widget classes (PyWryWidget for notebooks)
from pywry import PyWryWidget, PyWryPlotlyWidget, PyWryAgGridWidget

# Widget protocol (for type checking and custom implementations)
from pywry.widget_protocol import BaseWidget, NativeWindowHandle, is_base_widget

# Window manager
from pywry import BrowserMode, get_lifecycle

# Settings (exported from pywry)
from pywry import PyWrySettings, SecuritySettings, WindowSettings, ThemeSettings, HotReloadSettings, TimeoutSettings, AssetSettings, LogSettings

# Settings (require full path import)
from pywry.config import ServerSettings, DeploySettings

# Asset loading
from pywry import AssetLoader, get_asset_loader

# Callback registry
from pywry import CallbackFunc, WidgetType, get_registry

# Runtime (for low-level PyTauri access in native mode)
# Note: runtime is importable from pywry but not in __all__
from pywry import runtime

# State management (for deploy mode / horizontal scaling)
from pywry.state import (
    get_widget_store,
    get_event_bus,
    get_connection_router,
    get_session_store,
    is_deploy_mode,
    get_worker_id,
    get_state_backend,
    WidgetData,
    EventMessage,
    ConnectionInfo,
    UserSession,
    StateBackend,
)
```

### PyWry Class

```python
PyWry(
    mode: WindowMode = WindowMode.NEW_WINDOW,
    theme: ThemeMode = ThemeMode.DARK,
    title: str = "PyWry",
    width: int = 800,
    height: int = 600,
    settings: PyWrySettings | None = None,
    hot_reload: bool = False,
)
```

### Display Methods

```python
# Show HTML content - returns NativeWindowHandle (native) or widget (notebook)
handle = app.show(
    content,                    # str or HtmlContent
    title=None,
    width=None,                 # int for pixels, str for CSS (e.g., "60%")
    height=None,
    callbacks=None,             # Dict of event handlers {"event:name": handler}
    include_plotly=False,
    include_aggrid=False,
    aggrid_theme="alpine",
    label=None,
    watch=None,                 # Enable hot reload file watching
    toolbars=None,              # List of Toolbar objects
)

# Show Plotly figure
handle = app.show_plotly(
    figure,                     # Plotly Figure or dict
    title=None,
    width=None,
    height=None,
    callbacks=None,
    label=None,
    inline_css=None,
    on_click=None,              # Click callback (notebook mode)
    on_hover=None,              # Hover callback (notebook mode)
    on_select=None,             # Selection callback (notebook mode)
    toolbars=None,
    config=None,                # PlotlyConfig or dict
)

# Show DataFrame as AgGrid
handle = app.show_dataframe(
    data,                       # pandas DataFrame or dict
    title=None,
    width=None,
    height=None,
    callbacks=None,
    label=None,
    column_defs=None,           # List of ColDef objects
    aggrid_theme="alpine",
    grid_options=None,
    toolbars=None,
    inline_css=None,
    on_cell_click=None,         # Cell click callback (notebook mode)
    on_row_selected=None,       # Row selection callback (notebook mode)
    server_side=False,          # Use server-side mode for large datasets
)
```

### HtmlContent Model

Pass structured content with custom CSS/JS files and data:

```python
from pywry import HtmlContent

content = HtmlContent(
    html="<div id='app'></div>",       # HTML content
    json_data={"items": [1, 2, 3]},    # Accessible as window.json_data in JS
    css_files=["style.css"],            # CSS files to include
    script_files=["app.js"],            # JS files to include
    inline_css="body { padding: 20px; }", # Inline CSS
    init_script="initApp()",            # JS to run after DOM ready
    watch=True,                         # Enable hot reload for these files
)
app.show(content, title="Custom App")
```

| Field | Type | Description |
|-------|------|-------------|
| `html` | `str` | HTML content |
| `json_data` | `dict` | Data accessible as `window.json_data` |
| `css_files` | `list[str]` | CSS file paths to include |
| `script_files` | `list[str]` | JS file paths to include |
| `inline_css` | `str` | Inline CSS styles |
| `init_script` | `str` | JavaScript to run after DOM ready |
| `watch` | `bool` | Enable hot reload for included files |

### PlotlyConfig

Customize chart behavior and modebar:

```python
from pywry import PlotlyConfig, ModeBarButton, SvgIcon

config = PlotlyConfig(
    responsive=True,
    display_mode_bar=True,             # True, False, or "hover"
    scroll_zoom=False,
    mode_bar_buttons_to_remove=["lasso2d", "select2d"],
    mode_bar_buttons_to_add=[
        ModeBarButton(
            name="custom",
            title="Custom Action",
            icon=SvgIcon(path="M10 10 L90 90", width=100, height=100),
            click="function(gd) { window.pywry.emit('app:custom', {}); }"
        )
    ],
)
app.show_plotly(fig, config=config)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `responsive` | `bool` | Resize chart with container |
| `display_mode_bar` | `bool \| str` | Show modebar (True, False, "hover") |
| `scroll_zoom` | `bool` | Enable scroll to zoom |
| `mode_bar_buttons_to_add` | `list` | Custom `ModeBarButton` objects |
| `mode_bar_buttons_to_remove` | `list[str]` | Remove default buttons by name |

### ColDef and GridOptions

Configure AgGrid columns and behavior:

```python
from pywry.grid import ColDef, DefaultColDef, GridOptions, RowSelection

# Column definitions
col_defs = [
    ColDef(field="name", header_name="Name", pinned="left", width=150),
    ColDef(field="age", header_name="Age", filter="agNumberColumnFilter", sortable=True),
    ColDef(field="email", header_name="Email", editable=True),
]

# Default column settings
default_col_def = DefaultColDef(
    sortable=True,
    filter=True,
    resizable=True,
    flex=1,
)

# Grid options
grid_options = GridOptions(
    default_col_def=default_col_def,
    row_selection=RowSelection(mode="multiple", enable_click_selection=True),
    pagination=True,
    pagination_page_size=50,
)

app.show_dataframe(df, column_defs=col_defs, grid_options=grid_options)
```

**ColDef Key Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `field` | `str` | DataFrame column name |
| `header_name` | `str` | Display header |
| `pinned` | `str` | Pin column: "left", "right", None |
| `width` | `int` | Column width in pixels |
| `flex` | `int` | Flex grow factor |
| `filter` | `str \| bool` | Filter type or True for default |
| `sortable` | `bool` | Enable column sorting |
| `editable` | `bool` | Enable cell editing |
| `value_formatter` | `str` | JS formatter function |
| `cell_renderer` | `str` | JS renderer function |

### Server-Side AgGrid (Large Datasets)

For datasets >10K rows, use server-side mode with pagination callbacks:

```python
import pandas as pd
from pywry import PyWry

app = PyWry()
df = pd.DataFrame(...)  # Large dataset

def on_page_request(data, event_type, label):
    """Handle pagination requests from AgGrid."""
    start = data["startRow"]
    end = data["endRow"]
    
    # Slice your data based on request
    page_data = df.iloc[start:end].to_dict("records")
    
    # Send page response
    app.emit("grid:page-response", {
        "gridId": data["gridId"],
        "rows": page_data,
        "totalRows": len(df),
        "isLastPage": end >= len(df),
    }, label)

app.show_dataframe(
    df.head(100),  # Initial data (first page)
    server_side=True,
    callbacks={"grid:request-page": on_page_request}
)
```

### Hot Reload

Enable live updates during development:

```python
# Method 1: Constructor
app = PyWry(hot_reload=True)

# Method 2: HtmlContent with watch
content = HtmlContent(html="<h1>Hi</h1>", css_files=["style.css"], watch=True)
app.show(content, watch=True)

# Method 3: Toggle at runtime
app.enable_hot_reload()
app.refresh_css(label)  # Manual CSS reload
app.disable_hot_reload()
```

**Hot Reload Behavior:**
| File Type | Behavior |
|-----------|----------|
| `.css` | Injected without refresh (styles update instantly) |
| `.js`, `.html` | Full refresh with scroll position preservation |

### Multiple Charts/Grids (ID Targeting)

When a window has multiple charts or grids, use IDs to target specific ones:

```python
# Target specific chart with chart_id
widget.update_layout({"title": "Updated"}, chart_id="sales-chart")
widget.reset_zoom(chart_id="revenue-chart")

# Target specific grid with grid_id
widget.update_data(new_rows, grid_id="users-grid")
widget.update_cell("row1", "status", "Active", grid_id="orders-grid")

# Register handlers for specific components (compound event ID)
app.on("plotly:click:sales-chart", handle_sales_click)
app.on("grid:row-selected:users-grid", handle_user_selection)
```

**ID Hierarchy:**
| ID Type | Scope | Example |
|---------|-------|---------|
| `label` | Window/Widget | `"pywry-abc123"` |
| `chartId` | Plotly chart | `"sales-chart"` |
| `gridId` | AgGrid table | `"users-grid"` |
| `componentId` | Toolbar item | `"export-btn"` |

### Event Handler Signature

```python
def handler(data: dict, event_type: str, label: str) -> None:
    """
    data: Event payload from JavaScript
    event_type: The event name (e.g., "app:click", "plotly:click")
    label: Window/widget label that triggered the event
    """
    pass
```

### Sending Events to JavaScript

```python
# All modes return a handle/widget with emit() method
handle = app.show("<h1>Hello</h1>")
handle.emit("app:response", {"key": "value"})

# Alternative: use app.emit() with window label
app.emit("app:response", {"key": "value"}, handle.label)
```

> **Low-level alternative:** For direct access to PyTauri runtime in native mode, use `from pywry import runtime` then `runtime.emit_event(handle.label, ...)`.

### Widget Methods (Plotly/AgGrid)

Widgets returned by `show_plotly()` and `show_dataframe()` have convenience methods:

**Plotly Widget Methods:**
```python
widget = app.show_plotly(fig)
widget.update_figure(new_fig, chart_id=None)        # Replace entire figure
widget.update_layout({"title": "New Title"})        # Update layout properties
widget.update_traces({"marker.color": "red"}, [0])  # Update specific traces
widget.reset_zoom(chart_id=None)                    # Reset zoom/pan
widget.request_plotly_state(chart_id=None)          # Request current state -> plotly:state-response
```

**AgGrid Widget Methods:**
```python
widget = app.show_dataframe(df)
widget.update_data(rows, grid_id=None)              # Replace row data
widget.update_columns(col_defs, grid_id=None)       # Replace column definitions
widget.update_cell(row_id, col_id, value)           # Update single cell
widget.update_grid(data=None, columns=None)         # Combined update
widget.request_grid_state(grid_id=None)             # Request state -> grid:state-response
widget.restore_state(state, grid_id=None)           # Restore saved state
widget.reset_state(grid_id=None, hard=False)        # Reset to initial state
```

### Other Methods

| Method | Description |
|--------|-------------|
| `emit(event_type, data, label=None)` | Send event to JavaScript in window(s) |
| `alert(message, alert_type, ...)` | Show toast notification |
| `on(event_type, handler, ...)` | Register event handler |
| `on_grid(event_type, handler, ...)` | Register grid-specific event handler |
| `on_chart(event_type, handler, ...)` | Register chart-specific event handler |
| `on_toolbar(event_type, handler, ...)` | Register toolbar-specific event handler |
| `on_html(event_type, handler, ...)` | Register HTML element event handler |
| `on_window(event_type, handler, ...)` | Register window lifecycle event handler |
| `eval_js(script, label=None)` | Execute JavaScript in window(s) |
| `update_content(html, label=None)` | Update window HTML content |
| `show_window(label)` | Show a hidden window |
| `hide_window(label)` | Hide a window (keeps it alive) |
| `close(label=None)` | Close specific or all windows |
| `get_labels()` | Get list of all active window labels |
| `is_open(label=None)` | Check if window(s) are open |
| `refresh(label=None)` | Refresh window content |
| `refresh_css(label=None)` | Hot-reload CSS without page refresh |
| `enable_hot_reload()` | Enable hot reload |
| `disable_hot_reload()` | Disable hot reload |
| `block(label=None)` | Block until window(s) close |
| `destroy()` | Close all windows and cleanup |
| `get_lifecycle()` | Get WindowLifecycle manager |

---

## Event System

### Namespace Pattern

Events follow the format `namespace:event-name`:

| Part | Rules | Examples |
|------|-------|----------|
| **namespace** | Starts with letter, alphanumeric only | `app`, `plotly`, `grid`, `myapp` |
| **event-name** | Starts with letter, alphanumeric + hyphens + underscores | `click`, `row-select`, `update_data` |

**Valid:** `app:save`, `plotly:click`, `grid:row-select`

### Reserved Namespaces

| Namespace | Purpose |
|-----------|---------|
| `pywry:*` | System events (initialization, results) |
| `plotly:*` | Plotly chart events |
| `grid:*` | AgGrid table events |

> **Note:** The `toolbar:` namespace is NOT reserved. Toolbar state response events use `toolbar:state-response` by convention.

### Pre-Registered Events

**Plotly Events (JS → Python):**

| Event | Trigger | Key Payload Fields |
|-------|---------|-------------------|
| `plotly:click` | User clicks a data point | `chartId`, `points`, `widget_type: "chart"` |
| `plotly:hover` | User hovers over a point | `chartId`, `points`, `widget_type` |
| `plotly:selected` | User selects with box/lasso | `chartId`, `points`, `range`, `lassoPoints` |
| `plotly:relayout` | User zooms, pans, or resizes | `chartId`, `relayout_data`, `widget_type` |
| `plotly:state-response` | Response to state request | `chartId`, `layout`, `data` |

**Plotly Events (Python → JS):**

| Event | Description | Key Payload Fields |
|-------|-------------|-------------------|
| `plotly:update-figure` | Replace entire figure | `figure`, `chartId?`, `config?` |
| `plotly:update-layout` | Update layout properties | `layout`, `chartId?` |
| `plotly:update-traces` | Update trace data | `update`, `indices`, `chartId?` |
| `plotly:reset-zoom` | Reset chart zoom | `chartId?` |
| `plotly:request-state` | Request current chart state | `chartId?` |
| `plotly:export-data` | Request trace data export | `chartId?` |

> **Note:** `plotly:export-data` triggers `plotly:export-response` (JS → Python) with payload `{ data: [{ traceIndex, name, x, y, type }, ...] }`.

**AgGrid Events (JS → Python):**

| Event | Trigger | Key Payload Fields |
|-------|---------|-------------------|
| `grid:row-selected` | Row selection changes | `gridId`, `rows`, `widget_type: "grid"` |
| `grid:cell-click` | User clicks a cell | `gridId`, `rowIndex`, `colId`, `value`, `data` |
| `grid:cell-edit` | User edits a cell | `gridId`, `rowIndex`, `rowId`, `colId`, `oldValue`, `newValue`, `data` |
| `grid:filter-changed` | Filter applied | `gridId`, `filterModel`, `widget_type` |
| `grid:data-truncated` | Client-side dataset truncated | `gridId`, `displayedRows`, `truncatedRows`, `message` |
| `grid:mode` | Grid mode info (server-side) | `gridId`, `mode`, `serverSide`, `totalRows`, `blockSize` |
| `grid:request-page` | Server-side requests data block | `gridId`, `startRow`, `endRow`, `sortModel`, `filterModel` |
| `grid:state-response` | Response to state request | `gridId`, `columnState`, `filterModel`, `sortModel` |

**AgGrid Events (Python → JS):**

| Event | Description | Key Payload Fields |
|-------|-------------|-------------------|
| `grid:page-response` | Respond to page request | `gridId`, `rows`, `totalRows`, `isLastPage` |
| `grid:update-data` | Update row data | `data`, `gridId?`, `strategy?` |
| `grid:update-columns` | Update column definitions | `columnDefs`, `gridId?` |
| `grid:update-cell` | Update single cell | `rowId`, `colId`, `value`, `gridId?` |
| `grid:update-grid` | Combined update (data+columns+state) | `data?`, `columnDefs?`, `restoreState?`, `gridId?` |
| `grid:request-state` | Request grid state | `gridId?`, `context?` |
| `grid:restore-state` | Restore saved state | `state`, `gridId?` |
| `grid:reset-state` | Reset state | `gridId?`, `hard?` |
| `grid:update-theme` | Change grid theme | `theme`, `gridId?` |
| `grid:show-notification` | Show grid notification | `message`, `duration?`, `gridId?` |

**System Events (JS → Python):**

| Event | Trigger | Key Payload Fields |
|-------|---------|-------------------|
| `pywry:ready` | Window/widget initialized | `{}` |
| `pywry:result` | Data via `window.pywry.result()` | `any` |
| `pywry:content-request` | Request content (load/reload) | `widget_type`, `window_label`, `reason` |
| `pywry:disconnect` | Widget disconnected (inline mode) | `{}` |

**System Events (Python → JS):**

| Event | Description | Key Payload Fields |
|-------|-------------|-------------------|
| `pywry:update-theme` | Update theme | `theme` |
| `pywry:inject-css` | Inject CSS | `css`, `id?` |
| `pywry:remove-css` | Remove injected CSS | `id` |
| `pywry:set-style` | Update element styles | `id?`, `selector?`, `styles` |
| `pywry:set-content` | Update element content | `id?`, `selector?`, `html?`, `text?` |
| `pywry:update-html` | Replace widget HTML | `html` |
| `pywry:download` | Trigger file download | `content`, `filename`, `mimeType?` |
| `pywry:download-csv` | Trigger CSV download (widget mode) | `csv`, `filename` |
| `pywry:navigate` | Navigate to URL | `url` |
| `pywry:alert` | Show toast notification | `message`, `type?`, `title?`, `duration?` |
| `pywry:refresh` | Refresh window content | `{}` |

### Toast Notifications (`pywry:alert`)

PyWry provides a unified toast notification system across all rendering paths.

**Alert Types:**

| Type | Behavior | Use Case |
|------|----------|----------|
| `info` | Auto-dismiss 5s | Status updates |
| `success` | Auto-dismiss 3s | Completed actions |
| `warning` | Persist until clicked | Important notices |
| `error` | Persist until clicked | Errors requiring acknowledgment |
| `confirm` | Blocks UI until response | User confirmation needed |

**AlertPayload Model:**

```python
class AlertPayload(BaseModel):
    message: str  # Required
    type: Literal["info", "success", "warning", "error", "confirm"] = "info"
    title: str | None = None
    duration: int | None = None  # Auto-dismiss ms
    callback_event: str | None = None  # Event on confirm/cancel
    position: Literal["top-right", "bottom-right", "bottom-left", "top-left"] = "top-right"
```

**Usage:**

```python
# Convenience method
app.alert("Data loaded", alert_type="success", label=label)

# With emit
app.emit("pywry:alert", {"message": "Done", "type": "info"}, label)

# Confirm dialog with callback
app.alert("Delete item?", alert_type="confirm", callback_event="app:confirm-delete", label=label)

# Handle response
@app.on("app:confirm-delete")
def on_confirm(data, event_type, label):
    if data.get("confirmed"):
        # User clicked Confirm
        pass
```

**Keyboard:** Press `Escape` to dismiss all visible toasts.

### JavaScript Bridge

```javascript
// Send event to Python
window.pywry.emit("app:action", { key: "value" });

// Listen for Python events
window.pywry.on("app:update", function(data) {
    console.log("Received:", data);
});

// Access injected globals
window.__PYWRY_LABEL__        // Window label
window.json_data              // Data from HtmlContent.json_data
window.__PYWRY_PLOTLY_DIV__   // Plotly chart container
window.__PYWRY_GRID_API__     // AgGrid API
```

### Native File Dialogs (Desktop Mode Only)

In native desktop windows, access Tauri's file system APIs:

```javascript
// Save file dialog
const path = await window.__TAURI__.dialog.save({
    defaultPath: "export.csv",
    filters: [{ name: "CSV", extensions: ["csv"] }]
});
if (path) {
    await window.__TAURI__.fs.writeTextFile(path, csvContent);
}

// Open file dialog
const selected = await window.__TAURI__.dialog.open({
    multiple: false,
    filters: [{ name: "JSON", extensions: ["json"] }]
});
if (selected) {
    const content = await window.__TAURI__.fs.readTextFile(selected);
    window.pywry.emit("app:file-loaded", { path: selected, content });
}

// Confirmation dialog
const confirmed = await window.__TAURI__.dialog.confirm("Delete this item?", {
    title: "Confirm Delete",
    okLabel: "Delete",
    cancelLabel: "Cancel"
});
```

> **Note:** File dialogs are only available in native desktop mode. For notebook/browser mode, use `pywry:download` event for downloads.

---

## Toolbar System

### Components

| Component | Emits |
|-----------|-------|
| `Button` | `{ componentId, ...data }` |
| `Select` | `{ value: str, componentId }` |
| `MultiSelect` | `{ values: [str, ...], componentId }` |
| `TextInput` | `{ value: str, componentId }` |
| `TextArea` | `{ value: str, componentId }` |
| `SearchInput` | `{ value: str, componentId }` |
| `SecretInput` | `{ value, componentId, encoded }` + `{event}:reveal`, `{event}:copy` |
| `NumberInput` | `{ value: number, componentId }` |
| `DateInput` | `{ value: "YYYY-MM-DD", componentId }` |
| `SliderInput` | `{ value: number, componentId }` |
| `RangeInput` | `{ start: number, end: number, componentId }` |
| `Toggle` | `{ value: bool, componentId }` |
| `Checkbox` | `{ value: bool, componentId }` |
| `RadioGroup` | `{ value: str, componentId }` |
| `TabGroup` | `{ value: str, componentId }` |
| `Div` | Container (no events) |
| `Marquee` | `{ value, componentId }` when clickable |
| `TickerItem` | Helper for Marquee (not a ToolbarItem) |

### Toolbar Positions

PyWry automatically creates nested flexbox wrappers based on which toolbars are present:

| Position | Description |
|----------|-------------|
| `"header"` | Full-width bar at very top (outermost) |
| `"footer"` | Full-width bar at very bottom (outermost) |
| `"left"` | Vertical bar on left, full height |
| `"right"` | Vertical bar on right, full height |
| `"top"` | Horizontal bar above content (inside left/right) |
| `"bottom"` | Horizontal bar below content (inside left/right) |
| `"inside"` | Floating overlay at top-right of content |

> **Note:** Layout wrappers (`.pywry-wrapper-*`) are created dynamically. If you only use `top` and `bottom`, no left/right wrappers are generated.

### Example

```python
from pywry import PyWry, Toolbar, Button, Select, Option

app = PyWry()
widget = None

def on_export(data, event_type, label):
    """Trigger a file download when export is clicked."""
    widget.emit("pywry:download", {
        "content": "name,score\nAlice,95\nBob,87",
        "filename": "export.csv",
        "mimeType": "text/csv"
    })

toolbar = Toolbar(
    position="top",
    items=[
        Button(label="Export", event="app:export", data={"format": "csv"}),
        Select(
            label="View:",
            event="view:change",
            options=[Option(label="Table", value="table"), Option(label="Chart", value="chart")],
            selected="table",
        ),
    ],
)

widget = app.show(
    '<h1 id="heading">Dashboard</h1>',
    toolbars=[toolbar],
    callbacks={"app:export": on_export}
)
```

### Common Component Properties

All toolbar items share these properties:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `event` | `str` | `"toolbar:input"` | Event name in `namespace:event-name` format |
| `component_id` | `str` | auto-generated | Unique ID (format: `{type}-{uuid8}`) |
| `label` | `str` | `""` | Label text displayed next to control |
| `description` | `str` | `""` | Tooltip text on hover |
| `disabled` | `bool` | `False` | Whether control is disabled |
| `style` | `str` | `""` | Inline CSS styles |

### Component Parameters Quick Reference

**Button:**
```python
Button(label="Save", event="app:save", data={"key": "val"}, variant="primary")
# Variants: primary|secondary|neutral|ghost|outline|danger|warning|icon
```

**Select / MultiSelect:**
```python
Select(label="Theme:", event="theme:change", options=[Option(label="Dark", value="dark")], selected="dark")
MultiSelect(label="Cols:", event="cols:change", options=["A", "B", "C"], selected=["A"])
# Shorthand: strings auto-convert to Option(label=s, value=s)
```

**TextInput / TextArea / SearchInput:**
```python
TextInput(label="Name:", event="form:name", placeholder="Enter name", debounce_ms=300)
TextArea(label="Notes:", event="form:notes", rows=4, resizable=True)
SearchInput(label="Search:", event="search:query", placeholder="Type to search...")
```

**SecretInput:**
```python
SecretInput(label="API Key:", event="secret:key", placeholder="Enter key")
# Emits: {event} with {value, encoded}, plus {event}:reveal and {event}:copy
```

**NumberInput:**
```python
NumberInput(label="Qty:", event="form:qty", min_value=0, max_value=100, step=1, value=10)
```

**DateInput:**
```python
DateInput(label="Date:", event="form:date", value="2024-01-01", min_date="2020-01-01")
```

**SliderInput / RangeInput:**
```python
SliderInput(label="Volume:", event="audio:volume", min_value=0, max_value=100, value=50, show_value=True)
RangeInput(label="Price:", event="filter:price", min_value=0, max_value=1000, start=100, end=500)
```

**Toggle / Checkbox:**
```python
Toggle(label="Dark Mode:", event="theme:toggle", value=True)
Checkbox(label="Accept Terms", event="form:terms", value=False)
```

**RadioGroup / TabGroup:**
```python
RadioGroup(label="Size:", event="form:size", options=["S", "M", "L"], selected="M", layout="horizontal")
TabGroup(event="view:tab", options=[Option(label="Chart", value="chart"), Option(label="Table", value="table")])
```

**Div (Container):**
```python
Div(children=[Button(...), Select(...)], class_name="my-group", style="gap: 8px;")
```

**Marquee / TickerItem:**
```python
Marquee(
    event="ticker:click",
    items=[
        TickerItem(ticker="AAPL", text="$150.25", styles={"color": "green"}),
        TickerItem(ticker="MSFT", text="$380.00"),
    ],
    speed=50,
    separator=" | ",
)
# Update dynamically via toolbar:marquee-set-item event
```

### Toolbar Container Options

```python
Toolbar(
    position="top",              # header|footer|left|right|top|bottom|inside
    items=[...],
    component_id="main-toolbar", # For state management
    collapsible=False,           # Allow collapse/expand
    collapsed=False,             # Initial collapsed state
    resizable=False,             # Allow drag-to-resize
    min_width=None,              # Min size for resizable
    max_width=None,              # Max size for resizable
)
```

### Toolbar State Management

```python
# Request current toolbar state
app.emit("toolbar:request-state", {"context": "save"}, label)

# Handle state response
def on_state(data, event_type, label):
    values = data["components"]  # {componentId: value, ...}
app.on("toolbar:state-response", on_state)

# Set single component value
app.emit("toolbar:set-value", {"componentId": "my-select", "value": "option2"}, label)

# Set multiple values
app.emit("toolbar:set-values", {"values": {"select-1": "A", "toggle-1": True}}, label)
```

---

## Configuration System

### Priority Order (highest last)

1. Built-in defaults
2. `pyproject.toml` `[tool.pywry]` section
3. `./pywry.toml`
4. User config (`~/.config/pywry/config.toml`)
5. Environment variables (`PYWRY_*`)

### Configuration Sections

| Section | Env Prefix | Description |
|---------|------------|-------------|
| `window` | `PYWRY_WINDOW__` | Default window properties |
| `theme` | `PYWRY_THEME__` | Custom CSS file path |
| `server` | `PYWRY_SERVER__` | Inline server settings (host, port, SSL, CORS) |
| `hot_reload` | `PYWRY_HOT_RELOAD__` | Hot reload behavior |
| `csp` | `PYWRY_CSP__` | Content Security Policy |
| `log` | `PYWRY_LOG__` | Logging configuration |
| `timeout` | `PYWRY_TIMEOUT__` | Timeout values |
| `asset` | `PYWRY_ASSET__` | Library versions |
| `deploy` | `PYWRY_DEPLOY__` | Deploy mode and state backend |

### Example pywry.toml

```toml
[window]
title = "My Application"
width = 1280
height = 720
devtools = false

[hot_reload]
enabled = true
debounce_ms = 100

[log]
level = "WARNING"

[deploy]
state_backend = "redis"
redis_url = "redis://localhost:6379/0"
redis_prefix = "pywry:"
```

### Server Settings (for Notebook/Browser Mode)

| Setting | Env Var | Default | Description |
|---------|---------|---------|-------------|
| `host` | `PYWRY_SERVER__HOST` | `127.0.0.1` | Server bind address |
| `port` | `PYWRY_SERVER__PORT` | `8765` | Server port |
| `ssl_certfile` | `PYWRY_SERVER__SSL_CERTFILE` | `None` | SSL certificate path |
| `ssl_keyfile` | `PYWRY_SERVER__SSL_KEYFILE` | `None` | SSL key path |
| `cors_origins` | `PYWRY_SERVER__CORS_ORIGINS` | `["*"]` | Allowed CORS origins |
| `workers` | `PYWRY_SERVER__WORKERS` | `1` | Number of workers |
| `reload` | `PYWRY_SERVER__RELOAD` | `False` | Enable auto-reload (dev) |

```toml
# Example: Production server config
[server]
host = "0.0.0.0"
port = 443
ssl_certfile = "/path/to/cert.pem"
ssl_keyfile = "/path/to/key.pem"
cors_origins = ["https://myapp.com"]
```

---

## Deploy Mode & Scaling

Deploy mode enables horizontal scaling for multi-worker deployments (e.g., behind a load balancer).

### When to Use Deploy Mode

| Scenario | Deploy Mode | Backend |
|----------|-------------|---------|
| Single process (development, notebooks) | Not needed | Memory (default) |
| Multiple workers (gunicorn, uvicorn) | Required | Redis |
| Load-balanced deployment | Required | Redis |
| Kubernetes / Docker Swarm | Required | Redis |

### State Stores

| Store | Purpose | Key Methods |
|-------|---------|-------------|
| `WidgetStore` | Widget metadata persistence | `get()`, `set()`, `delete()`, `list_widgets()` |
| `EventBus` | Cross-worker event routing | `publish()`, `subscribe()` |
| `ConnectionRouter` | WebSocket connection tracking | `register()`, `unregister()`, `get_worker()` |
| `SessionStore` | User session management | `get_session()`, `set_session()`, `delete_session()` |

### Factory Functions

```python
from pywry.state import (
    get_widget_store,      # Returns WidgetStore (memory or redis)
    get_event_bus,         # Returns EventBus (memory or redis)
    get_connection_router, # Returns ConnectionRouter
    get_session_store,     # Returns SessionStore
    is_deploy_mode,        # Returns True if state_backend != "memory"
    get_worker_id,         # Returns unique worker identifier
)
```

### Environment Variables

```bash
# Enable Redis backend
PYWRY_DEPLOY__STATE_BACKEND=redis
PYWRY_DEPLOY__REDIS_URL=redis://localhost:6379/0
PYWRY_DEPLOY__REDIS_PREFIX=pywry:

# TTL settings
PYWRY_DEPLOY__WIDGET_TTL=86400      # 24 hours
PYWRY_DEPLOY__CONNECTION_TTL=300    # 5 minutes

# Authentication (optional)
PYWRY_DEPLOY__ENABLE_AUTH=true
PYWRY_DEPLOY__AUTH_SECRET=your-secret-key
PYWRY_DEPLOY__RBAC_ENABLED=true
PYWRY_DEPLOY__DEFAULT_ROLE=viewer
```

### DeploySettings Reference

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `state_backend` | `StateBackend` | `memory` | `"memory"` or `"redis"` |
| `redis_url` | `str` | `redis://localhost:6379/0` | Redis connection URL |
| `redis_prefix` | `str` | `pywry:` | Key prefix for Redis keys |
| `widget_ttl` | `int` | `86400` | Widget data TTL (seconds) |
| `connection_ttl` | `int` | `300` | Connection registration TTL |
| `auto_cleanup` | `bool` | `True` | Auto-cleanup expired entries |
| `enable_auth` | `bool` | `False` | Enable JWT authentication |
| `auth_secret` | `str \| None` | `None` | JWT signing secret |
| `rbac_enabled` | `bool` | `False` | Enable role-based access |
| `default_role` | `str` | `viewer` | Default user role |

---

## Key Classes Reference

### Core Classes

| Class | File | Responsibility |
|-------|------|----------------|
| `PyWry` | `app.py` | Main user-facing API |
| `CallbackRegistry` | `callbacks.py` | Singleton managing event callbacks |
| `HotReloadManager` | `hot_reload.py` | File watching and CSS injection |
| `AssetLoader` | `asset_loader.py` | CSS/JS file loading with caching |

### NativeWindowHandle (Desktop Mode)

In native desktop mode, `show()` returns a `NativeWindowHandle` that provides full window control:

**Core Methods:**
```python
handle = app.show("<h1>Hello</h1>", title="My Window")

# Event communication
handle.emit("app:update", {"key": "value"})   # Send event to JS
handle.on("app:click", callback)              # Register event handler
handle.eval_js("console.log('Hello')")        # Execute JavaScript

# Content
handle.update("<h1>New Content</h1>")         # Replace HTML content

# Window visibility
handle.close()                                 # Close and destroy
handle.hide()                                  # Hide (keep alive)
handle.show_window()                          # Show hidden window

# Window properties (via proxy)
handle.set_title("New Title")
handle.set_size(1280, 720)
handle.set_min_size(400, 300)
handle.set_max_size(1920, 1080)
handle.set_always_on_top(True)
handle.set_decorations(False)                 # Remove title bar
handle.set_background_color(30, 30, 30)       # RGBA

# Window actions
handle.maximize()
handle.minimize()
handle.center()

# Developer tools
handle.open_devtools()
handle.close_devtools()
handle.set_zoom(1.5)                          # 150% zoom
```

**Properties:**
```python
handle.label        # str: Window identifier
handle.resources    # WindowResources: Metadata (content, config, created_at, etc.)
handle.proxy        # WindowProxy: Full WebviewWindow API access
```

**WindowProxy (Advanced):**
```python
proxy = handle.proxy

# State queries
proxy.is_maximized      # bool
proxy.is_minimized      # bool
proxy.is_fullscreen     # bool
proxy.is_focused        # bool
proxy.is_decorated      # bool
proxy.is_resizable      # bool
proxy.is_visible        # bool

# Position & Size
proxy.inner_size        # PhysicalSize(width, height)
proxy.outer_size        # PhysicalSize(width, height)
proxy.inner_position    # PhysicalPosition(x, y)
proxy.outer_position    # PhysicalPosition(x, y)
proxy.scale_factor      # float (e.g., 1.0, 1.5, 2.0 for HiDPI)

# Monitor info
proxy.current_monitor   # Monitor or None
proxy.primary_monitor   # Monitor or None
proxy.available_monitors  # list[Monitor]

# Actions
proxy.set_fullscreen(True)
proxy.set_resizable(False)
proxy.set_visible_on_all_workspaces(True)
proxy.navigate("https://example.com")
proxy.reload()
```

### Widget Classes

| Class | File | Responsibility |
|-------|------|----------------|
| `BaseWidget` | `widget_protocol.py` | Protocol defining unified widget API |
| `NativeWindowHandle` | `widget_protocol.py` | Handle for native windows implementing BaseWidget |
| `InlineWidget` | `inline.py` | IFrame-based widget (notebook fallback) |
| `PyWryWidget` | `widget.py` | Base anywidget |
| `PyWryPlotlyWidget` | `widget.py` | Plotly-specific anywidget |
| `PyWryAgGridWidget` | `widget.py` | AgGrid anywidget |

### Window Modes

| Class | File | Behavior |
|-------|------|----------|
| `NewWindowMode` | `window_manager/modes/new_window.py` | New window per show() |
| `SingleWindowMode` | `window_manager/modes/single_window.py` | Reuses one window |
| `MultiWindowMode` | `window_manager/modes/multi_window.py` | Multiple windows |
| `BrowserMode` | `window_manager/modes/browser.py` | Opens in browser |

### Configuration Classes

| Class | File | Purpose |
|-------|------|---------|
| `PyWrySettings` | `config.py` | Root settings |
| `SecuritySettings` | `config.py` | CSP configuration |
| `ServerSettings` | `config.py` | FastAPI server settings |
| `WindowSettings` | `config.py` | Default window properties |
| `DeploySettings` | `config.py` | Deploy mode and state backend settings |
| `WindowConfig` | `models.py` | Window properties model |
| `HtmlContent` | `models.py` | Content with files/scripts |

### State Classes (Deploy Mode)

| Class | File | Purpose |
|-------|------|---------|
| `WidgetStore` | `state/memory.py`, `state/redis.py` | Widget metadata persistence |
| `EventBus` | `state/memory.py`, `state/redis.py` | Cross-worker event routing |
| `ConnectionRouter` | `state/memory.py`, `state/redis.py` | WebSocket connection tracking |
| `SessionStore` | `state/memory.py`, `state/redis.py` | User session management |
| `WidgetData` | `state/types.py` | Widget metadata model |
| `EventMessage` | `state/types.py` | Event payload model |
| `ConnectionInfo` | `state/types.py` | Connection metadata model |
| `UserSession` | `state/types.py` | Session data model |

### Enums

| Enum | File | Values |
|------|------|--------|
| `ThemeMode` | `models.py` | `LIGHT`, `DARK`, `SYSTEM` |
| `WindowMode` | `models.py` | `NEW_WINDOW`, `SINGLE_WINDOW`, `MULTI_WINDOW`, `NOTEBOOK`, `BROWSER` |
| `NotebookEnvironment` | `notebook.py` | `NONE`, `COLAB`, `KAGGLE`, `AZURE`, `VSCODE`, `JUPYTERLAB`, etc. |
| `StateBackend` | `state/types.py` | `MEMORY`, `REDIS` |

---

## Design Patterns

### Singleton Pattern

Used for global state managers:

```python
class CallbackRegistry:
    _instance: CallbackRegistry | None = None

    @classmethod
    def get_instance(cls) -> "CallbackRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

**Singletons:** `CallbackRegistry`, `_ServerState` (inline.py)

### Strategy Pattern

Window modes implement `WindowModeBase` interface:

```python
class WindowModeBase(ABC):
    @abstractmethod
    def show(self, content, config, callbacks) -> str: ...
```

### Mixin Pattern

State management via composable mixins:

```python
class PyWry(GridStateMixin, PlotlyStateMixin, ToolbarStateMixin):
    def emit(self, event_type, data, label=None): ...

class PyWryAgGridWidget(GridStateMixin, ToolbarStateMixin, PyWryWidget):
    def emit(self, event_type, data): ...
```

### Pydantic Models

All configuration uses Pydantic v2:

```python
from pydantic import BaseModel, Field

class WindowConfig(BaseModel):
    title: str = "PyWry"
    width: int = Field(default=1280, ge=200)
    height: int = Field(default=720, ge=150)
```

---

## ID Hierarchy

PyWry uses hierarchical IDs for event routing:

| ID Level | Scope | Format Example |
|----------|-------|----------------|
| `label` | Window/Widget | `"pywry-abc123"` |
| `chartId` | Plotly chart | `"chart_def456"` |
| `gridId` | AgGrid | `"grid_ghi789"` |
| `componentId` | Toolbar item | `"button-xyz123"` |

Events include `widget_type` for identification:
- Plotly events: `widget_type: "chart"`
- Grid events: `widget_type: "grid"`

---

## CSS Theming

PyWry provides 60+ CSS variables for comprehensive customization, plus component ID targeting for precise styling.

### Theme Classes

| Selector | Description |
|----------|-------------|
| `html.dark` / `html.light` | Document root theme (native windows) |
| `.pywry-theme-dark` / `.pywry-theme-light` | Widget container theme (notebooks) |
| `html.pywry-native` | Added to `<html>` in native window mode |

### Dynamic Styling via Events

```python
# Update element styles from Python
app.emit("pywry:set-style", {"id": "my-btn", "styles": {"backgroundColor": "green"}}, label)

# Inject CSS dynamically
app.emit("pywry:inject-css", {"css": "#title { color: blue; }", "id": "custom-styles"}, label)

# Remove injected CSS
app.emit("pywry:remove-css", {"id": "custom-styles"}, label)
```

### Component ID Targeting

Every toolbar component has a `component_id` (default: `{type}-{8-char-random}`):

```python
Button(label="Save", event="app:save", component_id="save-btn")  # Custom ID
```

Target in CSS: `#save-btn { background: green; }` or `[data-event="app:save"] { ... }`

### Key CSS Variables

```css
:root {
  --pywry-bg-primary: #212124;
  --pywry-bg-secondary: rgba(21, 21, 24, 1);
  --pywry-bg-tertiary: rgba(31, 30, 35, 1);
  --pywry-text-primary: #ebebed;
  --pywry-text-secondary: #a0a0a0;
  --pywry-accent: #0078d4;
  --pywry-border-color: #333;
  --pywry-radius: 4px;
}
```

### Layout Classes

| Class | Purpose |
|-------|---------|
| `.pywry-widget` | Root widget container |
| `.pywry-content` | Content flex container |
| `.pywry-toolbar` | Toolbar container |
| `.pywry-plotly` | Plotly container |
| `.pywry-grid` | AgGrid container |

### Toast Notification Classes

| Class | Purpose |
|-------|---------|
| `.pywry-toast-container` | Toast stack container (positioned absolutely) |
| `.pywry-toast-container--top-right` | Top-right position (default) |
| `.pywry-toast-container--blocking` | Elevated z-index for confirm |
| `.pywry-toast` | Base toast styling |
| `.pywry-toast--info/success/warning/error/confirm` | Type variants |
| `.pywry-toast__icon` | Toast icon |
| `.pywry-toast__title` | Toast title |
| `.pywry-toast__message` | Toast message |
| `.pywry-toast__close` | Close button |
| `.pywry-toast__buttons` | Confirm dialog buttons |
| `.pywry-toast__btn--cancel/--confirm` | Button variants |
| `.pywry-toast-overlay` | Blocking overlay for confirm |
| `.pywry-toast-overlay--visible` | Visible overlay state |

**Toast CSS Variables:**

```css
.pywry-toast {
  --pywry-toast-bg: rgba(30, 30, 30, 0.95);
  --pywry-toast-color: #ffffff;
  --pywry-toast-accent: #0ea5e9;  /* Left border color */
}
```

---

## Development

### Setup

```bash
git clone https://github.com/OpenBB-finance/OpenBB.git
cd pywry
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

### Testing

```bash
pytest tests/ -v
pytest tests/ --cov=pywry --cov-report=html
```

### Linting

```bash
ruff check pywry/ tests/
ruff format pywry/ tests/
mypy pywry/
```

### Environment Variables for Testing

```bash
PYWRY_HEADLESS=1  # Force InlineWidget, skip browser.open()
PYWRY_LOG__LEVEL=DEBUG  # Enable debug logging
```

---

## Quick Examples

### REPL vs Script Usage

**In a REPL (IPython, Jupyter, Python shell):** Windows stay open because the Python process keeps running. You can interact with handles directly.

```python
# IPython / Python REPL
>>> from pywry import PyWry
>>> app = PyWry()
>>> handle = app.show("<h1>Hello</h1>")  # Window opens, stays open
>>> handle.set_title("Updated Title")    # Interact with window
>>> handle.emit("app:update", {"x": 1})  # Send events
>>> handle.close()                        # Close when done
```

**In a script:** The script exits immediately after `show()`, closing the window. Use `app.block()` to keep it open:

```python
# my_script.py
from pywry import PyWry

app = PyWry()
handle = app.show("<h1>Hello</h1>")

# Without this, the script exits and window closes immediately
app.block()  # Blocks until user closes the window
```

**With callbacks (scripts):** Use `block()` after setting up handlers:

```python
# interactive_script.py
from pywry import PyWry, Toolbar, Button

app = PyWry()

def on_click(data, event_type, label):
    print(f"Button clicked: {data}")
    app.close(label)  # Close window to unblock

handle = app.show(
    "<h1>Click the button</h1>",
    toolbars=[Toolbar(position="top", items=[Button(label="Click Me", event="app:click")])],
    callbacks={"app:click": on_click}
)

app.block()  # Wait for window to close
print("Window closed, script continues...")
```

### Basic Window

```python
from pywry import PyWry, WindowMode, ThemeMode

app = PyWry(mode=WindowMode.SINGLE_WINDOW, theme=ThemeMode.DARK)
app.show("<h1>Hello World</h1>")
```

### Plotly Chart with Events

```python
from pywry import PyWry
import plotly.express as px

app = PyWry()
widget = None

def on_click(data, event_type, label):
    """Update chart title to show clicked point coordinates."""
    point = data["points"][0]
    widget.emit("plotly:update-layout", {
        "layout": {"title": f"Clicked: ({point['x']}, {point['y']})"}
    })

fig = px.scatter(x=[1, 2, 3], y=[4, 5, 6])
widget = app.show_plotly(fig, title="Click a point", callbacks={"plotly:click": on_click})
```

### DataFrame with Toolbar

```python
import pandas as pd
from pywry import PyWry, Toolbar, Button

app = PyWry()
df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
widget = None

def on_export(data, event_type, label):
    """Download the DataFrame as CSV."""
    widget.emit("pywry:download", {
        "content": df.to_csv(index=False),
        "filename": "data.csv",
        "mimeType": "text/csv"
    })

toolbar = Toolbar(position="top", items=[Button(label="Export", event="app:export")])
widget = app.show_dataframe(df, toolbars=[toolbar], callbacks={"app:export": on_export})
```

### Browser Mode (Server)

```python
from pywry import PyWry, WindowMode
from pywry.inline import block

app = PyWry(mode=WindowMode.BROWSER)
widget = app.show_plotly(fig)
print(f"Open: {widget.url}")
block()  # Keep server running
```

---

## CLI Commands

```bash
# Show current configuration
pywry config --show

# Export as TOML
pywry config --toml

# Initialize pywry.toml
pywry init
```

---

## Debugging

```python
# Enable debug logging
import pywry.log
pywry.log.enable_debug()

# Or via environment
# PYWRY_LOG__LEVEL=DEBUG
```
