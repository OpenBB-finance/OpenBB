# AGENTS.md - PyWry Library Guide for AI Coding Agents

> **Purpose**: This document provides AI coding agents with comprehensive context to understand, develop with, and contribute to the PyWry library.

## Quick Reference

| Aspect | Details |
|--------|---------|
| **Language** | Python 3.10+ |
| **Type System** | Strict typing with Pydantic v2 models |
| **Style** | Ruff (line length 100), NumPy docstrings |
| **Testing** | pytest with fixtures, `PYWRY_HEADLESS=1` for CI |
| **Architecture** | Subprocess IPC with PyTauri (Rust/Tauri backend) |

---

## Project Overview

**PyWry** is a lightweight 100% Python library for creating native desktop windows with bidirectional Python ↔ JavaScript communication. It uses the OS webview (via PyTauri/Tauri) instead of bundling a browser engine, resulting in binaries under 3MB.

### Core Capabilities

- **Three Window Modes**: `NEW_WINDOW`, `SINGLE_WINDOW`, `MULTI_WINDOW`
- **Hot Reload**: CSS injection and JS refresh with scroll preservation
- **Bundled Libraries**: Plotly.js 3.3.1 and AG Grid 35.0.0 (offline capable)
- **Event System**: Bidirectional Python ↔ JavaScript with namespace patterns
- **Dynamic Theming**: Light, Dark, and System modes
- **CLI Tools**: `pywry config` and `pywry init`

---

## Architecture

### Subprocess IPC Model

```
User Code → PyWry (app.py) → Runtime (runtime.py) → PyTauri Subprocess → OS Webview
                                    ↑                        ↓
                            JSON IPC (stdin/stdout)     JavaScript Bridge
                                    ↓                        ↑
                            Callbacks (callbacks.py) ← Events from JS
```

**Key Points:**
- Python manages the high-level API through the `PyWry` class
- A PyTauri subprocess handles actual window creation and OS webview
- Communication uses JSON IPC over stdin/stdout
- The subprocess starts lazily on first `show()` call

### IPC Protocol

Commands sent to PyTauri subprocess:
```python
{"action": "create", "window_id": str, "config": WindowConfig}
{"action": "set_content", "window_id": str, "html": str}
{"action": "show", "window_id": str}
{"action": "close", "window_id": str}
```

---

## Directory Structure

