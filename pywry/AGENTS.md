# AGENTS.md - PyWry Library Guide for AI Coding Agents

> **Purpose**: This document provides AI coding agents with comprehensive context to understand, develop with, and contribute to the PyWry library.

## Quick Reference

| Aspect | Details |
|--------|---------|
| **Language** | Python 3.10+ |
| **Type System** | Strict typing with Pydantic v2 models |
| **Style** | Ruff (line length 100), NumPy docstrings |
| **Testing** | pytest with fixtures, `PYWRY_HEADLESS=1` for CI |
| **Architecture** | Subprocess IPC (desktop) + FastAPI inline server (notebooks) |

---

## Project Overview

**PyWry** is a lightweight 100% Python library for creating native desktop windows with bidirectional Python ↔ JavaScript communication. It uses the OS webview (via PyTauri/Tauri) instead of bundling a browser engine, resulting in binaries under 3MB. It also supports inline rendering in Jupyter notebooks via FastAPI IFrame or anywidget integration.

### Core Capabilities

- **Three Window Modes**: `NEW_WINDOW`, `SINGLE_WINDOW`, `MULTI_WINDOW` (plus automatic `NOTEBOOK` mode)
- **Notebook Support**: Automatic inline rendering via FastAPI IFrame or anywidget
- **Hot Reload**: CSS injection and JS refresh with scroll preservation
- **Bundled Libraries**: Plotly.js 3.3.1 and AG Grid 35.0.0 (offline capable)
- **Native Tauri Plugins**: Dialog (file save/open) and Filesystem APIs via `window.__TAURI__`
- **Event System**: Bidirectional Python ↔ JavaScript with namespace patterns
- **Dynamic Theming**: Light, Dark, and System modes
- **CLI Tools**: `pywry config` and `pywry init`
- **anywidget Integration**: `PyWryWidget`, `PyWryPlotlyWidget`, `PyWryAgGridWidget`

---

## Architecture

### Dual Rendering Modes

PyWry supports two primary rendering architectures:

**1. Desktop Mode** (PyTauri subprocess):
```
User Code → PyWry (app.py) → Runtime (runtime.py) → PyTauri Subprocess → OS Webview
                                    ↑                        ↓
                            JSON IPC (stdin/stdout)     JavaScript Bridge
                                    ↓                        ↑
                            Callbacks (callbacks.py) ← Events from JS
```

**2. Notebook Mode** (FastAPI inline server):
```
User Code → inline.py → FastAPI Server → IFrame in Notebook
                 ↑              ↓
         WebSocket/HTTP    HTML/JS/CSS
                 ↓              ↑
         Callbacks ← Events via HTTP POST + Polling
```

**3. anywidget Mode** (Jupyter widget protocol):
```
User Code → widget.py → anywidget ESM → Jupyter Widget
                 ↑              ↓
         traitlets sync    Bundled Plotly/AG Grid
```

### Key Architectural Points

- **Desktop**: Python manages the high-level API through the `PyWry` class; a PyTauri subprocess handles actual window creation and OS webview; communication uses JSON IPC over stdin/stdout; subprocess starts lazily on first `show()` call
- **Notebook**: Detected automatically via `notebook.py`; FastAPI server starts on first render; IFrame displays content; bidirectional events via HTTP POST + polling
- **anywidget**: Uses anywidget/traitlets for Jupyter widget protocol; bundles Plotly.js and AG Grid as ESM modules

### Tauri Plugin Integration

PyWry registers Tauri plugins in `__main__.py` to expose native OS capabilities to JavaScript:

```python
from pytauri_plugins import dialog as dialog_plugin
from pytauri_plugins import fs as fs_plugin

# In builder.build():
plugins=[dialog_plugin.init(), fs_plugin.init()]
```

**Registered Plugins:**

| Plugin | Capability Permission | JavaScript API |
|--------|----------------------|----------------|
| `dialog` | `dialog:default` | `window.__TAURI__.dialog` |
| `fs` | `fs:default` | `window.__TAURI__.fs` |

