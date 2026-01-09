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
from pywry import PyWry, WindowMode, ThemeMode

# Create instance
pywry = PyWry(
    mode=WindowMode.SINGLE_WINDOW,
    theme=ThemeMode.DARK,
    title="My App",
    width=1280,
    height=720,
)

# Define handler that updates the window content
def on_click(data):
    pywry.eval_js("document.querySelector('h1').innerText = 'Toolbar Works!'")
    pywry.eval_js("document.body.style.backgroundColor = '#222244'")

pywry.on("app:click", on_click)

# Display HTML with an interactive toolbar
buttons = [{"label": "Update Text", "event": "app:click"}]
pywry.show(
    "<h1>Hello, World!</h1>", 
    buttons=buttons, 
    toolbar_position="bottom"
)

# Display Plotly figure with a custom PyWry toolbar on the left
# Note: This positions the PyWry toolbar independently of Plotly's internal modebar
def on_custom_action(data):
    # This runs in Python when the button is clicked
    print("Custom action triggered!")
    pywry.eval_js("alert('Custom action triggered from Python!')")

pywry.on("app:custom", on_custom_action)

fig = {"data": [{"x": [1, 2, 3], "y": [4, 5, 6], "type": "scatter"}]}
plotly_buttons = [{"label": "Custom Action", "event": "app:custom"}]
pywry.show_plotly(
    fig, 
    buttons=plotly_buttons, 
    toolbar_position="left"
)

# Display DataFrame with AG Grid
import pandas as pd
df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
pywry.show_dataframe(df, toolbar_position="top")

# Cleanup
pywry.destroy()
```

---

## Table of Contents

- [Window Modes](#window-modes)
- [PyWry Class API](#pywry-class-api)
- [CSS Selectors and Theming](#css-selectors-and-theming)
- [HtmlContent Model](#htmlcontent-model)
- [WindowConfig Model](#windowconfig-model)
- [Configuration System](#configuration-system)
- [Hot Reload](#hot-reload)
- [Plotly Templates](#plotly-templates)
- [Event System](#event-system)
- [JavaScript Bridge](#javascript-bridge)
- [Direct Tauri API Access](#direct-tauri-api-access)
- [CLI Commands](#cli-commands)
- [Debugging](#debugging)
- [Building from Source](#building-from-source)

---

## Window Modes

PyWry supports three window management strategies via the `WindowMode` enum.

> **Note on Notebooks**: When running in Jupyter, Colab, or VS Code notebooks, PyWry detects the environment and automatically renders content inline via IFrames, ignoring the native window mode.

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

All display methods support the following toolbar arguments:
- `buttons`: List of dicts `[{"label": "Btn Name", "event": "ns:event"}]`
- `toolbar_position`: `"top"`, `"bottom"`, `"left"`, `"right"`, `"inside"`, `"hidden"`

**`show(content, ...) -> str`**

Display HTML content in a window.

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
    buttons=None,               # Toolbar buttons
    toolbar_position="top"      # Toolbar position
)
```

**`show_plotly(figure, ...) -> str`**

Display a Plotly figure.

```python
label = pywry.show_plotly(
    figure,                     # Plotly Figure object or dict spec
    title=None,                 # Window title
    callbacks=None,             # Event handlers
    label=None,                 # Window label
    inline_css=None,            # Custom CSS to inject
    buttons=None,               # Toolbar buttons
    toolbar_position="top"      # Toolbar position
)
```

**`show_dataframe(data, ...) -> str`**

Display a DataFrame using AG Grid.

```python
label = pywry.show_dataframe(
    data,                       # pandas DataFrame or dict
    title=None,                 # Window title
    callbacks=None,             # Event handlers
    label=None,                 # Window label
    column_defs=None,           # AG Grid column definitions
    aggrid_theme="alpine",      # AG Grid theme
    grid_options=None,          # Custom AG Grid options
    inline_css=None,            # Custom CSS to inject
    buttons=None,               # Toolbar buttons
    toolbar_position="top",     # Toolbar position
)
```

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
pywry.show(
    "<h1>Content</h1>",
    buttons=[{"label": "Action", "event": "do-it"}],
    inline_css="""
        .pywry-btn { background: blue !important; border-radius: 20px; }
        .pywry-toolbar { justify-content: center; } /* Center buttons */
    """
)
```

#### Event Methods

**`on(event_type, handler, label=None) -> bool`**

Register an event handler. Returns `True` if successful.

**`send_event(event_type, data, label=None) -> bool`**

Send an event to window(s). If `label` is `None`, sends to all windows.

#### Window Management

| Method | Returns | Description |
|--------|---------|-------------|
| `update_content(html, label=None)` | `bool` | Update window HTML content |
| `eval_js(script, label=None)` | `bool` | Execute JavaScript in window(s) |
| `close(label=None)` | `bool` | Close window(s) |
| `refresh(label=None)` | `bool` | Refresh with scroll preservation |
| `refresh_css(label=None)` | `bool` | Hot-reload CSS without page refresh |
| `get_labels()` | `list[str]` | Get all active window labels |
| `is_open(label=None)` | `bool` | Check if window(s) are open |

#### JavaScript Execution

**`eval_js(script, label=None) -> bool`**

Execute JavaScript code in one or all windows. Useful for dynamic updates.

```python
# Update element in all windows
pywry.eval_js("document.querySelector('h1').textContent = 'Updated!'")

