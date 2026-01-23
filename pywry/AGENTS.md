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
- **Toolbar System**: Pydantic-based toolbar components with bidirectional state management
- **Hot Reload**: CSS injection and JS refresh with scroll preservation
- **Bundled Libraries**: Plotly.js 3.3.1 and AgGrid 35.0.0 (offline capable)
- **Native File Dialogs**: Tauri-powered save/open dialogs and filesystem access
- **Configuration System**: TOML files, pyproject.toml, and environment variables
- **Dynamic Theming**: Light, Dark, and System modes
- **Event System**: Bidirectional Python ↔ JavaScript communication
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
| Desktop (script/terminal) | Native Window | `pywry.app.PyWry` | `str` (window label) |
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
    Toolbar, Button, Select, MultiSelect, TextInput, NumberInput,
    DateInput, SliderInput, RangeInput, Toggle, Checkbox, RadioGroup,
    TabGroup, Div, Option, ToolbarItem
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

# Settings
from pywry import PyWrySettings, SecuritySettings, WindowSettings, ThemeSettings, ServerSettings, HotReloadSettings, TimeoutSettings, AssetSettings, LogSettings

# Asset loading
from pywry import AssetLoader, get_asset_loader

# Callback registry
from pywry import CallbackFunc, WidgetType, get_registry

# Runtime (alternative for sending events in native mode)
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

# Deploy settings (for programmatic configuration)
from pywry.config import DeploySettings
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
# Show HTML content
widget = app.show(
    content,                    # str or HtmlContent
    title=None,
    callbacks=None,             # Dict of event handlers {"event:name": handler}
    include_plotly=False,
    include_aggrid=False,
    toolbars=None,              # List of Toolbar objects
)

# Show Plotly figure
widget = app.show_plotly(
    figure,                     # Plotly Figure or dict
    title=None,
    callbacks=None,
    toolbars=None,
)

# Show DataFrame as AgGrid
widget = app.show_dataframe(
    data,                       # pandas DataFrame or dict
    title=None,
    callbacks=None,
    column_defs=None,           # List of ColDef objects
    aggrid_theme="alpine",
    grid_options=None,
    toolbars=None,
)
```

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
# All modes return a widget with emit() method
widget = app.show("<h1>Hello</h1>")
widget.emit("app:response", {"key": "value"})
```

> **Low-level alternative:** `runtime.emit_event(widget.label, ...)` for direct access in native windows.

### Other Methods

| Method | Description |
|--------|-------------|
| `eval_js(script, label=None)` | Execute JavaScript in window(s) |
| `update_content(html, label=None)` | Update window HTML content |
| `close(label=None)` | Close specific or all windows |
| `destroy()` | Close all windows and cleanup |
| `enable_hot_reload()` | Enable hot reload |
| `disable_hot_reload()` | Disable hot reload |
| `refresh_css(label=None)` | Hot-reload CSS without page refresh |

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
| `toolbar:*` | Toolbar state events |

### Pre-Registered Events

**Plotly Events (JS → Python):**

| Event | Trigger | Key Payload Fields |
|-------|---------|-------------------|
| `plotly:click` | User clicks a data point | `chartId`, `points`, `widget_type: "chart"` |
| `plotly:hover` | User hovers over a point | `chartId`, `points` |
| `plotly:selected` | User selects with box/lasso | `chartId`, `points`, `range` |
| `plotly:relayout` | User zooms, pans, or resizes | `chartId`, `relayout_data` |

**AgGrid Events (JS → Python):**

| Event | Trigger | Key Payload Fields |
|-------|---------|-------------------|
| `grid:row-selected` | Row selection changes | `gridId`, `rows`, `widget_type: "grid"` |
| `grid:cell-click` | User clicks a cell | `gridId`, `rowIndex`, `colId`, `value`, `data` |
| `grid:cell-edit` | User edits a cell | `gridId`, `rowIndex`, `rowId`, `colId`, `oldValue`, `newValue`, `data` |
| `grid:filter-changed` | Filter applied | `gridId`, `filterModel` |

**System Events:**

| Event | Direction | Description |
|-------|-----------|-------------|
| `pywry:ready` | JS → Python | Window/widget initialized |
| `pywry:update-theme` | Python → JS | Update theme dynamically |
| `pywry:inject-css` | Python → JS | Inject CSS dynamically |
| `pywry:set-style` | Python → JS | Update element styles |
| `pywry:set-content` | Python → JS | Update element innerHTML/textContent |
| `pywry:download` | Python → JS | Trigger file download |
| `pywry:alert` | Python → JS | Show toast notification |

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

---

## Toolbar System

### Components

| Component | Emits |
|-----------|-------|
| `Button` | `{ componentId, ...data }` |
| `Select` | `{ value: str, componentId }` |
| `MultiSelect` | `{ values: [str, ...], componentId }` |
| `TextInput` | `{ value: str, componentId }` |
| `NumberInput` | `{ value: number, componentId }` |
| `DateInput` | `{ value: "YYYY-MM-DD", componentId }` |
| `SliderInput` | `{ value: number, componentId }` |
| `RangeInput` | `{ start: number, end: number, componentId }` |
| `Toggle` | `{ value: bool, componentId }` |
| `Checkbox` | `{ value: bool, componentId }` |
| `RadioGroup` | `{ value: str, componentId }` |
| `TabGroup` | `{ value: str, componentId }` |
| `Div` | Container (no events) |

### Toolbar Positions

| Position | Description |
|----------|-------------|
| `"header"` | Full-width bar at very top |
| `"footer"` | Full-width bar at very bottom |
| `"left"` | Vertical bar on left |
| `"right"` | Vertical bar on right |
| `"top"` | Horizontal bar above content |
| `"bottom"` | Horizontal bar below content |
| `"inside"` | Floating overlay in content |

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

### Theme Classes

| Selector | Description |
|----------|-------------|
| `html.dark` / `html.light` | Document root theme |
| `.pywry-theme-dark` / `.pywry-theme-light` | Widget container theme |

### Key CSS Variables

```css
:root {
  --pywry-bg-primary: #212124;
  --pywry-bg-secondary: #1e1e1e;
  --pywry-text-primary: #ebebed;
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