**Capabilities file** (`capabilities/default.toml`) must include permissions:
```toml
permissions = [
  "core:default",
  "dialog:default",
  "fs:default"
]
```

**Usage in JavaScript** (e.g., AG Grid export):
```javascript
if (window.__TAURI__) {
    const filePath = await window.__TAURI__.dialog.save({
        defaultPath: 'export.csv',
        filters: [{ name: 'CSV', extensions: ['csv'] }]
    });
    if (filePath) {
        await window.__TAURI__.fs.writeTextFile(filePath, csvContent);
    }
}
```

---

## Directory Structure

```
pywry/
├── __init__.py          # Public API exports
├── __main__.py          # PyTauri subprocess entry point
├── app.py               # Main PyWry class - user entry point
├── runtime.py           # PyTauri subprocess management (stdin/stdout IPC)
├── inline.py            # FastAPI-based inline notebook rendering
├── notebook.py          # Notebook environment detection
├── widget.py            # anywidget-based widgets (PyWryWidget, PyWryPlotlyWidget, etc.)
├── widget_protocol.py   # BaseWidget protocol definition
├── config.py            # Layered configuration system (pydantic-settings)
├── models.py            # Pydantic models (WindowConfig, HtmlContent, ThemeMode, WindowMode)
├── templates.py         # HTML template builder with CSP, themes, scripts, toolbar
├── scripts.py           # JavaScript bridge code injected into windows
├── callbacks.py         # Event callback registry (singleton)
├── assets.py            # Bundled asset loading (Plotly.js, AG Grid, CSS)
├── asset_loader.py      # CSS/JS file loading with caching
├── hot_reload.py        # Hot reload manager
├── watcher.py           # File system watcher (watchdog-based)
├── log.py               # Logging utilities
├── cli.py               # CLI commands
├── Tauri.toml           # Tauri configuration
├── capabilities/        # Tauri capability permissions
│   └── default.toml
├── commands/            # IPC command handlers
│   ├── __init__.py
│   └── window_commands.py
├── frontend/            # Frontend HTML and bundled assets
│   ├── assets/          # Plotly.js, AG Grid, icons, widget JS
│   ├── src/             # Main JS files (main.js, aggrid-defaults.js, plotly-widget.js)
│   └── style/           # CSS files
│       └── pywry.css    # Core PyWry CSS with variables, toolbar, layout classes
├── utils/               # Utility helpers
│   ├── __init__.py
│   └── async_helpers.py
└── window_manager/      # Window mode implementations
    ├── __init__.py
    ├── controller.py        # WindowController
    ├── lifecycle.py         # WindowLifecycle with resource tracking
    └── modes/
        ├── __init__.py
        ├── base.py          # Abstract WindowModeBase interface
        ├── single_window.py # SINGLE_WINDOW mode
        ├── new_window.py    # NEW_WINDOW mode
        └── multi_window.py  # MULTI_WINDOW mode
```

---

## Key Classes and Their Responsibilities

### Core Classes

| Class | File | Responsibility |
|-------|------|----------------|
| `PyWry` | `app.py` | Main user-facing API; manages window modes, settings, hot reload |
| `CallbackRegistry` | `callbacks.py` | Singleton managing event callbacks with namespace support |
| `HotReloadManager` | `hot_reload.py` | Coordinates file watching and CSS injection |
| `FileWatcher` | `watcher.py` | Watchdog-based file monitoring with debouncing |

### Rendering Mode Classes

| Class | File | Responsibility |
|-------|------|----------------|
| `_ServerState` | `inline.py` | Global state for FastAPI inline server |
| `PyWryWidget` | `widget.py` | Base anywidget for notebook rendering |
| `PyWryPlotlyWidget` | `widget.py` | Plotly-specific anywidget with bundled Plotly.js |
| `PyWryAgGridWidget` | `widget.py` | AG Grid anywidget with bundled AG Grid |

### Window Management

