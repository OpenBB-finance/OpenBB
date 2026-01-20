![PyWry](./pywry/frontend/assets/PyWry.png)

PyWry is a blazingly fast rendering library for generating and managing native desktop windows, iFrames, and Jupyter widgets - with full bidirectional Python ↔ JavaScript communication. Get started in minutes, not hours.

Unlike other similar libraries, PyWry is **not** a web dashboard framework. It is a **rendering engine** that targets three output paths from one API:


| Mode | Where It Runs | Backend |
|------|---------------|---------|
| `NEW_WINDOW` / `SINGLE_WINDOW` / `MULTI_WINDOW` | Native OS window | PyTauri (Tauri/Rust) subprocess using OS webview |
| `NOTEBOOK` | Jupyter / VS Code / Colab | anywidget or IFrame + FastAPI + WebSocket |
| `BROWSER` | System browser tab | FastAPI server + WebSocket + Redis |

It uses declarative Pydantic components that automatically wrap content in a nested structure that can be targeted with CSS selectors:

HEADER → LEFT | TOP → CONTENT + INSIDE → BOTTOM | RIGHT → FOOTER

Built on [PyTauri](https://pypi.org/project/pytauri/) (which uses Rust's [Tauri](https://tauri.app/) framework), it leverages the OS webview instead of bundling a browser engine — a few MBs versus Electron's 150MB+ overhead.

Its unified API lets you build fast and use anywhere. Batteries included.

## Installation

Install in a virtual environment with a version of Python between 3.10 and 3.14.

### Linux

Linux requires WebKitGTK and GTK3 development libraries:

```bash
# Ubuntu/Debian
sudo apt-get install libwebkit2gtk-4.1-dev libgtk-3-dev libglib2.0-dev \
    libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
    libxcb-randr0 libxcb-render-util0 libxcb-xinerama0 libxcb-xfixes0 \
    libxcb-shape0 libgl1 libegl1
```

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

### Hello World!

```python
from pywry import PyWry

app = PyWry()

app.show("Hello World!")

app.block()  # block the main thread until the window closes

app.show("Hello again, World!")
```

### Button Updates Content

```python
from pywry import PyWry, Toolbar, Button

# Create instance
app = PyWry()

def on_click(data, event_type, label):
    """Update the heading text and inject custom CSS."""
    app.emit("pywry:set-content", {"selector": "h1", "text": "Toolbar Works!"}, label)

# Display HTML with an interactive toolbar
toolbar = Toolbar(
    position="top",
    items=[Button(label="Update Text", event="app:click")]
)
label = app.show(
    "<h1 text>Hello, World!</h1>",
    toolbars=[toolbar],
    callbacks={"app:click": on_click},
)
```

### DataFrame -> AgGrid

```python
from pywry import PyWry
import pandas as pd

app = PyWry()

df = pd.DataFrame({"name": ["Alice", "Bob", "Carol"], "age": [30, 25, 35]})

def on_select(data, event_type, label):
    """Print selected row names."""
    names = ", ".join(row["name"] for row in data["rows"])
    app.emit("pywry:alert", {"message": f"Selected: {names}" if names else "None selected"}, label)

label = app.show_dataframe(
    df,
    callbacks={"grid:row-selected": on_select},
)
```

### Plotly Chart

Install Plotly into the environment first (`pip install plotly`).

```python
from pywry import PyWry, Toolbar, Button
import plotly.express as px

app = PyWry(theme="light")

fig = px.scatter(px.data.iris(), x="sepal_width", y="sepal_length", color="species")

def on_click(data, event_type, label):
    """Update chart title when a point is clicked."""
    point = data["points"][0]
    app.emit(
        "plotly:update-layout", 
        {
            "layout": {
                "title": f"Clicked: ({point['x']:.2f}, {point['y']:.2f})"
            },
        },
        label
    )

def on_reset(data, event_type, label):
    """Reset the chart zoom."""
    app.emit("plotly:reset-zoom", {}, label)

label = app.show_plotly(
    fig,
    toolbars=[Toolbar(position="top", items=[Button(label="Reset Zoom", event="app:reset")])],
    callbacks={
        "plotly:click": on_click,
        "app:reset": on_reset,
    },
)
```

---

## Table of Contents

| Section | Description |
|---------|-------------|
| [Features](#features) | Overview of PyWry capabilities |
| [Installation](#installation) | How to install PyWry |
| [Quick Start](#quick-start) | Minimal working example |

**Core Documentation**

| Section | Description |
|---------|-------------|
| [Rendering Paths](#rendering-paths) | Native Window, Notebook, IFrame, Browser modes |
| ↳ [Native Window](#rendering-paths) ・ [Notebook Widget](#rendering-paths) ・ [Inline IFrame](#rendering-paths) ・ [Browser Mode](#rendering-paths) | |
| [Core API](#core-api) | PyWry class, imports, display & event methods |
| ↳ [Imports](#core-api) ・ [PyWry Class](#core-api) ・ [Display Methods](#core-api) ・ [Event Methods](#core-api) | |
| [HtmlContent Model](#htmlcontent-model) | Advanced content configuration |
| [WindowConfig Model](#windowconfig-model) | Window property configuration |
| [Configuration System](#configuration-system) | TOML files, environment variables, presets |
| ↳ [pywry.toml](#configuration-system) ・ [pyproject.toml](#configuration-system) ・ [Environment Variables](#configuration-system) ・ [Security Presets](#configuration-system) | |
| [Hot Reload](#hot-reload) | Live CSS/JS updates during development |

**Event & Toolbar Systems**

| Section | Description |
|---------|-------------|
| [Event System](#event-system) | Bidirectional Python ↔ JS communication |
| ↳ [Event Naming](#event-system) ・ [Handler Signature](#event-system) ・ [Toast Notifications](#toast-notifications-pywryalert) ・ [Utility Events](#utility-events-python-to-js) | |
| [Pre-Registered Events](#pre-registered-events-built-in) | Built-in system, Plotly, and AgGrid events |
| [Toolbar System](#toolbar-system) | All 14 toolbar components with examples |
| ↳ [Positions & Layout](#toolbar-system) ・ [Component Reference](#toolbar-system) ・ [State Management](#toolbar-system) | |
| [CSS Selectors and Theming](#css-selectors-and-theming) | Styling with CSS variables and classes |
| ↳ [Theme Classes](#css-selectors-and-theming) ・ [Layout Classes](#css-selectors-and-theming) ・ [Toast Classes](#toast-notification-classes) ・ [CSS Variables](#css-selectors-and-theming) | |

**Advanced Topics**

| Section | Description |
|---------|-------------|
| [JavaScript Bridge](#javascript-bridge) | `window.pywry` API reference |
| ↳ [Available Methods](#javascript-bridge) ・ [Injected Globals](#javascript-bridge) ・ [Plotly/AgGrid APIs](#javascript-bridge) ・ [Toolbar API](#javascript-bridge) ・ [Toast Notifications](#javascript-bridge) | |
| [Direct Tauri API Access](#direct-tauri-api-access) | Native filesystem, dialogs, clipboard |
| ↳ [`__TAURI__` Global](#direct-tauri-api-access) ・ [PyTauri IPC](#direct-tauri-api-access) ・ [Tauri Events](#direct-tauri-api-access) | |
| [Managing Multiple Windows/Widgets](#managing-multiple-windowswidgets) | Window lifecycle, widget references |
| ↳ [Window Modes](#managing-multiple-windowswidgets) ・ [Native Windows](#managing-multiple-windowswidgets) ・ [Widget Methods](#managing-multiple-windowswidgets) | |
| [Browser Mode & Server Configuration](#browser-mode--server-configuration) | Headless/web deployment, security settings |
| ↳ [Server Config](#server-configuration) ・ [HTTPS](#https-configuration) ・ [WebSocket Security](#websocket--api-security) | |
| [Deploy Mode & Scaling](#deploy-mode--scaling) | Redis backend, horizontal scaling, multi-worker |
| ↳ [State Backends](#deploy-mode--scaling) ・ [Redis Configuration](#deploy-mode--scaling) ・ [Authentication](#deploy-mode--scaling) | |
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

**In this section:** [Native Window](#native-window) · [Notebook Widget](#notebook-widget-anywidget) · [Inline IFrame](#inline-iframe) · [Browser Mode](#browser-mode)

---

PyWry automatically selects the appropriate rendering path based on your environment:

| Environment | Rendering Path | Module | Return Type |
|-------------|----------------|--------|-------------|
| Desktop (script/terminal) | Native Window | `pywry.app.PyWry` | `str` (window label) |
| Jupyter/VS Code with anywidget | Notebook Widget | `pywry.widget` | `PyWryWidget` |
| Jupyter/VS Code without anywidget | Inline IFrame | `pywry.inline` | `InlineWidget` |
| Headless / Server / SSH | Browser Mode | `pywry.window_manager.modes.browser` | `InlineWidget` |

<details>
<summary><b>Rendering Path Diagram</b></summary>

```
┌───────────────────────────────────────────────────────────────────────┐
│                         PyWry Rendering Paths                         │
└───────────────────────────────────────────────────────────────────────┘

                            ┌──────────────────┐
                            │   PyWry.show()   │
                            │  show_plotly()   │
                            │ show_dataframe() │
                            └────────┬─────────┘
                                     │
                       ┌─────────────┴─────────────┐
                       ▼                           ▼
            ┌────────────────────┐      ┌────────────────────┐
            │  Desktop/Terminal  │      │  Notebook/Browser  │
            │   (GUI Available)  │      │    Environment     │
            └─────────┬──────────┘      └──────────┬─────────┘
                      │                            │
                      ▼                      ┌─────┴─────┐
            ┌──────────────────┐             ▼           ▼
            │   NATIVE WINDOW  │      ┌───────────┐ ┌───────────┐
            │                  │      │ Notebook? │ │ Headless/ │
            │  PyTauri + Rust  │      │           │ │  Server   │
            │  WebView2/WebKit │      └─────┬─────┘ └─────┬─────┘
            │                  │            │             │
            │  ┌────────────┐  │      ┌─────┴─────┐       ▼
            │  │ OS WebView │  │      ▼           ▼  ┌─────────┐
            │  │            │  │  ┌───────┐ ┌─────┐  │ BROWSER │
            │  │ HTML/JS/CSS│  │  │ any-  │ │Falls│  │  MODE   │
            │  └────────────┘  │  │widget │ │back │  │         │
            │                  │  │ avail?│ │     │  │ FastAPI │
            │  Returns: label  │  └───┬───┘ └──┬──┘  │ Server  │
            │  (str)           │      │        │     │         │
            └──────────────────┘      ▼        │     │Opens in │
                      │         ┌─────────┐    │     │ Browser │
                      │         │NOTEBOOK │    │     └────┬────┘
                      │         │ WIDGET  │    │          │
                      │         │         │    ▼          ▼
                      │         │anywidget│ ┌─────────┐ Returns:
                      │         │ comms   │ │ INLINE  │ widget_id
                      │         │         │ │ IFRAME  │ (str)
                      │         │ Returns:│ │         │
                      │         │PyWry-   │ │ FastAPI │
                      │         │ Widget  │ │ Server  │
                      │         └─────────┘ │         │
                      │              │      │ Returns:│
                      │              │      │ Inline- │
                      │              │      │ Widget  │
                      │              │      └─────────┘
                      │              │           │
                      ▼              ▼           ▼
            ┌─────────────────────────────────────────────────┐
            │              Bidirectional Events               │
            │         Python ◄────────────► JavaScript        │
            │                                                 │
            │  • widget.emit("event:name", data)  (Python→JS) │
            │  • window.pywry.emit("event:name")  (JS→Python) │
            │  • callbacks={"event:name": handler}            │
            └─────────────────────────────────────────────────┘
```

**Decision Flow:**

1. **Desktop/Terminal with GUI** → Native Window (PyTauri + WebView)
2. **Jupyter/VS Code + anywidget installed** → Notebook Widget (anywidget comms)
3. **Jupyter/VS Code without anywidget** → Inline IFrame (FastAPI server)
4. **Headless/SSH/Server** → Browser Mode (FastAPI + system browser)

</details>

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

# Display content - returns window label (str)
label = app.show("<h1 id='greeting'>Hello</h1>")

# Update content using built-in utility event
app.emit("pywry:set-content", {"id": "greeting", "text": "Hello from Python!"}, label)
```

> **Note:** For low-level access, you can also use `runtime.emit_event(widget.label, ...)` directly.

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
widget = show_plotly(fig, callbacks={"plotly:click": my_handler})

# Update theme using built-in utility event
widget.emit("pywry:update-theme", {"theme": "plotly_white"})
```

### Inline IFrame

Fallback when `anywidget` is not available. Uses FastAPI server running in background thread.

```python
from pywry.inline import show_plotly, show_dataframe

# Returns InlineWidget (IFrame-based)
widget = show_plotly(fig, callbacks={"plotly:click": my_handler})

# Update theme using built-in utility event
widget.emit("pywry:update-theme", {"theme": "plotly_white"})
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

# Block until browser tab is closed
app.block()
```

Browser mode starts a FastAPI server and opens the widget URL in the browser. Use `app.block()` to keep the server running after your script completes.

</details>

---

## Core API

<details>
<summary>Click to expand</summary>

**In this section:** [Imports](#imports) · [PyWry Class](#pywry-class) · [Display Methods](#display-methods) · [Event Methods](#event-methods) · [Other Methods](#other-methods)

---

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

# Window manager
from pywry import BrowserMode, get_lifecycle

# Settings
from pywry import PyWrySettings, SecuritySettings, WindowSettings, ThemeSettings, ServerSettings, HotReloadSettings, TimeoutSettings, AssetSettings, LogSettings

# Asset loading
from pywry import AssetLoader, get_asset_loader

# Callback registry
from pywry import CallbackFunc, WidgetType, get_registry

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
from pywry import PyWry

app = PyWry()
label = app.show("<h1 id='title'>Hello</h1>")

# For native mode: use app.emit() with built-in utility events
app.emit("pywry:set-content", {"id": "title", "text": "Updated!"}, label)

# For notebook mode: show_*() returns a widget with .emit()
# widget.emit("pywry:set-content", {"id": "title", "text": "Updated!"})
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

### Window Management

PyWry provides fine-grained control over window visibility and lifecycle. Windows can be shown, hidden, and closed independently.

| Method | Description |
|--------|-------------|
| `show_window(label)` | Show a hidden window (brings to front) |
| `hide_window(label)` | Hide a window (keeps it alive, not destroyed) |
| `close(label)` | Close/destroy a specific window permanently |
| `close()` | Close/destroy all windows |
| `get_labels()` | Get list of currently visible window labels |
| `block(label=None)` | Block until specific window or all windows close |

**Window Lifecycle:**

```
Created → Visible → Hidden → Visible → Closed
             ↑         │                  ↑
             └─────────┘                  │
          (show_window)                (close)
```

**X Button Behavior by Mode:**

| Mode | X Button | Behavior |
|------|----------|----------|
| `SINGLE_WINDOW` | Always hides | Window reused on next `show()` |
| `NEW_WINDOW` | Always closes | Window destroyed, cannot recover |
| `MULTI_WINDOW` | Configurable | Uses `on_window_close` setting |

For `MULTI_WINDOW`, use `on_window_close` to control whether clicking X hides or destroys windows:

```python
from pywry import PyWry, PyWrySettings, WindowMode

# X button hides windows (default) - can recover with show_window()
app = PyWry(mode=WindowMode.MULTI_WINDOW)

# X button destroys windows - cannot recover
settings = PyWrySettings()
settings.window.on_window_close = "close"
app = PyWry(mode=WindowMode.MULTI_WINDOW, settings=settings)
```

**Example: Managing Multiple Windows**

```python
from pywry import PyWry, WindowMode

app = PyWry(mode=WindowMode.MULTI_WINDOW)

# Create windows with labels
app.show("<h1>Dashboard</h1>", label="dashboard")
app.show("<h1>Settings</h1>", label="settings")
app.show("<h1>Help</h1>", label="help")

# Check visible windows
print(app.get_labels())  # ['dashboard', 'settings', 'help']

# Hide the settings window
app.hide_window("settings")
print(app.get_labels())  # ['dashboard', 'help']

# Bring it back
app.show_window("settings")
print(app.get_labels())  # ['dashboard', 'settings', 'help']

# Close the help window permanently
app.close("help")
print(app.get_labels())  # ['dashboard', 'settings']

# Block until specific window closes
app.block("dashboard")  # Waits only for dashboard to close

print(app.get_labels())
# Or block until all windows close
app.block()  # Waits for all remaining windows
```

**SINGLE_WINDOW Mode Behavior:**

In `SINGLE_WINDOW` mode, calling `show()` multiple times reuses the same window without destroying it. If the window was hidden, it will be shown again with the new content:

```python
from pywry import PyWry, WindowMode

app = PyWry(mode=WindowMode.SINGLE_WINDOW)

# First show - creates window
app.show("<h1>Page 1</h1>")

# User hides window (clicks X)...

# Second show - reuses window, shows it again
app.show("<h1>Page 2</h1>")  # No "destroying" - just updates content

app.block()
```

</details>

---

## HtmlContent Model

<details>
<summary>Click to expand</summary>

For advanced content configuration, use the `HtmlContent` model:

```python
from pywry import PyWry, HtmlContent

app = PyWry()

content = HtmlContent(
    html="<div id='app'></div>",
    json_data={"key": "value"},
    init_script="console.log('ready');",
    css_files=["styles/main.css"],
    script_files=["js/app.js"],
    inline_css="body { margin: 0; }",
    watch=True,
)

app.show(content)
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

**In this section:** [pywry.toml](#configuration-file-pywrytoml) · [pyproject.toml](#pyprojecttoml) · [Environment Variables](#environment-variables) · [Configuration Sections](#configuration-sections) · [Programmatic Config](#programmatic-configuration) · [Security Presets](#security-presets)

---

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
on_window_close = "hide"  # "hide" or "close" (MULTI_WINDOW only)

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

[deploy]
state_backend = "redis"  # "memory" or "redis"
redis_url = "redis://localhost:6379/0"
redis_prefix = "pywry:"
widget_ttl = 86400  # 24 hours in seconds
connection_ttl = 300  # 5 minutes
auto_cleanup = true
enable_auth = false
# auth_secret = "your-secret-key"  # Required if enable_auth = true
# rbac_enabled = false
# default_role = "viewer"
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
export PYWRY_WINDOW__ON_WINDOW_CLOSE="close"  # "hide" or "close" (MULTI_WINDOW only)
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
| `server` | `PYWRY_SERVER__` | Inline server settings (host, port, CORS, security) |
| `deploy` | `PYWRY_DEPLOY__` | Deploy mode settings (Redis, scaling, auth) |

#### Server Security Settings

| Setting | Env Variable | Default | Description |
|---------|--------------|---------|-------------|
| `websocket_allowed_origins` | `PYWRY_SERVER__WEBSOCKET_ALLOWED_ORIGINS` | `[]` | Allowed WebSocket origins (empty = any) |
| `websocket_require_token` | `PYWRY_SERVER__WEBSOCKET_REQUIRE_TOKEN` | `true` | Require per-widget token |
| `internal_api_header` | `PYWRY_SERVER__INTERNAL_API_HEADER` | `X-PyWry-Token` | Internal API auth header |
| `internal_api_token` | `PYWRY_SERVER__INTERNAL_API_TOKEN` | auto-generated | Internal API token |
| `strict_widget_auth` | `PYWRY_SERVER__STRICT_WIDGET_AUTH` | `false` | Strict widget endpoint auth |

#### Deploy Mode Settings

| Setting | Env Variable | Default | Description |
|---------|--------------|---------|-------------|
| `state_backend` | `PYWRY_DEPLOY__STATE_BACKEND` | `memory` | State storage backend (`memory` or `redis`) |
| `redis_url` | `PYWRY_DEPLOY__REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `redis_prefix` | `PYWRY_DEPLOY__REDIS_PREFIX` | `pywry` | Key prefix for Redis keys |
| `widget_ttl` | `PYWRY_DEPLOY__WIDGET_TTL` | `86400` | Widget data TTL (seconds) |
| `auth_enabled` | `PYWRY_DEPLOY__AUTH_ENABLED` | `false` | Enable authentication |

See the [Deploy Mode & Scaling](#deploy-mode--scaling) section for complete documentation.

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

**In this section:** [Enable Hot Reload](#enable-hot-reload) · [Behavior](#behavior) · [Watch Files](#watch-files) · [Manual CSS Reload](#manual-css-reload) · [Configuration](#configuration)

---

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

<a id="utility-events-python-to-js"></a>

<details>
<summary>Click to expand</summary>

**In this section:** [What is an Event?](#what-is-an-event) · [Event Naming](#event-naming-format) · [Reserved Namespaces](#reserved-namespaces) · [Handler Signature](#handler-signature) · [Registering Handlers](#registering-handlers) · [Wildcard Handlers](#wildcard-handlers)

---

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
from pywry import PyWry, Toolbar, Button

app = PyWry()

# Full signature (recommended) - access all context
def on_action1(data, event_type, label):
    app.emit("pywry:set-content", {"id": "log", "text": f"[{label}] {event_type}: {data}"}, label)

# Two parameters - when you don't need the widget label
def on_action2(data, event_type):
    print(f"{event_type} received")

# One parameter - simplest, just the data
def on_action3(data):
    print(str(data))

label = app.show(
    '<div id="log" style="padding:20px;">Click a button...</div>',
    toolbars=[Toolbar(position="top", items=[
        Button(label="Action 1", event="app:action1"),
        Button(label="Action 2", event="app:action2"),
        Button(label="Action 3", event="app:action3"),
    ])],
    callbacks={
        "app:action1": on_action1,
        "app:action2": on_action2,
        "app:action3": on_action3,
    }
)
```

### Registering Handlers

**All modes support the `callbacks={}` parameter in `show()` methods.** This is the most portable approach.

| Mode | `callbacks={}` | `app.on()` | `widget.on()` | Returns |
|------|----------------|------------|---------------|---------|
| Native Window | ✅ | ✅ | ❌ | `str` (label) |
| Notebook (anywidget) | ✅ | ❌ | ✅ | `PyWryWidget` |
| Browser Mode | ✅ | ❌ | ✅ | `InlineWidget` |

#### Option 1: `callbacks={}` in show() — Works Everywhere

```python
from pywry import PyWry, Toolbar, Button
import plotly.express as px

app = PyWry()

# Create a Plotly figure
fig = px.scatter(px.data.iris(), x="sepal_width", y="sepal_length", color="species")

def on_click(data, event_type, label):
    """When user clicks a point, print the coordinates."""
    point = data["points"][0]
    print(f"Clicked: ({point['x']:.2f}, {point['y']:.2f})")

def on_export(data, event_type, label):
    """When export is clicked, save CSV."""
    csv_content = px.data.iris().to_csv(index=False)
    print(f"Exporting {len(csv_content)} bytes...")

# Works in ALL modes (native returns str, notebook returns widget)
label = app.show_plotly(
    fig,
    toolbars=[Toolbar(position="top", items=[Button(label="Export CSV", event="app:export")])],
    callbacks={
        "plotly:click": on_click,
        "app:export": on_export,
    }
)
```

#### Option 2: `app.on()` — Native Windows Only

For native desktop windows, you can register handlers separately using `app.on()`. **Important:** You must use the same `label` when registering handlers and showing content:

```python
from pywry import PyWry, Toolbar, Button
import plotly.express as px

app = PyWry()

fig = px.scatter(px.data.iris(), x="sepal_width", y="sepal_length", color="species")

def on_click(data, event_type, label):
    """When user clicks a point, update the chart title."""
    point = data["points"][0]
    app.emit("plotly:update-layout", {
        "layout": {"title": f"Selected: ({point['x']:.2f}, {point['y']:.2f})"}
    }, label)

def on_zoom_reset(data, event_type, label):
    """Reset chart zoom when button is clicked."""
    app.emit("plotly:reset-zoom", {}, label)

# Register handlers with explicit label BEFORE calling show()
app.on("plotly:click", on_click, label="my-chart")
app.on("app:zoom-reset", on_zoom_reset, label="my-chart")

# Use the SAME label when showing content
label = app.show_plotly(
    fig,
    title="Click points to select them",
    toolbars=[Toolbar(position="top", items=[Button(label="Reset Zoom", event="app:zoom-reset")])],
    label="my-chart",  # Must match the label used in app.on()
)
```

> **Note:** If you omit the `label` parameter, `show()` generates a random label and `app.on()` registers to `"main"`, causing a mismatch. For simpler code, prefer `callbacks={}` in `show()` (Option 1).
```

#### Option 3: `widget.on()` — All Modes

All widgets (native and notebook) support chaining handlers after `show()`. This is useful for adding handlers dynamically:

```python
from pywry import PyWry, Toolbar, Button
import plotly.express as px

app = PyWry()

fig = px.scatter(px.data.iris(), x="sepal_width", y="sepal_length", color="species")

def on_click(data, event_type, label):
    """When user clicks a point, update the chart title."""
    point = data["points"][0]
    app.emit("plotly:update-layout", {
        "layout": {"title": f"Last clicked: ({point['x']:.2f}, {point['y']:.2f})"}
    }, label)

def on_theme_toggle(data, event_type, label):
    """Toggle to dark theme."""
    app.emit("pywry:update-theme", {"theme": "plotly_dark"}, label)

# Using callbacks={} is recommended for most cases
label = app.show_plotly(
    fig,
    title="Click points to annotate",
    toolbars=[Toolbar(position="top", items=[Button(label="Dark Mode", event="app:theme")])],
    callbacks={
        "plotly:click": on_click,
        "app:theme": on_theme_toggle,
    }
)

# widget.on() can add additional handlers after show()
# widget.on("plotly:hover", on_hover)
```

### Wildcard Handlers

Wildcard handlers receive ALL events — useful for debugging during development:

```python
from pywry import PyWry, Toolbar, Button

app = PyWry()

def log_event(data, event_type, label):
    """Log the event to console."""
    print(f"[{event_type}] {data}")

# Show content with toolbar buttons
label = app.show(
    '<div id="log" style="padding:20px; font-family:monospace;">Click a button above...</div>',
    toolbars=[
        Toolbar(position="top", items=[
            Button(label="Action 1", event="app:action1"),
            Button(label="Action 2", event="app:action2"),
        ])
    ],
    # Use callbacks for each event - no race condition
    callbacks={
        "app:action1": log_event,
        "app:action2": log_event,
    }
)
```

> **Note:** For true wildcard logging in native mode, use `app.on("*", handler)` but be aware that events firing before `widget` is assigned (like `window:ready`) will need a guard check.

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
- **AgGrid events** (`grid:row-selected`, `grid:cell-click`, `grid:cell-edit`, etc.) include `gridId` and `widget_type: "grid"` in the payload.
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
| `pywry:download-csv` | `{ csv: str, filename: str }` | Trigger a CSV file download (Jupyter widget mode) |
| `pywry:navigate` | `{ url: str }` | Navigate to a URL (SPA-style navigation) |
| `pywry:alert` | `{ message, type?, title?, duration?, position? }` | Show a toast notification (info, success, warning, error, confirm) |
| `pywry:update-html` | `{ html: str }` | Replace widget content (triggers page reload) |

**Example: DOM Manipulation Without Custom JavaScript**

```python
from pywry import PyWry

app = PyWry()

# Show a plotly chart
label = app.show_plotly(fig, title="My Chart")

# After the window is open, you can emit events to manipulate the DOM:

# Update theme dynamically
app.emit("pywry:update-theme", {"theme": "plotly_white"}, label)

# Inject CSS dynamically
app.emit("pywry:inject-css", {
    "css": ".my-class { color: red; font-weight: bold; }",
    "id": "my-dynamic-styles"  # Optional: allows replacing later
}, label)

# Update element styles by ID
app.emit("pywry:set-style", {
    "id": "status-badge",
    "styles": {"backgroundColor": "green", "color": "white"}
}, label)

# Or by CSS selector (updates all matching elements)
app.emit("pywry:set-style", {
    "selector": ".highlight-row",
    "styles": {"backgroundColor": "#ffffcc"}
}, label)

# Update element content by ID
app.emit("pywry:set-content", {
    "id": "values-display",
    "html": "<strong>Updated!</strong> 42 items"
}, label)

# Or use plain text (safer, no HTML parsing)
app.emit("pywry:set-content", {
    "selector": ".status-text",
    "text": "Processing complete"
}, label)

# Trigger a CSV download
app.emit("pywry:download", {
    "content": "name,age\nAlice,30\nBob,25",
    "filename": "users.csv",
    "mimeType": "text/csv"
}, label)
```

> **Note:** For notebook mode, use `widget.emit("pywry:...", {...})` on the returned widget instead.
> `pywry:set-style` and `pywry:set-content` support either `id` (for a single element by ID) or `selector` (for multiple elements via CSS selector). If both are provided, `id` takes precedence.

### Toast Notifications (`pywry:alert`)

<details>
<summary>Complete alert system documentation with examples</summary>

PyWry provides a unified toast notification system that works consistently across all rendering paths (native window, notebook, and browser). Toast notifications are non-blocking (except `confirm` type) and support multiple types with automatic dismiss behavior.

#### Alert Types

| Type | Icon | Default Behavior | Use Case |
|------|------|------------------|----------|
| `info` | ℹ️ | Auto-dismiss 5s | Status updates, general information |
| `success` | ✅ | Auto-dismiss 3s | Completed actions, confirmations |
| `warning` | ⚠️ | Persist until clicked | Important notices requiring attention |
| `error` | ⛔ | Persist until clicked | Errors requiring acknowledgment |
| `confirm` | ❓ | Blocks UI until response | User confirmation needed before action |

#### AlertPayload Model

```python
from pydantic import BaseModel, Field
from typing import Literal

class AlertPayload(BaseModel):
    message: str  # Required - alert message text
    type: Literal["info", "success", "warning", "error", "confirm"] = "info"
    title: str | None = None  # Optional title/header
    duration: int | None = None  # Auto-dismiss ms (None uses type default)
    callback_event: str | None = None  # Event to emit on confirm/cancel
    position: Literal["top-right", "bottom-right", "bottom-left", "top-left"] = "top-right"
```

#### Using the Convenience Method

```python
from pywry import PyWry

app = PyWry()
label = app.show_plotly(fig, title="My Chart")

# Info toast (auto-dismisses after 5s)
app.alert("Data loaded successfully", alert_type="info", label=label)

# Success toast (auto-dismisses after 3s)
app.alert("Export complete!", alert_type="success", label=label)

# Warning toast (persists until clicked)
app.alert("No items selected", alert_type="warning", title="Selection Required", label=label)

# Error toast (persists until clicked)
app.alert("Connection failed", alert_type="error", title="Network Error", label=label)

# Confirm dialog with callback
app.alert(
    "Are you sure you want to delete?",
    alert_type="confirm",
    callback_event="user:confirm-delete",
    label=label
)

# Handle the confirm response
@app.on("user:confirm-delete")
def handle_confirm(data, event_type, label):
    if data.get("confirmed"):
        print("User confirmed deletion")
    else:
        print("User cancelled")
```

#### Using emit() Directly

```python
# Same as app.alert() but with explicit event emission
app.emit("pywry:alert", {
    "message": "Processing complete",
    "type": "success",
    "title": "Done",
    "duration": 4000,  # Override auto-dismiss time (ms)
    "position": "bottom-right"  # top-right, top-left, bottom-right, bottom-left
}, label)
```

#### Confirm Dialogs with Blocking Overlay

The `confirm` type creates a blocking overlay that prevents interaction with the content area until the user responds. This ensures critical confirmations are addressed before proceeding:

```python
from pywry import PyWry, Toolbar, Button

app = PyWry()

def on_delete(data, event_type, label):
    """Show confirmation before deleting."""
    app.alert(
        "This action cannot be undone. Are you sure?",
        alert_type="confirm",
        title="Delete Item",
        callback_event="app:confirm-delete",
        label=label
    )

def on_confirm_delete(data, event_type, label):
    """Handle the confirm/cancel response."""
    if data.get("confirmed"):
        # User clicked Confirm
        app.alert("Item deleted", alert_type="success", label=label)
    else:
        # User clicked Cancel or pressed Escape
        app.alert("Deletion cancelled", alert_type="info", label=label)

toolbar = Toolbar(
    position="top",
    items=[Button(label="Delete", event="app:delete", variant="danger")]
)

label = app.show(
    "<h1>My Content</h1>",
    toolbars=[toolbar],
    callbacks={
        "app:delete": on_delete,
        "app:confirm-delete": on_confirm_delete
    }
)
```

#### Toast Positions

Toasts can be positioned in any corner of the widget container:

| Position | Description |
|----------|-------------|
| `top-right` | Top-right corner (default) |
| `top-left` | Top-left corner |
| `bottom-right` | Bottom-right corner |
| `bottom-left` | Bottom-left corner |

```python
# Position toast in different corners
app.emit("pywry:alert", {"message": "Top right", "position": "top-right"}, label)
app.emit("pywry:alert", {"message": "Bottom left", "position": "bottom-left"}, label)
```

#### Multiple Toasts and Stacking

Multiple toasts stack vertically in their position container. New toasts appear at the top of the stack. When a toast is dismissed, remaining toasts stay in position without animation to prevent jarring visual effects.

```python
# Show multiple toasts - they stack
app.alert("First message", alert_type="info", label=label)
app.alert("Second message", alert_type="success", label=label)
app.alert("Third message", alert_type="warning", label=label)
```

#### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Escape` | Dismiss all visible toasts in the widget |

#### JavaScript API (Advanced)

The toast system exposes a global `PYWRY_TOAST` object for custom JavaScript integrations:

```javascript
// Show a toast programmatically
window.PYWRY_TOAST.show({
    message: "Hello from JS",
    type: "info",
    title: "Custom Title",
    duration: 5000,
    position: "top-right",
    container: document.querySelector('.pywry-widget')
});

// Show a confirm dialog
window.PYWRY_TOAST.confirm({
    message: "Are you sure?",
    title: "Confirm",
    position: "top-right",
    container: document.querySelector('.pywry-widget'),
    onConfirm: function() { console.log("Confirmed"); },
    onCancel: function() { console.log("Cancelled"); }
});

// Dismiss a specific toast by ID
window.PYWRY_TOAST.dismiss(toastId);

// Dismiss all toasts in a widget
window.PYWRY_TOAST.dismissAllInWidget(container);
```

</details>

### Plotly Events (`plotly:*`)

#### Events from JavaScript → Python (User Interactions)

These events fire automatically when users interact with Plotly charts:

| Event | Trigger | Payload |
|-------|---------|---------|
| `plotly:click` | User clicks a data point | `{ chartId, widget_type, points: [...], point_indices: [...], curve_number, event }` |
| `plotly:hover` | User hovers over a point | `{ chartId, widget_type, points: [...], point_indices: [...], curve_number }` |
| `plotly:selected` | User selects with box/lasso | `{ chartId, widget_type, points: [...], point_indices: [...], range, lassoPoints }` |
| `plotly:relayout` | User zooms, pans, or resizes | `{ chartId, widget_type, relayout_data: {...} }` |
| `plotly:state-response` | Response to state request | `{ chartId, layout: {...}, data: [...] }` |

> **Note:** All Plotly events include `chartId` and `widget_type: "chart"` in the payload for identifying which chart triggered the event.

**`plotly:click` payload structure:**
```python
{
    "chartId": "chart_abc123",      # Unique chart identifier
    "widget_type": "chart",         # Always "chart" for Plotly events
    "points": [
        {
            "curveNumber": 0,       # Which trace (0-indexed)
            "pointNumber": 5,       # Which point in the trace (0-indexed)
            "pointIndex": 5,        # Same as pointNumber (Plotly alias)
            "x": 2.5,               # X value
            "y": 10.3,              # Y value
            "z": None,              # Z value (for 3D charts)
            "text": "label",        # Point text label (if any)
            "customdata": {...},    # Custom data attached to point
            "data": {...},          # Full trace data object
            "trace_name": "Series A"  # Name of the trace
        }
    ],
    "point_indices": [5],           # List of all pointNumber values
    "curve_number": 0,              # curveNumber of first point (convenience)
    "event": {...}                  # Original browser event
}
```

**Example:**

```python
from pywry import PyWry
import plotly.express as px

app = PyWry()

fig = px.scatter(px.data.iris(), x="sepal_width", y="sepal_length", color="species")

def on_chart_click(data, event_type, label):
    """Display clicked point coordinates in the chart title."""
    point = data["points"][0]
    app.emit("plotly:update-layout", {
        "layout": {"title": f"Clicked: ({point['x']:.2f}, {point['y']:.2f})"}
    }, label)

label = app.show_plotly(fig, title="Click any point", callbacks={"plotly:click": on_chart_click})
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
| `grid:row-selected` | Row selection changes | `{ gridId, widget_type, rows: [...] }` |
| `grid:cell-click` | User clicks a cell | `{ gridId, widget_type, rowIndex, colId, value, data }` |
| `grid:cell-edit` | User edits a cell | `{ gridId, widget_type, rowIndex, rowId, colId, oldValue, newValue, data }` |
| `grid:filter-changed` | Filter applied | `{ gridId, widget_type, filterModel }` |
| `grid:data-truncated` | Dataset truncated (client-side) | `{ gridId, widget_type, displayedRows, truncatedRows, message }` |
| `grid:mode` | Grid mode info (server-side) | `{ gridId, widget_type, mode, serverSide, totalRows, blockSize, message }` |
| `grid:request-page` | Server-side requests data block | `{ gridId, widget_type, startRow, endRow, sortModel, filterModel }` |
| `grid:state-response` | Response to state request | `{ gridId, columnState, filterModel, sortModel, context? }` |

> **Note:** All AgGrid events include `gridId` and `widget_type: "grid"` in the payload for identifying which grid triggered the event.

**`grid:row-selected` payload structure:**
```python
{
    "gridId": "grid_def456",      # Unique grid identifier
    "widget_type": "grid",        # Always "grid" for AgGrid events
    "rows": [
        {"name": "Alice", "age": 30, "city": "NYC"},
        {"name": "Bob", "age": 25, "city": "LA"}
    ]
}
```

**Example:**

```python
from pywry import PyWry
import pandas as pd

app = PyWry()

df = pd.DataFrame({"name": ["Alice", "Bob", "Carol"], "age": [30, 25, 35], "city": ["NYC", "LA", "SF"]})

def on_row_select(data, event_type, label):
    """Print selected row names."""
    rows = data["rows"]
    names = ", ".join(row["name"] for row in rows)
    print(f"Selected: {names}" if names else "No selection")

label = app.show_dataframe(
    df,
    callbacks={"grid:row-selected": on_row_select}
)
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

#### System Toolbar Events (Automatic)

These events are emitted automatically when users interact with toolbar chrome:

| Event | Direction | Payload | Description |
|-------|-----------|---------|-------------|
| `toolbar:collapse` | JS → Python | `{ componentId, collapsed: true }` | User collapsed a toolbar |
| `toolbar:expand` | JS → Python | `{ componentId, collapsed: false }` | User expanded a toolbar |
| `toolbar:resize` | JS → Python | `{ componentId, position, width, height }` | User resized a toolbar |

#### State Management Events

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
from pywry import PyWry, Toolbar, Button, Select, Option
import pandas as pd

app = PyWry()

# Sample data to export
data = pd.DataFrame({"name": ["Alice", "Bob"], "score": [95, 87]})

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

def on_export(data_evt, event_type, label):
    """Trigger a CSV download when export button is clicked."""
    app.emit("pywry:download", {
        "content": data.to_csv(index=False),
        "filename": "export.csv",
        "mimeType": "text/csv"
    }, label)

def on_theme_change(data_evt, event_type, label):
    """Apply the selected theme to the chart."""
    theme = "plotly_dark" if data_evt["value"] == "dark" else "plotly_white"
    app.emit("pywry:update-theme", {"theme": theme}, label)

label = app.show(
    "<h1>Dashboard</h1><p>Select a theme or export data.</p>",
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
from pywry import PyWry, Toolbar, Button
import pandas as pd

app = PyWry()

# Sample data
data = pd.DataFrame({"name": ["Alice", "Bob"], "score": [95, 87]})

def on_action(evt_data, event_type, label):
    """Handle export button clicks - different buttons trigger different formats."""
    fmt = evt_data.get("format", "csv")
    if fmt == "csv":
        content = data.to_csv(index=False)
        mime = "text/csv"
    else:
        content = data.to_json(orient="records")
        mime = "application/json"
    
    # Trigger download in the browser
    app.emit("pywry:download", {
        "content": content,
        "filename": f"data.{fmt}",
        "mimeType": mime
    }, label)

toolbar = Toolbar(
    position="top",
    items=[
        Button(label="Export CSV", event="app:export", data={"format": "csv"}),
        Button(label="Export JSON", event="app:export", data={"format": "json"}),
    ]
)

label = app.show(
    "<h1>Data Export</h1><p>Click a button to download.</p>",
    toolbars=[toolbar],
    callbacks={"app:export": on_action}
)
```

#### Custom JavaScript Events

Emit events from your own JavaScript code:

```python
from pywry import PyWry

app = PyWry()

def on_action(data, event_type, label):
    """Respond to button click by updating the UI."""
    received = data.get("value", 0)
    doubled = received * 2
    app.emit("pywry:set-content", {
        "id": "result",
        "text": f"Received {received}, doubled = {doubled}"
    }, label)

label = app.show("""
<button onclick="window.pywry.emit('app:my-action', {value: 42})">
    Click Me
</button>
<div id="result" style="margin-top:10px;">Click the button...</div>
""", callbacks={"app:my-action": on_action})
```

### Python → JS: Sending Events to JavaScript

To update the browser UI from Python, use `app.emit()` for native mode or `widget.emit()` for notebooks.

**Using Built-in Utility Events (recommended):**

```python
from pywry import PyWry

app = PyWry()
label = app.show("<div id='msg'>Hello</div>")

# Update content without any custom JavaScript
app.emit("pywry:set-content", {"id": "msg", "text": "Updated!"}, label)

# Notebook mode: widget.emit() on the returned widget
# widget.emit("pywry:set-content", {"id": "msg", "text": "Updated!"})
```

**Using Custom Events (requires JavaScript handler):**

```python
from pywry import PyWry

app = PyWry()
label = app.show("""
<div id='msg'>Hello</div>
<script>
window.pywry.on('app:update-message', function(data) {
    document.getElementById('msg').textContent = data.text;
});
</script>
""")

# Now your custom event has a handler
app.emit("app:update-message", {"text": "Updated!"}, label)
```

### Complete Two-Way Communication Example

```python
from pywry import PyWry

app = PyWry()

def handle_request(data, event_type, label):
    """Handle request from JavaScript and send response back."""
    result = {"items": [1, 2, 3], "total": 3}
    # Use app.emit() to send response back to JavaScript
    app.emit("app:response", result, label)

label = app.show("""
<button onclick="requestData()">Fetch Data</button>
<div id="result">Click the button to fetch data...</div>
<script>
function requestData() {
    window.pywry.emit('app:request-data', {});
}
window.pywry.on('app:response', function(data) {
    document.getElementById('result').textContent = 
        'Received ' + data.total + ' items: ' + JSON.stringify(data.items);
});
</script>
""", callbacks={"app:request-data": handle_request})
```

</details>

---

## Toolbar System

<details>
<summary>Click to expand</summary>

**In this section:** [Quick Start](#quick-start) · [Imports](#imports-1) · [Positions & Layout](#toolbar-positions--layout) · [Common Properties](#common-properties) · [Component Reference](#component-reference) · [Toolbar Container](#toolbar-container) · [Examples](#examples) · [State Management](#state-management)

---

PyWry provides a flexible toolbar system for adding interactive controls to any window. The toolbar system uses Pydantic models for type-safe configuration with auto-generated component IDs for state tracking.

### Quick Start

```python
from pywry import PyWry, Toolbar, Button, Select, Option

app = PyWry()

def on_save(data, event_type, label):
    """Flash a success message when save is clicked."""
    app.emit("pywry:set-style", {
        "id": "status",
        "styles": {"backgroundColor": "#22c55e", "color": "#fff"}
    }, label)
    app.emit("pywry:set-content", {"id": "status", "text": "Saved!"}, label)

def on_view_change(data, event_type, label):
    """Update heading to show current view mode."""
    view = data["value"]
    app.emit("pywry:set-content", {"id": "heading", "text": f"Current View: {view}"}, label)

toolbar = Toolbar(
    position="top",
    items=[
        Button(label="Save", event="app:save"),
        Select(
            label="View:",
            event="view:change",
            options=["Table", "Chart", "Map"],
            selected="Table",
        ),
    ],
)

label = app.show(
    '<h1 id="heading">Current View: Table</h1><div id="status" style="padding:8px;">Ready</div>',
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
│                       HEADER                            │ ← Full width, outermost
├───────┬─────────────────────────────────────────┬───────┤
│       │                  TOP                    │       │
│       ├─────────────────────────────────────────┤       │
│ LEFT  │                                         │ RIGHT │ ← Extend full height
│       │               CONTENT                   │       │   between header/footer
│       │          ┌─────────────┐                │       │
│       │          │   INSIDE    │  (overlay)     │       │
│       │          └─────────────┘                │       │
│       ├─────────────────────────────────────────┤       │
│       │                 BOTTOM                  │       │
├───────┴─────────────────────────────────────────┴───────┤
│                       FOOTER                            │ ← Full width, outermost
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
components_label = None  # Will hold the window label

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
        app.emit("pywry:set-content", {
            "id": "values-display",
            "html": " | ".join(parts)
        }, label)
    return handler

def on_theme_toggle(data, event_type, label):
    """Toggle between dark and light mode using built-in pywry event."""
    global current_theme
    current_theme = "light" if current_theme == "dark" else "dark"
    app.emit("pywry:update-theme", {"theme": current_theme}, label)

def on_title_size(data, event_type, label):
    """Change the title size using built-in pywry:set-style event."""
    sizes = {"sm": "16px", "md": "20px", "lg": "26px"}
    size = data.get("value", "md")
    # Use built-in pywry:set-style event to update element styles
    app.emit("pywry:set-style", {
        "id": "demo-title",
        "styles": {"fontSize": sizes.get(size, "20px")}
    }, label)

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
    app.emit("pywry:set-style", {
        "selector": ".pywry-input-label",
        "styles": style_map.get(style, style_map["normal"])
    }, label)

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
    app.emit("pywry:inject-css", {
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
            content="<h3 id='demo-title' style='margin: 0;'>&#x1F9E9; All Toolbar Components</h3>",
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
        Button(label="\u2600\uFE0F", event="demo:theme", variant="ghost", component_id="theme-toggle-btn"),
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
        Button(label="\u2699", event="demo:btn", data={"btn": "icon"}, variant="icon"),
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

components_label = app.show(
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
from pywry import PyWry, Toolbar, Select, Option

app = PyWry()

def on_state(data, event_type, label):
    """Display current toolbar state in the UI."""
    components = data.get("components", {})
    state_text = ", ".join(f"{k}: {v.get('value')}" for k, v in components.items())
    app.emit("pywry:set-content", {"id": "state", "text": f"State: {state_text}"}, label)

toolbar = Toolbar(
    position="top",
    toolbar_id="my-toolbar",
    items=[Select(event="app:mode", options=["A", "B", "C"], selected="A")]
)

label = app.show(
    '<div id="state">Click refresh to see state...</div>',
    toolbars=[toolbar],
    callbacks={"toolbar:state-response": on_state}
)

# Request toolbar state
app.emit("toolbar:request-state", {"toolbarId": "my-toolbar"}, label)
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
from pywry import PyWry, Toolbar, Button, Select, NumberInput

app = PyWry()

def on_reset(data, event_type, label):
    """Reset all toolbar values to defaults."""
    app.emit("toolbar:set-values", {
        "values": {"theme-select": "light", "zoom-input": 100}
    }, label)
    app.emit("pywry:set-content", {"id": "status", "text": "Reset to defaults!"}, label)

toolbar = Toolbar(
    position="top",
    items=[
        Select(event="app:theme", component_id="theme-select", options=["light", "dark"], selected="dark"),
        NumberInput(event="app:zoom", component_id="zoom-input", value=150, min=50, max=200),
        Button(label="Reset", event="app:reset"),
    ]
)

label = app.show(
    '<div id="status">Adjust settings above...</div>',
    toolbars=[toolbar],
    callbacks={"app:reset": on_reset}
)
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

## CSS Selectors and Theming

<details>
<summary>Click to expand</summary>

**In this section:** [Theme Classes](#theme-classes) · [Container Classes](#container-classes) · [Layout Wrappers](#layout-wrappers) · [Toolbar Classes](#toolbar-classes) · [Component Classes](#component-classes) · [Toast Classes](#toast-notification-classes) · [Component ID Targeting](#component-id-targeting) · [CSS Variables](#css-variables) · [Example](#example-custom-styling)

---

PyWry provides a consistent DOM structure across all rendering modes (HTML, Plotly, AgGrid). Understanding the class hierarchy enables precise styling and JavaScript targeting.

### Theme Classes

PyWry uses a dual-class theming system for maximum compatibility:

| Selector | Description |
|----------|-------------|
| `html.dark` | Dark theme on document root (native windows) |
| `html.light` | Light theme on document root (native windows) |
| `html.pywry-native` | Added to `<html>` in native window mode |
| `.pywry-theme-dark` | Dark theme on widget container (notebook/browser mode) |
| `.pywry-theme-light` | Light theme on widget container (notebook/browser mode) |
| `.pywry-theme-system` | System preference theme (follows `prefers-color-scheme`) |

> **Note:** In native windows, theme classes are applied to `<html>`. In notebooks/inline mode, they're applied to `.pywry-widget` for scoped styling that doesn't affect the notebook theme.

### Container Classes

| Selector | Description |
|----------|-------------|
| `.pywry-container` | Root container for native windows (full page, absolute positioned) |
| `.pywry-widget` | Root container for widgets in notebook/browser mode |
| `.pywry-content` | Flex container for user content (HTML/Chart/Grid), includes 16px padding |
| `.pywry-plotly` | Plotly chart container with border styling |
| `.pywry-grid` | AgGrid container element |
| `.plotly-graph-div` | Plotly's internal container (Plotly's own class) |

### Layout Wrappers

<details>
<summary>Wrapper hierarchy diagram and classes</summary>

Layout wrappers create the nested flexbox structure for toolbar positioning. They are applied in a specific order to create the visual hierarchy:

```
┌────────────────────────────────────────────────────────────────┐
│ .pywry-wrapper-header (column: header toolbar + rest)          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ .pywry-toolbar-header                                    │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ .pywry-wrapper-left (row: left toolbar + rest)           │  │
│  │  ┌───────┬────────────────────────────────────────────┐  │  │
│  │  │ .left │ .pywry-wrapper-right (row: rest + right)   │  │  │
│  │  │       │  ┌──────────────────────────────────┬────┐ │  │  │
│  │  │       │  │ .pywry-wrapper-top               │.rt │ │  │  │
│  │  │       │  │  ┌────────────────────────────┐  │    │ │  │  │
│  │  │       │  │  │ .pywry-toolbar-top         │  │    │ │  │  │
│  │  │       │  │  ├────────────────────────────┤  │    │ │  │  │
│  │  │       │  │  │ .pywry-wrapper-bottom      │  │    │ │  │  │
│  │  │       │  │  │  ┌──────────────────────┐  │  │    │ │  │  │
│  │  │       │  │  │  │ .pywry-wrapper-ins   │  │  │    │ │  │  │
│  │  │       │  │  │  │  ┌────────────────┐  │  │  │    │ │  │  │
│  │  │       │  │  │  │  │ .pywry-cont    │  │  │  │    │ │  │  │
│  │  │       │  │  │  │  │   (content)    │  │  │  │    │ │  │  │
│  │  │       │  │  │  │  └────────────────┘  │  │  │    │ │  │  │
│  │  │       │  │  │  │ .pywry-toolbar-ins   │  │  │    │ │  │  │
│  │  │       │  │  │  └──────────────────────┘  │  │    │ │  │  │
│  │  │       │  │  │ .pywry-toolbar-bottom      │  │    │ │  │  │
│  │  │       │  │  └────────────────────────────┘  │    │ │  │  │
│  │  │       │  └──────────────────────────────────┴────┘ │  │  │
│  │  └───────┴────────────────────────────────────────────┘  │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ .pywry-toolbar-footer                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

| Selector | Description |
|----------|-------------|
| `.pywry-wrapper-header` | Outermost wrapper; column layout for header/footer toolbars |
| `.pywry-wrapper-left` | Row layout; left toolbar extends full height |
| `.pywry-wrapper-right` | Row layout; right toolbar extends full height |
| `.pywry-wrapper-top` | Column layout; top toolbar is inside left/right |
| `.pywry-wrapper-bottom` | Column layout; bottom toolbar is inside left/right |
| `.pywry-wrapper-inside` | Innermost wrapper; positions inside toolbar as overlay |

> **Nesting Behavior:** Wrappers are nested based on which toolbars are present. If you only have `top` and `bottom` toolbars, only `.pywry-wrapper-top` and `.pywry-wrapper-bottom` are created (no left/right wrappers). The `header` and `footer` positions are always outermost when present.

</details>

### Toolbar Classes

| Selector | Description |
|----------|-------------|
| `.pywry-toolbar` | Base toolbar container with flex layout |
| `.pywry-toolbar-header` | Full-width toolbar at page top, with bottom border |
| `.pywry-toolbar-footer` | Full-width toolbar at page bottom, with top border |
| `.pywry-toolbar-top` | Toolbar above content, inside left/right toolbars |
| `.pywry-toolbar-bottom` | Toolbar below content, inside left/right toolbars |
| `.pywry-toolbar-left` | Vertical toolbar on left, full height, with right border |
| `.pywry-toolbar-right` | Vertical toolbar on right, full height, with left border |
| `.pywry-toolbar-inside` | Floating toolbar overlay at top-right of content |
| `.pywry-toolbar-content` | Inner container for toolbar items |
| `.pywry-toolbar-toggle` | Collapse/expand button for collapsible toolbars |
| `.pywry-toggle-icon` | Arrow icon inside toggle button |
| `.pywry-collapsed` | State class for collapsed toolbars |
| `.pywry-resize-handle` | Drag handle for resizable toolbars |

### Component Classes

<details>
<summary>All component selectors (Buttons, Inputs, Dropdowns, Toggle, Radio, Tabs, Div)</summary>

#### Buttons

| Selector | Description |
|----------|-------------|
| `.pywry-btn` | Base button with primary styling |
| `.pywry-btn-primary` | Primary button (default) - accent background |
| `.pywry-btn-secondary` | Secondary button - subtle gray background |
| `.pywry-btn-neutral` | Neutral button - blue accent, always visible |
| `.pywry-btn-ghost` | Ghost button - transparent, text only |
| `.pywry-btn-outline` | Outline button - border only, no fill |
| `.pywry-btn-danger` | Danger button - red background |
| `.pywry-btn-warning` | Warning button - orange background |
| `.pywry-btn-icon` | Icon-only button - square aspect ratio |
| `.pywry-btn-xs` | Extra small size |
| `.pywry-btn-sm` | Small size |
| `.pywry-btn-lg` | Large size |
| `.pywry-btn-xl` | Extra large size |

#### Inputs

| Selector | Description |
|----------|-------------|
| `.pywry-input` | Base input styling (text, number, date) |
| `.pywry-input-text` | Text input specific styling |
| `.pywry-input-number` | Number input with hidden spinners |
| `.pywry-input-date` | Date picker input |
| `.pywry-input-range` | Slider/range input |
| `.pywry-input-group` | Container with label + input |
| `.pywry-input-inline` | Horizontal label + input layout |
| `.pywry-input-label` | Label text styling |
| `.pywry-number-wrapper` | Number input with custom spinner buttons |
| `.pywry-number-spinner` | Custom up/down spinner container |
| `.pywry-range-value` | Current value display for sliders |
| `.pywry-range-group` | Dual-range slider container |
| `.pywry-range-track` | Track element for range sliders |
| `.pywry-range-separator` | "–" separator between min/max values |

#### Dropdowns & Select

| Selector | Description |
|----------|-------------|
| `.pywry-select` | Native `<select>` element styling |
| `.pywry-dropdown` | Custom dropdown container |
| `.pywry-dropdown-selected` | Selected value display area |
| `.pywry-dropdown-text` | Text inside selected area |
| `.pywry-dropdown-arrow` | Chevron arrow indicator |
| `.pywry-dropdown-menu` | Dropdown options popup |
| `.pywry-dropdown-option` | Individual option in dropdown |
| `.pywry-dropdown-up` | Opens dropdown upward (for bottom toolbars) |
| `.pywry-open` | State class when dropdown is expanded |
| `.pywry-selected` | Selected state for options |
| `.pywry-disabled` | Disabled state for dropdowns |

#### Multi-Select

| Selector | Description |
|----------|-------------|
| `.pywry-multiselect` | Multi-select dropdown container |
| `.pywry-multiselect-header` | Header with search and actions |
| `.pywry-multiselect-search` | Search input in header |
| `.pywry-multiselect-actions` | Select All / Clear buttons container |
| `.pywry-multiselect-action` | Individual action button |
| `.pywry-multiselect-options` | Scrollable options container |
| `.pywry-multiselect-option` | Individual option row |
| `.pywry-multiselect-checkbox` | Checkbox input |
| `.pywry-multiselect-label` | Option label text |

#### Toggle & Checkbox

| Selector | Description |
|----------|-------------|
| `.pywry-toggle` | Toggle switch container |
| `.pywry-toggle-input` | Hidden checkbox input |
| `.pywry-toggle-slider` | Visual slider track |
| `.pywry-checkbox` | Checkbox container |
| `.pywry-checkbox-input` | Hidden checkbox input |
| `.pywry-checkbox-box` | Visual checkbox square |
| `.pywry-checkbox-label` | Checkbox label text |

#### Radio Group

| Selector | Description |
|----------|-------------|
| `.pywry-radio-group` | Radio button group container |
| `.pywry-radio-horizontal` | Horizontal layout |
| `.pywry-radio-vertical` | Vertical layout |
| `.pywry-radio-option` | Individual radio option |
| `.pywry-radio-button` | Visual radio circle |
| `.pywry-radio-label` | Radio option label |

#### Tab Group

| Selector | Description |
|----------|-------------|
| `.pywry-tab-group` | Tab container with background |
| `.pywry-tab` | Individual tab button |
| `.pywry-tab-active` | Currently selected tab |
| `.pywry-tab-sm` | Small tab size variant (on `.pywry-tab-group`) |
| `.pywry-tab-lg` | Large tab size variant (on `.pywry-tab-group`) |
| `.pywry-tab-group.pywry-disabled` | Disabled state for entire tab group |

#### Div Container

| Selector | Description |
|----------|-------------|
| `.pywry-div` | Custom HTML container in toolbars |

#### State Classes

These reusable state classes can be combined with component classes:

| Selector | Description |
|----------|-------------|
| `.pywry-open` | Open/expanded state (dropdowns) |
| `.pywry-selected` | Selected state (dropdown options) |
| `.pywry-disabled` | Disabled state (buttons, dropdowns, inputs, tab groups) |
| `.pywry-collapsed` | Collapsed state (toolbars) |

</details>

### Toast Notification Classes

<details>
<summary>Toast container, type variants, overlay, and light theme classes</summary>

PyWry's toast notification system uses the following CSS classes. These are positioned absolutely within the widget container to stay scoped and not break out of the content area.

#### Container Classes

| Selector | Description |
|----------|-------------|
| `.pywry-toast-container` | Base container for toast stack, positioned absolutely |
| `.pywry-toast-container--top-right` | Positioned in top-right corner (default) |
| `.pywry-toast-container--top-left` | Positioned in top-left corner |
| `.pywry-toast-container--bottom-right` | Positioned in bottom-right corner |
| `.pywry-toast-container--bottom-left` | Positioned in bottom-left corner |
| `.pywry-toast-container--blocking` | Elevated z-index for confirm dialogs (above overlay) |

#### Toast Element Classes

| Selector | Description |
|----------|-------------|
| `.pywry-toast` | Base toast notification styling |
| `.pywry-toast__icon` | Toast icon container |
| `.pywry-toast__content` | Toast message content wrapper |
| `.pywry-toast__title` | Toast title/header text |
| `.pywry-toast__message` | Toast message body text |
| `.pywry-toast__close` | Close button (hidden on confirm type) |
| `.pywry-toast__buttons` | Button container for confirm dialogs |
| `.pywry-toast__btn` | Base button styling |
| `.pywry-toast__btn--cancel` | Cancel button styling |
| `.pywry-toast__btn--confirm` | Confirm button styling |

#### Type Variants

Each type sets the `--pywry-toast-accent` CSS variable for the left border color:

| Selector | Accent Color | Description |
|----------|--------------|-------------|
| `.pywry-toast--info` | `#0ea5e9` (sky blue) | Informational messages |
| `.pywry-toast--success` | `#22c55e` (green) | Success confirmations |
| `.pywry-toast--warning` | `#f59e0b` (amber) | Warning notices |
| `.pywry-toast--error` | `#ef4444` (red) | Error messages |
| `.pywry-toast--confirm` | `#6366f1` (indigo) | Confirmation dialogs |

#### Overlay Classes

| Selector | Description |
|----------|-------------|
| `.pywry-toast-overlay` | Semi-transparent overlay for blocking confirm dialogs |
| `.pywry-toast-overlay--visible` | Visible state with pointer-events enabled |

#### Theme Variants

| Selector | Description |
|----------|-------------|
| `.pywry-theme-light .pywry-toast` | Light theme styling for toasts |
| `.pywry-toast--light` | Explicit light theme class |

#### CSS Variables for Customization

```css
/* Customize toast appearance */
.pywry-toast {
    --pywry-toast-bg: rgba(30, 30, 30, 0.95);
    --pywry-toast-color: #ffffff;
    --pywry-toast-accent: #0ea5e9;
}

/* Light theme */
.pywry-theme-light .pywry-toast {
    --pywry-toast-bg: rgba(255, 255, 255, 0.95);
    --pywry-toast-color: #1f2937;
}
```

#### Example: Custom Toast Styling

```css
/* Make toasts wider */
.pywry-toast {
    max-width: 500px;
}

/* Custom accent color for all toasts */
.pywry-toast {
    --pywry-toast-accent: #8b5cf6;  /* Purple */
}

/* Custom success color */
.pywry-toast--success {
    --pywry-toast-accent: #10b981;  /* Emerald */
}

/* Rounded toast corners */
.pywry-toast {
    border-radius: 12px;
}

/* Style the confirm buttons */
.pywry-toast__btn--confirm {
    background-color: #22c55e;
}
```

</details>

### Component ID Targeting

<details>
<summary>ID patterns, targeting examples, and parent-child relationships</summary>

Every toolbar component has a unique `component_id` that becomes its HTML `id` attribute. This enables precise CSS and JavaScript targeting.

**Default ID Pattern:** `{type}-{8-char-random}`

| Component | ID Prefix | Example |
|-----------|-----------|---------|
| `Button` | `button-` | `button-a1b2c3d4` |
| `Select` | `select-` | `select-e5f6g7h8` |
| `MultiSelect` | `multiselect-` | `multiselect-i9j0k1l2` |
| `TextInput` | `text-` | `text-m3n4o5p6` |
| `NumberInput` | `number-` | `number-q7r8s9t0` |
| `DateInput` | `date-` | `date-u1v2w3x4` |
| `SliderInput` | `slider-` | `slider-y5z6a7b8` |
| `RangeInput` | `range-` | `range-c9d0e1f2` |
| `Toggle` | `toggle-` | `toggle-g3h4i5j6` |
| `Checkbox` | `checkbox-` | `checkbox-k7l8m9n0` |
| `RadioGroup` | `radio-` | `radio-o1p2q3r4` |
| `TabGroup` | `tabs-` | `tabs-s5t6u7v8` |
| `Div` | `div-` | `div-w9x0y1z2` |
| `Toolbar` | `toolbar-` | `toolbar-a3b4c5d6` |

**Custom IDs:** Set `component_id` explicitly for stable targeting:

```python
Button(label="Save", event="app:save", component_id="save-btn")
Toolbar(position="top", items=[...], component_id="main-toolbar")
```

**HTML Output:**

```html
<button class="pywry-btn" id="save-btn" data-event="app:save">Save</button>
<div class="pywry-toolbar pywry-toolbar-top" id="main-toolbar" data-component-id="main-toolbar">
```

**Targeting in CSS:**

```css
/* Target specific component by ID */
#save-btn { background: green; }

/* Target component type */
[id^="button-"] { font-weight: bold; }

/* Target by data attribute */
[data-event="app:save"] { border: 2px solid gold; }
```

**Targeting in JavaScript:**

```javascript
// Direct selection
document.getElementById('save-btn').style.display = 'none';

// Query by data attribute
document.querySelector('[data-event="app:save"]').click();
```

**Parent-Child Relationships:**

`Div` containers pass their `component_id` as `data-parent-id` to children:

```python
Div(
    component_id="actions-group",
    children=[
        Button(label="Edit", event="app:edit"),
        Button(label="Delete", event="app:delete", variant="danger"),
    ]
)
```

```html
<div class="pywry-div" id="actions-group" data-component-id="actions-group">
    <button class="pywry-btn" id="button-xyz123" data-parent-id="actions-group" ...>Edit</button>
    <button class="pywry-btn pywry-btn-danger" id="button-abc456" data-parent-id="actions-group" ...>Delete</button>
</div>
```

</details>

### CSS Variables

<details>
<summary>All CSS custom properties (colors, typography, spacing, transitions)</summary>

Customize these variables via `inline_css` or a custom theme CSS file:

```css
:root {
  /* ---- Color Palette (Dark Theme Default) ---- */
  --pywry-bg-primary: #212124;
  --pywry-bg-secondary: #1e1e1e;
  --pywry-bg-hover: rgba(255, 255, 255, 0.08);
  --pywry-bg-overlay: rgba(30, 30, 30, 0.8);
  --pywry-text-primary: #ebebed;
  --pywry-text-secondary: #a0a0a0;
  --pywry-border-color: #333;

  /* ---- Scrollbar Colors ---- */
  --pywry-scrollbar-thumb: #555;
  --pywry-scrollbar-thumb-hover: #777;
  --pywry-scrollbar-track: transparent;

  /* ---- Accent Colors ---- */
  --pywry-accent: #0078d4;
  --pywry-accent-hover: #106ebe;
  --pywry-accent-text: #ffffff;

  /* ---- Button Colors ---- */
  --pywry-btn-primary-bg: #e2e2e2;
  --pywry-btn-primary-text: #151518;
  --pywry-btn-primary-hover: #cccccc;
  --pywry-btn-secondary-bg: rgba(54, 54, 63, 1);
  --pywry-btn-secondary-text: #ebebed;
  --pywry-btn-secondary-hover: rgba(42, 42, 48, 1);
  --pywry-btn-secondary-border: rgba(70, 70, 79, 0.5);
  --pywry-btn-neutral-bg: rgb(0, 136, 204);
  --pywry-btn-neutral-text: #ffffff;
  --pywry-btn-neutral-hover: rgb(0, 115, 173);

  /* ---- Tab Group Colors ---- */
  --pywry-tab-bg: #2a2a2e;
  --pywry-tab-active-bg: #3d3d42;
  --pywry-tab-hover-bg: #353538;

  /* ---- Typography ---- */
  --pywry-font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --pywry-font-size: 14px;
  --pywry-font-weight-normal: 400;
  --pywry-font-weight-medium: 500;

  /* ---- Spacing & Layout ---- */
  --pywry-radius: 4px;
  --pywry-radius-lg: 6px;
  --pywry-spacing-xs: 2px;
  --pywry-spacing-sm: 4px;
  --pywry-spacing-md: 6px;
  --pywry-spacing-lg: 8px;

  /* ---- Widget Sizing ---- */
  --pywry-widget-width: 100%;
  --pywry-widget-min-height: 200px;
  --pywry-widget-height: 500px;
  --pywry-grid-min-height: 200px;

  /* ---- Focus & Borders ---- */
  --pywry-border-focus: #555;

  /* ---- Transitions ---- */
  --pywry-transition-fast: 0.1s ease;
  --pywry-transition-normal: 0.2s ease;
}

/* ---- Light Theme Overrides ---- */
html.light, .pywry-theme-light {
  --pywry-bg-primary: #f5f5f5;
  --pywry-bg-secondary: #ffffff;
  --pywry-bg-hover: rgba(0, 0, 0, 0.06);
  --pywry-text-primary: #000000;
  --pywry-text-secondary: #666666;
  --pywry-border-color: #ccc;
  --pywry-scrollbar-thumb: #bbb;
  --pywry-scrollbar-thumb-hover: #999;
  --pywry-border-focus: #999;
  --pywry-tab-bg: #e8e8ec;
  --pywry-tab-active-bg: #ffffff;
  --pywry-tab-hover-bg: #f0f0f4;
  --pywry-btn-primary-bg: #2c2c32;
  --pywry-btn-primary-text: #ffffff;
  --pywry-btn-primary-hover: #1a1a1e;
  --pywry-btn-secondary-bg: #ffffff;
  --pywry-btn-secondary-text: #2c2c32;
  --pywry-btn-secondary-hover: #f3f3f6;
  --pywry-btn-secondary-border: rgba(215, 215, 222, 1);
}
```

</details>

### Example: Custom Styling with Built-in Events

```python
from pywry import PyWry, Toolbar, Button

app = PyWry()

def on_click(data, event_type, label):
    """Change the button to green when clicked."""
    app.emit("pywry:set-style", {
        "id": "my-btn",
        "styles": {"backgroundColor": "#22c55e", "color": "#fff"}
    }, label)

label = app.show(
    '<div id="status" style="padding:20px;">Click the button to change its color</div>',
    toolbars=[Toolbar(position="top", items=[
        Button(label="Click Me", event="app:click", component_id="my-btn")
    ])],
    callbacks={"app:click": on_click}
)
```

</details>

---

## JavaScript Bridge

<details>
<summary>Click to expand</summary>

**In this section:** [Available Methods](#available-methods) · [Injected Globals](#injected-globals) · [AgGrid API](#accessing-aggrid-api) · [Plotly API](#accessing-plotly-api) · [Toolbar API](#accessing-toolbar-api) · [Toast Notifications](#using-toast-notifications) · [Two-Way Communication](#example-two-way-communication) · [System Event Handlers](#built-in-system-event-handlers)

---

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
// ─────────────────────────────────────────────────────────────────────────────
// CORE GLOBALS (always present)
// ─────────────────────────────────────────────────────────────────────────────

window.__PYWRY_LABEL__          // Window label, e.g., "main-window"
window.json_data                // JSON data from Python (via HtmlContent.json_data)

// ─────────────────────────────────────────────────────────────────────────────
// PLOTLY GLOBALS (when include_plotly=True)
// ─────────────────────────────────────────────────────────────────────────────

window.__PYWRY_PLOTLY_DIV__     // Reference to main Plotly chart container
window.__PYWRY_CHARTS__         // Registry of all Plotly charts by ID
window.PYWRY_PLOTLY_TEMPLATES   // Bundled templates: ggplot2, seaborn, simple_white,
                                // plotly, plotly_white, plotly_dark, presentation,
                                // xgridoff, ygridoff, gridon

// ─────────────────────────────────────────────────────────────────────────────
// AGGRID GLOBALS (when include_aggrid=True)
// ─────────────────────────────────────────────────────────────────────────────

window.__PYWRY_GRID_API__       // Main AgGrid API for the primary grid
window.__PYWRY_GRIDS__          // Registry of all grid instances by ID
window.PYWRY_SHOW_NOTIFICATION  // Helper: PYWRY_SHOW_NOTIFICATION(msg, duration, container)

// ─────────────────────────────────────────────────────────────────────────────
// TOOLBAR GLOBALS (when toolbar is rendered)
// ─────────────────────────────────────────────────────────────────────────────

window.__PYWRY_TOOLBAR__        // Toolbar API: { getState(), getValue(id), setValue(id, val) }

// ─────────────────────────────────────────────────────────────────────────────
// TOAST NOTIFICATION SYSTEM
// ─────────────────────────────────────────────────────────────────────────────

window.PYWRY_TOAST              // Toast API: show(type, message, options), dismiss(id), clear()
                                // Types: 'info', 'success', 'warning', 'error', 'confirm'
```

### Accessing AgGrid API

```javascript
// ── Primary Grid API ──────────────────────────────────────────────────────────
// Get selected rows
const rows = window.__PYWRY_GRID_API__.getSelectedRows();

// Update data
window.__PYWRY_GRID_API__.setGridOption('rowData', newData);

// Apply transactions
window.__PYWRY_GRID_API__.applyTransaction({ update: [row1, row2] });

// Export to CSV
window.__PYWRY_GRID_API__.exportDataAsCsv();

// ── Multi-Grid Access ─────────────────────────────────────────────────────────
// Access any grid by its ID
const grid = window.__PYWRY_GRIDS__['my-grid-id'];
if (grid) {
    grid.api.getSelectedRows();
}

// Show a notification toast
window.PYWRY_SHOW_NOTIFICATION('Data updated!', 3000);
```

### Accessing Plotly API

```javascript
// ── Primary Chart API ─────────────────────────────────────────────────────────
// Update chart layout
Plotly.relayout(window.__PYWRY_PLOTLY_DIV__, { title: 'New Title' });

// Update chart data
Plotly.react(window.__PYWRY_PLOTLY_DIV__, newData, newLayout);

// Apply template
Plotly.update(window.__PYWRY_PLOTLY_DIV__, {}, {
    template: window.PYWRY_PLOTLY_TEMPLATES['seaborn']
});

// ── Multi-Chart Access ────────────────────────────────────────────────────────
// Access any chart by its ID
const chart = window.__PYWRY_CHARTS__['my-chart-id'];
if (chart) {
    Plotly.relayout(chart, { title: 'Updated' });
}
```

### Accessing Toolbar API

```javascript
// Get current state of all toolbar components
const state = window.__PYWRY_TOOLBAR__.getState();
// { "theme-select": "dark", "zoom-slider": 100 }

// Get value of a specific component by ID
const theme = window.__PYWRY_TOOLBAR__.getValue('theme-select');

// Set value of a component (triggers change event)
window.__PYWRY_TOOLBAR__.setValue('zoom-slider', 150);
```

### Using Toast Notifications

```javascript
// Show different toast types
window.PYWRY_TOAST.show('info', 'Processing your request...');
window.PYWRY_TOAST.show('success', 'Changes saved!');
window.PYWRY_TOAST.show('warning', 'This action cannot be undone');
window.PYWRY_TOAST.show('error', 'Failed to connect to server');

// Confirmation dialog with callback
window.PYWRY_TOAST.show('confirm', 'Delete this item?', {
    onConfirm: function() { deleteItem(); },
    onCancel: function() { console.log('Cancelled'); }
});

// Dismiss all toasts
window.PYWRY_TOAST.clear();
```

### Example: Two-Way Communication

```python
from pywry import PyWry

app = PyWry()

def handle_request(data, event_type, label):
    """Send response back to JavaScript."""
    app.emit("app:response", {"items": [1, 2, 3]}, label)

label = app.show("""
<button onclick="requestData()">Fetch Data</button>
<div id="result">Click the button...</div>
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
from pywry import PyWry

app = PyWry()

# Create a window first
label = app.show("""
<div id="message">Hello</div>
<div id="counter">0</div>
<span class="count">initial</span>
""")

# Theme switching (updates Plotly templates, AgGrid themes, and CSS classes)
app.emit("pywry:update-theme", {"theme": "light"}, label)

# Inject CSS dynamically (with optional id for replacement)
app.emit("pywry:inject-css", {"css": ".status { color: green; }", "id": "status-css"}, label)

# Update element styles by id
app.emit("pywry:set-style", {"id": "counter", "styles": {"fontSize": "24px", "fontWeight": "bold"}}, label)

# Update element content by id
app.emit("pywry:set-content", {"id": "message", "html": "<strong>Success!</strong>"}, label)

# Update element content by CSS selector
app.emit("pywry:set-content", {"selector": ".count", "text": "42"}, label)
```

See [Utility Events (Python → JS)](#utility-events-python-to-js) for complete documentation.

</details>

---

## Direct Tauri API Access

<details>
<summary>Click to expand</summary>

**In this section:** [`__TAURI__` Global](#the-__tauri__-global) · [PyTauri IPC](#pytauri-ipc-python--javascript) · [Listening to Events](#listening-to-python-events-javascript) · [Tauri Events](#tauri-internal-events-advanced) · [Custom Handler](#example-custom-tauri-handler) · [Environment Detection](#environment-detection)

---

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

app = PyWry()

def on_button_click(data, event_type, label):
    """Handle button click from JavaScript and send response."""
    count = data.get("count", 0)
    print(f'Received click #{count}')
    app.emit('custom:update', {'message': f'Hello from Python! Count: {count}'}, label)

label = app.show('''
<div id="output">Click the button...</div>
<button onclick="sendToPython()">Send to Python</button>
<script>
var count = 0;
window.pywry.on('custom:update', function(data) {
    document.getElementById('output').textContent = data.message;
});
function sendToPython() {
    count++;
    window.pywry.emit('custom:button-click', { count: count });
}
</script>
''', callbacks={'custom:button-click': on_button_click})
```

> **Note:** The `window.pywry` bridge is automatically initialized by PyWry. Use `window.pywry.on()` to listen for events from Python, and `window.pywry.emit()` to send events to Python. Native mode returns a string label - use `app.emit()` to send events. Notebook mode returns a widget with `.emit()`.

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

The `show_*()` methods return widget objects that provide a unified API:

| Mode | `show_*()` Returns | Control Via |
|------|-------------------|-------------|
| `NEW_WINDOW`, `SINGLE_WINDOW`, `MULTI_WINDOW` | `str` (label) | `app.emit(event, data, label)`, `app.close(label)` |
| `NOTEBOOK`, `BROWSER` | `BaseWidget` (PyWryWidget/InlineWidget) | `widget.emit(...)`, `widget.on(...)`, `widget.update(...)` |

**Native mode:** use `app.emit(event, data, label)` to send events to JavaScript.
**Notebook mode:** use `widget.emit(event, data)` on the returned widget.

---

### Native Window Management

In native modes, `show_*()` returns a **string label** that identifies the window:

```python
from pywry import PyWry, WindowMode
import plotly.express as px
import pandas as pd

app = PyWry(mode=WindowMode.MULTI_WINDOW)

fig = px.scatter(px.data.iris(), x="sepal_width", y="sepal_length")
df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})

# Each show_*() returns a unique window label (str)
label1 = app.show_plotly(fig, title="Chart 1")
label2 = app.show_dataframe(df, title="Data")
label3 = app.show("<h1 id='heading'>Custom</h1>", title="Custom")

# Send built-in events using app.emit() with the label
app.emit("pywry:set-content", {"id": "heading", "text": "Updated!"}, label3)

# Close a specific window by label
app.close(label1)
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
# Update content using built-in utility event
app.emit("pywry:set-content", {"id": "heading", "text": "Hello!"}, label1)

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
import plotly.express as px

app = PyWry(mode=WindowMode.NOTEBOOK)

fig = px.scatter(px.data.iris(), x="sepal_width", y="sepal_length", color="species")

# show_*() returns a widget object (not a string)
widget = app.show_plotly(fig, title="Interactive Chart")

# The widget has a label property for identification
# widget.label  # "w-abc12345"
```

#### Widget Properties

| Property | Type | Description |
|----------|------|-------------|
| `widget.label` | `str` | Unique identifier (e.g., `"w-abc12345"`) |
| `widget.url` | `str` | Full URL to access in a browser (e.g., `"http://localhost:8765/widget/w-abc12345"`) |
| `widget.output` | `Output` | IPython Output widget for callback print statements |

#### Registering Event Handlers

```python
def on_click(data, event_type, label):
    """Update the chart title when a point is clicked."""
    point = data["points"][0]
    widget.emit("plotly:update-layout", {
        "layout": {"title": f"Clicked: ({point['x']:.2f}, {point['y']:.2f})"}
    })

def handle_action(data, event_type, label):
    """Handle custom action by updating status."""
    widget.emit("pywry:set-content", {"id": "status", "text": "Action complete!"})

# Register handlers — method chaining supported
widget.on("plotly:click", on_click)
widget.on("custom:action", handle_action)

# Chaining works too
widget.on("plotly:click", on_click).on("plotly:hover", on_hover)
```

#### Sending Events to JavaScript

```python
# Update theme using built-in utility event
widget.emit("pywry:update-theme", {"theme": "plotly_dark"})

# Or update content
widget.emit("pywry:set-content", {"id": "status", "text": "Updated!"})
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

**In this section:** [Getting Widget URL](#getting-the-widget-url) · [Server Configuration](#server-configuration) · [Environment Variables](#environment-variables) · [Production Deployment](#production-deployment-pattern) · [HTTPS](#https-configuration) · [Health Check](#server-health-check) · [WebSocket & API Security](#websocket--api-security)

---

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

# WebSocket Security
websocket_allowed_origins = [] # Allowed origins for WebSocket (empty = any, rely on token)
websocket_require_token = true # Require per-widget token for WebSocket auth

# Internal API Security
internal_api_header = "X-PyWry-Token"  # Header name for internal auth
internal_api_token = ""                # Auto-generated if not set
strict_widget_auth = false             # false = notebook (lenient), true = browser (strict)
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

# WebSocket Security
export PYWRY_SERVER__WEBSOCKET_ALLOWED_ORIGINS='http://localhost:8080,https://app.example.com'
export PYWRY_SERVER__WEBSOCKET_REQUIRE_TOKEN=true

# Internal API Security
export PYWRY_SERVER__INTERNAL_API_HEADER=X-PyWry-Token
export PYWRY_SERVER__INTERNAL_API_TOKEN=my-secret-token  # Or leave empty for auto-gen
export PYWRY_SERVER__STRICT_WIDGET_AUTH=true  # Browser mode (stricter)
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
Static Route           View Factory           Widget Instance
──────────────         ──────────────         ─────────────────
GET /dashboard    →    create_dashboard()  →  /widget/{unique_id}
GET /analytics    →    create_analytics()  →  /widget/{unique_id}
GET /sales        →    create_sales()      →  /widget/{unique_id}
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
        callbacks={"grid:row-selected": handle_row_select},
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
# Use runtime.emit_event(label, event, data) when widget reference unavailable
# ═══════════════════════════════════════════════════════════

def handle_export(data, event_type, label):
    """Handle export request from any sales dashboard."""
    # Use label to target the correct widget
    from pywry import runtime
    runtime.emit_event(label, "pywry:set-content", {"id": "status", "text": "Exporting..."})
    # ... do export work ...
    runtime.emit_event(label, "pywry:set-content", {"id": "status", "text": "Export complete!"})

def handle_row_select(data, event_type, label):
    """Handle row selection from any inventory grid."""
    from pywry import runtime
    selected = data.get("selected_rows", [])
    runtime.emit_event(label, "pywry:set-content", {
        "id": "selection-count",
        "text": f"Selected {len(selected)} rows"
    })

def handle_chart_click(data, event_type, label):
    """Handle chart click from any analytics dashboard."""
    from pywry import runtime
    point = data.get("points", [{}])[0]
    runtime.emit_event(label, "pywry:set-content", {
        "id": "click-info",
        "text": f"Clicked: ({point.get('x')}, {point.get('y')})"
    })

def refresh_analytics(data, event_type, label):
    """Refresh analytics for a specific widget."""
    from pywry import runtime
    runtime.emit_event(label, "pywry:set-content", {"id": "status", "text": "Refreshing..."})
    # ... refresh logic ...
    runtime.emit_event(label, "pywry:set-content", {"id": "status", "text": "Data refreshed!"})

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
from pywry import PyWry, WindowMode

# Create a global app instance for browser mode
app = PyWry(mode=WindowMode.BROWSER)

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
    widget = app.show_plotly(fig, title="Sales", open_browser=True)
    
    # Track the session
    manager.create(widget.label, "sales", user_id)
    
    return widget.label

# Use in event handlers
def handle_filter_change(data, event_type, label):
    """Update state and show feedback in the widget."""
    from pywry import runtime
    
    manager.update_state(label, "filters", data)
    session = manager.get(label)
    
    if session:
        # Show visual feedback in the widget
        runtime.emit_event(label, "pywry:set-content", {
            "id": "filter-status",
            "text": f"Filters updated for {session.user_id}"
        })
```

#### Cleanup on Disconnect

Register a disconnect callback to clean up sessions:

```python
from pywry import PyWry, WindowMode
import plotly.express as px
from datetime import datetime

app = PyWry(mode=WindowMode.BROWSER)
fig = px.scatter(px.data.iris(), x="sepal_width", y="sepal_length", color="species")

def on_disconnect(data, event_type, label):
    """Called when widget WebSocket disconnects - cleanup resources."""
    session = manager.get(label)
    if session:
        manager.remove(label)

def handle_click(data, event_type, label):
    """Show clicked point info in the chart title."""
    point = data.get("points", [{}])[0]
    # In BROWSER mode, show_plotly returns a widget, but the callback
    # receives the label parameter, so we can use app.emit()
    app.emit("plotly:update-layout", {
        "layout": {"title": f"Clicked: ({point.get('x')}, {point.get('y')})"}
    }, label)

widget = app.show_plotly(fig, callbacks={
    "pywry:disconnect": on_disconnect,
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

> **Note:** The `/health` endpoint requires internal API authentication when accessed externally. Python code using `_make_server_request()` automatically includes the required header.

### WebSocket & API Security

PyWry implements a multi-layer security model for WebSocket connections and internal API endpoints.

#### Security Model Overview

| Layer | Setting | Purpose |
|-------|---------|---------|
| **Origin Validation** | `websocket_allowed_origins` | Restrict which origins can connect via WebSocket |
| **Per-Widget Tokens** | `websocket_require_token` | Each widget gets a unique token embedded in HTML |
| **Internal API Auth** | `internal_api_header/token` | Protect internal endpoints from external access |
| **Widget Auth Mode** | `strict_widget_auth` | Browser (strict) vs Notebook (lenient) security |

#### Per-Widget Token Authentication

Each widget instance generates a unique short-lived token that's embedded in its HTML:

```python
# Token flow (automatic, no user code needed):
# 1. show_plotly() creates widget with unique ID
# 2. Server generates token, stores in widget_tokens[id]
# 3. Token embedded in HTML as window.PYWRY_TOKEN
# 4. JavaScript sends token via Sec-WebSocket-Protocol header
# 5. Server validates token on WebSocket upgrade
```

The token is passed during WebSocket handshake via the `Sec-WebSocket-Protocol` header, ensuring it's not exposed in URLs or browser history.

#### Allowed Origins

For deployments where widgets are embedded in iframes on external sites, configure allowed origins:

```toml
[server]
# Allow specific origins (empty = allow any, rely on token auth only)
websocket_allowed_origins = [
    "http://localhost:8080",
    "https://app.example.com",
    "https://dashboard.mycompany.com"
]
```

> **Note:** When a widget is embedded in an iframe, the **origin** is the embedding site, not the PyWry server. Configure origins based on where your widgets will be embedded.

#### Internal API Protection

Internal endpoints (`/health`, `/register_widget`, `/disconnect`) are protected from external access:

```toml
[server]
internal_api_header = "X-PyWry-Token"  # Custom header name
internal_api_token = "my-secret"       # Set explicitly, or leave empty for auto-generation
```

Requests without the correct header receive `404 Not Found` (not `401`/`403`), hiding endpoint existence from attackers.

#### Strict vs Lenient Widget Auth

The `strict_widget_auth` setting controls how the `/widget/{id}` endpoint is protected:

| Mode | `strict_widget_auth` | Behavior | Use Case |
|------|----------------------|----------|----------|
| **Notebook** | `false` (default) | Only checks widget ID exists | Jupyter iframes (can't send headers) |
| **Browser** | `true` | Requires internal API header | Standalone browser mode |

```toml
[server]
# For Jupyter/notebook deployments (default)
strict_widget_auth = false

# For standalone browser deployments
strict_widget_auth = true
```

#### Programmatic Configuration

```python
from pywry import PyWry, PyWrySettings, ServerSettings

settings = PyWrySettings(
    server=ServerSettings(
        # WebSocket security
        websocket_allowed_origins=["https://app.example.com"],
        websocket_require_token=True,
        
        # Internal API security
        internal_api_header="X-MyApp-Token",
        internal_api_token="my-secret-token",  # Or None for auto-gen
        
        # Widget auth mode
        strict_widget_auth=True,  # Browser mode
    )
)

app = PyWry(settings=settings)
```

#### Security Configuration Reference

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `websocket_allowed_origins` | `list[str]` | `[]` | Origins allowed for WebSocket. Empty = any origin (token-only auth) |
| `websocket_require_token` | `bool` | `true` | Require per-widget token via `Sec-WebSocket-Protocol` |
| `internal_api_header` | `str` | `"X-PyWry-Token"` | Header name for internal API auth |
| `internal_api_token` | `str \| None` | `None` | Internal API token. `None` = auto-generate on start |
| `strict_widget_auth` | `bool` | `false` | `true` = require header for `/widget/{id}`, `false` = check ID exists |

</details>

---

## Deploy Mode & Scaling

<details>
<summary>Click to expand</summary>

**In this section:** [Overview](#deploy-mode-overview) · [Enable Deploy Mode](#enabling-deploy-mode) · [State Backends](#state-backends) · [Redis Configuration](#redis-configuration) · [State Stores](#state-stores) · [Multi-Worker Architecture](#multi-worker-architecture) · [Authentication & Sessions](#authentication--sessions)

---

For production deployments with multiple workers or horizontal scaling, PyWry provides a **deploy mode** that externalizes state to Redis. This enables running PyWry behind a load balancer with multiple Uvicorn workers while maintaining consistent widget state and event routing.

### Deploy Mode Overview

| Feature | Single Process (Default) | Deploy Mode (Redis) |
|---------|--------------------------|---------------------|
| **State Storage** | In-memory (dict) | Redis with TTL |
| **Event Bus** | In-memory queue | Redis Pub/Sub |
| **Connection Routing** | Local tracking | Redis with worker affinity |
| **Session Management** | N/A | Redis with RBAC support |
| **Horizontal Scaling** | ❌ | ✅ |
| **Worker Crash Recovery** | ❌ | ✅ |

### Enabling Deploy Mode

Deploy mode is activated automatically when:

1. `PYWRY_DEPLOY__STATE_BACKEND=redis` is set, OR
2. `PYWRY_DEPLOY_MODE=1` is set explicitly

```bash
# Via environment variables (recommended for production)
export PYWRY_DEPLOY__STATE_BACKEND=redis
export PYWRY_DEPLOY__REDIS_URL=redis://localhost:6379/0

# Run with multiple workers
uvicorn app:app --host 0.0.0.0 --port 8080 --workers 4
```

### State Backends

| Backend | Use Case | Configuration |
|---------|----------|---------------|
| `memory` | Single process, development | Default, no configuration needed |
| `redis` | Multi-worker, production | Requires Redis server |

### Redis Configuration

Configure Redis connection via `pywry.toml`, `pyproject.toml`, or environment variables:

```toml
# pywry.toml or [tool.pywry.deploy] in pyproject.toml
[deploy]
state_backend = "redis"
redis_url = "redis://localhost:6379/0"
redis_prefix = "pywry"              # Key namespace
redis_pool_size = 10                # Connection pool size per store

# TTL settings (seconds)
widget_ttl = 86400                  # Widget data TTL (24 hours)
connection_ttl = 300                # WebSocket connection TTL (5 minutes)
session_ttl = 86400                 # User session TTL (24 hours)

# Worker identification
worker_id = ""                      # Auto-generated if empty

# Authentication (optional)
auth_enabled = false
auth_session_cookie = "pywry_session"
auth_header = "Authorization"

# RBAC (optional)
default_roles = ["viewer"]
admin_users = []
```

#### Environment Variables

```bash
# Core Redis settings
export PYWRY_DEPLOY__STATE_BACKEND=redis
export PYWRY_DEPLOY__REDIS_URL=redis://user:password@host:6379/0
export PYWRY_DEPLOY__REDIS_PREFIX=myapp

# TTL settings
export PYWRY_DEPLOY__WIDGET_TTL=86400
export PYWRY_DEPLOY__CONNECTION_TTL=300
export PYWRY_DEPLOY__SESSION_TTL=86400

# Worker ID (optional - auto-generated if not set)
export PYWRY_DEPLOY__WORKER_ID=worker-1

# Authentication
export PYWRY_DEPLOY__AUTH_ENABLED=true
export PYWRY_DEPLOY__AUTH_SESSION_COOKIE=pywry_session
export PYWRY_DEPLOY__AUTH_HEADER=Authorization

# RBAC
export PYWRY_DEPLOY__DEFAULT_ROLES=viewer,editor
export PYWRY_DEPLOY__ADMIN_USERS=admin@example.com,super@example.com
```

### State Stores

Deploy mode provides four pluggable state stores:

| Store | Interface | Purpose |
|-------|-----------|---------|
| `WidgetStore` | `get_widget_store()` | Widget HTML, tokens, metadata |
| `EventBus` | `get_event_bus()` | Cross-worker event routing |
| `ConnectionRouter` | `get_connection_router()` | WebSocket connection affinity |
| `SessionStore` | `get_session_store()` | User sessions for RBAC |

#### Using State Stores Programmatically

```python
from pywry.state import (
    get_widget_store,
    get_event_bus,
    get_connection_router,
    get_session_store,
    is_deploy_mode,
    get_worker_id,
)

# Check if deploy mode is active
if is_deploy_mode():
    print(f"Running in deploy mode, worker: {get_worker_id()}")

# Access stores (automatically returns Redis or Memory implementation)
widget_store = get_widget_store()
event_bus = get_event_bus()
connection_router = get_connection_router()
session_store = get_session_store()

# Example: Register a widget
await widget_store.register(
    widget_id="my-widget",
    html="<h1>Hello</h1>",
    token="secret-token",
    owner_worker_id=get_worker_id(),
    metadata={"title": "My Widget"},
)

# Example: Get widget data
widget_data = await widget_store.get("my-widget")
if widget_data:
    print(f"Widget HTML: {widget_data.html[:50]}...")
    print(f"Owner: {widget_data.owner_worker_id}")
```

#### State Store Interfaces

<details>
<summary><strong>WidgetStore Interface</strong></summary>

```python
class WidgetStore(Protocol):
    """Store for widget HTML content and metadata."""

    async def register(
        self,
        widget_id: str,
        html: str,
        token: str | None = None,
        owner_worker_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register a widget with its HTML content."""

    async def get(self, widget_id: str) -> WidgetData | None:
        """Get complete widget data."""

    async def get_html(self, widget_id: str) -> str | None:
        """Get widget HTML content."""

    async def get_token(self, widget_id: str) -> str | None:
        """Get widget authentication token."""

    async def exists(self, widget_id: str) -> bool:
        """Check if a widget exists."""

    async def delete(self, widget_id: str) -> bool:
        """Delete a widget."""

    async def list_active(self) -> list[str]:
        """List all active widget IDs."""

    async def update_html(self, widget_id: str, html: str) -> bool:
        """Update widget HTML content."""
```

</details>

<details>
<summary><strong>EventBus Interface</strong></summary>

```python
class EventBus(Protocol):
    """Cross-worker event bus for widget events."""

    async def publish(self, event: EventMessage) -> None:
        """Publish an event to the bus."""

    async def subscribe(self, widget_id: str) -> AsyncIterator[EventMessage]:
        """Subscribe to events for a widget."""

    async def publish_to_worker(
        self,
        worker_id: str,
        event: EventMessage,
    ) -> None:
        """Publish an event to a specific worker."""
```

</details>

<details>
<summary><strong>ConnectionRouter Interface</strong></summary>

```python
class ConnectionRouter(Protocol):
    """Route WebSocket connections to appropriate workers."""

    async def register(self, connection: ConnectionInfo) -> None:
        """Register a new WebSocket connection."""

    async def get(self, widget_id: str) -> ConnectionInfo | None:
        """Get connection info for a widget."""

    async def heartbeat(self, widget_id: str) -> bool:
        """Update connection heartbeat timestamp."""

    async def remove(self, widget_id: str) -> bool:
        """Remove a connection registration."""

    async def get_worker_connections(self, worker_id: str) -> list[str]:
        """Get all widget IDs connected to a worker."""
```

</details>

<details>
<summary><strong>SessionStore Interface</strong></summary>

```python
class SessionStore(Protocol):
    """User session management for RBAC."""

    async def create(
        self,
        user_id: str,
        roles: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> UserSession:
        """Create a new user session."""

    async def get(self, session_id: str) -> UserSession | None:
        """Get a session by ID."""

    async def get_by_user(self, user_id: str) -> list[UserSession]:
        """Get all sessions for a user."""

    async def update_roles(self, session_id: str, roles: list[str]) -> bool:
        """Update session roles."""

    async def delete(self, session_id: str) -> bool:
        """Delete a session."""

    async def touch(self, session_id: str) -> bool:
        """Refresh session TTL."""
```

</details>

### Multi-Worker Architecture

When running with multiple workers, PyWry uses the following architecture:

```
                    ┌─────────────────────────────┐
                    │        Load Balancer        │
                    └─────────────┬───────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│   Worker 1    │       │   Worker 2    │       │   Worker 3    │
│   (uvicorn)   │       │   (uvicorn)   │       │   (uvicorn)   │
│               │       │               │       │               │
│  Callbacks A  │       │  Callbacks B  │       │  Callbacks C  │
│  WebSockets   │       │  WebSockets   │       │  WebSockets   │
└───────┬───────┘       └───────┬───────┘       └───────┬───────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │        Redis          │
                    │                       │
                    │  • Widget Store       │
                    │  • Event Bus (Pub/Sub)│
                    │  • Connection Router  │
                    │  • Session Store      │
                    └───────────────────────┘
```

**Key Concepts:**

1. **Widget Store**: All workers can serve any widget's HTML since content is in Redis
2. **Connection Router**: Tracks which worker owns each WebSocket connection
3. **Event Bus**: Routes events to the correct worker for callback execution
4. **Callbacks**: Python callbacks are executed by the worker that registered them

### Authentication & Sessions

When `auth_enabled=true`, PyWry provides session-based authentication:

```python
from pywry.state import get_session_store, UserSession

session_store = get_session_store()

# Create a session for a user
session = await session_store.create(
    user_id="user@example.com",
    roles=["viewer", "editor"],
    metadata={"display_name": "John Doe"},
)

# Session token can be set as a cookie or header
# session.session_id = "abc123..."

# Validate a session
session = await session_store.get(session_id)
if session and "admin" in session.roles:
    # Allow admin action
    pass

# Refresh session TTL on activity
await session_store.touch(session.session_id)
```

#### RBAC Configuration

```toml
[deploy]
auth_enabled = true
default_roles = ["viewer"]      # Roles for new users
admin_users = [                 # Users with admin privileges
    "admin@example.com",
    "super@example.com"
]
```

### DeploySettings Reference

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `state_backend` | `"memory"` \| `"redis"` | `"memory"` | State storage backend |
| `redis_url` | `str` | `"redis://localhost:6379/0"` | Redis connection URL |
| `redis_prefix` | `str` | `"pywry"` | Key prefix for Redis keys |
| `redis_pool_size` | `int` | `10` | Connection pool size |
| `widget_ttl` | `int` | `86400` | Widget data TTL (seconds) |
| `connection_ttl` | `int` | `300` | Connection routing TTL (seconds) |
| `session_ttl` | `int` | `86400` | User session TTL (seconds) |
| `worker_id` | `str \| None` | `None` | Worker ID (auto-generated if None) |
| `auth_enabled` | `bool` | `false` | Enable authentication |
| `auth_session_cookie` | `str` | `"pywry_session"` | Session cookie name |
| `auth_header` | `str` | `"Authorization"` | Auth header name |
| `default_roles` | `list[str]` | `["viewer"]` | Default roles for new users |
| `admin_users` | `list[str]` | `[]` | User IDs with admin privileges |

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
│   ├── state/             # State management for deploy mode
│   │   ├── __init__.py    # Public state API exports
│   │   ├── base.py        # Abstract interfaces (WidgetStore, EventBus, etc.)
│   │   ├── memory.py      # In-memory implementations (default)
│   │   ├── redis.py       # Redis implementations (deploy mode)
│   │   ├── types.py       # Type definitions (WidgetData, EventMessage, etc.)
│   │   ├── auth.py        # Authentication helpers
│   │   ├── callbacks.py   # Callback registry for state
│   │   ├── server.py      # Server state management
│   │   ├── sync_helpers.py # Async-to-sync utilities
│   │   └── _factory.py    # Factory functions for state stores
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
from pywry import PyWry, ModeBarButton, PlotlyConfig, PlotlyIconName
import plotly.express as px
import pandas as pd

app = PyWry()

# Sample data
df = px.data.iris()
fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species")

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

def on_export(data, event_type, label):
    """Trigger a CSV download when the custom modebar button is clicked."""
    csv_content = df.to_csv(index=False)
    app.emit("pywry:download", {
        "content": csv_content,
        "filename": "iris_data.csv",
        "mimeType": "text/csv"
    }, label)

label = app.show_plotly(fig, config=config, callbacks={"app:export": on_export})
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
