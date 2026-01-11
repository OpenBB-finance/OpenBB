![PyWry](./pywry/frontend/assets/PyWry.png)

A lightweight 100% Python library for creating native desktop windows with full bidirectional Python ↔ JavaScript communication. Built on [PyTauri](https://pypi.org/project/pytauri/) (which uses Rust's [Tauri](https://tauri.app/) framework), it leverages the OS webview instead of bundling a browser engine—resulting in binaries under 3MB compared to Electron's 150MB+ overhead. Unlike dashboard libraries that only render output, PyWry provides a complete event system where Python can send events to JavaScript and JavaScript can invoke Python callbacks, enabling truly interactive applications.

## Features

- **Three Window Modes**: NEW_WINDOW, SINGLE_WINDOW, MULTI_WINDOW
- **Notebook Support**: Automatic inline rendering (IFrame) in Jupyter/Colab
- **Toolbar System**: Simplified toolbar container and handling for use with the event system.
- **Hot Reload**: CSS injection and JS refresh with scroll preservation
- **Bundled Libraries**: Plotly.js 3.3.1 and AG Grid 35.0.0 (offline capable)
- **Native File Dialogs**: Tauri-powered save/open dialogs and filesystem access
- **Configuration System**: TOML files, pyproject.toml, and environment variables
- **Dynamic Theming**: Light, Dark, and System modes
- **Event System**: Bidirectional Python ↔ JavaScript communication
- **CLI Tools**: Configuration management and project initialization

## Dependencies

- Python 3.10+
- pytauri >= 0.8.0
- pytauri-wheel >= 0.8.0
- pydantic >= 2.0.0
- pydantic-settings >= 2.0.0
- anyio >= 4.0.0
- fastapi >= 0.128.0
- uvicorn >= 0.40.0
- watchdog >= 3.0.0
- websockets >= 15.0.1

### Optional

- anywidget >= 0.9.0

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
from pywry import PyWry, WindowMode, ThemeMode, Toolbar, Button

# Create instance
app = PyWry(
    mode=WindowMode.SINGLE_WINDOW,
    theme=ThemeMode.DARK,
    title="My App",
    width=1280,
    height=720,
)

# Define handler (receives data, event_type, and window label)
def on_click(data, event_type, label):
    app.eval_js("document.querySelector('h1').innerText = 'Toolbar Works!'")
    app.eval_js("document.body.style.backgroundColor = '#222244'")

# Display HTML with an interactive toolbar using callbacks parameter
toolbar = Toolbar(
    position="bottom",
    items=[Button(label="Update Text", event="app:click")]
)
app.show(
    "<h1>Hello, World!</h1>",
    toolbars=[toolbar],
    callbacks={"app:click": on_click},
)

# Display Plotly figure with a custom PyWry toolbar
import logging
logging.basicConfig(level=logging.INFO)

def on_custom_action(data, event_type, label):
    logging.info("Custom action triggered!")
    app.eval_js("alert('Custom action triggered from Python!')")

fig = {"data": [{"x": [1, 2, 3], "y": [4, 5, 6], "type": "scatter"}]}
plotly_toolbar = Toolbar(
    position="top",
    items=[Button(label="Custom Action", event="app:custom")]
)
app.show_plotly(
    fig,
    toolbars=[plotly_toolbar],
    callbacks={"app:custom": on_custom_action},
)

# Display DataFrame with AG Grid
import pandas as pd
df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
app.show_dataframe(df)

# Cleanup
app.destroy()
```

---

## Table of Contents

- [Rendering Paths](#rendering-paths)
  - [Native Window](#native-window)
  - [Notebook Widget (anywidget)](#notebook-widget-anywidget)
  - [Inline IFrame](#inline-iframe)
- [Core API](#core-api)
  - [Imports](#imports)
  - [PyWry Class](#pywry-class)
  - [Display Methods](#display-methods)
  - [Event Methods](#event-methods)
- [Theming & Styling](#css-selectors-and-theming)
- [Data Models](#data-models)
  - [HtmlContent Model](#htmlcontent-model)
  - [WindowConfig Model](#windowconfig-model)
- [Configuration System](#configuration-system)
- [Hot Reload](#hot-reload)
- [Plotly Templates](#plotly-templates)
- [Event System](#event-system)
- [AG Grid Configuration](#ag-grid-configuration)
- [Toolbar System](#toolbar-system)
- [JavaScript Bridge](#javascript-bridge)
- [Direct Tauri API Access](#direct-tauri-api-access)
- [CLI Commands](#cli-commands)
- [Debugging](#debugging)
- [Building from Source](#building-from-source)

---

## Rendering Paths

PyWry automatically selects the appropriate rendering path based on your environment:

| Environment | Rendering Path | Module | Return Type |
|-------------|----------------|--------|-------------|
| Desktop (script/terminal) | Native Window | `pywry.app.PyWry` | `str` (window label) |
| Jupyter/VS Code with anywidget | Notebook Widget | `pywry.widget` | `PyWryWidget` |
| Jupyter/VS Code without anywidget | Inline IFrame | `pywry.inline` | `InlineWidget` |

### Native Window

Uses PyTauri/Tauri to create native OS windows with WebView2 (Windows), WebKit (macOS/Linux).

```python
from pywry import PyWry, WindowMode, ThemeMode
from pywry import runtime  # For sending events to JS

app = PyWry(
    mode=WindowMode.SINGLE_WINDOW,  # or NEW_WINDOW, MULTI_WINDOW
    theme=ThemeMode.DARK,
    title="My App",
    width=1280,
    height=720,
)

# Display content - returns window label
label = app.show("<h1>Hello</h1>")

# Send event to JavaScript
runtime.emit_event(label, "app:update", {"message": "Hello from Python"})
```

**Window Modes:**

| Mode | Behavior |
|------|----------|
| `NEW_WINDOW` | Creates new window for each `show()` call |
| `SINGLE_WINDOW` | Reuses one window, replaces content |
| `MULTI_WINDOW` | Multiple labeled windows, update by label |

### Notebook Widget (anywidget)

When `anywidget` is installed, PyWry uses it for tighter Jupyter integration with bidirectional communication without a local server.

```python
from pywry.inline import show_plotly, show_dataframe

# Returns PyWryPlotlyWidget or PyWryAgGridWidget
widget = show_plotly(fig, callbacks={"custom:toggle": my_handler})

# Send event to JavaScript via widget
widget.emit("app:update", {"message": "Hello"})
```

### Inline IFrame

Fallback when `anywidget` is not available. Uses FastAPI server running in background thread.

```python
from pywry.inline import show_plotly, show_dataframe

# Returns InlineWidget (IFrame-based)
widget = show_plotly(fig, callbacks={"custom:toggle": my_handler})

# Send event to JavaScript via widget
widget.emit("app:update", {"message": "Hello"})
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
from pywry import Toolbar, Button, Select, MultiSelect, TextInput, NumberInput, DateInput, RangeInput, Option

# Grid models (for AG Grid customization)
from pywry.grid import ColDef, ColGroupDef, DefaultColDef, RowSelection, GridOptions

# Runtime (for sending events to native windows)
from pywry import runtime

# Inline functions (for notebooks)
from pywry.inline import show_plotly, show_dataframe

# Settings
from pywry import PyWrySettings, SecuritySettings, WindowSettings, ThemeSettings
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

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | `WindowMode` | `NEW_WINDOW` | Window management mode |
| `theme` | `ThemeMode` | `DARK` | Theme mode (DARK, LIGHT, SYSTEM) |
| `title` | `str` | `"PyWry"` | Default window title |
| `width` | `int` | `800` | Default window width |
| `height` | `int` | `600` | Default window height |
| `settings` | `PyWrySettings` | `None` | Configuration settings |
| `hot_reload` | `bool` | `False` | Enable hot reload |

### Display Methods

**`show(content, ...) -> str | BaseWidget`**

```python
label = app.show(
    content,                    # str or HtmlContent
    title=None,                 # Window title override
    width=None,                 # Window width override
    height=None,                # Window height override
    callbacks=None,             # Dict of event handlers {"event:name": handler}
    include_plotly=False,       # Include Plotly.js
    include_aggrid=False,       # Include AG Grid
    label=None,                 # Window label (auto-generated if None)
    watch=None,                 # Enable file watching for hot reload
    toolbars=None,              # List of Toolbar objects
)
```

**`show_plotly(figure, ...) -> str | BaseWidget`**

```python
label = app.show_plotly(
    figure,                     # Plotly Figure or dict
    title=None,
    callbacks=None,
    label=None,
    inline_css=None,
    toolbars=None,
)
```

**`show_dataframe(data, ...) -> str | BaseWidget`**

```python
label = app.show_dataframe(
    data,                       # pandas DataFrame or dict
    title=None,
    callbacks=None,
    label=None,
    column_defs=None,           # List of ColDef objects
    aggrid_theme="alpine",      # quartz, alpine, balham, material
    grid_options=None,          # GridOptions dict
    toolbars=None,
    inline_css=None,
)
```

### Event Methods

**Callback Signature:**

```python
def my_handler(data: dict, event_type: str, label: str) -> None:
    """
    data: Event payload from JavaScript
    event_type: The event name (e.g., "app:click")
    label: Window label that triggered the event
    """
    pass
```

**Sending Events to JavaScript:**

```python
# Native windows - use runtime.emit_event
from pywry import runtime
runtime.emit_event(label, "app:response", {"key": "value"})

# Notebook widgets - use widget.emit
widget = show_plotly(fig)
widget.emit("app:response", {"key": "value"})
```

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

## CSS Selectors and Theming

PyWry provides a consistent DOM structure across all rendering modes (HTML, Plotly, AG Grid).

### Key Classes

| Selector | Description |
|----------|-------------|
| `.pywry-container` | Root container for native window rendering |
| `.pywry-widget` | Container for anywidget/notebook rendering |
| `.pywry-toolbar` | Toolbar container flexbox |
| `.pywry-toolbar-{pos}` | Toolbar position variant (`top`, `bottom`, `left`, `right`, `inside`) |
| `.pywry-btn` | Button element class with accent styling |
| `.pywry-content` | Flex container for user content (HTML/Chart/Grid) |
| `.pywry-wrapper-{pos}` | Layout wrapper for toolbar positioning (`top`, `bottom`, `left`, `right`, `inside`) |
| `.pywry-grid` | AG Grid container element |
| `.pywry-plotly` | Plotly container element |
| `.plotly-graph-div` | Plotly internal container |
| `html.pywry-native` | Added to html element in native window mode |
| `html.light` | Light theme indicator on html element |

### CSS Variables

Customize these variables via `inline_css` or a custom theme CSS file to style the application.

```css
:root {
  /* Color Palette (Dark Theme Default) */
  --pywry-bg-primary: #212124;
  --pywry-bg-secondary: #1e1e1e;
  --pywry-bg-overlay: rgba(30, 30, 30, 0.8);
  --pywry-text-primary: #ebebed;
  --pywry-text-secondary: #a0a0a0;
  --pywry-border-color: #333;

  /* Accent Colors */
  --pywry-accent: #0078d4;
  --pywry-accent-hover: #106ebe;
  --pywry-accent-text: #ffffff;

  /* Typography */
  --pywry-font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --pywry-font-size: 14px;

  /* Spacing & Layout */
  --pywry-radius: 4px;
  --pywry-radius-lg: 6px;
  --pywry-spacing-xs: 4px;
  --pywry-spacing-sm: 6px;
  --pywry-spacing-md: 8px;
  --pywry-spacing-lg: 12px;

  /* Widget Sizing */
  --pywry-widget-width: 100%;
  --pywry-widget-min-height: 200px;
  --pywry-grid-min-height: 200px;

  /* Transitions */
  --pywry-transition-fast: 0.1s ease;
  --pywry-transition-normal: 0.2s ease;
}

/* Light Theme Overrides */
html.light, .pywry-theme-light {
  --pywry-bg-primary: #f5f5f5;
  --pywry-bg-secondary: #ffffff;
  --pywry-text-primary: #000000;
  --pywry-text-secondary: #666666;
  --pywry-border-color: #ccc;
}
```

### Example: Custom Styling

```python
from pywry import PyWry, HtmlContent, Toolbar, Button

app = PyWry()

def on_action(data, event_type, label):
    app.eval_js("document.querySelector('h1').textContent = 'Styled action!'")

content = HtmlContent(
    html="<h1>Click me</h1>",
    inline_css="""
        .pywry-btn { background: blue !important; border-radius: 20px; }
        .pywry-toolbar { justify-content: center; }
    """
)

toolbar = Toolbar(position="top", items=[Button(label="Action", event="app:action")])

app.show(
    content,
    toolbars=[toolbar],
    callbacks={"app:action": on_action},
)
```

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
| `plotly_theme` | `str` | `"plotly_dark"` | Plotly theme |
| `aggrid_theme` | `str` | `"alpine"` | AG Grid theme |

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
# Optional: Path to custom CSS file for styling overrides
# css_file = "/path/to/custom.css"

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

[tool.pywry.log]
level = "DEBUG"
```

### Environment Variables

Override any setting with environment variables using the pattern `PYWRY_{SECTION}__{KEY}`:

```bash
export PYWRY_WINDOW__TITLE="Production App"
export PYWRY_WINDOW__WIDTH=1920
export PYWRY_THEME__CSS_FILE="/path/to/custom.css"
export PYWRY_HOT_RELOAD__ENABLED=true
export PYWRY_LOG__LEVEL=DEBUG
```

### Configuration Sections

| Section | Env Prefix | Description |
|---------|------------|-------------|
| `csp` | `PYWRY_CSP__` | Content Security Policy directives |
| `theme` | `PYWRY_THEME__` | Custom CSS file path |
| `timeout` | `PYWRY_TIMEOUT__` | Timeout values in seconds |
| `asset` | `PYWRY_ASSET__` | Library versions and asset paths |
| `log` | `PYWRY_LOG__` | Log level and format |
| `window` | `PYWRY_WINDOW__` | Default window properties |
| `hot_reload` | `PYWRY_HOT_RELOAD__` | Hot reload behavior |
| `server` | `PYWRY_SERVER__` | Inline server settings (host, port, CORS) |

### Programmatic Configuration

Pass settings directly to PyWry:

```python
from pywry import PyWry, PyWrySettings, WindowSettings

settings = PyWrySettings(
    window=WindowSettings(
        title="My App",
        width=1920,
        height=1080,
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
| `ggplot2` | ggplot2 style |
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
- `toolbar:*` - Toolbar state events

### Register Event Handlers (Python)

```python
import logging
logging.basicConfig(level=logging.INFO)

# Register handler
def handle_click(data, event_type, label):
    logging.info(f"Received {event_type} from {label}: {data}")

app.on("app:button-click", handle_click)

# Wildcard - receive all events
def handle_all(data, event_type, label):
    logging.info(f"Event: {event_type}")

app.on("*", handle_all)
```

### Send Events to JavaScript (Python → JS)

For native windows, use `runtime.emit_event()`:

```python
from pywry import runtime

# Send to specific window (native windows)
runtime.emit_event(label, "app:update", {"message": "Hello"})
```

For notebook widgets, use `widget.emit()`:

```python
# widget is returned from show_plotly() or show_dataframe()
widget.emit("app:update", {"message": "Hello"})
```

### Built-in Events

**System events** (`pywry:*`):
- `pywry:ready` - Window/widget initialized and ready
- `pywry:result` - Result data returned from JavaScript
- `pywry:theme-update` - Theme changed (payload: `{ mode }`)

**Plotly events** (when `include_plotly=True`):
- `plotly:click` - Point clicked (payload: `{ points, point_indices, curve_number }`)
- `plotly:select` - Points selected (payload: `{ points, range }`)
- `plotly:hover` - Point hovered (payload: `{ points }`)
- `plotly:relayout` - Layout changed/zoom/pan (payload: `{ relayout_data }`)

**AG Grid events** (when `include_aggrid=True`):
- `grid:select` - Row selection changed (payload: `{ selected_rows, selected_row_ids }`)
- `grid:cell-edit` - Cell value edited (payload: `{ row_id, row_index, column, old_value, new_value }`)
- `grid:row-click` - Row clicked (payload: `{ row_data, row_id, row_index }`)
- `grid:state_response` - Grid state returned (for state persistence)
- `grid:request_state` - Request grid state (emitted by widget)

**Toolbar events** (when using toolbars):
- `toolbar:state_response` - Toolbar/component state returned (payload: `{ toolbars, components, timestamp }` or `{ componentId, value }`)
- `toolbar:request_state` - Request toolbar state (emitted by widget)
- `toolbar:set_value` - Set single component value (emitted by widget)
- `toolbar:set_values` - Set multiple component values (emitted by widget)

```python
import logging
logging.basicConfig(level=logging.INFO)

def on_chart_click(data, event_type, label):
    logging.info(f"Clicked point: {data}")

app.on("plotly:click", on_chart_click)

def on_row_select(data, event_type, label):
    logging.info(f"Selected rows: {data}")

app.on("grid:select", on_row_select)

def on_toolbar_state(data, event_type, label):
    logging.info(f"Toolbar state: {data}")

app.on("toolbar:state_response", on_toolbar_state)
```

---

## AG Grid Configuration

PyWry provides Pydantic models that mirror AG Grid's JavaScript API for type-safe grid configuration.

### Import Grid Models

```python
from pywry.grid import ColDef, ColGroupDef, DefaultColDef, RowSelection, GridOptions, build_grid_config
```

### Column Definitions

Use `ColDef` to define individual columns with all common AG Grid options:

```python
from pywry import PyWry
from pywry.grid import ColDef
import pandas as pd

app = PyWry()
df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30], "salary": [50000, 60000]})

# Define custom column configurations
column_defs = [
    ColDef(field="name", header_name="Full Name", pinned="left", min_width=120),
    ColDef(field="age", filter="agNumberColumnFilter", sortable=True),
    ColDef(field="salary", value_formatter="'$' + value.toLocaleString()", flex=1),
]

app.show_dataframe(df, column_defs=column_defs)
```

### ColDef Properties

| Property | Type | Description |
|----------|------|-------------|
| `field` | `str` | Column field name (matches DataFrame column) |
| `header_name` | `str` | Display name in header |
| `hide` | `bool` | Whether column is hidden |
| `pinned` | `"left"` \| `"right"` | Pin column to side |
| `width`, `min_width`, `max_width` | `int` | Column sizing |
| `flex` | `int` | Flex sizing weight |
| `sortable` | `bool` | Enable sorting |
| `filter` | `bool` \| `str` | Enable/specify filter type |
| `resizable` | `bool` | Allow column resizing |
| `editable` | `bool` | Allow cell editing |
| `cell_data_type` | `str` | Data type hint (`"text"`, `"number"`, `"boolean"`, `"date"`) |
| `value_formatter` | `str` | JS expression for formatting display value |
| `cell_renderer` | `str` | Custom cell renderer name |
| `cell_class` | `str` \| `list` | CSS class(es) for cells |
| `cell_style` | `dict` | Inline styles for cells |

### Row Selection

Configure row selection behavior:

```python
from pywry.grid import RowSelection

selection = RowSelection(
    mode="multiRow",           # or "singleRow"
    checkboxes=True,
    header_checkbox=True,
    enable_click_selection=True,
)
```

### Grid Options

For full control, use `GridOptions`:

```python
from pywry.grid import GridOptions, DefaultColDef

grid_options = GridOptions(
    pagination=True,
    pagination_page_size=50,
    animate_rows=True,
    default_col_def=DefaultColDef(
        sortable=True,
        filter=True,
        resizable=True,
        min_width=80,
    ).to_dict(),
)

app.show_dataframe(df, grid_options=grid_options.to_dict())
```

### Available Grid Models

| Model | Purpose |
|-------|---------|
| `ColDef` | Column definition with all common options |
| `ColGroupDef` | Column group for MultiIndex columns |
| `DefaultColDef` | Default settings applied to all columns |
| `RowSelection` | Row selection configuration |
| `GridOptions` | Complete AG Grid configuration |
| `GridConfig` | Combined AG Grid options + PyWry context |
| `GridData` | Normalized grid data from various inputs |

For full AG Grid API reference, see: https://www.ag-grid.com/javascript-data-grid/grid-options/

---

## Toolbar System

PyWry provides a flexible toolbar system for adding interactive controls to any window. The toolbar system uses Pydantic models for type-safe configuration.

### Toolbar Models

Import the toolbar components:

```python
from pywry import Toolbar, Button, Select, MultiSelect, TextInput, NumberInput, DateInput, RangeInput, Option
```

### Toolbar Positions

Each toolbar has a `position` attribute that controls where it appears:

| Position | Description |
|----------|-------------|
| `"top"` | Horizontal bar above content |
| `"bottom"` | Horizontal bar below content |
| `"left"` | Vertical bar to the left of content |
| `"right"` | Vertical bar to the right of content |
| `"inside"` | Overlay positioned in top-right corner |

### Complete Example

```python
from pywry import PyWry, Toolbar, Button

app = PyWry()

# Define handlers - receive (data, event_type, label)
def on_save(data, event_type, label):
    app.eval_js("document.getElementById('status').textContent = 'Saved!'", label=label)

def on_export(data, event_type, label):
    app.eval_js("document.getElementById('status').textContent = 'Exported!'", label=label)

def on_theme_toggle(data, event_type, label):
    app.eval_js("""
        document.documentElement.classList.toggle('light');
        document.getElementById('status').textContent = 'Theme toggled!';
    """, label=label)

# Define toolbar with buttons
toolbar = Toolbar(
    position="top",
    items=[
        Button(label="Save", event="app:save"),
        Button(label="Export CSV", event="app:export"),
        Button(label="Toggle Theme", event="app:theme", style="margin-left: auto;"),
    ]
)

# Show with toolbar - pass callbacks directly to show()
app.show(
    "<h1>My Application</h1><p id='status'>Click a button...</p>",
    toolbars=[toolbar],
    callbacks={
        "app:save": on_save,
        "app:export": on_export,
        "app:theme": on_theme_toggle,
    }
)
```

### Supported Toolbar Item Types

| Type | Properties | Event Payload |
|------|------------|---------------|
| `Button` | `label`, `event`, `data`, `style`, `description` | `data` dict |
| `Select` | `label`, `event`, `options`, `selected` | `{value: string}` |
| `MultiSelect` | `label`, `event`, `options`, `selected` | `{values: string[]}` |
| `TextInput` | `label`, `event`, `value`, `placeholder`, `debounce` | `{value: string}` |
| `NumberInput` | `label`, `event`, `value`, `min`, `max`, `step` | `{value: number}` |
| `DateInput` | `label`, `event`, `value`, `min`, `max` | `{value: string}` |
| `RangeInput` | `label`, `event`, `value`, `min`, `max`, `step`, `show_value` | `{value: number}` |

### Advanced Toolbar Example

```python
from pywry import Toolbar, Button, Select, TextInput, Option

toolbar = Toolbar(
    position="top",
    items=[
        Button(label="Export", event="toolbar:export", data={"format": "csv"}),
        Select(
            label="View:",
            event="view:change",
            options=[Option(label="Table", value="table"), Option(label="Chart", value="chart")],
            selected="table",
        ),
        TextInput(label="Search:", event="search:query", placeholder="Type...", debounce=300),
    ],
)
```

### Styling Buttons

Buttons use the `.pywry-btn` class. Override styles via `HtmlContent.inline_css` or custom CSS:

```python
from pywry import PyWry, HtmlContent, Toolbar, Button

app = PyWry()

def on_action(data, event_type, label):
    app.eval_js("document.querySelector('h1').textContent = 'Action triggered!'", label=label)

content = HtmlContent(
    html="<h1>Click the button</h1>",
    inline_css="""
        .pywry-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            padding: 8px 20px;
        }
        .pywry-btn:hover {
            transform: scale(1.05);
        }
        .pywry-toolbar {
            justify-content: center;
            gap: 12px;
        }
    """
)

toolbar = Toolbar(position="top", items=[Button(label="Action", event="app:action")])

app.show(
    content,
    toolbars=[toolbar],
    callbacks={"app:action": on_action},
)
```

### Toolbar with Plotly/AG Grid

Toolbars work with all display methods:

```python
from pywry import Toolbar, Button

# Plotly with toolbar - reset zoom on click
def on_reset(data, event_type, label):
    app.eval_js("Plotly.relayout(window.__PYWRY_PLOTLY_DIV__, {xaxis: {autorange: true}, yaxis: {autorange: true}})")

toolbar = Toolbar(position="bottom", items=[Button(label="Reset Zoom", event="app:reset")])

app.show_plotly(
    fig,
    toolbars=[toolbar],
    callbacks={"app:reset": on_reset},
)

# AG Grid with toolbar - export on click
def on_export(data, event_type, label):
    app.eval_js("window.__PYWRY_GRID_API__.exportDataAsCsv()")

toolbar = Toolbar(position="top", items=[Button(label="Export CSV", event="app:export")])

app.show_dataframe(
    df,
    toolbars=[toolbar],
    callbacks={"app:export": on_export},
)
```

### Toolbar State Management

PyWry provides bidirectional communication for querying and setting toolbar component values.

**Query toolbar state:**

```python
# For notebook widgets - request all toolbar state
def on_toolbar_state(data, event_type, label):
    print(f"Toolbar state: {data}")
    # data = { 
    #   toolbars: { "toolbar-id": { position: "top", components: [...ids...] } },
    #   components: { "component-id": { type: "select", value: "dark" } },
    #   timestamp: 1234567890
    # }

widget.on("toolbar:state_response", on_toolbar_state)
widget.request_toolbar_state()

# Query specific toolbar
widget.request_toolbar_state(toolbar_id="my-toolbar")

# Query single component value
def on_value(data, event_type, label):
    print(f"Component value: {data['value']}")

widget.on("toolbar:state_response", on_value)
widget.get_toolbar_value("theme-select")
```

**Set toolbar values from Python:**

```python
# Set single component
widget.set_toolbar_value("theme-select", "dark")
widget.set_toolbar_value("columns-multiselect", ["name", "age"])
widget.set_toolbar_value("search-input", "query text")

# Set multiple components at once
widget.set_toolbar_values({
    "theme-select": "dark",
    "columns-multiselect": ["name", "age"],
    "limit-number": 50
})
```

**Native window toolbar state (via runtime):**

```python
from pywry import runtime

# Request toolbar state (response comes via toolbar:state_response callback)
runtime.emit_event("window-label", "toolbar:request_state", {})

# Request specific toolbar
runtime.emit_event("window-label", "toolbar:request_state", {"toolbarId": "my-toolbar"})

# Set single value
runtime.emit_event("window-label", "toolbar:set_value", {
    "componentId": "theme-select",
    "value": "dark"
})

# Set multiple values
runtime.emit_event("window-label", "toolbar:set_values", {
    "values": {
        "theme-select": "dark",
        "columns-multiselect": ["name", "age"]
    }
})
```

**JavaScript access to toolbar state:**

```javascript
// Get state of all toolbars
const state = window.__PYWRY_TOOLBAR__.getState();

// Get state of specific toolbar
const state = window.__PYWRY_TOOLBAR__.getState("my-toolbar-id");

// Get/set individual component value
const value = window.__PYWRY_TOOLBAR__.getValue("component-id");
window.__PYWRY_TOOLBAR__.setValue("component-id", "new-value");
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

// Get current theme
console.log(window.pywry.theme);  // "dark" or "light"
```

### Injected Globals

PyWry injects several globals into the browser context:

```javascript
// Window label (always present)
window.__PYWRY_LABEL__  // e.g., "main-window"

// JSON data from Python (via HtmlContent.json_data)
window.json_data  // e.g., { key: "value" }

// Plotly reference (when include_plotly=True)
window.__PYWRY_PLOTLY_DIV__  // Reference to Plotly chart container

// AG Grid API (when include_aggrid=True)
window.__PYWRY_GRID_API__  // AG Grid API for programmatic control

// Bundled Plotly templates (when include_plotly=True)
window.PYWRY_PLOTLY_TEMPLATES  // Object with all Plotly templates
```

### Accessing AG Grid API

```javascript
// Get selected rows
const rows = window.__PYWRY_GRID_API__.getSelectedRows();

// Update data
window.__PYWRY_GRID_API__.setGridOption('rowData', newData);

// Apply transactions
window.__PYWRY_GRID_API__.applyTransaction({ update: [row1, row2] });

// Export to CSV
window.__PYWRY_GRID_API__.exportDataAsCsv();
```

### Accessing Plotly API

```javascript
// Update chart layout
Plotly.relayout(window.__PYWRY_PLOTLY_DIV__, { title: 'New Title' });

// Update chart data
Plotly.react(window.__PYWRY_PLOTLY_DIV__, newData, newLayout);

// Apply template
Plotly.update(window.__PYWRY_PLOTLY_DIV__, {}, {
    template: window.PYWRY_PLOTLY_TEMPLATES['seaborn']
});
```

### Example: Two-Way Communication

```python
from pywry import PyWry
from pywry import runtime

app = PyWry()

def handle_request(data, event_type, label):
    # Send response back to JavaScript using runtime.emit_event
    runtime.emit_event(label, "app:response", {"items": [1, 2, 3]})

app.show("""
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
""", callbacks={"app:request-data": handle_request})
```

---

## Direct Tauri API Access

For advanced use cases, you can access the underlying Tauri IPC system directly. PyWry is built on [PyTauri](https://pypi.org/project/pytauri/), which provides full access to Tauri's capabilities.

### The `__TAURI__` Global

When running in a desktop window (not in notebook/inline mode), the `window.__TAURI__` object provides direct access to Tauri APIs:

```javascript
// Check if running in Tauri context
if (window.__TAURI__) {
    console.log("Running in Tauri desktop mode");
}

// Available Tauri plugin APIs:
window.__TAURI__.dialog    // Native file dialogs (save, open, message, ask, confirm)
window.__TAURI__.fs        // Filesystem operations (readTextFile, writeTextFile, exists, mkdir)
window.__TAURI__.event     // Event system (listen, emit)
window.__TAURI__.pytauri   // Python IPC (pyInvoke)
```

### PyTauri IPC (Python ↔ JavaScript)

Use `window.__TAURI__.pytauri.pyInvoke` to call Python-registered commands:

```javascript
// Invoke a PyWry command
window.__TAURI__.pytauri.pyInvoke('pywry_event', {
    label: window.__PYWRY_LABEL__,
    event_type: 'custom:action',
    data: { key: 'value' }
});

// Send result to Python
window.__TAURI__.pytauri.pyInvoke('pywry_result', {
    data: { result: 'success' },
    window_label: window.__PYWRY_LABEL__
});

// Open a file with system default app
window.__TAURI__.pytauri.pyInvoke('open_file', { path: '/path/to/file.pdf' });
```

### Listening to Python Events

Use the `window.pywry` bridge to listen for events from Python:

```javascript
// Preferred: Use window.pywry.on() for Python events
window.pywry.on('custom:update', function(data) {
    console.log('Received:', data);
});

// Listen for theme changes
window.pywry.on('pywry:theme-update', function(data) {
    const { mode } = data;  // 'dark' or 'light'
    console.log('Theme changed to:', mode);
});

// Wildcard listener for all events
window.pywry.on('*', function(data, eventType) {
    console.log('Any event:', eventType, data);
});
```

For low-level Tauri access (advanced use cases):

```javascript
// Listen for cleanup signal (before window closes)
window.__TAURI__.event.listen('pywry:cleanup', function() {
    console.log('Window closing, cleanup resources');
});

// Listen for Plotly data updates
window.__TAURI__.event.listen('pywry:plotly-data', function(event) {
    // event.payload contains { data, layout, config }
});
```

### Tauri Internal Events

These are the internal event types used by PyWry:

| Event | Payload | Description |
|-------|---------|-------------|
| `pywry:event` | `{ event_type, data }` | Generic Python → JS event |
| `pywry:theme-update` | `{ mode }` | Theme changed |
| `pywry:cleanup` | None | Window about to close |
| `pywry:plotly-data` | `{ data, layout, config }` | Plotly chart update |

### Example: Custom Tauri Handler

```python
from pywry import PyWry
from pywry import runtime

app = PyWry()

# Define callback - will be called when JS emits 'custom:button-click'
def on_button_click(data, event_type, label):
    print(f'Received: {event_type}, data: {data}')
    # Send event back to JavaScript using runtime.emit_event for native windows
    runtime.emit_event(label, 'custom:update', {'message': f'Hello from Python! Count: {data.get("count", 0)}'})

# Pass callbacks directly to show() - this is the correct pattern
label = app.show('''
<div id="output">Click the button...</div>
<button onclick="sendToPython()">Send to Python</button>
<script>
var count = 0;

// Use window.pywry.on() to listen for Python events
window.pywry.on('custom:update', function(data) {
    document.getElementById('output').textContent = data.message;
});

function sendToPython() {
    count++;
    // Send event to Python
    window.pywry.emit('custom:button-click', { count: count });
}
</script>
''', callbacks={'custom:button-click': on_button_click})
```

> **Note:** The `window.pywry` bridge is automatically initialized by PyWry. Use `window.pywry.on()` to listen for events from Python, and `window.pywry.emit()` to send events to Python. For native windows, use `runtime.emit_event(label, event_type, data)` to send events from Python to JavaScript.

### Environment Detection

Check whether you're running in desktop mode vs notebook/inline:

```javascript
// In desktop mode, __TAURI__ exists
const isDesktop = !!window.__TAURI__;

// In notebook mode, content is in an iframe
const isNotebook = window.frameElement !== null;

// Conditional logic
if (isDesktop) {
    // Use Tauri APIs
    window.__TAURI__.pytauri.pyInvoke('pywry_event', payload);
} else {
    // Use postMessage for iframe communication
    window.parent.postMessage({ type: 'pywry:event', ...payload }, '*');
}
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
git clone https://github.com/OpenBB-finance/OpenBB.git
cd pywry

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install in development mode
pip install -e ".[dev]"
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
pywry/
├── pywry/
│   ├── __init__.py        # Public API exports
│   ├── app.py             # Main PyWry class
│   ├── asset_loader.py    # CSS/JS file loading with caching
│   ├── assets.py          # Bundled asset management
│   ├── callbacks.py       # Event callback registry
│   ├── cli.py             # CLI commands
│   ├── config.py          # Configuration system
│   ├── hot_reload.py      # Hot reload manager
│   ├── inline.py          # FastAPI-based inline server for notebooks
│   ├── log.py             # Logging utilities
│   ├── models.py          # Pydantic models
│   ├── notebook.py        # Notebook detection and widget factory
│   ├── runtime.py         # PyTauri subprocess IPC
│   ├── scripts.py         # JavaScript bridge code
│   ├── templates.py       # HTML template builder
│   ├── watcher.py         # File system watcher
│   ├── widget.py          # anywidget-based widgets
│   ├── widget_protocol.py # BaseWidget protocol
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