| Class | File | Responsibility |
|-------|------|----------------|
| `WindowModeBase` | `window_manager/modes/base.py` | Abstract interface for window modes |
| `SingleWindowMode` | `window_manager/modes/single_window.py` | Reuses one window, replaces content |
| `NewWindowMode` | `window_manager/modes/new_window.py` | Creates new window for each `show()` |
| `MultiWindowMode` | `window_manager/modes/multi_window.py` | Multiple independent labeled windows |
| `WindowLifecycle` | `window_manager/lifecycle.py` | Window lifecycle with resource tracking |
| `WindowController` | `window_manager/controller.py` | Window controller for mode switching |

### Configuration Classes

| Class | File | Purpose |
|-------|------|---------|
| `PyWrySettings` | `config.py` | Root settings composing all subsettings |
| `SecuritySettings` | `config.py` | CSP with factory methods (permissive, strict, localhost) |
| `ThemeSettings` | `config.py` | External CSS file for custom styling |
| `ServerSettings` | `config.py` | Inline FastAPI/uvicorn server settings |
| `WindowSettings` | `config.py` | Default window properties |
| `TimeoutSettings` | `config.py` | Timeout values |
| `HotReloadSettings` | `config.py` | Hot reload behavior |
| `AssetSettings` | `config.py` | Library versions |
| `LogSettings` | `config.py` | Logging configuration |
| `WindowConfig` | `models.py` | Pydantic model for window properties |
| `HtmlContent` | `models.py` | Pydantic model for content with files and scripts |

### Enums

| Enum | File | Values |
|------|------|--------|
| `ThemeMode` | `models.py` | `LIGHT`, `DARK`, `SYSTEM` |
| `WindowMode` | `models.py` | `NEW_WINDOW`, `SINGLE_WINDOW`, `MULTI_WINDOW`, `NOTEBOOK` |
| `NotebookEnvironment` | `notebook.py` | `NONE`, `COLAB`, `KAGGLE`, `AZURE`, `VSCODE`, `NTERACT`, `COCALC`, `DATABRICKS`, `JUPYTERLAB`, `JUPYTER_NOTEBOOK`, `IPYTHON_TERMINAL`, `REMOTE_JUPYTER` |

---

## Design Patterns

### 1. Singleton Pattern

Used for managers that need global state. Always use `_instance` class variable:

```python
class CallbackRegistry:
    _instance: CallbackRegistry | None = None
    _initialized: bool = False

    def __new__(cls) -> CallbackRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._callbacks: dict[str, dict[str, list[CallbackFunc]]] = {}
```

**Singletons in codebase:**
- `CallbackRegistry` (callbacks.py)
- `_ServerState` (inline.py) - module-level singleton

### 2. Strategy Pattern

Window modes implement the abstract `WindowModeBase` interface:

```python
from abc import ABC, abstractmethod

class WindowModeBase(ABC):
    @abstractmethod
    def show(
        self,
        config: WindowConfig,
        html: str,
        callbacks: dict[str, Any] | None = None,
        label: str | None = None,
    ) -> str:
        """Show content and return window label."""
        ...

    @abstractmethod
    def close(self, label: str) -> bool:
        """Close window."""
        ...

    @abstractmethod
    def is_open(self, label: str) -> bool:
        """Check if window is open."""
        ...

    @abstractmethod
    def update_content(self, label: str, html: str, theme: str = "dark") -> bool:
        """Update window content."""
        ...
```

### 3. Pydantic Models

All configuration and data models use Pydantic v2:

```python
from pydantic import BaseModel, Field, field_validator

class WindowConfig(BaseModel):
    title: str = "PyWry"
    width: int = Field(default=1280, ge=200)
    height: int = Field(default=720, ge=150)
    theme: ThemeMode = ThemeMode.DARK
    enable_plotly: bool = False
    enable_aggrid: bool = False
    plotly_theme: Literal["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white"] = "plotly_dark"
    aggrid_theme: Literal["quartz", "alpine", "balham", "material"] = "alpine"
```

### 4. Layered Configuration