```
pywry/
├── __init__.py          # Public API exports
├── app.py               # Main PyWry class - user entry point
├── runtime.py           # PyTauri subprocess management
├── config.py            # Layered configuration system (pydantic-settings)
├── models.py            # Pydantic models (WindowConfig, HtmlContent, ThemeMode)
├── templates.py         # HTML template builder with CSP, themes, scripts
├── scripts.py           # JavaScript bridge code injected into windows
├── callbacks.py         # Event callback registry (singleton)
├── assets.py            # Bundled asset loading (Plotly.js, AG Grid)
├── asset_loader.py      # CSS/JS file loading with caching
├── hot_reload.py        # Hot reload manager
├── watcher.py           # File system watcher (watchdog-based)
├── logging.py           # Logging utilities
├── cli.py               # CLI commands
├── Tauri.toml           # Tauri configuration
├── capabilities/        # Tauri capability permissions
│   └── default.toml
├── commands/            # IPC command handlers
│   └── __init__.py
├── frontend/            # Frontend HTML and bundled assets
│   └── assets/          # Plotly, AG Grid, icons
├── utils/               # Utility helpers
│   └── async_helpers.py
└── window_manager/      # Window mode implementations
    ├── lifecycle.py     # Window lifecycle with resource tracking
    └── modes/
        ├── base.py          # Abstract WindowMode interface
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
| `WindowLifecycleManager` | `runtime.py` | Singleton managing window creation/destruction via IPC |
| `CallbackRegistry` | `callbacks.py` | Singleton managing event callbacks with namespace support |
| `HotReloadManager` | `hot_reload.py` | Coordinates file watching and CSS injection |
| `FileWatcher` | `watcher.py` | Watchdog-based file monitoring with debouncing |

### Window Modes

| Class | File | Behavior |
|-------|------|----------|
| `WindowMode` | `modes/base.py` | Abstract interface for window modes |
| `SingleWindowMode` | `modes/single_window.py` | Reuses one window, replaces content |
| `NewWindowMode` | `modes/new_window.py` | Creates new window for each `show()` |
| `MultiWindowMode` | `modes/multi_window.py` | Multiple independent labeled windows |

### Configuration Classes

| Class | File | Purpose |
|-------|------|---------|
| `PyWrySettings` | `config.py` | Root settings composing all subsettings |
| `ContentSecurityPolicy` | `config.py` | CSP with factory methods (permissive, strict, localhost) |
| `ThemeSettings` | `config.py` | Theme colors and fonts |
| `WindowConfig` | `models.py` | Pydantic model for window properties |
| `HtmlContent` | `models.py` | Pydantic model for content with files and scripts |

---

## Design Patterns

### 1. Singleton Pattern

Used for managers that need global state. Always use `_instance` class variable:

```python
class CallbackRegistry:
    _instance: ClassVar[CallbackRegistry | None] = None

    def __new__(cls) -> CallbackRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._callbacks = {}
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton for testing."""
        cls._instance = None
```

**Singletons in codebase:**
- `CallbackRegistry` (callbacks.py)
- `WindowLifecycleManager` (runtime.py)
- `HotReloadManager` (hot_reload.py)
- `FileWatcher` (watcher.py)

### 2. Strategy Pattern

Window modes implement the abstract `WindowMode` interface:

```python
from abc import ABC, abstractmethod

class WindowMode(ABC):
    @abstractmethod
    def show(self, content: HtmlContent, config: WindowConfig) -> str:
        """Show content and return window_id."""
        ...

    @abstractmethod
    def close(self, window_id: str | None = None) -> None:
        """Close window(s)."""
        ...
```

### 3. Pydantic Models

All configuration and data models use Pydantic v2:

```python
from pydantic import BaseModel, Field, field_validator

class WindowConfig(BaseModel):
    title: str = "PyWry"
    width: int = Field(default=800, ge=100)
    height: int = Field(default=600, ge=100)
    resizable: bool = True
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()
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

Regex pattern: `^[a-zA-Z][a-zA-Z0-9]*:[a-zA-Z][a-zA-Z0-9_-]*$`

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
from pywry import PyWry, HtmlContent, WindowConfig

app = PyWry()

content = HtmlContent(
    body="<h1>Hello World</h1>",
    css_files=["styles.css"],
)

config = WindowConfig(
    title="My App",
    width=1024,
    height=768,
)

app.show(content, config)
app.run()  # Blocks until all windows closed
```

### With Plotly Chart

```python
from pywry import PyWry, HtmlContent
import plotly.graph_objects as go

app = PyWry()

fig = go.Figure(data=go.Scatter(x=[1, 2, 3], y=[4, 5, 6]))

content = HtmlContent(
    body=f'<div id="chart"></div>',
    scripts=[f"Plotly.newPlot('chart', {fig.to_json()})"],
    include_plotly=True,
)

app.show(content)
app.run()
```

### With Event Callbacks

```python
from pywry import PyWry, HtmlContent

app = PyWry()

def handle_click(data: dict) -> None:
    print(f"Clicked point: {data}")

app.on("plotly:click", handle_click)

content = HtmlContent(
    body='<div id="chart"></div>',
    scripts=[
        "const fig = {data: [{x: [1,2,3], y: [4,5,6], type: 'scatter'}]};",
        "Plotly.newPlot('chart', fig);",
        "document.getElementById('chart').on('plotly_click', (data) => {",
        "    window.pywry.emit('plotly:click', data.points[0]);",
        "});",
    ],
    include_plotly=True,
)

app.show(content)
app.run()
```

### Multi-Window Mode

```python
from pywry import PyWry, HtmlContent, WindowMode

app = PyWry(mode=WindowMode.MULTI_WINDOW)

# Show multiple independent windows
app.show(HtmlContent(body="<h1>Window 1</h1>"), label="win1")
app.show(HtmlContent(body="<h1>Window 2</h1>"), label="win2")

# Update specific window
app.show(HtmlContent(body="<h1>Updated Window 1</h1>"), label="win1")

app.run()
```

### Hot Reload Development

```python
from pywry import PyWry, HtmlContent

app = PyWry(hot_reload=True)

content = HtmlContent(
    body='<div class="container">Content</div>',
    css_files=["styles.css"],  # Changes to this file auto-reload
)

app.show(content)
app.run()
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
    >>> window_id = app.create_window(HtmlContent(body="<h1>Hi</h1>"))
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
    from pywry.models import WindowConfig
    from collections.abc import Callable

class MyClass:
    def __init__(self, callback: Callable[[dict], None]) -> None:
        self._callback = callback
```

### Error Handling

Use `logging_utils.warn_instead_of_raise` for non-fatal errors:

```python
from pywry.logging import warn_instead_of_raise

@warn_instead_of_raise
def load_optional_asset(path: Path) -> str | None:
    """Load asset, returning None and logging warning on failure."""
    return path.read_text()
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
├── conftest.py          # Shared fixtures
├── test_models.py       # Unit tests for models
├── test_config.py       # Configuration tests
├── test_templates.py    # HTML template tests
├── test_assets.py       # Asset loading tests
├── test_callbacks.py    # Event system tests
├── test_csp.py          # CSP tests
├── test_integration.py  # Integration tests
└── test_e2e.py          # End-to-end tests
```

### Key Fixtures (conftest.py)

```python
import pytest
from pywry import HtmlContent, WindowConfig, PyWrySettings

@pytest.fixture
def sample_content() -> HtmlContent:
    return HtmlContent(body="<h1>Test</h1>")

@pytest.fixture
def sample_config() -> WindowConfig:
    return WindowConfig(title="Test Window", width=800, height=600)

@pytest.fixture
def default_settings() -> PyWrySettings:
    return PyWrySettings()

@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset all singletons between tests."""
    yield
    CallbackRegistry.reset()
    WindowLifecycleManager.reset()
    HotReloadManager.reset()
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
        assert config.width == 800
        assert config.height == 600
        assert config.resizable is True

    def test_validation_rejects_negative_width(self) -> None:
        """Test that negative width raises validation error."""
        with pytest.raises(ValueError, match="greater than"):
            WindowConfig(width=-100)

    @pytest.mark.parametrize("width,height", [
        (100, 100),
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
from pywry.window_manager.modes.base import WindowMode
from pywry.models import HtmlContent, WindowConfig

class MyCustomMode(WindowMode):
    def show(self, content: HtmlContent, config: WindowConfig) -> str:
        # Implementation
        ...

    def close(self, window_id: str | None = None) -> None:
        # Implementation
        ...
```

2. Register in `pywry/window_manager/modes/__init__.py`
3. Add to `WindowMode` enum in `pywry/models.py`
4. Write tests in `tests/test_my_mode.py`

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
import logging
logging.getLogger("pywry").setLevel(logging.DEBUG)
```

### Inspect IPC Messages

```python
import logging
logging.getLogger("pywry.runtime").setLevel(logging.DEBUG)
```

### Check Subprocess Status

```python
from pywry.runtime import WindowLifecycleManager

manager = WindowLifecycleManager()
print(f"Subprocess running: {manager.is_running}")
print(f"Active windows: {manager.window_count}")
```

### Validate HTML Output

```python
from pywry.templates import build_html
from pywry.models import HtmlContent
from pywry.config import PyWrySettings

html = build_html(
    HtmlContent(body="<h1>Test</h1>"),
    PyWrySettings(),
)
print(html)  # Inspect generated HTML
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
from pywry.config import ContentSecurityPolicy

# Development - allows everything
csp = ContentSecurityPolicy.permissive()

# Production - strict, self-only
csp = ContentSecurityPolicy.strict()

# Local development server
csp = ContentSecurityPolicy.localhost(port=8000)
```

### Custom CSP

```python
csp = ContentSecurityPolicy(
    default_src=["'self'"],
    script_src=["'self'", "'unsafe-inline'", "https://cdn.plot.ly"],
    style_src=["'self'", "'unsafe-inline'"],
    img_src=["'self'", "data:", "https:"],
)
```

---

## Integration with External Libraries

### Plotly.js

```python
content = HtmlContent(
    body='<div id="chart"></div>',
    include_plotly=True,  # Bundles Plotly.js 3.3.1
    scripts=["Plotly.newPlot('chart', [{x: [1,2,3], y: [4,5,6]}])"],
)
```

### AG Grid

```python
content = HtmlContent(
    body='<div id="grid" class="ag-theme-alpine"></div>',
    include_ag_grid=True,  # Bundles AG Grid 35.0.0
    scripts=[
        "const gridOptions = { columnDefs: [...], rowData: [...] };",
        "agGrid.createGrid(document.getElementById('grid'), gridOptions);",
    ],
)
```

### Asset Loading Priority

1. Local bundled assets (offline capable)
2. Compressed versions (.min.js, .min.css)
3. Uncompressed versions
4. CDN fallback (if configured)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Window doesn't appear | Check `PYWRY_HEADLESS` not set; verify PyTauri installed |
| Events not firing | Verify namespace format; check callback registered before `show()` |
| CSS not loading | Check file path is absolute or relative to working directory |
| Hot reload not working | Ensure `hot_reload=True` and file is in `css_files` list |
| Subprocess crashes | Check logs with DEBUG level; verify system has WebKit/WebView2 |

---

## Dependencies

### Runtime

- `pytauri` - Rust/Tauri backend for native windows
- `pydantic` >= 2.0 - Data validation
- `pydantic-settings` - Configuration management
- `watchdog` - File system monitoring (for hot reload)

### Development

- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `ruff` - Linting and formatting
- `mypy` - Type checking

---

## File Locations Reference

| What | Where |
|------|-------|
| Public API | `pywry/__init__.py` |
| Main class | `pywry/app.py` |
| All models | `pywry/models.py` |
| All config | `pywry/config.py` |
| JS bridge code | `pywry/scripts.py` |
| HTML assembly | `pywry/templates.py` |
| Bundled assets | `pywry/frontend/assets/` |
| Test fixtures | `tests/conftest.py` |
| CI workflows | `.github/workflows/` |
| Style config | `ruff.toml`, `.pylintrc` |
