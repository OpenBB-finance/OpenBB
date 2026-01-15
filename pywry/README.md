![PyWry](./pywry/frontend/assets/PyWry.png)

PyWry is a blazingly fast rendering library for generating and managing native desktop windows, iFrames, and Jupyter widgets - with full bidirectional Python ↔ JavaScript communication.

Unlike dashboard libraries that only render output, PyWry provides a complete event system where Python can send events to JavaScript and JavaScript can invoke Python callbacks, enabling truly interactive applications.

Built on [PyTauri](https://pypi.org/project/pytauri/) (which uses Rust's [Tauri](https://tauri.app/) framework), it leverages the OS webview instead of bundling a browser engine—resulting in binaries under 3MB compared to Electron's 150MB+ overhead.

Its unified API lets you build fast and use anywhere. Batteries included.

## Features

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
- requests >= 2.32.5
- pandas >= 1.5.3

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

With anywidget (recommended):

```bash
pip install 'pywry[notebook]'
```

For development:

```bash
pip install 'pywry[dev]'
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
import plotly.graph_objects as go

logging.basicConfig(level=logging.INFO)

def on_custom_action(data, event_type, label):
    logging.info("Custom action triggered!")
    app.eval_js("alert('Custom action triggered from Python!')")

fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 5, 6])])
plotly_toolbar = Toolbar(
    position="top",
    items=[Button(label="Custom Action", event="app:custom")]
)
app.show_plotly(
    fig,
    toolbars=[plotly_toolbar],
    callbacks={"app:custom": on_custom_action},
)

# Display DataFrame with AgGrid
import pandas as pd
df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
app.show_dataframe(df)

# Cleanup
app.destroy()
```

---

## Table of Contents

| Section | Description |
|---------|-------------|
| [Features](#features) | Overview of PyWry capabilities |
| [Dependencies](#dependencies) | Required and optional packages |
| [Installation](#installation) | How to install PyWry |
| [Quick Start](#quick-start) | Minimal working example |

**Core Documentation**

| Section | Description |
|---------|-------------|
| [Rendering Paths](#rendering-paths) | Native Window, Notebook, IFrame, Browser modes |
| [Core API](#core-api) | PyWry class, imports, display & event methods |
| [CSS Selectors and Theming](#css-selectors-and-theming) | Styling with CSS variables and classes |
| [HtmlContent Model](#htmlcontent-model) | Advanced content configuration |
| [WindowConfig Model](#windowconfig-model) | Window property configuration |
| [Configuration System](#configuration-system) | TOML files, environment variables, presets |
| [Hot Reload](#hot-reload) | Live CSS/JS updates during development |

**Event & Toolbar Systems**

| Section | Description |
|---------|-------------|
| [Event System](#event-system) | Bidirectional Python ↔ JS communication |
| [Pre-Registered Events](#pre-registered-events-built-in) | Built-in system, Plotly, and AgGrid events |
| [Toolbar System](#toolbar-system) | All 14 toolbar components with examples |

**Advanced Topics**

| Section | Description |
|---------|-------------|
| [JavaScript Bridge](#javascript-bridge) | `window.pywry` API reference |
| [Direct Tauri API Access](#direct-tauri-api-access) | Native filesystem, dialogs, clipboard |
| [CLI Commands](#cli-commands) | Command-line tools |
| [Debugging](#debugging) | DevTools, logging, troubleshooting |
| [Building from Source](#building-from-source) | Development setup |

**Integrations**

| Section | Description |
|---------|-------------|
| [Plotly Integration](#plotly-integration) | Charts with custom modebar buttons |
| [AgGrid Integration](#ag-grid-integration) | DataFrames with column definitions |

---

## Rendering Paths

<details>
<summary>Click to expand</summary>

PyWry automatically selects the appropriate rendering path based on your environment:

| Environment | Rendering Path | Module | Return Type |
|-------------|----------------|--------|-------------|
| Desktop (script/terminal) | Native Window | `pywry.app.PyWry` | `str` (window label) |
| Jupyter/VS Code with anywidget | Notebook Widget | `pywry.widget` | `PyWryWidget` |
| Jupyter/VS Code without anywidget | Inline IFrame | `pywry.inline` | `InlineWidget` |
| Headless / Server / SSH | Browser Mode | `pywry.window_manager.modes.browser` | `str` (widget ID) |

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
| `NOTEBOOK` | Inline rendering in Jupyter notebooks (auto-detected) |
| `BROWSER` | Opens in system browser, uses FastAPI server (headless/SSH) |

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

### Browser Mode

For headless environments (servers, SSH sessions, containers), use `BROWSER` mode to open content in the system's default browser:

```python
from pywry import PyWry, WindowMode

app = PyWry(mode=WindowMode.BROWSER)

# Opens in default browser, returns widget_id
widget_id = app.show("<h1>Hello from Browser</h1>")

# Works with Plotly and DataFrames too
app.show_plotly(fig)
app.show_dataframe(df)
```

Browser mode starts a FastAPI server and opens the widget URL in the browser. Use `pywry.inline.block()` to keep the server running after your script completes.

</details>

---

## Core API

<details>
<summary>Click to expand</summary>

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

# Widget classes
from pywry import PyWryWidget, PyWryPlotlyWidget, PyWryAgGridWidget

# Window manager
from pywry import BrowserMode, get_lifecycle

# Settings
from pywry import PyWrySettings, SecuritySettings, WindowSettings, ThemeSettings, ServerSettings, HotReloadSettings, TimeoutSettings, AssetSettings, LogSettings

# Asset loading
from pywry import AssetLoader, get_asset_loader

# Callback registry
from pywry import CallbackFunc, WidgetType, get_registry
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
    include_aggrid=False,       # Include AgGrid
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

</details>

---

## CSS Selectors and Theming

<details>
<summary>Click to expand</summary>

PyWry provides a consistent DOM structure across all rendering modes (HTML, Plotly, AgGrid).

### Theme Classes

PyWry uses a dual-class theming system for maximum compatibility:

| Selector | Description |
|----------|-------------|
| `html.dark` | Dark theme indicator on document root |
| `html.light` | Light theme indicator on document root |
| `html.pywry-native` | Added to html element in native window mode |
| `.pywry-theme-dark` | Dark theme on widget container (notebook/browser mode) |
| `.pywry-theme-light` | Light theme on widget container (notebook/browser mode) |

> **Note:** The `html.dark`/`html.light` classes are applied to the document root for global styling. The `.pywry-theme-*` classes are applied to widget containers for scoped styling in notebooks.

### Layout Classes

| Selector | Description |
|----------|-------------|
| `.pywry-widget` | Root container for widgets (notebook/browser mode) |
| `.pywry-content` | Flex container for user content (HTML/Chart/Grid) |
| `.pywry-wrapper-{pos}` | Layout wrapper for toolbar positioning (`top`, `bottom`, `left`, `right`) |
| `.pywry-plotly` | Plotly chart container element |
| `.pywry-grid` | AgGrid container element |
| `.plotly-graph-div` | Plotly internal container (Plotly's own class) |

### Toolbar Classes

| Selector | Description |
|----------|-------------|
| `.pywry-toolbar` | Toolbar container flexbox |
| `.pywry-toolbar-{pos}` | Toolbar position variant (`top`, `bottom`, `left`, `right`, `inside`) |
| `.pywry-toolbar-content` | Inner container for toolbar items |
| `.pywry-toolbar-toggle` | Collapsible toolbar toggle button |
| `.pywry-toolbar-button` | Button within toolbar |

### Component Classes

| Selector | Description |
|----------|-------------|
| `.pywry-btn` | Button element with accent styling |
| `.pywry-btn-{variant}` | Button variant (`secondary`, `ghost`, `danger`) |
| `.pywry-btn-{size}` | Button size (`sm`, `lg`) |
| `.pywry-dropdown` | Select/dropdown container |
| `.pywry-dropdown-selected` | Selected value display |
| `.pywry-dropdown-menu` | Dropdown options container |
| `.pywry-dropdown-option` | Individual dropdown option |
| `.pywry-multiselect` | Multi-select dropdown container |
| `.pywry-multiselect-checkbox` | Checkbox input in multi-select |
| `.pywry-input-group` | Input with label container |
| `.pywry-input-label` | Label for input elements |
| `.pywry-tab` | Tab button element |
| `.pywry-tab-active` | Active tab indicator |
| `.pywry-selected` | Selected state for options |

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

</details>

---

## HtmlContent Model

<details>
<summary>Click to expand</summary>

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

</details>

---

## WindowConfig Model

<details>
<summary>Click to expand</summary>

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
| `enable_aggrid` | `bool` | `False` | Include AgGrid library |
| `plotly_theme` | `str` | `"plotly_dark"` | Plotly theme |
| `aggrid_theme` | `str` | `"alpine"` | AgGrid theme |

</details>

---

## Configuration System

<details>
<summary>Click to expand</summary>

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

</details>

---

## Hot Reload

<details>
<summary>Click to expand</summary>

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

</details>

---

## Event System

<details>
<summary>Click to expand</summary>

PyWry provides bidirectional communication between Python and JavaScript through a **namespace-based event system**. This allows your Python code to respond to user interactions in the browser (clicks, selections, form inputs) and to send updates back to the browser UI.

### What is an Event?

An **event** is a message with a name and optional data. Events flow in two directions:

1. **JS → Python**: User does something in the browser (clicks a chart, selects a row) → JavaScript sends an event → Python callback is triggered
2. **Python → JS**: Your Python code wants to update the UI → Python sends an event → JavaScript handler updates the display

### Event Naming Format

All events follow the pattern: `namespace:event-name`

| Part | Rules | Examples |
|------|-------|----------|
| **namespace** | Starts with letter, alphanumeric only | `app`, `plotly`, `grid`, `myapp` |
| **event-name** | Starts with letter, alphanumeric + hyphens + underscores | `click`, `row-select`, `update_data` |

**Valid examples:** `app:save`, `plotly:click`, `grid:row-select`, `myapp:refresh`

**Invalid examples:** `save` (no namespace), `:click` (empty namespace), `123:event` (starts with number)

> **Note:** JavaScript validation is stricter (lowercase only) than Python validation. For maximum compatibility, use **lowercase with hyphens** (e.g., `app:my-action`).

#### Compound Event IDs (Advanced)

Events can optionally include a third component for targeting specific widgets: `namespace:event-name:component-id`

```python
# Handle clicks from ANY chart
app.on("plotly:click", handle_all_charts)

# Handle clicks from a SPECIFIC chart
app.on("plotly:click:sales-chart", handle_sales_chart)
```

### Reserved Namespaces

These namespaces are used by PyWry internally. **Do not use them for custom events:**

| Namespace | Purpose |
|-----------|---------|
| `pywry:*` | System events (initialization, results) |
| `plotly:*` | Plotly chart events |
| `grid:*` | AgGrid table events |

> **Tip:** Use a namespace that makes sense for your app (e.g., `app:`, `data:`, `view:`, `myapp:`).

### Handler Signature

All event handlers receive three arguments:

```python
def handler(data: dict, event_type: str, label: str) -> None:
    """
    Parameters
    ----------
    data : dict
        Event payload from JavaScript (e.g., clicked point, selected rows)
    event_type : str
        The event that was triggered (e.g., "plotly:click", "app:export")
    label : str
        Window/widget identifier (e.g., "main", "chart-1")
    """
    pass
```

PyWry inspects your function signature and supports shorter versions for convenience:

```python
# Full signature (recommended)
def handler(data, event_type, label):
    print(f"[{label}] {event_type}: {data}")

# Two parameters
def handler(data, event_type):
    print(f"{event_type}: {data}")

# One parameter
def handler(data):
    print(data)
```

### Registering Handlers

**All modes support the `callbacks={}` parameter in `show()` methods.** This is the most portable approach.

| Mode | `callbacks={}` | `app.on()` | `widget.on()` | Returns |
|------|----------------|------------|---------------|---------|
| Native Window | ✅ | ✅ | ❌ | `str` (label) |
| Notebook (anywidget) | ✅ | ❌ | ✅ | `BaseWidget` |
| Browser Mode | ✅ | ❌ | ✅ | `BaseWidget` |

#### Option 1: `callbacks={}` in show() — Works Everywhere

```python
def on_click(data, event_type, label):
    print(f"Clicked: {data}")

def on_export(data, event_type, label):
    print("Exporting...")

# Works in ALL modes
result = app.show_plotly(
    fig,
    callbacks={
        "plotly:click": on_click,
        "app:export": on_export,
    }
)
```

#### Option 2: `app.on()` — Native Windows Only

For native desktop windows, you can register handlers separately:

```python
app = PyWry()

# Register before or after show()
app.on("plotly:click", on_click)
app.on("app:export", on_export)

label = app.show_plotly(fig)  # Returns window label (str)
```

#### Option 3: `widget.on()` — Notebooks/Browser Mode Only

For notebook widgets, you can chain handlers on the returned widget:

```python
# In Jupyter notebook
widget = app.show_plotly(fig)  # Returns BaseWidget

widget.on("plotly:click", on_click)
widget.on("app:export", on_export)

# Method chaining works too
widget.on("plotly:click", on_click).on("app:export", on_export)
```

### Wildcard Handlers

Listen to all events for debugging or logging:

```python
def log_all_events(data, event_type, label):
    print(f"[{label}] {event_type}: {data}")

app.on("*", log_all_events)
```

---

## Pre-Registered Events (Built-in)

PyWry automatically hooks into Plotly and AgGrid event systems. These **pre-registered events** are emitted automatically when users interact with charts and grids — **no JavaScript required**.

### What "Pre-Registered" Means

When you create a Plotly chart or AgGrid table, PyWry injects JavaScript that:
1. Listens for native library events (e.g., Plotly's `plotly_click`)
2. Transforms the raw event data into a standardized payload
3. Emits a PyWry event (e.g., `plotly:click`) that triggers your Python callback

**You just register a Python handler; PyWry handles the JavaScript wiring.**

### Understanding IDs: label vs. chartId/gridId/componentId

PyWry uses a hierarchy of identifiers:

| ID Type | Scope | Purpose | Example |
|---------|-------|---------|---------|
| `label` | Window/Widget | Identifies a window (native) or widget (notebook/browser) | `"pywry-abc123"`, `"w-def456"` |
| `chartId` | Component | Identifies a specific Plotly chart within a window | `"sales-chart"` |
| `gridId` | Component | Identifies a specific AgGrid table within a window | `"users-grid"` |
| `componentId` | Toolbar Item | Identifies a specific toolbar control | `"theme-select"`, `"export-btn"` |

**Event Payloads Include IDs:**
- **Plotly events** (`plotly:click`, `plotly:hover`, etc.) include `chartId` and `widget_type: "chart"` in the payload.
- **AgGrid events** (`grid:select`, `grid:cell-edit`, etc.) include `gridId` and `widget_type: "grid"` in the payload.
- **Toolbar components** always include `componentId` in their payloads.
- **Python → JS events** support targeting via `chartId`/`gridId` when using widget methods like `widget.update_figure(fig, chart_id="my-chart")`.

### System Events (`pywry:*`)

These are internal events for window/widget lifecycle and utility operations.

#### Lifecycle Events (JS → Python)

| Event | Payload | Description |
|-------|---------|-------------|
| `pywry:ready` | `{}` | Window/widget has finished initializing |
| `pywry:result` | `any` | Data sent via `window.pywry.result(data)` |
| `pywry:disconnect` | `{}` | Widget disconnected (browser closed, tab closed) |

#### Utility Events (Python → JS)

These events trigger built-in browser behaviors. They are handled automatically by PyWry's JavaScript bridge — **no custom JavaScript required**:

| Event | Payload | Description |
|-------|---------|-------------|
| `pywry:update-theme` | `{ theme: str }` | Update theme dynamically (e.g., `"plotly_dark"`, `"plotly_white"`) |
| `pywry:inject-css` | `{ css: str, id?: str }` | Inject CSS dynamically; optional `id` for replacing existing styles |
| `pywry:set-style` | `{ id?: str, selector?: str, styles: {} }` | Update inline styles on element(s) by id or CSS selector |
| `pywry:set-content` | `{ id?: str, selector?: str, html?: str, text?: str }` | Update innerHTML or textContent on element(s) |
| `pywry:download` | `{ content: str, filename: str, mimeType?: str }` | Trigger a file download (IFrame/browser mode only) |
| `pywry:navigate` | `{ url: str }` | Navigate to a URL (SPA-style navigation) |
| `pywry:alert` | `{ message: str }` or `{ text: str }` | Show a browser alert dialog |
| `pywry:update-html` | `{ html: str }` | Replace widget content (triggers page reload) |

**Example: DOM Manipulation Without Custom JavaScript**

```python
# Update theme dynamically
widget.emit("pywry:update-theme", {"theme": "plotly_white"})

# Inject CSS dynamically
widget.emit("pywry:inject-css", {
    "css": ".my-class { color: red; font-weight: bold; }",
    "id": "my-dynamic-styles"  # Optional: allows replacing later
})

# Update element styles by ID
widget.emit("pywry:set-style", {
    "id": "status-badge",
    "styles": {"backgroundColor": "green", "color": "white"}
})

# Or by CSS selector (updates all matching elements)
widget.emit("pywry:set-style", {
    "selector": ".highlight-row",
    "styles": {"backgroundColor": "#ffffcc"}
})

# Update element content by ID
widget.emit("pywry:set-content", {
    "id": "values-display",
    "html": "<strong>Updated!</strong> 42 items"
})

# Or use plain text (safer, no HTML parsing)
widget.emit("pywry:set-content", {
    "selector": ".status-text",
    "text": "Processing complete"
})

# Trigger a CSV download
widget.emit("pywry:download", {
    "content": "name,age\nAlice,30\nBob,25",
    "filename": "users.csv",
    "mimeType": "text/csv"
})
```

> **Note:** `pywry:set-style` and `pywry:set-content` support either `id` (for a single element by ID) or `selector` (for multiple elements via CSS selector). If both are provided, `id` takes precedence.

### Plotly Events (`plotly:*`)

#### Events from JavaScript → Python (User Interactions)

These events fire automatically when users interact with Plotly charts:

| Event | Trigger | Payload |
|-------|---------|---------|
| `plotly:click` | User clicks a data point | `{ chartId, widget_type: "chart", points: [...], point_indices: [...], curve_number: int }` |
| `plotly:hover` | User hovers over a point | `{ chartId, widget_type: "chart", points: [{ x, y, curveNumber }, ...] }` |
| `plotly:select` | User selects with box/lasso | `{ chartId, widget_type: "chart", points: [...], range: {...} or null }` |
| `plotly:relayout` | User zooms, pans, or resizes | `{ chartId, widget_type: "chart", relayout_data: {...} }` |
| `plotly:state-response` | Response to state request | `{ chartId, layout: {...}, data: [...] }` |

> **Note:** All Plotly events include `chartId` and `widget_type: "chart"` in the payload for identifying which chart triggered the event.

**`plotly:click` payload structure:**
```python
{
    "chartId": "chart_abc123",    # Unique chart identifier
    "widget_type": "chart",       # Always "chart" for Plotly events
    "points": [
        {
            "curveNumber": 0,      # Which trace (0-indexed)
            "pointIndex": 5,       # Which point in the trace
            "x": 2.5,              # X value
            "y": 10.3,             # Y value
            "data": {"name": "Series A"}  # Trace metadata
        }
    ],
    "point_indices": [5],
    "curve_number": 0
}
```

**Example:**

```python
def on_chart_click(data, event_type, label):
    # Use chartId to identify which chart triggered the event
    chart_id = data.get("chartId", "unknown")
    point = data["points"][0]
    print(f"[{chart_id}] Clicked: ({point['x']}, {point['y']}) on trace {point['curveNumber']}")

app.on("plotly:click", on_chart_click)
```

#### Events from Python → JavaScript (Update Chart)

Use these to update the chart programmatically. These methods support optional `chart_id` targeting:

| Event | Method | Payload |
|-------|--------|---------|
| `plotly:update-figure` | `widget.update_figure(fig, chart_id=...)` | `{ figure: {...}, chartId?, config?: {...}, animate?: bool }` |
| `plotly:update-layout` | `widget.update_layout({...})` | `{ layout: {...} }` |
| `plotly:update-traces` | `widget.update_traces({...}, indices)` | `{ update: {...}, indices: [int, ...] or null }` |
| `plotly:reset-zoom` | `widget.reset_zoom()` | `{}` |
| `plotly:request-state` | `widget.request_plotly_state(chart_id=...)` | `{ chartId? }` |

### AgGrid Events (`grid:*`)

#### Events from JavaScript → Python (User Interactions)

These events fire automatically when users interact with AgGrid tables:

| Event | Trigger | Payload |
|-------|---------|---------|
| `grid:select` | Row selection changes | `{ gridId, widget_type: "grid", selected_rows: [...], selected_row_ids: [...] }` |
| `grid:cell-edit` | User edits a cell | `{ gridId, widget_type: "grid", row_id, row_index, column, old_value, new_value }` |
| `grid:row-click` | User clicks a row | `{ gridId, widget_type: "grid", row_data: {...}, row_id, row_index }` |
| `grid:state-response` | Response to state request | `{ gridId, state: { columnState, filterModel } }` |

> **Note:** All AgGrid events include `gridId` and `widget_type: "grid"` in the payload for identifying which grid triggered the event.

**`grid:select` payload structure:**
```python
{
    "gridId": "grid_def456",      # Unique grid identifier
    "widget_type": "grid",        # Always "grid" for AgGrid events
    "selected_rows": [
        {"name": "Alice", "age": 30, "city": "NYC"},
        {"name": "Bob", "age": 25, "city": "LA"}
    ],
    "selected_row_ids": ["0", "2"]
}
```

**Example:**

```python
def on_row_select(data, event_type, label):
    # Use gridId to identify which grid triggered the event
    grid_id = data.get("gridId", "unknown")
    rows = data["selected_rows"]
    print(f"[{grid_id}] Selected {len(rows)} rows")
    for row in rows:
        print(f"  - {row['name']}")

app.on("grid:select", on_row_select)
```

#### Events from Python → JavaScript (Update Grid)

Use these to update the grid programmatically. These methods support optional `grid_id` targeting:

| Event | Method | Payload |
|-------|--------|---------|
| `grid:update-data` | `widget.update_data(rows, grid_id=...)` | `{ data: [...], gridId? }` |
| `grid:update-columns` | `widget.update_columns(col_defs, grid_id=...)` | `{ columnDefs: [...], gridId? }` |
| `grid:update-cell` | `widget.update_cell(row_id, col, value, grid_id=...)` | `{ rowId, colId, value, gridId? }` |
| `grid:update-options` | `widget.update_grid(options, grid_id=...)` | `{ options: {...}, gridId? }` |
| `grid:request-state` | `widget.request_grid_state(grid_id=...)` | `{ gridId? }` |
| `grid:restore-state` | `widget.restore_state(state, grid_id=...)` | `{ state: {...}, gridId? }` |
| `grid:reset-state` | `widget.reset_state(grid_id=...)` | `{ gridId?, hard?: bool }` |

### Toolbar Events (`toolbar:*`)

Toolbar events are used for state management (querying and setting component values).

| Event | Direction | Payload | Description |
|-------|-----------|---------|-------------|
| `toolbar:state-response` | JS → Python | `{ toolbars, components, timestamp, context? }` | Response to state request |
| `toolbar:request-state` | Python → JS | `{ toolbarId?, componentId?, context? }` | Request current state |
| `toolbar:set-value` | Python → JS | `{ componentId, value, toolbarId? }` | Set single component value |
| `toolbar:set-values` | Python → JS | `{ values: { id: value, ... }, toolbarId? }` | Set multiple component values |

> **Note:** Toolbar *components* (Button, Select, etc.) emit their own custom events that you define via the `event` parameter. All component events automatically include `componentId` in their payload. See the Toolbar System section.

---

## Custom Events

Custom events are events **you define** for your application. Unlike pre-registered events, custom events require you to either:

1. Use toolbar components (which emit events automatically), or
2. Write JavaScript that calls `window.pywry.emit()`

### Event Direction Overview

| Direction | How to Send | How to Receive | Use Case |
|-----------|-------------|----------------|----------|
| **JS → Python** | `window.pywry.emit(event, data)` | `callbacks={}`, `app.on()`, `widget.on()` | User interactions |
| **Python → JS** | `app.emit(event, data, label=...)` or `widget.emit(event, data)` | `window.pywry.on(event, handler)` | Update UI |

### JS → Python: Receiving Events from JavaScript

#### Toolbar Component Events (Easiest)

Toolbar components automatically emit events — you just specify the event name:

```python
from pywry import Toolbar, Button, Select, Option

toolbar = Toolbar(
    position="top",
    items=[
        Button(label="Export CSV", event="app:export-csv"),
        Button(label="Refresh", event="app:refresh"),
        Select(
            label="Theme:",
            event="app:theme-change",
            options=[Option(label="Light", value="light"), Option(label="Dark", value="dark")],
            selected="dark"
        ),
    ]
)

def on_export(data, event_type, label):
    print("Exporting CSV...")
    # data = {} for buttons (or whatever you set in Button's `data` param)

def on_theme_change(data, event_type, label):
    print(f"Theme changed to: {data['value']}")
    # data = { "value": "dark", "componentId": "select-a1b2c3d4" }

app.show(
    content,
    toolbars=[toolbar],
    callbacks={
        "app:export-csv": on_export,
        "app:theme-change": on_theme_change,
    }
)
```

**Toolbar component payloads:**

All toolbar components include `componentId` in their event payload for identification. Component IDs are auto-generated in the format `{type}-{uuid8}` (e.g., `button-a1b2c3d4`, `select-f099cfba`).

| Component | Payload |
|-----------|---------|
| `Button` | `{ componentId, ...data }` (merges `Button(data={...})` with componentId) |
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

**Using componentId to identify which button was clicked:**

```python
def on_action(data, event_type, label):
    component = data.get("componentId", "unknown")
    print(f"Button {component} was clicked")
    
    # Custom data from Button(data={...}) is also included
    if "format" in data:
        print(f"Export format: {data['format']}")

toolbar = Toolbar(
    position="top",
    items=[
        Button(label="Export CSV", event="app:export", data={"format": "csv"}),
        Button(label="Export JSON", event="app:export", data={"format": "json"}),
    ]
)

app.show(content, toolbars=[toolbar], callbacks={"app:export": on_action})
```

#### Custom JavaScript Events

Emit events from your own JavaScript code:

```python
app.show("""
<button onclick="window.pywry.emit('app:my-action', {value: 42})">
    Click Me
</button>
""", callbacks={"app:my-action": lambda data, evt, lbl: print(data)})
```

### Python → JS: Sending Events to JavaScript

To update the browser UI from Python, use `emit()`:

**Native windows:**
```python
from pywry import runtime

# app.emit() sends to a specific window by label
label = app.show("<div id='msg'>Hello</div>")

# Later, send an event to that window
runtime.emit_event(label, "app:update-message", {"text": "Updated!"})
```

**Notebook/Browser widgets:**
```python
widget = app.show("<div id='msg'>Hello</div>")

# Use widget.emit() to send to that specific widget
widget.emit("app:update-message", {"text": "Updated!"})
```

**Receiving in JavaScript:**
```javascript
window.pywry.on('app:update-message', function(data) {
    document.getElementById('msg').textContent = data.text;
});
```

### Complete Two-Way Communication Example

```python
from pywry import PyWry
from pywry import runtime

app = PyWry()

def handle_request(data, event_type, label):
    # Process the request from JavaScript
    result = {"items": [1, 2, 3], "total": 3}
    # Send response back to JavaScript
    runtime.emit_event(label, "app:response", result)

label = app.show("""
<button onclick="requestData()">Fetch Data</button>
<div id="result"></div>
<script>
function requestData() {
    window.pywry.emit('app:request-data', {});  // JS → Python
}
window.pywry.on('app:response', function(data) {  // Python → JS
    document.getElementById('result').textContent = JSON.stringify(data);
});
</script>
""", callbacks={"app:request-data": handle_request})
```

</details>

---

## Toolbar System

<details>
<summary>Click to expand</summary>

PyWry provides a flexible toolbar system for adding interactive controls to any window. The toolbar system uses Pydantic models for type-safe configuration with auto-generated component IDs for state tracking.

### Quick Start

```python
from pywry import PyWry, Toolbar, Button, Select, Option

app = PyWry()

def on_save(data, event_type, label):
    print(f"Save clicked! Component: {data['componentId']}")

def on_view_change(data, event_type, label):
    print(f"View changed to: {data['value']}")

toolbar = Toolbar(
    position="top",
    items=[
        Button(label="Save", event="app:save"),
        Select(
            label="View:",
            event="view:change",
            options=["Table", "Chart", "Map"],  # Simple strings work too
            selected="Table",
        ),
    ],
)

app.show(
    "<h1>My App</h1>",
    toolbars=[toolbar],
    callbacks={"app:save": on_save, "view:change": on_view_change},
)
```

### Imports

```python
from pywry import (
    Toolbar,           # Container for toolbar items
    Button,            # Clickable button
    Select,            # Single-select dropdown
    MultiSelect,       # Multi-select dropdown with checkboxes
    TextInput,         # Text input with debounce
    NumberInput,       # Numeric input with min/max/step
    DateInput,         # Date picker (YYYY-MM-DD)
    SliderInput,       # Single-value slider
    RangeInput,        # Dual-handle range slider
    Toggle,            # Boolean switch (on/off)
    Checkbox,          # Boolean checkbox
    RadioGroup,        # Radio button group
    TabGroup,          # Tab-style selection
    Div,               # Container for custom HTML/nested items
    Option,            # Option for Select/MultiSelect/RadioGroup/TabGroup
)
```

### Toolbar Positions & Layout

PyWry supports **7 toolbar positions** that combine to create a flexible layout system:

| Position | Description |
|----------|-------------|
| `"header"` | Full-width bar at the very top (outermost) |
| `"footer"` | Full-width bar at the very bottom (outermost) |
| `"left"` | Vertical bar on the left, extends between header/footer |
| `"right"` | Vertical bar on the right, extends between header/footer |
| `"top"` | Horizontal bar above content, inside left/right sidebars |
| `"bottom"` | Horizontal bar below content, inside left/right sidebars |
| `"inside"` | Floating overlay in the top-right corner of content |

<details>
<summary><strong>Layout Diagram</strong> — How positions nest together</summary>

When you use multiple toolbars, they are layered from outside in:

```
┌─────────────────────────────────────────────────────────┐
│                      HEADER                             │  ← Full width, outermost
├───────┬─────────────────────────────────────────┬───────┤
│       │                 TOP                     │       │
│       ├─────────────────────────────────────────┤       │
│ LEFT  │                                         │ RIGHT │  ← Extend full height
│       │              CONTENT                    │       │    between header/footer
│       │         ┌─────────────┐                 │       │
│       │         │   INSIDE    │ (overlay)       │       │
│       │         └─────────────┘                 │       │
│       ├─────────────────────────────────────────┤       │
│       │                BOTTOM                   │       │
├───────┴─────────────────────────────────────────┴───────┤
│                      FOOTER                             │  ← Full width, outermost
└─────────────────────────────────────────────────────────┘
```

**Nesting order (outside → inside):**
1. `header` / `footer` — Span full width at very top/bottom
2. `left` / `right` — Extend full height between header and footer
3. `top` / `bottom` — Inside left/right columns, above/below content
4. `inside` — Floating overlay on top of content
5. Content — Your actual HTML/chart/grid

</details>

<details>
<summary><strong>Multi-Toolbar Example</strong></summary>

```python
from pywry import PyWry, Toolbar, Button, Select, Toggle

app = PyWry()

# Header: App-wide navigation
header = Toolbar(
    position="header",
    items=[
        Button(label="Home", event="nav:home"),
        Button(label="Settings", event="nav:settings", style="margin-left: auto;"),
    ],
)

# Left sidebar: View controls
sidebar = Toolbar(
    position="left",
    items=[
        Button(label="📊", event="view:chart", variant="icon"),
        Button(label="📋", event="view:table", variant="icon"),
        Button(label="🗺️", event="view:map", variant="icon"),
    ],
)

# Top: Context-specific controls
top_bar = Toolbar(
    position="top",
    items=[
        Select(label="Period:", event="filter:period", options=["1D", "1W", "1M", "1Y"]),
        Toggle(label="Live:", event="data:live", value=True),
    ],
)

# Inside: Quick actions overlay
overlay = Toolbar(
    position="inside",
    items=[
        Button(label="⟳", event="data:refresh", variant="icon"),
    ],
)

# Footer: Status bar
footer = Toolbar(
    position="footer",
    items=[
        Button(label="Last updated: 12:34:56", event="status:info", variant="ghost", disabled=True),
    ],
)

app.show(
    "<h1>Dashboard</h1>",
    toolbars=[header, sidebar, top_bar, overlay, footer],
    callbacks={...},
)
```

</details>

### Common Properties

All toolbar items share these properties:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `event` | `str` | `"toolbar:input"` | Event name in `namespace:event-name` format |
| `component_id` | `str` | auto-generated | Unique ID (format: `{type}-{uuid8}`, e.g., `button-a1b2c3d4`) |
| `label` | `str` | `""` | Label text displayed next to the control |
| `description` | `str` | `""` | Tooltip text shown on hover |
| `disabled` | `bool` | `False` | Whether the control is disabled |
| `style` | `str` | `""` | Inline CSS styles |

---

### Component Reference

<details>
<summary><strong>Button</strong> — Clickable button with optional data payload</summary>

```python
Button(
    label="Export",
    event="app:export",
    data={"format": "csv"},     # Optional payload merged into event data
    variant="primary",          # Style: primary|secondary|neutral|ghost|outline|danger|warning|icon
    size=None,                  # Size: None|xs|sm|lg|xl
)
```

**Emits:** `{ componentId, ...data }` — The `data` dict merged with `componentId`.

**Variants:**
- `"primary"` — Theme-aware (light bg in dark mode, accent in light mode)
- `"secondary"` — Subtle background, theme-aware
- `"neutral"` — Always blue accent (for primary actions)
- `"ghost"` — Transparent background
- `"outline"` — Bordered, transparent fill
- `"danger"` — Red accent for destructive actions
- `"warning"` — Orange accent for caution
- `"icon"` — Square aspect ratio for icon-only buttons

</details>

<details>
<summary><strong>Select</strong> — Single-select dropdown</summary>

```python
Select(
    label="Theme:",
    event="theme:change",
    options=[
        Option(label="Dark", value="dark"),
        Option(label="Light", value="light"),
    ],
    selected="dark",
)

# Shorthand: strings auto-convert to Option(label=s, value=s)
Select(event="view:change", options=["Table", "Chart", "Map"], selected="Table")
```

**Emits:** `{ value: str, componentId: str }`

</details>

<details>
<summary><strong>MultiSelect</strong> — Multi-select dropdown with checkboxes</summary>

```python
MultiSelect(
    label="Columns:",
    event="columns:filter",
    options=["Name", "Age", "City", "Country"],
    selected=["Name", "Age"],   # Initially selected values
)
```

Features a search box and "All" / "None" quick-select buttons. Selected items appear at the top.

**Emits:** `{ values: [str, ...], componentId: str }`

</details>

<details>
<summary><strong>TextInput</strong> — Text input with debounce</summary>

```python
TextInput(
    label="Search:",
    event="search:query",
    value="",                   # Initial value
    placeholder="Type...",      # Placeholder text
    debounce=300,               # Delay in ms before emitting (default: 300)
)
```

**Emits:** `{ value: str, componentId: str }` after debounce delay.

</details>

<details>
<summary><strong>NumberInput</strong> — Numeric input with constraints</summary>

```python
NumberInput(
    label="Limit:",
    event="filter:limit",
    value=10,
    min=1,
    max=100,
    step=1,
)
```

Includes up/down spinner buttons.

**Emits:** `{ value: number, componentId: str }`

</details>

<details>
<summary><strong>DateInput</strong> — Date picker</summary>

```python
DateInput(
    label="Start Date:",
    event="filter:date",
    value="2025-01-01",         # YYYY-MM-DD format
    min="2020-01-01",           # Optional minimum
    max="2030-12-31",           # Optional maximum
)
```

**Emits:** `{ value: "YYYY-MM-DD", componentId: str }`

</details>

<details>
<summary><strong>SliderInput</strong> — Single-value slider</summary>

```python
SliderInput(
    label="Zoom:",
    event="zoom:level",
    value=50,
    min=0,
    max=100,
    step=5,
    show_value=True,            # Display current value (default: True)
    debounce=50,                # Delay in ms (default: 50)
)
```

**Emits:** `{ value: number, componentId: str }`

</details>

<details>
<summary><strong>RangeInput</strong> — Dual-handle range slider</summary>

```python
RangeInput(
    label="Price Range:",
    event="filter:price",
    start=100,                  # Initial start value
    end=500,                    # Initial end value
    min=0,
    max=1000,
    step=10,
    show_value=True,            # Display start/end values
    debounce=50,
)
```

Two handles on a single track for selecting a value range.

**Emits:** `{ start: number, end: number, componentId: str }`

</details>

<details>
<summary><strong>Toggle</strong> — Boolean switch</summary>

```python
Toggle(
    label="Dark Mode:",
    event="theme:toggle",
    value=True,                 # Initial state (default: False)
)
```

A sliding on/off switch.

**Emits:** `{ value: bool, componentId: str }`

</details>

<details>
<summary><strong>Checkbox</strong> — Boolean checkbox</summary>

```python
Checkbox(
    label="Enable notifications",
    event="settings:notify",
    value=True,                 # Initial checked state
)
```

A standard checkbox with label.

**Emits:** `{ value: bool, componentId: str }`

</details>

<details>
<summary><strong>RadioGroup</strong> — Radio button group</summary>

```python
RadioGroup(
    label="View:",
    event="view:change",
    options=["List", "Grid", "Cards"],
    selected="List",
    direction="horizontal",     # horizontal|vertical (default: horizontal)
)
```

Mutually exclusive radio buttons.

**Emits:** `{ value: str, componentId: str }`

</details>

<details>
<summary><strong>TabGroup</strong> — Tab-style selection</summary>

```python
TabGroup(
    label="View:",
    event="view:change",
    options=[
        Option(label="Table", value="table"),
        Option(label="Chart", value="chart"),
        Option(label="Map", value="map"),
    ],
    selected="table",
    size="md",                  # sm|md|lg (default: md)
)
```

Similar to RadioGroup but styled as tabs. Ideal for view switching.

**Emits:** `{ value: str, componentId: str }`

</details>

<details>
<summary><strong>Div</strong> — Container for custom HTML and nested items</summary>

```python
Div(
    content="<h3>Controls</h3>",          # Custom HTML
    class_name="my-controls",             # CSS class (added to pywry-div)
    children=[                            # Nested toolbar items
        Button(label="Action", event="app:action"),
        Div(content="<span>Nested</span>"),
    ],
    script="console.log('Div loaded');",  # JS file path or inline script
)
```

Container for grouping items or injecting custom HTML. Supports unlimited nesting.

**Emits:** No automatic events (children emit their own events).

</details>

<details>
<summary><strong>Option</strong> — Choice for Select/MultiSelect/RadioGroup/TabGroup</summary>

```python
Option(
    label="Display Text",       # Text shown in UI
    value="internal_value",     # Value sent in event (defaults to label)
)

# Shorthand: strings auto-convert
options=["A", "B", "C"]  # → [Option(label="A", value="A"), ...]
```

</details>

---

### Toolbar Container

```python
Toolbar(
    position="top",                     # top|bottom|left|right|inside
    items=[...],                        # List of toolbar items
    component_id="my-toolbar",          # Optional custom ID (auto-generated if omitted)
    class_name="my-toolbar-class",      # Custom CSS class
    style="gap: 12px;",                 # Inline CSS for the content wrapper
    collapsible=False,                  # Enable collapse/expand toggle button
    resizable=False,                    # Enable drag-to-resize edge handle
    script="console.log('loaded');",    # JS file path or inline script
)
```

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `position` | `str` | `"top"` | Toolbar placement |
| `items` | `list` | `[]` | List of toolbar items |
| `component_id` | `str` | `"toolbar-{uuid8}"` | Unique toolbar ID |
| `class_name` | `str` | `""` | Additional CSS class |
| `style` | `str` | `""` | Inline CSS for content area |
| `collapsible` | `bool` | `False` | Show collapse/expand toggle |
| `resizable` | `bool` | `False` | Enable drag-to-resize |
| `script` | `str\|Path` | `None` | Custom JavaScript to inject |

---

### Examples

<details>
<summary><strong>Complete Example with Multiple Components</strong></summary>

```python
from pywry import PyWry, Toolbar, Button, Select, TextInput, Toggle, Option

app = PyWry()

def on_save(data, event_type, label):
    app.eval_js("document.getElementById('status').textContent = 'Saved!'", label)

def on_export(data, event_type, label):
    app.eval_js("document.getElementById('status').textContent = 'Exported!'", label)

def on_theme(data, event_type, label):
    is_dark = data["value"]
    app.eval_js(f"document.documentElement.classList.toggle('light', {str(not is_dark).lower()})", label)

def on_search(data, event_type, label):
    app.eval_js(f"document.getElementById('status').textContent = 'Searching: {data['value']}'", label)

toolbar = Toolbar(
    position="top",
    items=[
        Button(label="Save", event="app:save"),
        Button(label="Export", event="app:export", variant="secondary"),
        Select(
            label="View:",
            event="view:change",
            options=["Table", "Chart"],
            selected="Table",
        ),
        TextInput(label="Search:", event="search:query", placeholder="Type..."),
        Toggle(label="Dark:", event="theme:toggle", value=True, style="margin-left: auto;"),
    ],
)

app.show(
    "<h1>My App</h1><p id='status'>Ready</p>",
    toolbars=[toolbar],
    callbacks={
        "app:save": on_save,
        "app:export": on_export,
        "theme:toggle": on_theme,
        "search:query": on_search,
    },
)
```

</details>

<details>
<summary><strong>Styling Buttons</strong></summary>

```python
from pywry import PyWry, HtmlContent, Toolbar, Button

content = HtmlContent(
    html="<h1>Styled Buttons</h1>",
    inline_css="""
        .pywry-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            padding: 8px 20px;
        }
        .pywry-btn:hover { transform: scale(1.05); }
        .pywry-toolbar { justify-content: center; gap: 12px; }
    """
)

toolbar = Toolbar(
    position="top",
    items=[
        Button(label="Primary", event="app:primary"),
        Button(label="Secondary", event="app:secondary", variant="secondary"),
        Button(label="Danger", event="app:danger", variant="danger"),
    ],
)

app.show(content, toolbars=[toolbar])
```

</details>

<details>
<summary><strong>Toolbar with Plotly/AgGrid</strong></summary>

```python
from pywry import PyWry, Toolbar, Button

app = PyWry()

# Plotly with toolbar
def on_reset(data, event_type, label):
    app.eval_js(
        "Plotly.relayout(window.__PYWRY_PLOTLY_DIV__, "
        "{xaxis: {autorange: true}, yaxis: {autorange: true}})"
    )

toolbar = Toolbar(
    position="bottom",
    items=[Button(label="Reset Zoom", event="app:reset")],
)

app.show_plotly(fig, toolbars=[toolbar], callbacks={"app:reset": on_reset})

# AgGrid with toolbar
def on_export(data, event_type, label):
    app.eval_js("window.__PYWRY_GRID_API__.exportDataAsCsv()")

toolbar = Toolbar(
    position="top",
    items=[Button(label="Export CSV", event="app:export")],
)

app.show_dataframe(df, toolbars=[toolbar], callbacks={"app:export": on_export})
```

</details>
 
<details>
<summary><strong>All Toolbar Inputs - No Javascript Required</strong></summary>

```python
from pywry import (
    PyWry,
    Toolbar,
    Button,
    Select,
    MultiSelect,
    TextInput,
    NumberInput,
    SliderInput,
    DateInput,
    RangeInput,
    Toggle,
    Checkbox,
    RadioGroup,
    TabGroup,
    Option,
    Div,
)


app = PyWry()

# State to display current values
component_values = {}
current_theme = "dark"  # Track current theme

def make_handler(name):
    """Create a handler that updates the display with the component's value."""
    def handler(data, event_type, label):
        # Extract the relevant value(s) from the event data
        if "value" in data:
            component_values[name] = data["value"]
        elif "values" in data:
            component_values[name] = data["values"]
        elif "start" in data and "end" in data:
            component_values[name] = f"{data['start']} - {data['end']}"
        elif "btn" in data:
            component_values[name] = data["btn"]
        else:
            component_values[name] = "clicked"
        
        # Build display text for footer using built-in pywry:set-content
        parts = [f"<strong>{k}:</strong> {v}" for k, v in component_values.items()]
        components_widget.emit("pywry:set-content", {
            "id": "values-display",
            "html": " | ".join(parts)
        })
    return handler

def on_theme_toggle(data, event_type, label):
    """Toggle between dark and light mode using built-in pywry event."""
    global current_theme
    current_theme = "light" if current_theme == "dark" else "dark"
    components_widget.emit("pywry:update-theme", {"theme": current_theme})

def on_title_size(data, event_type, label):
    """Change the title size using built-in pywry:set-style event."""
    sizes = {"sm": "16px", "md": "20px", "lg": "26px"}
    size = data.get("value", "md")
    # Use built-in pywry:set-style event to update element styles
    components_widget.emit("pywry:set-style", {
        "id": "demo-title",
        "styles": {"fontSize": sizes.get(size, "20px")}
    })

def on_label_style(data, event_type, label):
    """Change all component label styles using built-in pywry:set-style event."""
    style_map = {
        "normal": {"fontWeight": "400", "fontStyle": "normal"},
        "semi": {"fontWeight": "500", "fontStyle": "normal"},
        "bold": {"fontWeight": "700", "fontStyle": "normal"},
        "italic": {"fontWeight": "400", "fontStyle": "italic"},
    }
    style = data.get("value", "normal")
    # Use built-in pywry:set-style event to update all labels
    components_widget.emit("pywry:set-style", {
        "selector": ".pywry-input-label",
        "styles": style_map.get(style, style_map["normal"])
    })

def on_accent_color(data, event_type, label):
    """Change the accent color using built-in pywry:inject-css event."""
    colors = {
        "blue": "#0078d4",
        "green": "#28a745",
        "purple": "#6f42c1",
        "orange": "#fd7e14",
        "pink": "#e91e63",
    }
    color = data.get("value", "blue")
    accent = colors.get(color, colors["blue"])
    
    # Use built-in pywry:inject-css to dynamically inject CSS
    # The 'id' allows replacing the same style block on subsequent calls
    components_widget.emit("pywry:inject-css", {
        "id": "custom-accent-color",
        "css": f"""
            :root {{
                --pywry-accent: {accent} !important;
                --pywry-accent-hover: {accent}dd !important;
            }}
            .pywry-btn-neutral {{
                background: {accent} !important;
            }}
            .pywry-btn-neutral:hover {{
                background: {accent}dd !important;
            }}
        """
    })

# Header toolbar with title and theme toggle
components_header = Toolbar(
    position="header",
    items=[
        Div(
            content="<h3 id='demo-title' style='margin: 0;'>🧩 All Toolbar Components</h3>",
            style="flex: 1;",
        ),
        Select(
            label="Accent:",
            event="demo:accent",
            options=[
                Option(label="Blue", value="blue"),
                Option(label="Green", value="green"),
                Option(label="Purple", value="purple"),
                Option(label="Orange", value="orange"),
                Option(label="Pink", value="pink"),
            ],
            selected="blue",
        ),
        Select(
            label="Title:",
            event="demo:title_size",
            options=[Option(label="SM", value="sm"), Option(label="MD", value="md"), Option(label="LG", value="lg")],
            selected="md",
        ),
        Select(
            label="Labels:",
            event="demo:label_style",
            options=[Option(label="Normal", value="normal"), Option(label="Semi", value="semi"), Option(label="Bold", value="bold"), Option(label="Italic", value="italic")],
            selected="normal",
        ),
        Button(label="☀️", event="demo:theme", variant="ghost", component_id="theme-toggle-btn"),
    ],
)

# Top toolbar with text, number, and date inputs
inputs_row = Toolbar(
    position="top",
    items=[
        TextInput(
            label="Text:",
            event="demo:text",
            value="Hello",
            placeholder="Type here...",
        ),
        NumberInput(
            label="Number:",
            event="demo:number",
            value=42,
            min=0,
            max=100,
            step=1,
        ),
        DateInput(
            label="Date:",
            event="demo:date",
            value="2026-01-13",
        ),
    ],
)

# Second row with select, multi-select
selects_row = Toolbar(
    position="top",
    items=[
        Select(
            label="Select:",
            event="demo:select",
            options=[
                Option(label="Option A", value="a"),
                Option(label="Option B", value="b"),
                Option(label="Option C", value="c"),
            ],
            selected="a",
        ),
        MultiSelect(
            label="Multi:",
            event="demo:multi",
            options=[
                Option(label="Red", value="red"),
                Option(label="Green", value="green"),
                Option(label="Blue", value="blue"),
            ],
            selected=["red"],
        ),
    ],
)

# Third row with sliders and range
sliders_row = Toolbar(
    position="top",
    items=[
        SliderInput(
            label="Slider:",
            event="demo:slider",
            value=50,
            min=0,
            max=100,
            step=5,
            show_value=True,
        ),
        RangeInput(
            label="Range:",
            event="demo:range",
            min=0,
            max=100,
            start=20,
            end=80,
            show_value=True,
        ),
    ],
)

# Fourth row with toggle, checkbox, and horizontal radio
booleans_row = Toolbar(
    position="top",
    items=[
        Toggle(label="Toggle:", event="demo:toggle", value=True),
        Div(content="<span class='pywry-input-label'>Check:</span>", style="margin-right: 4px;"),
        Checkbox(label="", event="demo:checkbox", value=False),
        RadioGroup(
            label="Radio:",
            event="demo:radio",
            options=[Option(label="A", value="a"), Option(label="B", value="b"), Option(label="C", value="c")],
            selected="a",
            direction="horizontal",
        ),
    ],
)

# Fifth row with TabGroups
tabs_row = Toolbar(
    position="top",
    items=[
        TabGroup(
            label="View:",
            event="demo:tabs",
            options=[
                Option(label="Table", value="table"),
                Option(label="Chart", value="chart"),
                Option(label="Map", value="map"),
            ],
            selected="table",
        ),
        TabGroup(
            label="Size:",
            event="demo:tabsize",
            options=["SM", "MD", "LG"],
            selected="MD",
            size="sm",
        ),
    ],
)

# Right sidebar with vertical radio group
right_sidebar = Toolbar(
    position="right",
    style="padding: 8px 12px;",
    items=[
        Div(content="<span class='pywry-input-label'>Priority</span>", style="margin-bottom: 4px;"),
        RadioGroup(
            event="demo:priority",
            options=[
                Option(label="Low", value="low"),
                Option(label="Medium", value="med"),
                Option(label="High", value="high"),
            ],
            selected="med",
            direction="vertical",
        ),
    ],
    collapsible=True,
)

# Bottom toolbar with buttons (all variants)
buttons_row = Toolbar(
    position="top",
    items=[
        Div(content="<span class='pywry-input-label'>Variants:</span>", style="margin-right: 4px;"),
        Button(label="Primary", event="demo:btn", data={"btn": "primary"}, variant="primary"),
        Button(label="Secondary", event="demo:btn", data={"btn": "secondary"}, variant="secondary"),
        Button(label="Neutral", event="demo:btn", data={"btn": "neutral"}, variant="neutral"),
        Button(label="Ghost", event="demo:btn", data={"btn": "ghost"}, variant="ghost"),
        Button(label="Outline", event="demo:btn", data={"btn": "outline"}, variant="outline"),
        Button(label="Danger", event="demo:btn", data={"btn": "danger"}, variant="danger"),
        Button(label="Warning", event="demo:btn", data={"btn": "warning"}, variant="warning"),
        Button(label="⚙", event="demo:btn", data={"btn": "icon"}, variant="icon"),
    ],
)

# Size variants row
sizes_row = Toolbar(
    position="top",
    items=[
        Div(content="<span class='pywry-input-label'>Sizes</span>", style="margin-right: 4px;"),
        Button(label="XS", event="demo:btn", data={"btn": "xs"}, variant="neutral", size="xs"),
        Button(label="SM", event="demo:btn", data={"btn": "sm"}, variant="neutral", size="sm"),
        Button(label="Default", event="demo:btn", data={"btn": "default"}, variant="neutral"),
        Button(label="LG", event="demo:btn", data={"btn": "lg"}, variant="neutral", size="lg"),
        Button(label="XL", event="demo:btn", data={"btn": "xl"}, variant="neutral", size="xl"),
    ],
)

# Footer with live status display
components_footer = Toolbar(
    position="footer",
    items=[
        Div(
            content="<span id='values-display'><em>Interact with components above...</em></span>",
            style="color: var(--pywry-text-secondary); width: 100%; text-align: center;",
        ),
    ],
)

# No custom HTML or custom JS needed - all interactions use built-in pywry events!
components_html = ""

components_widget = app.show(
    components_html,
    title="All Components Demo",
    toolbars=[
        components_header,
        inputs_row,
        selects_row,
        sliders_row,
        booleans_row,
        tabs_row,
        buttons_row,
        sizes_row,
        right_sidebar,
        components_footer,
    ],
    callbacks={
        "demo:text": make_handler("Text"),
        "demo:number": make_handler("Number"),
        "demo:date": make_handler("Date"),
        "demo:select": make_handler("Select"),
        "demo:multi": make_handler("Multi"),
        "demo:slider": make_handler("Slider"),
        "demo:range": make_handler("Range"),
        "demo:toggle": make_handler("Toggle"),
        "demo:checkbox": make_handler("Checkbox"),
        "demo:radio": make_handler("Radio"),
        "demo:tabs": make_handler("Tabs"),
        "demo:tabsize": make_handler("TabSize"),
        "demo:priority": make_handler("Priority"),
        "demo:btn": make_handler("Button"),
        "demo:theme": on_theme_toggle,
        "demo:title_size": on_title_size,
        "demo:label_style": on_label_style,
        "demo:accent": on_accent_color,
    },
    height=375
)
```

</details>

---

### State Management

<details>
<summary><strong>Querying Toolbar State</strong></summary>

```python
# Notebook widgets
def on_state(data, event_type, label):
    print(f"Toolbars: {data['toolbars']}")
    print(f"Components: {data['components']}")

widget.on("toolbar:state-response", on_state)
widget.request_toolbar_state()

# Query specific toolbar
widget.request_toolbar_state(toolbar_id="my-toolbar")

# Native windows (via runtime)
from pywry import runtime
runtime.emit_event("window-label", "toolbar:request-state", {})
```

**Response payload:**
```python
{
    "toolbars": {"toolbar-a1b2c3d4": {"position": "top", "components": ["button-x1y2z3", ...]}},
    "components": {"button-x1y2z3": {"type": "button", "value": None}, ...},
    "timestamp": 1234567890
}
```

</details>

<details>
<summary><strong>Setting Toolbar Values</strong></summary>

```python
# Notebook widgets
widget.set_toolbar_value("select-a1b2c3d4", "dark")
widget.set_toolbar_value("multiselect-x1y2z3", ["name", "age"])

# Set multiple at once
widget.set_toolbar_values({
    "select-a1b2c3d4": "dark",
    "number-b2c3d4e5": 50,
})

# Native windows (via runtime)
from pywry import runtime

runtime.emit_event("window-label", "toolbar:set-value", {
    "componentId": "select-a1b2c3d4",
    "value": "dark"
})

runtime.emit_event("window-label", "toolbar:set-values", {
    "values": {"select-a1b2c3d4": "dark", "number-b2c3d4e5": 50}
})
```

</details>

<details>
<summary><strong>JavaScript Access</strong></summary>

```javascript
// Get all toolbar state
const state = window.__PYWRY_TOOLBAR__.getState();

// Get specific toolbar state
const state = window.__PYWRY_TOOLBAR__.getState("toolbar-a1b2c3d4");

// Get/set individual component value
const value = window.__PYWRY_TOOLBAR__.getValue("select-a1b2c3d4");
window.__PYWRY_TOOLBAR__.setValue("select-a1b2c3d4", "light");
```

</details>

</details>

---

## JavaScript Bridge

<details>
<summary>Click to expand</summary>

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

// AgGrid API (when include_aggrid=True)
window.__PYWRY_GRID_API__  // AgGrid API for programmatic control

// Bundled Plotly templates (when include_plotly=True)
window.PYWRY_PLOTLY_TEMPLATES  // Object with all Plotly templates
```

### Accessing AgGrid API

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

### Built-in System Event Handlers

PyWry pre-registers handlers for common UI manipulation events. These are handled automatically by the JavaScript bridge — **you don't need to write any JavaScript to use them**:

```python
# Theme switching (updates Plotly templates, AgGrid themes, and CSS classes)
widget.emit("pywry:update-theme", {"theme": "plotly_white"})

# Inject CSS dynamically (with optional id for replacement)
widget.emit("pywry:inject-css", {"css": ".status { color: green; }", "id": "status-css"})

# Update element styles by id or CSS selector
widget.emit("pywry:set-style", {"id": "counter", "styles": {"fontSize": "24px", "fontWeight": "bold"}})
widget.emit("pywry:set-style", {"selector": ".highlight", "styles": {"backgroundColor": "yellow"}})

# Update element content by id or CSS selector
widget.emit("pywry:set-content", {"id": "message", "html": "<strong>Success!</strong>"})
widget.emit("pywry:set-content", {"selector": ".count", "text": "42"})

# Trigger file download (IFrame/browser mode only)
widget.emit("pywry:download", {"content": "CSV data...", "filename": "data.csv", "mimeType": "text/csv"})
```

See [Utility Events (Python → JS)](#utility-events-python--js) for complete documentation.

</details>

---

## Direct Tauri API Access

<details>
<summary>Click to expand</summary>

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

### Listening to Python Events (JavaScript)

Use `window.pywry.on()` to receive events sent from Python:

```javascript
// Listen for custom events from Python
window.pywry.on('app:data-update', function(data) {
    console.log('Received data:', data);
    updateUI(data);
});

// Wildcard listener for debugging
window.pywry.on('*', function(payload) {
    console.log('Event:', payload.type, payload.data);
});
```

### Tauri Internal Events (Advanced)

> **Warning:** These are low-level internal events used by PyWry's core. Most users should use the `window.pywry` bridge instead.

For advanced use cases, you can listen to raw Tauri IPC events:

```javascript
// Only works in desktop mode (not notebooks)
if (window.__TAURI__) {
    // Listen for cleanup signal before window closes
    window.__TAURI__.event.listen('pywry:cleanup', function() {
        console.log('Window closing, save state...');
    });
}
```

| Internal Event | Payload | Description |
|----------------|---------|-------------|
| `pywry:content` | `{ html, theme }` | Set window HTML content |
| `pywry:eval` | `{ script }` | Execute JavaScript in window |
| `pywry:event` | `{ type, data }` | Wrapper for Python → JS events |
| `pywry:init` | `{ label }` | Window initialization |
| `pywry:cleanup` | None | Window about to close |
| `pywry:inject-css` | `{ id, css }` | Inject CSS dynamically |
| `pywry:remove-css` | `{ id }` | Remove injected CSS |
| `pywry:refresh` | None | Refresh window content |

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

</details>

---

## Managing Multiple Windows/Widgets

<details>
<summary>Click to expand</summary>

PyWry can display content in multiple ways, and each has its own management model. This section explains how to create, control, and clean up your display contexts.

### What is a Window vs. a Widget?

| Term | What It Is | When You Get It |
|------|------------|-----------------|
| **Window** | A native desktop window (Tauri/WRY) | `WindowMode.NEW_WINDOW`, `SINGLE_WINDOW`, `MULTI_WINDOW` |
| **Widget** | An embedded display in a notebook cell or browser tab | `WindowMode.NOTEBOOK`, `BROWSER` |

Both **windows** and **widgets** display the same content (HTML, Plotly charts, AgGrid tables). The difference is where and how they appear to the user.

### WindowMode Options

When you create a `PyWry` instance, you choose a mode:

```python
from pywry import PyWry, WindowMode

# Choose your mode
app = PyWry(mode=WindowMode.MULTI_WINDOW)
```

| Mode | Behavior | Use Case |
|------|----------|----------|
| `NEW_WINDOW` | Each `show_*()` opens a fresh native window | Simple scripts, one-off displays |
| `SINGLE_WINDOW` | Reuses the same window, replaces content | Dashboard with tab-like navigation |
| `MULTI_WINDOW` | Each `show_*()` opens a new window, all stay open | Multi-monitor setups, side-by-side views |
| `NOTEBOOK` | Renders inline in Jupyter/VS Code notebooks | Interactive data exploration |
| `BROWSER` | Renders via URL in system browser | Server/headless mode, remote access |

> **Auto-Detection:** If you don't specify a mode, PyWry detects your environment:
> - Jupyter notebook detected → `NOTEBOOK`
> - No display available (headless) → `BROWSER`
> - Otherwise → `NEW_WINDOW`

### Return Types by Mode

The `show_*()` methods return different types depending on the mode:

| Mode | `show_*()` Returns | Control Via |
|------|-------------------|-------------|
| `NEW_WINDOW`, `SINGLE_WINDOW`, `MULTI_WINDOW` | `str` (label) | `app.emit(label, ...)`, `app.close(label)`, etc. |
| `NOTEBOOK`, `BROWSER` | `BaseWidget` object | `widget.emit(...)`, `widget.on(...)`, `widget.update(...)` |

**The return value is your handle** — save it to interact with that window/widget later.

---

### Native Window Management

In native modes, `show_*()` returns a **label** (string) that identifies the window:

```python
from pywry import PyWry, WindowMode

app = PyWry(mode=WindowMode.MULTI_WINDOW)

# Each show_*() returns a unique label
label1 = app.show_plotly(fig1, title="Chart 1")  # "pywry-a1b2c3"
label2 = app.show_dataframe(df, title="Data")     # "pywry-d4e5f6"
label3 = app.show("<h1>Custom</h1>", title="Custom")  # "pywry-g7h8i9"

print(label1)  # "pywry-a1b2c3"
```

#### Querying Windows

```python
# Get all active window labels
labels = app.get_labels()  # ["pywry-a1b2c3", "pywry-d4e5f6", "pywry-g7h8i9"]

# Check if a specific window is still open
if app.is_open(label1):
    print(f"Window {label1} is still open")

# Check if ANY window is open
if app.is_open():
    print("At least one window is open")
```

#### Controlling Windows

```python
# Send an event to a specific window
app.emit("app:update", {"message": "Hello!"}, label=label1)

# Refresh a specific window (full page reload)
app.refresh(label1)

# Close a specific window
app.close(label1)

# Close ALL windows
app.close()  # No label = close all
```

---

### Widget Management (Notebook/Browser)

In notebook or browser mode, `show_*()` returns a **widget object** with methods for control:

```python
from pywry import PyWry, WindowMode

app = PyWry(mode=WindowMode.NOTEBOOK)

# show_*() returns a widget object (not a string)
widget = app.show_plotly(fig, title="Interactive Chart")

# The widget has a label property for identification
print(widget.label)  # "w-abc12345"
```

#### Widget Properties

| Property | Type | Description |
|----------|------|-------------|
| `widget.label` | `str` | Unique identifier (e.g., `"w-abc12345"`) |
| `widget.url` | `str` | Full URL to access in a browser (e.g., `"http://localhost:8765/widget/w-abc12345"`) |
| `widget.output` | `Output` | IPython Output widget for callback print statements |

#### Registering Event Handlers

```python
# Register handlers — method chaining supported
widget.on("plotly:click", lambda data, ev, lbl: print(f"Clicked: {data}"))
widget.on("custom:action", handle_action)

# Chaining
widget.on("plotly:click", on_click).on("plotly:hover", on_hover)
```

#### Sending Events to JavaScript

```python
# Send an event that JavaScript can listen for
widget.emit("app:refresh", {"data": new_data})
```

#### Updating Content

```python
# Replace the widget's HTML content
widget.update("<h1>New content</h1>")

# For Plotly widgets: update the figure
widget.update_figure(new_fig)

# For AgGrid widgets: update the data
widget.update_data(new_rows)
```

#### Display Methods

```python
# Display in notebook (usually automatic)
widget.display()

# Open the widget's URL in system browser (useful for BROWSER mode)
widget.open_in_browser()
```

---

### Storing References for Later Control

Save the return values to control windows/widgets later:

```python
from pywry import PyWry, WindowMode

app = PyWry(mode=WindowMode.MULTI_WINDOW)

# Store references in a dict for easy access
windows = {}
windows["main"] = app.show_plotly(fig, title="Main Chart")
windows["sidebar"] = app.show_dataframe(df, title="Data Panel")

# Later: send events to specific windows
def refresh_main():
    app.emit("plotly:update-figure", {"figure": new_fig_dict}, label=windows["main"])

def close_sidebar():
    app.close(windows["sidebar"])
    del windows["sidebar"]
```

---

### Non-Blocking Scripts with `block()`

In BROWSER mode (scripts, not notebooks), windows open but the script continues immediately. Use `block()` to wait for users to close all windows:

```python
from pywry import PyWry, WindowMode
from pywry.inline import block

app = PyWry(mode=WindowMode.BROWSER)
widget = app.show_plotly(fig, title="Dashboard")
widget.open_in_browser()  # Opens in default browser

# Script continues immediately — window is open in browser

# Do other work while user interacts with the chart
print("Chart is open, doing other work...")

# When ready, block until all browser tabs are closed
block()  # Waits for all widgets to disconnect
print("All windows closed, exiting")
```

---

### Graceful Shutdown with `stop_server()`

For clean shutdown in long-running processes (web servers, daemons):

```python
from pywry import PyWry, WindowMode
from pywry.inline import block, stop_server
import signal

app = PyWry(mode=WindowMode.BROWSER)

def cleanup(signum, frame):
    print("Shutting down...")
    app.close()      # Close all windows
    stop_server()    # Stop the inline server, release port
    exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

# Show windows
widget1 = app.show_plotly(fig1)
widget2 = app.show_plotly(fig2)
widget1.open_in_browser()
widget2.open_in_browser()

# Keep running until interrupted
block()
```

---

### Summary: PyWry Instance Methods

Methods available on the `PyWry` app instance:

| Method | Description |
|--------|-------------|
| `app.show(html, ...)` | Show HTML content, returns label or widget |
| `app.show_plotly(fig, ...)` | Show Plotly figure, returns label or widget |
| `app.show_dataframe(df, ...)` | Show DataFrame as AgGrid, returns label or widget |
| `app.get_labels()` | Get list of all active window labels |
| `app.is_open(label=None)` | Check if window(s) are open |
| `app.emit(event, data, label=None)` | Send event to window(s) |
| `app.close(label=None)` | Close specific or all windows |
| `app.refresh(label=None)` | Refresh specific or all windows |
| `app.refresh_css(label=None)` | Hot-reload CSS without page refresh |
| `app.on(event, handler)` | Register global event handler |
| `app.on_chart(event, handler)` | Register Plotly event handler (convenience) |
| `app.on_grid(event, handler)` | Register AgGrid event handler (convenience) |
| `app.on_toolbar(event, handler)` | Register toolbar event handler (convenience) |
| `app.on_html(event, handler)` | Register HTML element event handler (convenience) |
| `app.on_window(event, handler)` | Register window lifecycle event handler (convenience) |
| `app.eval_js(script, label)` | Execute JavaScript in a window |

### Summary: Widget Methods (Notebook/Browser)

Methods available on widget objects returned by `show_*()` in NOTEBOOK/BROWSER modes:

| Property/Method | Description |
|-----------------|-------------|
| `widget.label` | Unique identifier for this widget |
| `widget.url` | Full URL to access this widget in a browser |
| `widget.output` | IPython Output widget for callback prints |
| `widget.on(event, handler)` | Register event handler (chainable) |
| `widget.emit(event, data)` | Send event to JavaScript |
| `widget.update(html)` | Replace widget HTML content |
| `widget.display()` | Display widget in notebook cell |
| `widget.open_in_browser()` | Open widget URL in system browser |

**Plotly-specific widget methods:**

| Method | Description |
|--------|-------------|
| `widget.update_figure(fig)` | Update the Plotly figure |
| `widget.reset_zoom()` | Reset chart zoom to auto-range |
| `widget.set_zoom(x_range, y_range)` | Set chart zoom to specific range |

**AgGrid-specific widget methods:**

| Method | Description |
|--------|-------------|
| `widget.update_data(rows)` | Replace grid data |
| `widget.update_columns(col_defs)` | Replace column definitions |
| `widget.update_cell(row_id, col, value)` | Update a single cell |
| `widget.update_grid(data, columns, state)` | Update multiple aspects at once |
| `widget.request_grid_state()` | Request current grid state (emits `grid:state-response`) |
| `widget.restore_state(state)` | Restore a saved grid state |
| `widget.reset_state()` | Reset grid to default state |

**Toolbar-specific widget methods:**

| Method | Description |
|--------|-------------|
| `widget.request_toolbar_state()` | Request current toolbar state (emits `toolbar:state-response`) |
| `widget.get_toolbar_value(component_id)` | Request a specific component's value |
| `widget.set_toolbar_value(id, value)` | Set a component's value |
| `widget.set_toolbar_values(values)` | Set multiple component values at once |

</details>

---

## Browser Mode & Server Configuration

<details>
<summary>Click to expand</summary>

For headless environments, remote deployments, or when you want to serve dashboards via HTTP, use `BROWSER` mode with the inline FastAPI server.

### Getting the Widget URL

Every widget has a `.url` property that provides the direct HTTP endpoint:

```python
from pywry import PyWry, WindowMode

app = PyWry(mode=WindowMode.BROWSER)

# show_* returns an InlineWidget with a .url property
widget = app.show_plotly(fig, title="Dashboard")

print(widget.url)  # http://127.0.0.1:8765/widget/abc123def456
```

You can share this URL with anyone who can reach the server.

### Server Configuration

Configure the inline server via `pywry.toml`, `pyproject.toml`, or environment variables:

```toml
# pywry.toml or [tool.pywry.server] in pyproject.toml
[server]
host = "0.0.0.0"              # Bind to all interfaces (for remote access)
port = 8080                   # Custom port
auto_start = true             # Auto-start when first widget created
force_notebook = false        # Force notebook mode in headless environments

# Uvicorn settings
workers = 1                   # Worker processes
log_level = "info"            # Uvicorn log level
access_log = true             # Enable access logging
reload = false                # Auto-reload (dev mode)

# Timeouts
timeout_keep_alive = 5        # Keep-alive timeout (seconds)
timeout_graceful_shutdown = 30  # Graceful shutdown timeout

# SSL/TLS for HTTPS
ssl_keyfile = "/path/to/key.pem"
ssl_certfile = "/path/to/cert.pem"
ssl_keyfile_password = "optional-password"
ssl_ca_certs = "/path/to/ca-bundle.crt"

# CORS settings (for cross-origin requests)
cors_origins = ["*"]          # Allowed origins (use specific domains in production)
cors_allow_credentials = true
cors_allow_methods = ["*"]
cors_allow_headers = ["*"]

# Limits
limit_concurrency = 100       # Max concurrent connections
limit_max_requests = 10000    # Max requests before worker restart
backlog = 2048                # Socket backlog size
```

### Environment Variables

Override any server setting with `PYWRY_SERVER__*`:

```bash
# Remote deployment: bind to all interfaces
export PYWRY_SERVER__HOST=0.0.0.0
export PYWRY_SERVER__PORT=8080

# Enable HTTPS
export PYWRY_SERVER__SSL_CERTFILE=/etc/ssl/certs/server.crt
export PYWRY_SERVER__SSL_KEYFILE=/etc/ssl/private/server.key

# Restrict CORS for production
export PYWRY_SERVER__CORS_ORIGINS='["https://myapp.com"]'

# Enable logging
export PYWRY_SERVER__LOG_LEVEL=info
export PYWRY_SERVER__ACCESS_LOG=true
```

### Production Deployment Pattern

For production deployments, create **view factory functions** that generate widgets on demand. Each user request gets a fresh widget instance with a unique ID, while you maintain static, bookmarkable routes.

#### Environment Variables for Production

```bash
# Set this environment variable on your server:
export PYWRY_HEADLESS=1  # Forces InlineWidget, skips browser.open()
```

**What `PYWRY_HEADLESS=1` does:**
- Forces `InlineWidget` (FastAPI/IFrame) instead of `anywidget` - ensuring `.url` and `.label` are always available
- Prevents `open_in_browser()` from being called (which would fail on headless servers)
- No code changes needed - the same API works locally and in production

#### Architecture Overview

```
Static Route          View Factory         Widget Instance
─────────────         ────────────         ────────────────
GET /dashboard   →    create_dashboard()  →  /widget/{unique_id}
GET /analytics   →    create_analytics()  →  /widget/{unique_id}
GET /sales       →    create_sales()      →  /widget/{unique_id}
```

**How it works:**

1. `pywry.inline.show_plotly()` creates an `InlineWidget` and **immediately** registers it in `_state.widgets`
2. The server reads from `_state.widgets` when serving `/widget/{id}`
3. The redirect happens **after** the widget is registered, so it's always available

> **Important:** Set `PYWRY_HEADLESS=1` on your production server. This ensures the same code works both locally (opens browser) and on servers (no browser, just widget registration).

> **Note:** Call `_start_server()` at module load time (not inside route handlers) to avoid a startup delay on the first request.

#### Complete Production Example

```python
# app.py - Production PyWry server with static routes
from fastapi import Request
from fastapi.responses import RedirectResponse
from pywry.inline import (
    _state, 
    _start_server,
    show,              # For HTML content
    show_plotly,       # For Plotly figures  
    show_dataframe,    # For DataFrames/AgGrid
)
import plotly.express as px
import pandas as pd

# Start the server at module load time (before defining routes)
_start_server()

# Get PyWry's FastAPI app and add custom routes
app = _state.app

# ═══════════════════════════════════════════════════════════
# VIEW FACTORIES - Each creates a fresh widget for each request
# open_browser=True forces InlineWidget (required for server deployments)
# With PYWRY_HEADLESS=1, browser.open() is automatically skipped
# ═══════════════════════════════════════════════════════════

def create_sales_dashboard(user_id: str | None = None) -> str:
    """Create a sales dashboard widget, return its label."""
    df = get_sales_data(user_id)
    fig = px.bar(df, x="month", y="revenue", title="Sales Dashboard")
    
    # open_browser=True forces InlineWidget which has .url for redirects
    # With PYWRY_HEADLESS=1, open_in_browser() is automatically skipped
    widget = show_plotly(
        fig, 
        title="Sales Dashboard",
        callbacks={"chart:export": handle_export},
        open_browser=True,  # Forces InlineWidget for server deployments
    )
    return widget.label  # .label works on all widget types

def create_inventory_view(warehouse_id: str | None = None) -> str:
    """Create an inventory grid widget."""
    df = get_inventory_data(warehouse_id)
    
    widget = show_dataframe(
        df,
        title="Inventory",
        callbacks={"grid:select": handle_row_select},
        open_browser=True,
    )
    return widget.label

def create_analytics_dashboard() -> str:
    """Create an analytics dashboard with multiple charts."""
    widget = show(
        generate_analytics_html(),
        title="Analytics",
        include_plotly=True,
        callbacks={
            "plotly:click": handle_chart_click,
            "toolbar:refresh": refresh_analytics,
        },
        open_browser=True,
    )
    return widget.label

# ═══════════════════════════════════════════════════════════
# EVENT HANDLERS - Shared across all widget instances
# ═══════════════════════════════════════════════════════════

def handle_export(data, event_type, label):
    """Handle export request from any sales dashboard."""
    print(f"[{label}] Export requested: {data}")

def handle_row_select(data, event_type, label):
    """Handle row selection from any inventory grid."""
    print(f"[{label}] Selected: {data['selected_rows']}")

def handle_chart_click(data, event_type, label):
    """Handle chart click from any analytics dashboard."""
    print(f"[{label}] Clicked: {data}")

def refresh_analytics(data, event_type, label):
    print(f"Refreshing analytics for {label}")

# ═══════════════════════════════════════════════════════════
# FASTAPI ROUTES - Static URLs that redirect to dynamic widgets
# ═══════════════════════════════════════════════════════════

@app.get("/")
async def index():
    """Landing page with links to dashboards."""
    return {
        "dashboards": {
            "sales": "/sales",
            "inventory": "/inventory",
            "analytics": "/analytics",
        }
    }

@app.get("/sales")
async def sales_dashboard(request: Request, user_id: str | None = None):
    """Static route that creates a fresh sales dashboard."""
    widget_id = create_sales_dashboard(user_id)
    return RedirectResponse(f"/widget/{widget_id}")

@app.get("/inventory")
async def inventory_view(warehouse_id: str | None = None):
    """Static route that creates a fresh inventory view."""
    widget_id = create_inventory_view(warehouse_id)
    return RedirectResponse(f"/widget/{widget_id}")

@app.get("/analytics")
async def analytics_dashboard():
    """Static route that creates a fresh analytics dashboard."""
    widget_id = create_analytics_dashboard()
    return RedirectResponse(f"/widget/{widget_id}")

# ═══════════════════════════════════════════════════════════
# HELPER FUNCTIONS (replace with your data sources)
# ═══════════════════════════════════════════════════════════

def get_sales_data(user_id: str | None = None) -> pd.DataFrame:
    return pd.DataFrame({
        "month": ["Jan", "Feb", "Mar", "Apr"],
        "revenue": [100, 150, 120, 180]
    })

def get_inventory_data(warehouse_id: str | None = None) -> pd.DataFrame:
    return pd.DataFrame({
        "sku": ["A001", "B002", "C003"],
        "quantity": [50, 30, 100],
        "location": ["Shelf 1", "Shelf 2", "Shelf 3"]
    })

def generate_analytics_html() -> str:
    return "<h1>Analytics Dashboard</h1><div id='charts'></div>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

Run with:

```bash
python app.py
# Or with uvicorn directly:
# uvicorn app:app --host 0.0.0.0 --port 8080
```

Now users can access:
- `http://yourserver:8080/sales` → Creates fresh widget, redirects to `/widget/{id}`
- `http://yourserver:8080/inventory?warehouse_id=NYC` → Parameterized view
- `http://yourserver:8080/analytics` → Analytics dashboard

#### State Management Across Widgets

Track widget instances and their state:

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import threading

@dataclass
class WidgetSession:
    """Track a widget instance and its state."""
    widget_id: str
    view_name: str
    user_id: str | None
    created_at: datetime
    state: dict[str, Any] = field(default_factory=dict)

class WidgetManager:
    """Manage all active widget sessions."""
    
    def __init__(self):
        self._sessions: dict[str, WidgetSession] = {}
        self._lock = threading.Lock()
    
    def create(self, widget_id: str, view_name: str, user_id: str | None = None) -> WidgetSession:
        session = WidgetSession(
            widget_id=widget_id,
            view_name=view_name,
            user_id=user_id,
            created_at=datetime.now(),
        )
        with self._lock:
            self._sessions[widget_id] = session
        return session
    
    def get(self, widget_id: str) -> WidgetSession | None:
        return self._sessions.get(widget_id)
    
    def update_state(self, widget_id: str, key: str, value: Any) -> None:
        session = self._sessions.get(widget_id)
        if session:
            session.state[key] = value
    
    def remove(self, widget_id: str) -> None:
        with self._lock:
            self._sessions.pop(widget_id, None)
    
    def get_by_user(self, user_id: str) -> list[WidgetSession]:
        return [s for s in self._sessions.values() if s.user_id == user_id]

# Global manager
manager = WidgetManager()

# Use in view factories
def create_sales_dashboard(user_id: str | None = None) -> str:
    widget = show_plotly(fig, title="Sales", open_browser=True)
    
    # Track the session
    manager.create(widget.label, "sales", user_id)
    
    return widget.label

# Use in event handlers
def handle_filter_change(data, event_type, label):
    # label is the widget identifier
    manager.update_state(label, "filters", data)
    
    session = manager.get(label)
    if session:
        print(f"User {session.user_id} changed filters: {data}")
```

#### Cleanup on Disconnect

Register a disconnect callback to clean up sessions:

```python
def on_disconnect(data, event_type, label):
    """Called when widget WebSocket disconnects."""
    session = manager.get(label)
    if session:
        print(f"Widget {label} disconnected after {datetime.now() - session.created_at}")
        manager.remove(label)

# Register on each widget
widget = pywry.show_plotly(fig, callbacks={
    "pywry:disconnect": on_disconnect,  # Internal disconnect event
    "plotly:click": handle_click,
})
```

### Simple Script Example

For quick testing or simple scripts (not production):

```python
# simple.py - Quick script for local testing
from pywry import PyWry, WindowMode
from pywry.inline import block
import plotly.express as px

app = PyWry(mode=WindowMode.BROWSER)

fig = px.scatter(px.data.iris(), x="sepal_width", y="sepal_length", color="species")
widget = app.show_plotly(fig, title="Quick Test")

print(f"Open: {widget.url}")
block()  # Keep server running
```

```bash
PYWRY_SERVER__HOST=0.0.0.0 python simple.py
```

### Programmatic URL Access

```python
from pywry import PyWry, WindowMode

app = PyWry(mode=WindowMode.BROWSER)
widget = app.show_plotly(fig)

# Get the URL
url = widget.url  # http://127.0.0.1:8765/widget/abc123

# Open in system browser programmatically
widget.open_in_browser()

# Get widget ID (used in URL path)
widget_id = widget.widget_id  # "abc123"

# Construct URL manually if needed
from pywry.config import get_settings
settings = get_settings().server
protocol = "https" if settings.ssl_certfile else "http"
base_url = f"{protocol}://{settings.host}:{settings.port}"
full_url = f"{base_url}/widget/{widget_id}"
```

### HTTPS Configuration

For production deployments, enable SSL/TLS:

```toml
[server]
host = "0.0.0.0"
port = 443
ssl_certfile = "/etc/letsencrypt/live/myapp.com/fullchain.pem"
ssl_keyfile = "/etc/letsencrypt/live/myapp.com/privkey.pem"
```

The widget URL will automatically use `https://`:

```python
widget = app.show_plotly(fig)
print(widget.url)  # https://0.0.0.0:443/widget/abc123
```

### Server Health Check

The inline server exposes a `/health` endpoint:

```bash
curl http://localhost:8765/health
# {"status": "ok"}
```

Use this for load balancer health checks or monitoring.

</details>

---

## CLI Commands

<details>
<summary>Click to expand</summary>

PyWry provides a CLI for **configuration management only**. Entry point: `pywry`

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

</details>

---

## Debugging

<details>
<summary>Click to expand</summary>

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

</details>

---

## Building from Source

<details>
<summary>Click to expand</summary>

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
│   ├── __init__.py        # Public API exports (version: 2.0.0)
│   ├── __main__.py        # PyTauri subprocess entry point
│   ├── app.py             # Main PyWry class - user entry point
│   ├── asset_loader.py    # CSS/JS file loading with caching
│   ├── assets.py          # Bundled asset loading (Plotly.js, AgGrid, CSS)
│   ├── callbacks.py       # Event callback registry (singleton)
│   ├── cli.py             # CLI commands (pywry config, pywry init)
│   ├── config.py          # Layered configuration system (pydantic-settings)
│   ├── grid.py            # AgGrid Pydantic models (ColDef, GridOptions, etc.)
│   ├── hot_reload.py      # Hot reload manager
│   ├── inline.py          # FastAPI-based inline server + InlineWidget
│   ├── log.py             # Logging utilities
│   ├── models.py          # Pydantic models (HtmlContent, WindowConfig, ThemeMode, WindowMode)
│   ├── notebook.py        # Notebook environment detection
│   ├── plotly_config.py   # Plotly configuration models (PlotlyConfig, ModeBarButton, etc.)
│   ├── runtime.py         # PyTauri subprocess management (stdin/stdout IPC)
│   ├── scripts.py         # JavaScript bridge code injected into windows
│   ├── state_mixins.py    # Widget state management mixins (GridStateMixin, PlotlyStateMixin, ToolbarStateMixin)
│   ├── Tauri.toml         # Tauri configuration
│   ├── templates.py       # HTML template builder with CSP, themes, scripts
│   ├── toolbar.py         # Toolbar component models (Button, Select, etc.)
│   ├── watcher.py         # File system watcher (watchdog-based)
│   ├── widget.py          # anywidget-based widgets (PyWryWidget, PyWryPlotlyWidget, PyWryAgGridWidget)
│   ├── widget_protocol.py # BaseWidget protocol definition
│   ├── capabilities/      # Tauri capability permissions
│   │   └── default.toml   # Default permissions (core, dialog, fs)
│   ├── commands/          # IPC command handlers
│   │   ├── __init__.py
│   │   └── window_commands.py
│   ├── frontend/          # Frontend HTML and bundled assets
│   │   ├── assets/        # Plotly.js, AgGrid, icons
│   │   ├── src/           # main.js, aggrid-defaults.js, plotly-widget.js, plotly-templates.js
│   │   └── style/         # CSS files (pywry.css)
│   ├── utils/             # Utility helpers
│   │   ├── __init__.py
│   │   └── async_helpers.py
│   └── window_manager/    # Window mode implementations
│       ├── __init__.py
│       ├── controller.py      # WindowController
│       ├── lifecycle.py       # WindowLifecycle with resource tracking
│       └── modes/
│           ├── __init__.py
│           ├── base.py        # Abstract WindowModeBase interface
│           ├── browser.py     # BROWSER mode - opens in system browser
│           ├── new_window.py  # NEW_WINDOW mode
│           ├── single_window.py # SINGLE_WINDOW mode
│           └── multi_window.py  # MULTI_WINDOW mode
├── tests/                 # Unit and E2E tests
├── examples/              # Demo notebooks
├── build_assets.py        # Asset download script
├── build_widget.py        # Widget build script
├── pyproject.toml         # Package configuration
├── ruff.toml              # Ruff linting configuration
├── pytest.ini             # Pytest configuration
├── AGENTS.md              # AI coding agent guide
└── README.md
```

</details>

---

# Integrations

## Plotly Integration

<details>
<summary>Click to expand</summary>

PyWry bundles Plotly.js 3.3.1 for offline charting with full event integration. Display figures with `show_plotly()` and handle chart events in Python.

### Basic Usage

```python
import plotly.graph_objects as go
from pywry import PyWry

app = PyWry()
fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 5, 6])])
app.show_plotly(fig)
```

### Plotly Templates

PyWry bundles all official Plotly templates for consistent theming with no network dependencies.

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

### PlotlyConfig

Top-level configuration object passed to `Plotly.newPlot()`. Controls responsiveness, interactivity, modebar behavior, and more.

```python
from pywry import PlotlyConfig, PlotlyIconName, ModeBarButton

config = PlotlyConfig(
    responsive=True,           # Resize with container (default: True)
    display_mode_bar="hover",  # Show on hover (default), True, or False
    display_logo=False,        # Hide Plotly logo
    scroll_zoom=True,          # Enable scroll-to-zoom
    double_click="reset",      # Reset on double-click ("reset+autosize", "reset", "autosize", False)
    static_plot=False,         # Disable all interactivity
    editable=False,            # Allow editing titles, annotations, etc.
    mode_bar_buttons_to_remove=["lasso2d", "select2d"],  # Remove specific buttons
    mode_bar_buttons_to_add=[...],  # Add custom buttons (see ModeBarButton)
)

# Pass to show_plotly
app.show_plotly(fig, config=config)
```

### ModeBarButton

Define custom buttons for the Plotly modebar. Buttons can emit PyWry events when clicked.

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Unique identifier for the button |
| `title` | `str` | Tooltip text shown on hover |
| `icon` | `SvgIcon \| PlotlyIconName \| str` | Button icon (built-in or custom SVG) |
| `event` | `str \| None` | PyWry event to emit when clicked |
| `data` | `dict \| None` | Additional data to include in event payload |
| `toggle` | `bool \| None` | Whether button has toggle state |
| `click` | `str \| None` | JavaScript handler (use `event` for PyWry events instead) |

```python
from pywry import ModeBarButton, PlotlyIconName

# Custom button that emits a PyWry event
export_button = ModeBarButton(
    name="exportData",
    title="Export Data",
    icon=PlotlyIconName.SAVE,
    event="app:export",
    data={"format": "csv"},
)

config = PlotlyConfig(
    mode_bar_buttons_to_add=[export_button],
)

# Handle the event in Python
def on_export(data, event_type, label):
    print(f"Export requested: {data}")

app.show_plotly(fig, config=config, callbacks={"app:export": on_export})
```

### SvgIcon

Define custom SVG icons for modebar buttons.

| Field | Type | Description |
|-------|------|-------------|
| `width` | `int` | SVG viewBox width (default: 500) |
| `height` | `int` | SVG viewBox height (default: 500) |
| `path` | `str \| None` | SVG path `d` attribute |
| `svg` | `str \| None` | Full SVG markup (alternative to `path`) |
| `transform` | `str \| None` | SVG transform attribute |

```python
from pywry import SvgIcon, ModeBarButton

# Custom icon using SVG path
custom_icon = SvgIcon(
    width=24,
    height=24,
    path="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5",
)

button = ModeBarButton(
    name="customAction",
    title="Custom Action",
    icon=custom_icon,
    event="app:custom",
)
```

### PlotlyIconName

Enum of built-in Plotly icon names. Use these instead of custom SVGs when possible.

```python
from pywry import PlotlyIconName

# Available icons
PlotlyIconName.CAMERA_RETRO  # Download/screenshot
PlotlyIconName.HOME          # Reset/home
PlotlyIconName.ZOOM_IN       # Zoom in
PlotlyIconName.ZOOM_OUT      # Zoom out
PlotlyIconName.PAN           # Pan mode
PlotlyIconName.LASSO         # Lasso select
PlotlyIconName.SAVE          # Save
PlotlyIconName.PENCIL        # Edit
PlotlyIconName.ERASER        # Erase
PlotlyIconName.UNDO          # Undo
# ... and more (see PlotlyIconName enum)
```

### Pre-built Buttons

PyWry includes convenience button classes:

```python
from pywry.plotly_config import DownloadImageButton, ResetAxesButton, ToggleGridButton

config = PlotlyConfig(
    mode_bar_buttons_to_add=[
        DownloadImageButton(),
        ResetAxesButton(),
        ToggleGridButton(),  # Emits "plotly:toggle-grid" event
    ],
)
```

### StandardButton

Enum of standard Plotly modebar button names. Use with `mode_bar_buttons_to_remove`:

```python
from pywry.plotly_config import StandardButton

config = PlotlyConfig(
    mode_bar_buttons_to_remove=[
        StandardButton.LASSO_2D,
        StandardButton.SELECT_2D,
        StandardButton.TOGGLE_SPIKELINES,
    ],
)
```

### Accessing Plotly API (JavaScript)

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

</details>

## AgGrid Integration

<details>
<summary>Click to expand</summary>

PyWry bundles AgGrid 35.0.0 for high-performance data tables. Display DataFrames with `show_dataframe()` and handle grid events in Python.

### Basic Usage

```python
import pandas as pd
from pywry import PyWry

app = PyWry()
df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
app.show_dataframe(df)
```

### Import Grid Models

```python
from pywry.grid import ColDef, ColGroupDef, DefaultColDef, RowSelection, GridOptions, build_grid_config
```

### Column Definitions

Use `ColDef` to define individual columns with all common AgGrid options:

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
| `GridOptions` | Complete AgGrid configuration |
| `GridConfig` | Combined AgGrid options + PyWry context |
| `GridData` | Normalized grid data from various inputs |

### Accessing AgGrid API (JavaScript)

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

For full AgGrid API reference, see: https://www.ag-grid.com/javascript-data-grid/grid-options/

</details>

---