Configuration sources (lowest to highest priority):
1. Built-in defaults (in code)
2. `pyproject.toml` `[tool.pywry]` section
3. `pywry.toml` file
4. User config file
5. Environment variables (`PYWRY_*`)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class PyWrySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PYWRY_",
        env_nested_delimiter="__",
    )
```

---

## Event System

### Namespace Pattern

Events follow the format `namespace:event_name`:

```python
# Register callback
pywry.on("plotly:click", handle_plotly_click)
pywry.on("grid:select", handle_grid_select)
pywry.on("custom:my_event", handle_custom)

# Wildcard for all events in namespace
pywry.on("plotly:*", handle_all_plotly_events)
```

### Event Validation

Regex pattern in `models.py`: `^[a-zA-Z][a-zA-Z0-9]*:[a-zA-Z][a-zA-Z0-9_-]*$`

**Reserved namespaces:**
- `pywry` - System events
- `plotly` - Plotly.js events
- `grid` - AG Grid events

### JavaScript Bridge

From JavaScript, emit events to Python:

```javascript
// In browser context
window.pywry.emit("custom:button_click", { buttonId: "submit" });

// Listen for Python events
window.pywry.on("python:update", (data) => {
    console.log("Received from Python:", data);
});
```

---

## Usage Examples

### Basic Window

```python
from pywry import PyWry, WindowMode, ThemeMode

pywry = PyWry(
    mode=WindowMode.SINGLE_WINDOW,
    theme=ThemeMode.DARK,
    title="My App",
    width=1280,
    height=720,
)

pywry.show("<h1>Hello World</h1>")
```

### With Plotly Chart

```python
from pywry import PyWry

pywry = PyWry()

fig = {"data": [{"x": [1, 2, 3], "y": [4, 5, 6], "type": "scatter"}]}
pywry.show_plotly(fig, title="My Chart")
```

### With DataFrame (AG Grid)

```python
import pandas as pd
from pywry import PyWry

pywry = PyWry()
df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
pywry.show_dataframe(df, title="My Table")
```

### With Event Callbacks

```python
import logging
from pywry import PyWry

logging.basicConfig(level=logging.INFO)
pywry = PyWry()

def handle_click(data, event_type, label):
    logging.info(f"Clicked: {data}")

pywry.on("plotly:click", handle_click)
pywry.show_plotly(fig)
```

### With Toolbar Buttons

```python
pywry = PyWry()

def on_action(data, event_type, label):
    pywry.eval_js("alert('Button clicked!')")

pywry.on("app:action", on_action)

buttons = [{"label": "Click Me", "event": "app:action"}]
pywry.show("<h1>Content</h1>", buttons=buttons, toolbar_position="top")
```

### Inline Notebook Usage

```python
# Direct functions (auto-detect notebook environment)
from pywry import show_plotly, show_dataframe

fig = {"data": [{"x": [1, 2, 3], "y": [4, 5, 6]}]}
show_plotly(fig)  # Renders inline in Jupyter

df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
show_dataframe(df)  # Renders AG Grid inline
```

### anywidget Usage

The anywidget classes (`PyWryWidget`, `PyWryPlotlyWidget`, `PyWryAgGridWidget`) are low-level widgets that accept raw HTML content. For easier usage, prefer the high-level `show_plotly()` and `show_dataframe()` functions:

```python
from pywry.inline import show_plotly, show_dataframe
import plotly.graph_objects as go
import pandas as pd

# Plotly - high-level API (recommended)
fig = go.Figure(data=go.Scatter(x=[1, 2, 3], y=[4, 5, 6]))
widget = show_plotly(fig, theme="dark", height=500)
widget  # Displays in notebook

# DataFrame - high-level API (recommended)
df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
grid = show_dataframe(df, theme="dark", aggrid_theme="alpine")
grid  # Displays in notebook
```

For direct widget usage (advanced):

```python
from pywry import PyWryPlotlyWidget

# Low-level: you must provide the HTML content yourself
widget = PyWryPlotlyWidget(
    content="<div id='chart'></div><script>...</script>",
    theme="dark",
    width="100%",
    height="500px",
)
display(widget)
```

### Multi-Window Mode

```python
from pywry import PyWry, WindowMode