# Update specific window
pywry.eval_js("alert('Hello!')", label="main-window")

# Complex operations
pywry.eval_js("""
    const chart = document.querySelector('.plotly-graph-div');
    Plotly.relayout(chart, { title: 'Dynamic Title' });
""")
```

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
| `toolbar_position` | `str` | `"top"` | Toolbar position |
| `center` | `bool` | `True` | Center window on screen |
| `resizable` | `bool` | `True` | Allow window resizing |
| `decorations` | `bool` | `True` | Show window decorations |
| `always_on_top` | `bool` | `False` | Keep window above others |
| `devtools` | `bool` | `False` | Open developer tools |
| `allow_network` | `bool` | `True` | Allow network requests |
| `enable_plotly` | `bool` | `False` | Include Plotly.js library |
| `enable_aggrid` | `bool` | `False` | Include AG Grid library |
| `plotly_theme` | `str` | `"plotly_dark"` | Plotly theme |
| `aggrid_theme` | `str` | `"quartz"` | AG Grid theme |

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

## Direct Tauri API Access

For advanced use cases, you can access the underlying Tauri IPC system directly. PyWry is built on [PyTauri](https://pypi.org/project/pytauri/), which provides full access to Tauri's capabilities.

### The `__TAURI__` Global

When running in a desktop window (not in notebook/inline mode), the `window.__TAURI__` object provides direct access to Tauri APIs:

```javascript
// Check if running in Tauri context
if (window.__TAURI__) {
    console.log("Running in Tauri desktop mode");
}
```

### Native File Dialogs and Filesystem

PyWry registers Tauri's dialog and filesystem plugins, enabling native OS file dialogs instead of browser-based ones. This avoids browser security warnings and provides a native experience.

```javascript
// Save file with native dialog
if (window.__TAURI__) {
    const filePath = await window.__TAURI__.dialog.save({
        defaultPath: 'data.csv',
        filters: [{ name: 'CSV', extensions: ['csv'] }]
    });
    if (filePath) {
        await window.__TAURI__.fs.writeTextFile(filePath, csvContent);
    }
}

// Open file dialog
if (window.__TAURI__) {
    const selected = await window.__TAURI__.dialog.open({
        multiple: false,
        filters: [{ name: 'JSON', extensions: ['json'] }]
    });
    if (selected) {
        const content = await window.__TAURI__.fs.readTextFile(selected);
        console.log(content);
    }
}

// Show message dialog
if (window.__TAURI__) {
    await window.__TAURI__.dialog.message('Operation completed!', {
        title: 'Success',
        kind: 'info'
    });
}
```

**Available Dialog APIs:**

| Function | Description |
|----------|-------------|
| `dialog.save(options)` | Show native save file dialog |
| `dialog.open(options)` | Show native open file dialog |
| `dialog.message(message, options)` | Show message/alert dialog |
| `dialog.ask(message, options)` | Show confirmation dialog |
| `dialog.confirm(message, options)` | Show yes/no dialog |

**Available Filesystem APIs:**

| Function | Description |
|----------|-------------|
| `fs.readTextFile(path)` | Read text file contents |
| `fs.writeTextFile(path, content)` | Write text to file |
| `fs.readFile(path)` | Read binary file |
| `fs.writeFile(path, content)` | Write binary to file |
| `fs.exists(path)` | Check if file exists |
| `fs.mkdir(path)` | Create directory |

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

### Listening to Tauri Events

Use the Tauri event system to listen for Python-sent events:

```javascript
// Listen for PyWry events
window.__TAURI__.event.listen('pywry:event', function(event) {
    const { event_type, data } = event.payload;
    console.log('Received:', event_type, data);
});

// Listen for theme changes
window.__TAURI__.event.listen('pywry:theme-update', function(event) {
    const { mode } = event.payload;  // 'dark', 'light', or 'system'
    console.log('Theme changed to:', mode);
});

// Listen for cleanup signal (before window closes)
window.__TAURI__.event.listen('pywry:cleanup', function() {
    console.log('Window closing, cleanup resources');
});

// Listen for Plotly data updates
window.__TAURI__.event.listen('pywry:plotly-data', function(event) {
    // event.payload contains { data, layout, config }
});

// Listen for Grid data updates
window.__TAURI__.event.listen('pywry:grid-data', function(event) {
    // event.payload contains { rows }
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
| `pywry:grid-data` | `{ rows }` | AG Grid row data update |
| `pywry:grid-update` | `{ rows }` | AG Grid transaction update |

### Example: Custom Tauri Handler

```python
from pywry import PyWry

pywry = PyWry()

pywry.show("""
<div id="output"></div>
<script>
// Listen directly to Tauri events
window.__TAURI__.event.listen('pywry:event', function(event) {
    const { event_type, data } = event.payload;
    
    // Handle custom event types
    if (event_type === 'custom:update') {
        document.getElementById('output').textContent = data.message;
    }
});
</script>
""")

# Send event to JavaScript
pywry.send_event("custom:update", {"message": "Hello from Python!"})
```

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
