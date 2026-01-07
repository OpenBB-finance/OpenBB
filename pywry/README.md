![PyWry](./pywry/frontend/assets/PyWry.png)

A lightweight 100% Python library for creating native desktop windows with full bidirectional Python ↔ JavaScript communication. Built on [PyTauri](https://pypi.org/project/pytauri/) (which uses Rust's [Tauri](https://tauri.app/) framework), it leverages the OS webview instead of bundling a browser engine—resulting in binaries under 3MB compared to Electron's 150MB+ overhead. Unlike dashboard libraries that only render output, PyWry provides a complete event system where Python can send events to JavaScript and JavaScript can invoke Python callbacks, enabling truly interactive applications.

## Features

- **Three Window Modes**: NEW_WINDOW, SINGLE_WINDOW, MULTI_WINDOW
- **Hot Reload**: CSS injection and JS refresh with scroll preservation
- **Bundled Libraries**: Plotly.js 3.3.1 and AG Grid 35.0.0 (offline capable)
- **Configuration System**: TOML files, pyproject.toml, and environment variables
- **Dynamic Theming**: Light, Dark, and System modes
- **Event System**: Bidirectional Python ↔ JavaScript communication
- **CLI Tools**: Configuration management and project initialization

## Requirements

- Python 3.10+
- pytauri >= 0.8.0
- pytauri-wheel >= 0.8.0
- pydantic >= 2.0.0
- pydantic-settings >= 2.0.0
- anyio >= 4.0.0
- watchdog >= 3.0.0

### Linux

Linux requires WebKitGTK and GTK3 development libraries:

```bash
# Ubuntu/Debian
sudo apt-get install libwebkit2gtk-4.1-dev libgtk-3-dev libglib2.0-dev \
    libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
    libxcb-randr0 libxcb-render-util0 libxcb-xinerama0 libxcb-xfixes0 \
    libxcb-shape0 libgl1 libegl1
```

## Installation

```bash
pip install pywry
```

For development:

```bash
pip install pywry[dev]
```

---

## Quick Start

```python
from pywry import PyWry, WindowMode, ThemeMode

# Create instance
pywry = PyWry(
    mode=WindowMode.SINGLE_WINDOW,
    theme=ThemeMode.DARK,
    title="My App",
    width=1280,
    height=720,
)

# Display HTML
pywry.show("<h1>Hello, World!</h1>")

# Display Plotly figure (using a dict spec - no plotly import needed)
fig = {"data": [{"x": [1, 2, 3], "y": [4, 5, 6], "type": "scatter"}]}
pywry.show_plotly(fig)

# Display DataFrame with AG Grid
import pandas as pd
df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
pywry.show_dataframe(df)

# Cleanup
pywry.destroy()
```

---

## Table of Contents

- [Window Modes](#window-modes)
- [PyWry Class API](#pywry-class-api)
- [HtmlContent Model](#htmlcontent-model)
- [WindowConfig Model](#windowconfig-model)
- [Configuration System](#configuration-system)
- [Hot Reload](#hot-reload)
- [Event System](#event-system)
- [JavaScript Bridge](#javascript-bridge)
- [CLI Commands](#cli-commands)
- [Building from Source](#building-from-source)

---

## Window Modes

PyWry supports three window management strategies via the `WindowMode` enum:

### NEW_WINDOW (Default)

Creates a new window for each `show()` call:

```python
from pywry import PyWry, WindowMode

pywry = PyWry(mode=WindowMode.NEW_WINDOW)
pywry.show("<h1>Window 1</h1>")  # Opens window 1
pywry.show("<h1>Window 2</h1>")  # Opens window 2
```

### SINGLE_WINDOW

Reuses one window, replacing content:

```python
pywry = PyWry(mode=WindowMode.SINGLE_WINDOW)
pywry.show("<h1>First</h1>")   # Shows "First"
pywry.show("<h1>Second</h1>")  # Replaces with "Second"
```

### MULTI_WINDOW

Multiple independent windows with unique labels:

```python
pywry = PyWry(mode=WindowMode.MULTI_WINDOW)
pywry.show("<h1>Chart</h1>", label="chart-window")
pywry.show("<h1>Table</h1>", label="table-window")

# Update specific window
pywry.update_content("<h1>Updated Chart</h1>", label="chart-window")
```

---

## PyWry Class API

### Constructor

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

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | `WindowMode` | `NEW_WINDOW` | Window management mode |
| `theme` | `ThemeMode` | `SYSTEM` | Theme mode (DARK, LIGHT, SYSTEM) |
| `title` | `str` | `"PyWry"` | Default window title |
| `width` | `int` | `800` | Default window width |
| `height` | `int` | `600` | Default window height |
| `settings` | `PyWrySettings` | `None` | Configuration settings (loads from files/env if None) |
| `hot_reload` | `bool` | `False` | Enable hot reload for CSS/JS files |

### Methods

#### Display Methods

**`show(content, ...) -> str`**

Display HTML content in a window. Returns the window label.

```python
label = pywry.show(
    content,                    # str or HtmlContent
    title=None,                 # Window title override
    width=None,                 # Window width override
    height=None,                # Window height override
    callbacks=None,             # Dict of event handlers
    include_plotly=False,       # Include Plotly.js
    include_aggrid=False,       # Include AG Grid
    label=None,                 # Window label (auto-generated if None)
    watch=None,                 # Enable file watching for hot reload
)
```

**`show_plotly(figure, ...) -> str`**

Display a Plotly figure. Automatically includes Plotly.js and applies theme-appropriate templates.

```python
label = pywry.show_plotly(
    figure,                     # Plotly Figure object or dict spec
    title=None,                 # Window title
    callbacks=None,             # Event handlers
    label=None,                 # Window label
    inline_css=None,            # Custom CSS to inject (e.g., override window background)
)
```

> **Templates**: If your figure has a template set, it is used as-is. If not, the window theme template (`plotly_dark`/`plotly_white`) is applied.

**`show_dataframe(data, ...) -> str`**

Display a DataFrame using AG Grid.

```python
label = pywry.show_dataframe(
    data,                       # pandas DataFrame or dict
    title=None,                 # Window title
    callbacks=None,             # Event handlers
    label=None,                 # Window label
    column_defs=None,           # AG Grid column definitions
    aggrid_theme="alpine",      # AG Grid theme (quartz, alpine, balham, material)
    grid_options=None,          # Custom AG Grid options (merged with defaults)
    inline_css=None,            # Custom CSS to inject (e.g., override window background)
)
```

> **Options Merging**: Custom `grid_options` are merged with pywry defaults. Your options take precedence.

#### Custom Window Styling

Use `inline_css` to customize the window background or other styles:

```python
import plotly.graph_objects as go
from pywry import PyWry, ThemeMode

pywry = PyWry(theme=ThemeMode.DARK)

# Plotly chart with custom window background
fig = go.Figure()
fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6]))
fig.update_layout(paper_bgcolor='#000066', plot_bgcolor='#000099')

pywry.show_plotly(
    fig,
    inline_css='''
        :root { --pywry-bg: #ff0000 !important; }
        html, body { background-color: #ff0000 !important; }
        .plotly-graph-div { width: 90% !important; height: 90% !important; margin: 5% !important; }
    '''
)
```

> **CSS Variables**: The window uses `--pywry-bg` for background color. Override it to customize.

#### Event Methods

**`on(event_type, handler, label=None) -> bool`**

Register an event handler. Returns `True` if successful.

**`send_event(event_type, data, label=None) -> bool`**

Send an event to window(s). If `label` is `None`, sends to all windows.

#### Window Management

| Method | Returns | Description |
|--------|---------|-------------|
| `update_content(html, label=None)` | `bool` | Update window HTML content |
| `close(label=None)` | `bool` | Close window(s) |
| `refresh(label=None)` | `bool` | Refresh with scroll preservation |
| `refresh_css(label=None)` | `bool` | Hot-reload CSS without page refresh |
| `get_labels()` | `list[str]` | Get all active window labels |
| `is_open(label=None)` | `bool` | Check if window(s) are open |

#### Lifecycle

| Method | Description |
|--------|-------------|
| `enable_hot_reload()` | Enable hot reload for file watching |
| `disable_hot_reload()` | Disable hot reload and stop watchers |
| `destroy()` | Close all windows and cleanup resources |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `settings` | `PyWrySettings` | Current settings (read-only) |
| `theme` | `ThemeMode` | Current theme mode (read/write) |

---

## HtmlContent Model

For advanced content configuration, use the `HtmlContent` model:

```python
from pywry import HtmlContent

content = HtmlContent(
    html="<div id='app'></div>",
    json_data={"key": "value"},
    init_script="console.log('ready');",
    css_files=["styles/main.css"],
    script_files=["js/app.js"],
    inline_css="body { margin: 0; }",
    watch=True,
)

pywry.show(content)
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `html` | `str` | Required | HTML content |
| `json_data` | `dict` | `None` | Injected as `window.json_data` |
| `init_script` | `str` | `None` | Custom initialization JavaScript |
| `css_files` | `list[Path \| str]` | `None` | CSS files to include |
| `script_files` | `list[Path \| str]` | `None` | JS files to include |
| `inline_css` | `str` | `None` | Inline CSS styles |
| `watch` | `bool` | `False` | Enable hot reload for these files |

---

## WindowConfig Model

The `WindowConfig` model controls window properties:

```python
from pywry import WindowConfig, ThemeMode

config = WindowConfig(
    title="My Window",
    width=1280,
    height=720,
    theme=ThemeMode.DARK,
)
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | `str` | `"PyWry"` | Window title |
| `width` | `int` | `1280` | Window width (min: 200) |
| `height` | `int` | `720` | Window height (min: 150) |
| `min_width` | `int` | `400` | Minimum width (min: 100) |
| `min_height` | `int` | `300` | Minimum height (min: 100) |
| `theme` | `ThemeMode` | `DARK` | Theme mode |
| `center` | `bool` | `True` | Center window on screen |
| `resizable` | `bool` | `True` | Allow window resizing |
| `decorations` | `bool` | `True` | Show window decorations |
| `always_on_top` | `bool` | `False` | Keep window above others |
| `devtools` | `bool` | `False` | Open developer tools |
| `allow_network` | `bool` | `True` | Allow network requests |
| `enable_plotly` | `bool` | `False` | Include Plotly.js library |
| `enable_aggrid` | `bool` | `False` | Include AG Grid library |
| `plotly_theme` | `str` | `"plotly_dark"` | Plotly theme (plotly, plotly_white, plotly_dark, ggplot2, seaborn, simple_white) |
| `aggrid_theme` | `str` | `"quartz"` | AG Grid theme (quartz, alpine, balham, material) |

---

## Configuration System

PyWry uses a layered configuration system. Settings are merged in this order (highest priority last):

1. **Built-in defaults**
2. **pyproject.toml**: `[tool.pywry]` section
3. **Project config**: `./pywry.toml`
4. **User config**: `~/.config/pywry/config.toml` (Linux/macOS) or `%APPDATA%\pywry\config.toml` (Windows)
5. **Environment variables**: `PYWRY_*` prefix

User config overrides project-level settings, allowing personal preferences across all projects.

### Configuration File (pywry.toml)

```toml
[theme]
dark_bg = "#1a1a2e"
dark_text = "#e4e4e7"
light_bg = "#ffffff"
light_text = "#18181b"
font_family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

[window]
title = "My Application"
width = 1280
height = 720
center = true
resizable = true
devtools = false

[timeout]
startup = 10.0
response = 5.0
create_window = 5.0
set_content = 5.0
shutdown = 2.0

[hot_reload]
enabled = true
debounce_ms = 100
css_reload = "inject"
preserve_scroll = true
watch_directories = ["./src", "./styles"]

[csp]
default_src = "'self' 'unsafe-inline' 'unsafe-eval' data: blob:"
connect_src = "'self' http://*:* https://*:* ws://*:* wss://*:*"
script_src = "'self' 'unsafe-inline' 'unsafe-eval'"
style_src = "'self' 'unsafe-inline'"
img_src = "'self' http://*:* https://*:* data: blob:"
font_src = "'self' data:"

[asset]
plotly_version = "3.3.1"
aggrid_version = "35.0.0"

[log]
level = "WARNING"
format = "%(name)s - %(levelname)s - %(message)s"
```

### pyproject.toml

Add configuration to your existing `pyproject.toml`:

```toml
[tool.pywry]
[tool.pywry.window]
title = "My App"
width = 1280

[tool.pywry.theme]
dark_bg = "#0d1117"
```

### Environment Variables

Override any setting with environment variables using the pattern `PYWRY_{SECTION}__{KEY}`:

```bash
export PYWRY_WINDOW__TITLE="Production App"
export PYWRY_WINDOW__WIDTH=1920
export PYWRY_THEME__DARK_BG="#000000"
export PYWRY_HOT_RELOAD__ENABLED=true
export PYWRY_LOG__LEVEL=DEBUG
```

### Configuration Sections

| Section | Env Prefix | Description |
|---------|------------|-------------|
| `csp` | `PYWRY_CSP__` | Content Security Policy directives |
| `theme` | `PYWRY_THEME__` | Colors and fonts |
| `timeout` | `PYWRY_TIMEOUT__` | Timeout values in seconds |
| `asset` | `PYWRY_ASSET__` | Library versions and CDN URLs |
| `log` | `PYWRY_LOG__` | Log level and format |
| `window` | `PYWRY_WINDOW__` | Default window properties |
| `hot_reload` | `PYWRY_HOT_RELOAD__` | Hot reload behavior |

### Programmatic Configuration

Pass settings directly to PyWry:

```python
from pywry import PyWry, PyWrySettings, ThemeSettings

settings = PyWrySettings(
    theme=ThemeSettings(
        dark_bg="#1e1e1e",
        dark_text="#d4d4d4",
    )
)

pywry = PyWry(settings=settings)
```

### Security Presets

PyWry provides CSP (Content Security Policy) factory methods:

```python
from pywry import SecuritySettings

# Permissive - allows unsafe-inline/eval (default, good for development)
permissive = SecuritySettings.permissive()

# Strict - removes unsafe-eval, restricts to self and specific CDNs
strict = SecuritySettings.strict()

# Localhost - allows only localhost connections
localhost = SecuritySettings.localhost()

# Localhost with specific ports
localhost_ports = SecuritySettings.localhost(ports=[8000, 8080])
```

---

## Hot Reload

Hot reload enables live updates during development without restarting.

### Enable Hot Reload

```python
# Via constructor
pywry = PyWry(hot_reload=True)

# Or enable/disable at runtime
pywry.enable_hot_reload()
pywry.disable_hot_reload()
```

### Behavior

| File Type | Behavior |
|-----------|----------|
| **CSS** | Injected without page reload |
| **JS/HTML** | Full page refresh with scroll preservation |

### Watch Files

Use the `watch` parameter in `HtmlContent` or `show()`:

```python
from pywry import PyWry, HtmlContent

pywry = PyWry(hot_reload=True)

content = HtmlContent(
    html="<div id='app'></div>",
    css_files=["styles/main.css", "styles/theme.css"],
    script_files=["js/app.js"],
    watch=True,
)

pywry.show(content)
# Editing main.css will inject new styles instantly
```

Or pass `watch=True` directly to `show()`:

```python
pywry.show("<h1>Hello</h1>", watch=True)
```

### Manual CSS Reload

```python
# Reload CSS for all windows
pywry.refresh_css()

# Reload CSS for specific window
pywry.refresh_css(label="main-window")
```

### Configuration

```toml
[hot_reload]
enabled = true
debounce_ms = 100        # Wait before reloading (milliseconds)
css_reload = "inject"    # "inject" or "refresh"
preserve_scroll = true   # Keep scroll position on JS refresh
watch_directories = ["./src", "./styles"]
```

---

## Plotly Templates

PyWry bundles all official Plotly templates for consistent theming with no network dependencies.

### Available Templates

| Template | Description |
|----------|-------------|
| `plotly` | Default Plotly theme |
| `plotly_white` | Light theme with white background |
| `plotly_dark` | Dark theme with dark background |
| `ggplot2` | R ggplot2 style |
| `seaborn` | Seaborn style |
| `simple_white` | Minimal white theme |
| `presentation` | High contrast for presentations |
| `xgridoff` | No vertical grid lines |
| `ygridoff` | No horizontal grid lines |
| `gridon` | Grid lines enabled |

### Theme Coordination

The window theme determines the default Plotly template when no template is specified:

| Window Theme | Default Plotly Template |
|--------------|-------------------------|
| `ThemeMode.DARK` | `plotly_dark` |
| `ThemeMode.LIGHT` | `plotly_white` |
| `ThemeMode.SYSTEM` | Follows OS preference |

### User Templates

When you specify a template on your figure, **it is used exactly as-is**:

```python
import plotly.graph_objects as go
from pywry import PyWry, ThemeMode

pywry = PyWry(theme=ThemeMode.DARK)

# Your template is used completely - seaborn's light backgrounds included
fig = go.Figure(data=[...])
fig.update_layout(template='seaborn')

pywry.show_plotly(fig)  # Shows seaborn template exactly
```

PyWry does not modify or merge user templates. The window theme only affects charts without an explicit template.

### JavaScript Access

Templates are available in the browser via `window.PYWRY_PLOTLY_TEMPLATES`:

```javascript
// Access any template directly
const darkTemplate = window.PYWRY_PLOTLY_TEMPLATES['plotly_dark'];

// Apply to a chart
Plotly.update('my-chart', {}, { template: darkTemplate });
```

---

## Event System

PyWry uses a namespace-based event system for Python ↔ JavaScript communication.

### Event Format

Events follow the pattern: `namespace:event-name`

**Reserved namespaces:**
- `pywry:*` - System events
- `plotly:*` - Plotly chart events
- `grid:*` - AG Grid events

### Register Event Handlers (Python)

```python
# Register handler
def handle_click(data, event_type, label):
    print(f"Received {event_type} from {label}: {data}")

pywry.on("app:button-click", handle_click)

# Wildcard - receive all events
def handle_all(data, event_type, label):
    print(f"Event: {event_type}")

pywry.on("*", handle_all)
```

### Send Events to JavaScript (Python → JS)

```python
# Send to all windows
pywry.send_event("app:update", {"message": "Hello"})

# Send to specific window
pywry.send_event("app:update", {"message": "Hello"}, label="main-window")
```

### Built-in Events

**Plotly events** (when `include_plotly=True`):
- `plotly:click` - Point clicked
- `plotly:select` - Points selected
- `plotly:hover` - Point hovered
- `plotly:relayout` - Layout changed (zoom, pan)

**AG Grid events** (when `include_aggrid=True`):
- `grid:select` - Row selection changed
- `grid:cell-edit` - Cell value edited
- `grid:row-click` - Row clicked

```python
def on_chart_click(data):
    print(f"Clicked point: {data}")

pywry.on("plotly:click", on_chart_click)

def on_row_select(data):
    print(f"Selected rows: {data}")

pywry.on("grid:select", on_row_select)
```

---

## JavaScript Bridge

PyWry injects a `window.pywry` object for JavaScript ↔ Python communication.

### Available Methods

```javascript
// Send result back to Python
window.pywry.result(data);

// Emit event to Python
window.pywry.emit("app:action", { key: "value" });

// Register JS event handler
window.pywry.on("app:update", function(data) {
    console.log("Received:", data);
});

// Remove event handler
window.pywry.off("app:update", handler);

// Open file with system default application
window.pywry.openFile("/path/to/file.pdf");
```

### Injected Globals

```javascript
// Window label
window.__PYWRY_LABEL__  // e.g., "main-window"

// JSON data from Python (via HtmlContent.json_data)
window.json_data  // e.g., { key: "value" }
```

### Example: Two-Way Communication

```python
from pywry import PyWry

pywry = PyWry()

def handle_request(data, event_type, label):
    return {"items": [1, 2, 3]}

pywry.on("app:request-data", handle_request)

pywry.show("""
<button onclick="requestData()">Fetch Data</button>
<div id="result"></div>
<script>
function requestData() {
    window.pywry.emit('app:request-data', {});
}
window.pywry.on('app:response', function(data) {
    document.getElementById('result').textContent = JSON.stringify(data);
});
</script>
""")
```

---

## CLI Commands

PyWry provides a CLI for configuration management. Entry point: `pywry`

### Show Configuration

```bash
# Human-readable format
pywry config --show

# TOML format (for creating config files)
pywry config --toml

# Environment variable format
pywry config --env

# Show configuration file sources
pywry config --sources

# Write to file
pywry config --toml --output pywry.toml
```

### Initialize Configuration

```bash
# Create pywry.toml with defaults
pywry init

# Overwrite existing file
pywry init --force

# Custom output path
pywry init --path my-config.toml
```

### Example: Show Sources

```bash
$ pywry config --sources
Configuration sources (in priority order):
  1. Built-in defaults
  2. ~/.config/pywry/config.toml (not found)
  3. pyproject.toml [tool.pywry] (found)
  4. ./pywry.toml (found)
  5. Environment variables (PYWRY_*)
```

---

## Debugging

### Enable Debug Logging

```python
import pywry.log

# Enable verbose debug output for all pywry modules
pywry.log.enable_debug()
```

### Standard Python Logging

```python
import logging

# Enable debug for specific modules
logging.getLogger("pywry").setLevel(logging.DEBUG)
logging.getLogger("pywry.runtime").setLevel(logging.DEBUG)
```

### Environment Variable

```bash
export PYWRY_LOG__LEVEL=DEBUG
```

---

## Building from Source

### Prerequisites

- Python 3.10+
- Git

### Setup

```bash
# Clone repository
git clone https://github.com/OpenBB-finance/pywry.git
cd pywry/pywry-pytauri

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install in development mode
pip install -e ".[dev]"

# Download bundled assets
python build_assets.py
```

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=pywry --cov-report=html
```

### Lint and Format

```bash
# Check code style
ruff check pywry/ tests/

# Format code
ruff format pywry/ tests/

# Type checking
mypy pywry/
```

### Project Structure

```
pywry-pytauri/
├── pywry/
│   ├── __init__.py        # Public API exports
│   ├── app.py             # Main PyWry class
│   ├── asset_loader.py    # CSS/JS file loading with caching
│   ├── assets.py          # Bundled asset management
│   ├── callbacks.py       # Event callback registry
│   ├── cli.py             # CLI commands
│   ├── config.py          # Configuration system
│   ├── hot_reload.py      # Hot reload manager
│   ├── logging.py         # Logging utilities
│   ├── models.py          # Pydantic models
│   ├── runtime.py         # PyTauri subprocess IPC
│   ├── scripts.py         # JavaScript bridge code
│   ├── templates.py       # HTML template builder
│   ├── watcher.py         # File system watcher
│   ├── assets/            # Bundled JS/CSS files
│   ├── commands/          # IPC command handlers
│   ├── frontend/          # Frontend HTML/assets
│   ├── utils/             # Async helpers
│   └── window_manager/    # Window mode implementations
├── tests/                 # Unit tests
├── build_assets.py        # Asset download script
├── pyproject.toml         # Package configuration
└── README.md
```

---