pywry = PyWry(mode=WindowMode.MULTI_WINDOW)

# Show multiple independent windows
pywry.show("<h1>Window 1</h1>", label="win1")
pywry.show("<h1>Window 2</h1>", label="win2")

# Update specific window
pywry.update_content("<h1>Updated Window 1</h1>", label="win1")
```

### Hot Reload Development

```python
from pywry import PyWry

pywry = PyWry(hot_reload=True)

pywry.show(
    '<div class="container">Content</div>',
    css_files=["styles.css"],  # Changes to this file auto-reload
)
```

---

## Coding Conventions

### Style Rules (from ruff.toml)

- **Line length**: 100 characters
- **Python target**: 3.10+
- **Import sorting**: isort-compatible (I rules)
- **Docstrings**: NumPy style (D rules)

### Docstring Format

```python
def create_window(
    self,
    content: HtmlContent,
    config: WindowConfig | None = None,
) -> str:
    """Create a new window with the given content.

    Parameters
    ----------
    content : HtmlContent
        The HTML content to display in the window.
    config : WindowConfig | None, optional
        Window configuration. Uses defaults if None.

    Returns
    -------
    str
        The unique window ID.

    Raises
    ------
    RuntimeError
        If the PyTauri subprocess is not running.

    Examples
    --------
    >>> app = PyWry()
    >>> window_id = app.create_window(HtmlContent(html="<h1>Hi</h1>"))
    """
```

### Type Hints

Always use modern type hints (Python 3.10+ syntax):

```python
# Good
def process(items: list[str], config: dict[str, Any] | None = None) -> bool:
    ...

# Avoid (old style)
def process(items: List[str], config: Optional[Dict[str, Any]] = None) -> bool:
    ...
```

### TYPE_CHECKING Guards

Use for imports only needed for type hints:

```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from plotly.graph_objects import Figure

class MyClass:
    def __init__(self, callback: Callable[[dict], None]) -> None:
        self._callback = callback
```

### Mypy Disable Comments

For modules with untyped dependencies (anywidget, traitlets), use module-level disables:

```python
# mypy: disable-error-code="import-untyped,no-untyped-call,no-untyped-def,arg-type,type-arg"
```

### Error Handling

For non-fatal errors, prefer logging over raising exceptions:

```python
import logging

logger = logging.getLogger(__name__)

def load_optional_asset(path: Path) -> str | None:
    """Load asset, returning None and logging warning on failure."""
    try:
        return path.read_text()
    except OSError:
        logger.warning("Failed to load asset: %s", path)
        return None
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `WindowConfig` |
| Functions/Methods | snake_case | `create_window` |
| Constants | UPPER_SNAKE | `DEFAULT_WIDTH` |
| Private | Leading underscore | `_internal_method` |
| Type aliases | PascalCase | `EventCallback = Callable[[dict], None]` |

---

## Testing

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=pywry --cov-report=html

# Specific test file
pytest tests/test_models.py -v

# Headless mode (no visible windows)
PYWRY_HEADLESS=1 pytest tests/
```

### Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── test_assets.py        # Bundled asset tests
├── test_asset_loader.py  # Asset loader tests
├── test_cli.py           # CLI tests
├── test_config.py        # Configuration tests
├── test_csp.py           # CSP tests
├── test_e2e.py           # End-to-end window tests
├── test_inline_e2e.py    # Inline/FastAPI server tests
├── test_integration.py   # Integration tests
├── test_models.py        # Model validation tests
├── test_scripts.py       # JavaScript bridge tests
├── test_server_config.py # Server configuration tests
├── test_tauri_plugins.py # Tauri plugin integration tests (dialog, fs)
├── test_templates.py     # HTML template tests
└── test_window_modes.py  # Window mode tests
```

### Key Fixtures (conftest.py)

```python
import pytest
from pywry import HtmlContent, WindowConfig, PyWrySettings

@pytest.fixture
def sample_content() -> HtmlContent:
    return HtmlContent(html="<h1>Test</h1>")

@pytest.fixture
def sample_config() -> WindowConfig:
    return WindowConfig(title="Test Window", width=800, height=600)

@pytest.fixture
def default_settings() -> PyWrySettings:
    return PyWrySettings()
```

### Writing Tests

```python
import pytest
from pywry.models import WindowConfig

class TestWindowConfig:
    """Tests for WindowConfig model."""

    def test_default_values(self) -> None:
        """Test that defaults are applied correctly."""
        config = WindowConfig()
        assert config.width == 1280
        assert config.height == 720

    def test_validation_rejects_small_width(self) -> None:
        """Test that width below minimum raises validation error."""
        with pytest.raises(ValueError, match="greater than"):
            WindowConfig(width=100)

    @pytest.mark.parametrize("width,height", [
        (200, 150),
        (1920, 1080),
        (4096, 2160),
    ])
    def test_valid_dimensions(self, width: int, height: int) -> None:
        """Test various valid dimension combinations."""
        config = WindowConfig(width=width, height=height)
        assert config.width == width
        assert config.height == height
```

---

## CI/CD

### GitHub Actions Workflows

**test_pywry.yml** - Runs on push/PR:
- **Lint job**: Ruff check, Ruff format, Mypy
- **Test job**: Matrix across OS × Python versions
  - Ubuntu, Windows, macOS
  - Python 3.10, 3.11, 3.12, 3.13, 3.14
- Linux uses Xvfb for headless display

**publish_pywry.yml** - Release publishing:
- Builds sdist and wheels for all platforms
- Includes ARM builds (ubuntu-24.04-arm, windows-11-arm, macos-latest)
- Publishes to PyPI

### CI Environment Variables

```yaml
env:
  PYWRY_HEADLESS: "1"  # Hide windows during tests
```

### Linux CI Setup

```yaml
- name: Install X11 dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y xvfb libwebkit2gtk-4.1-dev

- name: Run tests
  run: xvfb-run pytest tests/ -v
```

---

## Common Tasks

### Adding a New Window Mode

1. Create `pywry/window_manager/modes/my_mode.py`:

```python
from pywry.window_manager.modes.base import WindowModeBase
from pywry.models import WindowConfig

class MyCustomMode(WindowModeBase):
    def show(
        self,
        config: WindowConfig,
        html: str,
        callbacks: dict | None = None,
        label: str | None = None,
    ) -> str:
        # Implementation
        ...

    def close(self, label: str) -> bool:
        # Implementation
        ...

    def is_open(self, label: str) -> bool:
        # Implementation
        ...

    def update_content(self, label: str, html: str, theme: str = "dark") -> bool:
        # Implementation
        ...
```

2. Register in `pywry/window_manager/modes/__init__.py`
3. Add to `WindowMode` enum in `pywry/models.py`
4. Write tests in `tests/test_window_modes.py`

### Adding a New Configuration Option

1. Add to appropriate settings class in `config.py`:

```python
class WindowSettings(BaseModel):
    existing_option: str = "default"
    new_option: bool = Field(default=False, description="My new option")
```

2. Update `PyWrySettings` if needed
3. Document in README.md
4. Add tests in `tests/test_config.py`

### Adding a New Event Namespace

1. Document the namespace in this file
2. Add JavaScript bridge code in `scripts.py` if needed
3. Update CSP in `config.py` if external resources needed
4. Add tests for event handling

---

## Debugging Tips

### Enable Verbose Logging

```python
import pywry.log
pywry.log.enable_debug()
```

### Environment Variable

```bash
export PYWRY_DEBUG=1
export PYWRY_LOG__LEVEL=DEBUG
```

### Check Subprocess Status

```python
# For terminal/script debugging
from pywry.runtime import is_running, wait_ready

status = is_running()
wait_ready(timeout=5.0)
```

### Validate HTML Output

```python
# For terminal/script debugging - inspect generated HTML
from pywry.templates import build_html
from pywry.models import HtmlContent
from pywry.config import PyWrySettings

html = build_html(
    HtmlContent(html="<h1>Test</h1>"),
    PyWrySettings(),
)
# html contains the full generated HTML string
```

---

## Theme System

### Theme Coordination Rule

Window theme ALWAYS controls AG Grid class and Plotly template. The framework auto-fixes mismatches.

```python
from pywry import PyWry, ThemeMode

app = PyWry()
app.settings.theme.mode = ThemeMode.DARK  # All components follow
```

### Theme Modes

| Mode | Behavior |
|------|----------|
| `ThemeMode.LIGHT` | Light theme for all components |
| `ThemeMode.DARK` | Dark theme for all components |
| `ThemeMode.SYSTEM` | Follows OS preference |

---

## Content Security Policy

### Factory Methods

```python
from pywry.config import SecuritySettings

# Development - allows everything
csp = SecuritySettings.permissive()

# Production - strict, self-only
csp = SecuritySettings.strict()

# Local development server
csp = SecuritySettings.localhost(port=8000)
```

### Custom CSP

```python
csp = SecuritySettings(
    default_src="'self'",
    script_src="'self' 'unsafe-inline' https://cdn.plot.ly",
    style_src="'self' 'unsafe-inline'",
    img_src="'self' data: https:",
)
```

---

## Bundled Assets

Located in `pywry/frontend/assets/`:

| File | Description |
|------|-------------|
| `plotly-3.3.1.js.gz` | Compressed Plotly.js full bundle |
| `plotly-templates.js` | Plotly templates (plotly_dark, plotly_white, ggplot2, seaborn, simple_white, plotly, presentation, xgridoff, ygridoff, gridon) |
| `plotly-widget.js` | Plotly anywidget render code |
| `ag-grid-community-35.0.0.min.js.gz` | Compressed AG Grid |
| `ag-grid-35.0.0.css.gz` | AG Grid base CSS |
| `ag-theme-*.css.gz` | Theme CSS files (quartz, alpine, balham, material × light/dark) |
| `pywry.css` | PyWry CSS variables and classes |
| `PyWry.png`, `icon.*` | Icons |

---

## CSS Classes

PyWry provides consistent CSS classes across all rendering modes:

| Class | Description |
|-------|-------------|
| `.pywry-container` | Root container for native window |
| `.pywry-widget` | Container for anywidget/notebook |
| `.pywry-toolbar` | Toolbar container |
| `.pywry-toolbar-{pos}` | Position variant (top, bottom, left, right, inside) |
| `.pywry-btn` | Button element with accent styling |
| `.pywry-content` | Flex content container |
| `.pywry-wrapper-{pos}` | Layout wrapper (top, bottom, left, right, inside) |
| `.pywry-grid` | AG Grid container |
| `.pywry-plotly` | Plotly container |
| `.plotly-graph-div` | Plotly internal container |
| `html.pywry-native` | Native window mode indicator |
| `html.light` | Light theme indicator |

### CSS Variables

Key CSS variables defined in `pywry.css`:

| Variable | Default (Dark) | Description |
|----------|----------------|-------------|
| `--pywry-bg-primary` | `#212124` | Primary background |
| `--pywry-bg-secondary` | `#1e1e1e` | Secondary background |
| `--pywry-text-primary` | `#ebebed` | Primary text color |
| `--pywry-accent` | `#0078d4` | Accent/button color |
| `--pywry-accent-hover` | `#106ebe` | Button hover color |
| `--pywry-border-color` | `#333` | Border color |
| `--pywry-radius` | `4px` | Border radius |
| `--pywry-spacing-md` | `8px` | Medium spacing |
| `--pywry-font-family` | Inter, system | Font stack |

Light theme overrides these via `html.light` class selector.

---

## JavaScript Bridge Globals

Injected into browser context:

```javascript
// Window label
window.__PYWRY_LABEL__

// JSON data from Python
window.json_data

// Plotly reference (when include_plotly=True)
window.__PYWRY_PLOTLY_DIV__

// AG Grid API (when include_aggrid=True)
window.__PYWRY_GRID_API__

// Bundled Plotly templates
window.PYWRY_PLOTLY_TEMPLATES

// Tauri API (desktop mode only)
window.__TAURI__
window.__TAURI__.pytauri.pyInvoke(command, payload)
window.__TAURI__.event.listen(event, handler)
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PYWRY_HEADLESS` | Enable headless mode (1/true/yes/on) |
| `PYWRY_DEBUG` | Enable debug logging |
| `PYWRY_CONFIG_FILE` | Override config file path |
| `PYWRY_CSP__*` | CSP settings (e.g., `PYWRY_CSP__CONNECT_SRC`) |
| `PYWRY_THEME__*` | Theme settings |
| `PYWRY_WINDOW__*` | Window settings |
| `PYWRY_TIMEOUT__*` | Timeout settings |
| `PYWRY_HOT_RELOAD__*` | Hot reload settings |
| `PYWRY_LOG__*` | Logging settings |
| `PYWRY_ASSET__*` | Asset settings |

---

## Integration with External Libraries

### Plotly.js

```python
from pywry import PyWry

pywry = PyWry()

# Simple dict-based figure
fig = {"data": [{"x": [1, 2, 3], "y": [4, 5, 6], "type": "scatter"}]}
pywry.show_plotly(fig, title="My Chart")

# Or with plotly.graph_objects
import plotly.graph_objects as go
fig = go.Figure(data=go.Scatter(x=[1, 2, 3], y=[4, 5, 6]))
pywry.show_plotly(fig)
```

### AG Grid

```python
import pandas as pd
from pywry import PyWry

pywry = PyWry()
df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
pywry.show_dataframe(df, title="My Table")
```

### Asset Loading Priority

1. Local bundled assets (offline capable)
2. Compressed versions (.gz)
3. Uncompressed versions
4. CDN fallback (if configured)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Window doesn't appear | Check `PYWRY_HEADLESS` not set; verify PyTauri installed |
| Events not firing | Verify namespace format (`namespace:event_name`); check callback registered before `show()` |
| CSS not loading | Check file path is absolute or relative to working directory |
| Hot reload not working | Ensure `hot_reload=True` and file is in `css_files` list |
| Subprocess crashes | Check logs with DEBUG level; verify system has WebKit/WebView2 |
| Notebook rendering fails | Check FastAPI/uvicorn installed; try `pip install pywry[notebook]` |

---

## Dependencies

### Runtime (pyproject.toml)

- `pytauri >= 0.8.0` - Rust/Tauri backend
- `pytauri-wheel >= 0.8.0` - Tauri wheel
- `pydantic >= 2.0.0` - Data validation
- `pydantic-settings >= 2.0.0` - Configuration management
- `anyio >= 4.0.0` - Async utilities
- `fastapi >= 0.128.0` - Inline server
- `uvicorn >= 0.40.0` - ASGI server
- `watchdog >= 3.0.0` - File monitoring
- `websockets >= 15.0.1` - WebSocket support

### Optional (notebook extra)

- `anywidget >= 0.9.0` - Jupyter widget support

### Development

- `pytest`, `pytest-asyncio`, `pytest-timeout` - Testing
- `ruff >= 0.13` - Linting/formatting
- `mypy >= 1.0.0` - Type checking
- `pylint >= 3.0.0` - Additional linting

---

## File Locations Reference

| What | Where |
|------|-------|
| Public API | `pywry/__init__.py` |
| Main class | `pywry/app.py` |
| Inline server | `pywry/inline.py` |
| anywidget widgets | `pywry/widget.py` |
| Notebook detection | `pywry/notebook.py` |
| All models | `pywry/models.py` |
| All config | `pywry/config.py` |
| JS bridge code | `pywry/scripts.py` |
| HTML assembly | `pywry/templates.py` |
| Logging utilities | `pywry/log.py` |
| Bundled assets | `pywry/frontend/assets/` |
| Test fixtures | `tests/conftest.py` |
| CI workflows | `.github/workflows/` |
| Style config | `ruff.toml`, `.pylintrc` |
