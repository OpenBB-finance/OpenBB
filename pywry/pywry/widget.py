"""PyWry widget for inline notebook rendering using anywidget."""
# mypy: disable-error-code="import-untyped,no-untyped-call,no-untyped-def,arg-type,type-arg"
# pylint: disable=too-many-lines

from __future__ import annotations

import json
import pathlib
import uuid

from functools import lru_cache
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from collections.abc import Callable

    from plotly.graph_objects import Figure

try:
    import anywidget
    import traitlets

    HAS_ANYWIDGET = True
except ImportError:
    HAS_ANYWIDGET = False


# Path to the source JS directory
_SRC_DIR = pathlib.Path(__file__).parent / "frontend" / "src"


@lru_cache(maxsize=1)
def _get_plotly_widget_esm() -> str:
    """Build the Plotly widget ESM by combining Plotly.js with the widget code."""
    from .assets import get_plotly_js, get_plotly_templates_js

    # Get the widget render code
    widget_js_file = _SRC_DIR / "plotly-widget.js"
    if not widget_js_file.exists():
        raise FileNotFoundError(f"Widget JS not found: {widget_js_file}")

    widget_js = widget_js_file.read_text(encoding="utf-8")

    # Get Plotly.js
    plotly_js = get_plotly_js()
    if not plotly_js:
        raise RuntimeError("Plotly.js not found in bundled assets")

    # Get Plotly templates for theme switching
    templates_js = get_plotly_templates_js() or ""

    # Wrap Plotly.js in IIFE to expose to window
    # Plotly 3.x UMD checks for AMD/CommonJS first, we force global export
    return f"""
console.log('[PyWry Plotly ESM] Module loading...');

// Module-level reference to Plotly (survives re-renders within same module)
let _plotlyLib = (typeof window !== 'undefined' && window.Plotly) ? window.Plotly : null;

// Helper to get Plotly library (checks multiple sources)
function getPlotly() {{
    if (_plotlyLib) return _plotlyLib;
    if (typeof window !== 'undefined' && window.Plotly) {{
        _plotlyLib = window.Plotly;
        return _plotlyLib;
    }}
    if (typeof Plotly !== 'undefined') {{
        _plotlyLib = Plotly;
        if (typeof window !== 'undefined') window.Plotly = Plotly;
        return _plotlyLib;
    }}
    return null;
}}

// Only load Plotly.js if not already present
if (!getPlotly()) {{
    console.log('[PyWry Plotly ESM] Plotly not found, loading library...');

    // Hide AMD define to force global export (like AG Grid)
    var _origDefine = (typeof define !== 'undefined') ? define : undefined;
    if (typeof define !== 'undefined') define = undefined;

    // Ensure self exists for UMD
    if (typeof self === 'undefined' && typeof window !== 'undefined') {{
        var self = window;
    }}

{plotly_js}

    // Restore define
    if (_origDefine) define = _origDefine;

    // Store reference
    if (typeof Plotly !== 'undefined') {{
        _plotlyLib = Plotly;
        if (typeof window !== 'undefined') window.Plotly = Plotly;
        console.log('[PyWry Plotly ESM] Plotly attached to window, version:', Plotly.version);
    }} else if (typeof self !== 'undefined' && self.Plotly) {{
        _plotlyLib = self.Plotly;
        if (typeof window !== 'undefined') window.Plotly = self.Plotly;
        console.log('[PyWry Plotly ESM] Plotly found on self, attached to window');
    }} else {{
        console.error('[PyWry Plotly ESM] ERROR: Plotly not found after loading!');
    }}
}} else {{
    console.log('[PyWry Plotly ESM] Plotly already loaded, version:', getPlotly().version);
}}

// Load Plotly templates (plotly_dark, plotly_white, etc.) for theme switching
if (typeof window !== 'undefined' && !window.PYWRY_PLOTLY_TEMPLATES) {{
{templates_js}
    console.log('[PyWry Plotly ESM] Templates loaded:', Object.keys(window.PYWRY_PLOTLY_TEMPLATES || {{}}).join(', '));
}}

{widget_js}
"""


@lru_cache(maxsize=1)
def _get_aggrid_css_all() -> str:
    """Load all AG Grid CSS themes at once for the widget, plus pywry base CSS."""
    from .assets import get_aggrid_css, get_pywry_css
    from .models import ThemeMode

    css_parts = []
    # Add pywry base CSS first for theming variables and widget classes
    pywry_css = get_pywry_css()
    if pywry_css:
        css_parts.append(pywry_css)
    # Then add AG Grid theme CSS
    for theme_name in ["quartz", "alpine", "balham", "material"]:
        for mode in [ThemeMode.LIGHT, ThemeMode.DARK]:
            css = get_aggrid_css(theme_name, mode)
            if css:
                css_parts.append(css)
    return "\n".join(css_parts) if css_parts else ""


@lru_cache(maxsize=1)
def _get_aggrid_widget_esm() -> str:
    """Build the AG Grid widget ESM by combining AG Grid with widget code."""
    from .assets import get_aggrid_defaults_js, get_aggrid_js

    aggrid_js = get_aggrid_js()
    if not aggrid_js:
        raise RuntimeError("AG Grid JS not found in bundled assets")

    aggrid_defaults_js = get_aggrid_defaults_js()
    if not aggrid_defaults_js:
        raise RuntimeError("AG Grid defaults JS not found in bundled assets")

    # AG Grid widget render code - with ensureAgGrid() that guarantees availability
    widget_js = """
console.log('[PyWry AG Grid] Widget module loaded');

// Module-level render counter to detect/cancel stale renders
let currentRenderId = 0;

function render({ model, el }) {
    // Increment render ID to invalidate any pending async operations from previous renders
    currentRenderId++;
    const myRenderId = currentRenderId;

    console.log('[PyWry AG Grid] render() called, renderId:', myRenderId);

    // CRITICAL: Clear el completely to avoid stale content from re-renders
    el.innerHTML = '';

    const container = document.createElement('div');
    container.className = 'pywry-widget';
    // Theme class for CSS variable switching
    container.classList.add(model.get('theme') === 'dark' ? 'pywry-theme-dark' : 'pywry-theme-light');
    // Set CSS variables from model for flexible sizing
    const modelHeight = model.get('height');
    const modelWidth = model.get('width');
    if (modelHeight) {
        container.style.setProperty('--pywry-widget-height', modelHeight);
    }
    if (modelWidth) {
        container.style.setProperty('--pywry-widget-width', modelWidth);
    }

    el.appendChild(container);

    let gridApi = null;

    function getThemeClass() {
        const isDark = model.get('theme') === 'dark';
        const baseTheme = model.get('aggrid_theme') || 'alpine';
        return 'ag-theme-' + baseTheme + (isDark ? '-dark' : '');
    }

    function applyTheme() {
        const isDark = model.get('theme') === 'dark';
        container.classList.remove('pywry-theme-dark', 'pywry-theme-light');
        container.classList.add(isDark ? 'pywry-theme-dark' : 'pywry-theme-light');

        // Update grid theme class
        const gridDiv = container.querySelector('#grid');
        if (gridDiv) {
            const baseTheme = model.get('aggrid_theme') || 'alpine';
            gridDiv.className = 'pywry-grid ag-theme-' + baseTheme + (isDark ? '-dark' : '');
        }
    }
    applyTheme();

    // Attach model to container for global dispatch lookup
    container._pywryModel = model;

    // Initialize global dispatcher if not present
    if (!window.pywry) {
        window.pywry = {};
    }
    if (!window.pywry.emitButton) {
        window.pywry.emitButton = function(el, type, data) {
            const widget = el.closest('.pywry-widget');
            if (widget && widget._pywryModel) {
                 const model = widget._pywryModel;
                 const evt = JSON.stringify({ type: type, data: data, ts: Date.now() });
                 model.set('_js_event', evt);
                 model.save_changes();
            } else {
                 console.warn('[PyWry] Could not find widget model for element', el);
            }
        };
    }

    // Local bridge - specialized for this widget instance
    const pywry = {
        _ready: false,
        _handlers: {},
        _pending: [],
        result: function(data) {
            const event = JSON.stringify({ type: 'pywry:result', data: data, ts: Date.now() });
            model.set('_js_event', event);
            model.save_changes();
        },
        emit: function(type, data) {
            const event = JSON.stringify({ type: type, data: data, ts: Date.now() });
            model.set('_js_event', event);
            model.save_changes();
        },
        on: function(type, callback) {
            if (!this._handlers[type]) this._handlers[type] = [];
            this._handlers[type].push(callback);
            const pending = this._pending.filter(p => p.type === type);
            this._pending = this._pending.filter(p => p.type !== type);
            pending.forEach(p => callback(p.data));
        },
        _fire: function(type, data) {
            const handlers = this._handlers[type] || [];
            if (handlers.length === 0) {
                this._pending.push({type: type, data: data});
            } else {
                handlers.forEach(h => h(data));
            }
        }
    };

    // Attach local pywry to container for debugging if needed
    container._pywryInstance = pywry;

    model.on('change:_py_event', () => {
        try {
            const event = JSON.parse(model.get('_py_event') || '{}');
            if (event.type) {
                // Handle theme updates - set model property AND apply directly
                if (event.type === 'pywry:update_theme' && event.data && event.data.theme) {
                    const gridDiv = container.querySelector('#grid');
                    if (gridDiv) {
                        // Update grid theme class
                        const classes = Array.from(gridDiv.classList).filter(c => !c.startsWith('ag-theme-'));
                        gridDiv.className = classes.join(' ') + ' ' + event.data.theme;
                        console.log('[PyWry] Grid theme class updated to:', event.data.theme);
                    }
                    // Determine if light or dark and set model property
                    const isDark = event.data.theme.includes('dark');
                    const newTheme = isDark ? 'dark' : 'light';
                    model.set('theme', newTheme);
                    model.save_changes();
                    // Apply theme directly (model.on('change:theme') only fires for changes FROM Python)
                    applyTheme();
                    console.log('[PyWry] Model theme set to:', newTheme);
                }
                // Handle grid data updates (row data)
                if (event.type === 'pywry:update_rows' && gridApi && event.data && event.data.rows) {
                    gridApi.setGridOption('rowData', event.data.rows);
                    console.log('[PyWry] Grid rows updated:', event.data.rows.length, 'rows');
                }
                // Handle column definition updates
                if (event.type === 'pywry:update_columns' && gridApi && event.data && event.data.columnDefs) {
                    gridApi.setGridOption('columnDefs', event.data.columnDefs);
                    console.log('[PyWry] Grid columns updated:', event.data.columnDefs.length, 'columns');
                }
                // Handle full grid config update (rows + columns)
                if (event.type === 'pywry:update_grid' && gridApi && event.data) {
                    if (event.data.columnDefs) {
                        gridApi.setGridOption('columnDefs', event.data.columnDefs);
                    }
                    if (event.data.rows) {
                        gridApi.setGridOption('rowData', event.data.rows);
                    }
                    console.log('[PyWry] Grid fully updated');
                }
                pywry._fire(event.type, event.data);
            }
        } catch(e) {
            console.error('[PyWry] Failed to parse Python event:', e);
        }
    });

    function renderContent(retryCount = 0) {
        // CRITICAL: Check if this render is stale (a newer render has started)
        if (myRenderId !== currentRenderId) {
            console.log('[PyWry AG Grid] Stale render detected, aborting. myId:', myRenderId, 'current:', currentRenderId);
            return;
        }

        console.log('[PyWry AG Grid] renderContent() called, retry:', retryCount);
        const content = model.get('content');

        if (content) {
            // Only set innerHTML on first attempt to avoid flicker
            if (retryCount === 0) {
                container.innerHTML = content;
            }

            // Initialize AG Grid if grid config is present
            const gridConfig = model.get('grid_config');

            if (gridConfig) {
                try {
                    const config = JSON.parse(gridConfig);
                    const gridDiv = container.querySelector('#grid');
                    // Use ensureAgGrid() which tries to load if not present
                    const agGridLib = ensureAgGrid();
                    console.log('[PyWry AG Grid] gridDiv:', !!gridDiv, 'agGridLib:', !!agGridLib, 'retry:', retryCount);

                    if (gridDiv && agGridLib) {
                        // Add pywry-grid class for consistent styling, plus AG Grid theme class
                        const themeClass = getThemeClass();
                        gridDiv.className = 'pywry-grid ' + themeClass;

                        // Get grid ID for scoping (use model's grid_id or generate one)
                        const gridId = model.get('grid_id') || ('grid-' + Math.random().toString(36).substr(2, 9));

                        console.log('[PyWry AG Grid ' + gridId + '] Creating grid with config, class:', gridDiv.className);
                        // Use centralized AG Grid defaults from aggrid-defaults.js
                        const gridOptions = window.PYWRY_AGGRID_BUILD_OPTIONS(config, gridId);
                        gridApi = agGridLib.createGrid(gridDiv, gridOptions);

                        // Register Python event listeners + context menu using centralized function (scoped by gridId)
                        if (window.PYWRY_AGGRID_REGISTER_LISTENERS) {
                            window.PYWRY_AGGRID_REGISTER_LISTENERS(gridApi, gridDiv, gridId);
                        }

                        console.log('[PyWry AG Grid ' + gridId + '] Grid created successfully!');
                    } else {
                        // AG Grid not ready yet - retry with backoff (max 20 retries, 50ms apart = 1 second total)
                        if (!agGridLib && retryCount < 20) {
                            console.log('[PyWry AG Grid] AG Grid not ready, retry', retryCount + 1, 'in 50ms...');
                            setTimeout(() => renderContent(retryCount + 1), 50);
                            return;
                        }
                        console.error('[PyWry AG Grid] FAILED - gridDiv:', !!gridDiv, 'agGridLib:', !!agGridLib, 'retries:', retryCount);
                        container.innerHTML = '<div style="color:red;padding:20px;font-family:monospace;">ERROR: ' +
                            (gridDiv ? 'AG Grid library failed to load after ' + retryCount + ' retries. Check console.' : '#grid div not found in HTML') + '</div>';
                    }
                } catch(e) {
                    console.error('[PyWry] AG Grid init error:', e);
                    container.innerHTML = '<div style="color:red;padding:20px;">ERROR: ' + e.message + '</div>';
                }
            }
        } else {
            console.log('[PyWry AG Grid] No content to render');
        }
    }

    model.on('change:content', () => renderContent(0));
    model.on('change:theme', applyTheme);

    // Show loading state immediately
    container.innerHTML = '<div style="padding:20px;color:#888;font-family:monospace;">Loading AG Grid...</div>';

    // Wait for AG Grid to be ready before first render (poll every 50ms, max 100 attempts = 5s)
    function waitAndRender(attempt) {
        // CRITICAL: Check if this render is stale (a newer render has started)
        if (myRenderId !== currentRenderId) {
            console.log('[PyWry AG Grid] Stale waitAndRender detected, aborting. myId:', myRenderId, 'current:', currentRenderId);
            return;
        }

        const agGridLib = ensureAgGrid();
        const hasContent = !!model.get('content');
        // Log every 10th attempt to reduce spam
        if (attempt % 10 === 0) {
            console.log('[PyWry AG Grid] waitAndRender attempt', attempt, '- agGrid:', !!agGridLib, 'content:', hasContent);
        }

        if (agGridLib && hasContent) {
            renderContent(0);
        } else if (attempt < 100) {
            setTimeout(() => waitAndRender(attempt + 1), 50);
        } else {
            console.error('[PyWry AG Grid] Timeout waiting for AG Grid/content');
            container.innerHTML = '<div style="color:#ff4444;padding:20px;font-family:monospace;">' +
                'ERROR: Timeout waiting for ' + (!agGridLib ? 'AG Grid library' : 'content') + '</div>';
        }
    }
    waitAndRender(0);
}
export default { render };
"""
    # AG Grid UMD checks for AMD (define) first - we must disable it temporarily
    return f"""
console.log('[PyWry AG Grid ESM] Module loading...');

// Module-level reference to AG Grid (survives re-renders within same module)
// Also use window._pywryAgGrid as a fallback for cross-module persistence
let _agGridLib = (typeof window !== 'undefined' && window._pywryAgGrid) ? window._pywryAgGrid : null;

// Helper to get AG Grid library (checks multiple sources)
function getAgGrid() {{
    if (_agGridLib && _agGridLib.createGrid) return _agGridLib;
    if (typeof window !== 'undefined' && window._pywryAgGrid && window._pywryAgGrid.createGrid) {{
        _agGridLib = window._pywryAgGrid;
        return _agGridLib;
    }}
    if (typeof window !== 'undefined' && window.agGrid && window.agGrid.createGrid) {{
        _agGridLib = window.agGrid;
        window._pywryAgGrid = _agGridLib; // Persist for other modules
        return _agGridLib;
    }}
    if (typeof self !== 'undefined' && self.agGrid && self.agGrid.createGrid) {{
        _agGridLib = self.agGrid;
        if (typeof window !== 'undefined') window._pywryAgGrid = _agGridLib;
        return _agGridLib;
    }}
    return null;
}}

// ensureAgGrid - returns AG Grid lib, checking all possible locations
function ensureAgGrid() {{
    // Check cached reference first
    let lib = getAgGrid();
    if (lib) return lib;

    // Check if loading is in progress (self.agGrid might exist now)
    if (typeof self !== 'undefined' && self.agGrid && self.agGrid.createGrid) {{
        _agGridLib = self.agGrid;
        if (typeof window !== 'undefined') {{
            window.agGrid = self.agGrid;
            window._pywryAgGrid = self.agGrid;
        }}
        return _agGridLib;
    }}

    return null;
}}

// Only load AG Grid if not already present (prevents double-loading issues)
if (!getAgGrid()) {{
    console.log('[PyWry AG Grid ESM] AG Grid not found, loading library...');

    // CRITICAL: AG Grid UMD checks for AMD define() first.
    // If define exists, it registers as AMD module instead of setting self.agGrid.
    // We must temporarily hide define to force the global export path.
    var _originalDefine = typeof define !== 'undefined' ? define : undefined;
    var define = undefined;

    // Ensure self exists and equals window
    if (typeof self === 'undefined') {{
        var self = window;
    }}

    // Execute AG Grid UMD - with define hidden, it will set self.agGrid
    {aggrid_js}

    // Restore define
    if (typeof _originalDefine !== 'undefined') {{
        define = _originalDefine;
    }}

    // Store references in multiple places for reliability
    console.log('[PyWry AG Grid ESM] After load - self.agGrid:', typeof self.agGrid);
    if (typeof self.agGrid !== 'undefined') {{
        _agGridLib = self.agGrid;
        window.agGrid = self.agGrid;
        window._pywryAgGrid = self.agGrid; // Extra persistence
        console.log('[PyWry AG Grid ESM] SUCCESS - loaded AG Grid');
    }} else {{
        console.error('[PyWry AG Grid ESM] FAILED - self.agGrid is undefined after loading');
    }}
}} else {{
    console.log('[PyWry AG Grid ESM] AG Grid already loaded, reusing existing instance');
}}

// Load PyWry AG Grid defaults (single source of truth for all grid config)
{aggrid_defaults_js}

{widget_js}
"""


# Basic widget ESM without Plotly
_WIDGET_ESM = """
function render({ model, el }) {
    const container = document.createElement('div');
    container.className = 'pywry-widget';
    container.classList.add(model.get('theme') === 'dark' ? 'pywry-theme-dark' : 'pywry-theme-light');
    // Set CSS variables from model for flexible sizing
    const modelHeight = model.get('height');
    const modelWidth = model.get('width');
    if (modelHeight) {
        container.style.setProperty('--pywry-widget-max-height', modelHeight);
    }
    if (modelWidth) {
        container.style.setProperty('--pywry-widget-width', modelWidth);
    }

    function applyTheme() {
        const isDark = model.get('theme') === 'dark';
        container.classList.remove('pywry-theme-dark', 'pywry-theme-light');
        container.classList.add(isDark ? 'pywry-theme-dark' : 'pywry-theme-light');
    }
    applyTheme();
    el.appendChild(container);

    // Attach model to container for global dispatch lookup
    container._pywryModel = model;

    // Initialize global dispatcher if not present
    if (!window.pywry) {
        window.pywry = {};
    }
    if (!window.pywry.emitButton) {
        window.pywry.emitButton = function(el, type, data) {
            const widget = el.closest('.pywry-widget');
            if (widget && widget._pywryModel) {
                 const model = widget._pywryModel;
                 const evt = JSON.stringify({ type: type, data: data, ts: Date.now() });
                 model.set('_js_event', evt);
                 model.save_changes();
            } else {
                 console.warn('[PyWry] Could not find widget model for element', el);
            }
        };
    }

    // Local bridge - specialized for this widget instance
    const pywry = {
        _ready: false,
        _handlers: {},
        _pending: [],
        result: function(data) {
            const event = JSON.stringify({ type: 'pywry:result', data: data, ts: Date.now() });
            model.set('_js_event', event);
            model.save_changes();
        },
        emit: function(type, data) {
            const event = JSON.stringify({ type: type, data: data, ts: Date.now() });
            model.set('_js_event', event);
            model.save_changes();
        },
        on: function(type, callback) {
            if (!this._handlers[type]) this._handlers[type] = [];
            this._handlers[type].push(callback);
            const pending = this._pending.filter(p => p.type === type);
            this._pending = this._pending.filter(p => p.type !== type);
            pending.forEach(p => callback(p.data));
        },
        _fire: function(type, data) {
            const handlers = this._handlers[type] || [];
            if (handlers.length === 0) {
                this._pending.push({type: type, data: data});
            } else {
                handlers.forEach(h => h(data));
            }
        }
    };

    // Attach local pywry to container for debugging if needed
    container._pywryInstance = pywry;

    model.on('change:_py_event', () => {
        try {
            const event = JSON.parse(model.get('_py_event') || '{}');
            if (event.type) {
                // Handle theme updates - set model property AND apply directly
                if (event.type === 'pywry:update_theme' && event.data && event.data.theme) {
                    const isDark = event.data.theme.includes('dark');
                    const newTheme = isDark ? 'dark' : 'light';
                    model.set('theme', newTheme);
                    model.save_changes();
                    // Apply theme directly (model.on('change:theme') only fires for changes FROM Python)
                    applyTheme();
                    console.log('[PyWry] Model theme set to:', newTheme);
                }
                pywry._fire(event.type, event.data);
            }
        } catch(e) {
            console.error('[PyWry] Failed to parse Python event:', e);
        }
    });

    function runScripts(parent) {
        const scripts = Array.from(parent.querySelectorAll('script'));
        scripts.forEach(oldScript => {
            if (oldScript.src) return;
            try {
                const newScript = document.createElement('script');
                newScript.textContent = oldScript.textContent;
                oldScript.parentNode.replaceChild(newScript, oldScript);
            } catch(e) {
                console.error('[PyWry] Script execution error:', e);
                const errDiv = document.createElement('div');
                errDiv.style.cssText = 'background:#ff4444;color:white;padding:10px;margin:5px;border-radius:4px;';
                errDiv.textContent = 'Script Error: ' + e.message;
                parent.appendChild(errDiv);
            }
        });
        pywry._ready = true;
    }

    function renderContent() {
        const content = model.get('content');
        if (content) {
            container.innerHTML = content;
            setTimeout(() => runScripts(container), 0);
        }
    }

    model.on('change:content', renderContent);
    model.on('change:theme', applyTheme);
    renderContent();
}
export default { render };
"""


@lru_cache(maxsize=1)
def _get_pywry_base_css() -> str:
    """Load pywry base CSS for widget theming."""
    from .assets import get_pywry_css

    return get_pywry_css() or ""


if HAS_ANYWIDGET:

    class PyWryWidget(anywidget.AnyWidget):  # pylint: disable=abstract-method
        """Widget for inline notebook rendering using anywidget (no Plotly).

        Implements BaseWidget protocol for unified API.
        """

        _esm = _WIDGET_ESM
        _css = _get_pywry_base_css()

        content = traitlets.Unicode("").tag(sync=True)
        theme = traitlets.Unicode("dark").tag(sync=True)
        width = traitlets.Unicode("100%").tag(sync=True)
        height = traitlets.Unicode("500px").tag(sync=True)
        _js_event = traitlets.Unicode("").tag(sync=True)
        _py_event = traitlets.Unicode("").tag(sync=True)

        def __init__(
            self,
            content: str = "",
            theme: str = "dark",
            width: str = "100%",
            height: str = "500px",
            **kwargs,
        ):
            """Initialize the widget."""
            super().__init__(**kwargs)
            self._label = f"w-{uuid.uuid4().hex[:8]}"
            self._handlers: dict[str, list[Callable[[dict[str, Any], str, str], Any]]] = {}
            self.content = content
            self.theme = theme
            self.width = width
            self.height = height
            self.observe(self._handle_js_event, names=["_js_event"])

        @property
        def label(self) -> str:
            """Get widget label."""
            return self._label

        def _handle_js_event(self, change: dict[str, Any]) -> None:
            """Handle events from JavaScript."""
            if not change["new"]:
                return
            try:
                event = json.loads(change["new"])
                event_type = event.get("type", "")
                event_data = event.get("data", {})
                for handler in self._handlers.get(event_type, []):
                    handler(event_data, event_type, self._label)
            except Exception as e:
                print(f"[PyWry] Error handling JS event: {e}")

        def on(
            self, event_type: str, callback: Callable[[dict[str, Any], str, str], Any]
        ) -> PyWryWidget:
            """Register a callback for events from JavaScript.

            Parameters
            ----------
            event_type : str
                Event name (e.g., 'toggle', 'custom_event').
            callback : Callable[[dict[str, Any], str, str], Any]
                Handler function receiving (data, event_type, label).

            Returns
            -------
            PyWryWidget
                Self for method chaining.
            """
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(callback)
            return self

        def emit(self, event_type: str, data: dict) -> None:
            """Send an event from Python to JavaScript.

            Parameters
            ----------
            event_type : str
                Event name that JS listeners can subscribe to.
            data : dict
                JSON-serializable payload to send to JavaScript.
            """
            event = json.dumps({"type": event_type, "data": data or {}, "ts": uuid.uuid4().hex})
            self._py_event = event

        def update(self, html: str) -> None:
            """Update the widget's HTML content.

            Parameters
            ----------
            html : str
                New HTML content to render.
            """
            self.content = html

        def set_content(self, content: str) -> None:
            """Alias for update()."""
            self.update(content)

        def display(self) -> None:
            """Display the widget in the current output context."""
            from IPython.display import display as ipy_display

            ipy_display(self)

        def update_figure(self, figure: Figure) -> None:
            """Update the Plotly figure (convenience method for Plotly widgets).

            Parameters
            ----------
            figure : plotly.graph_objects.Figure
                New Plotly figure to display.
            """
            # For generic PyWryWidget, just update with figure HTML
            # This is a fallback - PyWryPlotlyWidget has better implementation
            from . import inline

            html = inline.generate_plotly_html(
                figure.to_json(), self._label, "PyWry", self.theme, full_document=False
            )
            self.update(html)

    class PyWryPlotlyWidget(anywidget.AnyWidget):  # pylint: disable=abstract-method
        """Widget for inline notebook rendering with Plotly.js bundled.

        Dynamically loads Plotly.js from bundled assets and combines it
        with the widget rendering code at runtime.

        Implements BaseWidget protocol for unified API.
        """

        # Build ESM at init by combining Plotly.js with widget code
        _esm = _get_plotly_widget_esm()
        _css = _get_pywry_base_css()

        content = traitlets.Unicode("").tag(sync=True)
        figure_json = traitlets.Unicode("").tag(sync=True)  # Plotly figure as JSON
        theme = traitlets.Unicode("dark").tag(sync=True)
        width = traitlets.Unicode("100%").tag(sync=True)
        height = traitlets.Unicode("500px").tag(sync=True)
        _js_event = traitlets.Unicode("").tag(sync=True)
        _py_event = traitlets.Unicode("").tag(sync=True)

        def __init__(
            self,
            content: str = "",
            theme: str = "dark",
            width: str = "100%",
            height: str = "500px",
            figure_json: str = "",
            **kwargs,
        ):
            """Initialize the widget with Plotly bundled."""
            super().__init__(**kwargs)
            self._label = f"w-{uuid.uuid4().hex[:8]}"
            self._handlers: dict[str, list[Callable[[dict[str, Any], str, str], Any]]] = {}
            self.content = content
            self.figure_json = figure_json
            self.theme = theme
            self.width = width
            self.height = height
            self.observe(self._handle_js_event, names=["_js_event"])

        @property
        def label(self) -> str:
            """Get widget label."""
            return self._label

        def _handle_js_event(self, change: dict[str, Any]) -> None:
            """Handle events from JavaScript."""
            if not change["new"]:
                return
            try:
                event = json.loads(change["new"])
                event_type = event.get("type", "")
                event_data = event.get("data", {})
                for handler in self._handlers.get(event_type, []):
                    handler(event_data, event_type, self._label)
            except Exception as e:
                print(f"[PyWry] Error handling JS event: {e}")

        def on(
            self, event_type: str, callback: Callable[[dict[str, Any], str, str], Any]
        ) -> PyWryPlotlyWidget:
            """Register a callback for events from JavaScript.

            Parameters
            ----------
            event_type : str
                Event name (e.g., 'plotly_click', 'plotly_hover', 'plotly_selected').
            callback : Callable[[dict[str, Any], str, str], Any]
                Handler function receiving (data, event_type, label).

            Returns
            -------
            PyWryPlotlyWidget
                Self for method chaining.
            """
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(callback)
            return self

        def emit(self, event_type: str, data: dict) -> None:
            """Send an event from Python to JavaScript.

            Parameters
            ----------
            event_type : str
                Event name that JS listeners can subscribe to.
            data : dict
                JSON-serializable payload to send to JavaScript.
            """
            event = json.dumps({"type": event_type, "data": data or {}, "ts": uuid.uuid4().hex})
            self._py_event = event

        def update(self, html: str) -> None:
            """Update the widget's HTML content.

            Parameters
            ----------
            html : str
                New HTML content to render.
            """
            self.content = html

        def set_content(self, content: str) -> None:
            """Alias for update()."""
            self.update(content)

        def display(self) -> None:
            """Display the widget in the current output context."""
            from IPython.display import display as ipy_display

            ipy_display(self)

        def update_figure(self, figure: Figure) -> None:
            """Update the Plotly figure without manual HTML generation.

            Parameters
            ----------
            figure : plotly.graph_objects.Figure
                New Plotly figure to display.

            Examples
            --------
            >>> widget.update_figure(new_fig)  # Clean API!
            """
            # Merge config into figure JSON
            fig_dict = json.loads(figure.to_json())
            config = getattr(self, "_plotly_config", None)
            if config:
                fig_dict["config"] = config

            # Send update event to JS (handled by pywry:update_plotly listener)
            # This avoids regenerating the HTML and resetting the widget state
            self.emit("pywry:update_plotly", {"figure": fig_dict, "config": config or {}})

    class PyWryAgGridWidget(anywidget.AnyWidget):  # pylint: disable=abstract-method
        """Widget for inline notebook rendering with AG Grid bundled.

        Implements BaseWidget protocol for unified API.
        """

        _esm = _get_aggrid_widget_esm()
        _css = _get_aggrid_css_all()

        content = traitlets.Unicode("").tag(sync=True)
        theme = traitlets.Unicode("dark").tag(sync=True)
        aggrid_theme = traitlets.Unicode("alpine").tag(sync=True)
        width = traitlets.Unicode("100%").tag(sync=True)
        height = traitlets.Unicode("500px").tag(sync=True)
        grid_config = traitlets.Unicode("").tag(sync=True)
        grid_id = traitlets.Unicode("").tag(sync=True)  # Unique ID for scoped events
        _js_event = traitlets.Unicode("").tag(sync=True)
        _py_event = traitlets.Unicode("").tag(sync=True)

        def __init__(
            self,
            content: str = "",
            theme: str = "dark",
            aggrid_theme: str = "alpine",
            width: str = "100%",
            height: str = "500px",
            grid_config: str = "",
            grid_id: str = "",
            export_dir: str | None = None,
            **kwargs,
        ):
            """Initialize the widget with AG Grid bundled.

            Parameters
            ----------
            export_dir : str, optional
                Directory for CSV exports from context menu. If None, uses current directory.
            """
            super().__init__(**kwargs)
            self._label = f"w-{uuid.uuid4().hex[:8]}"
            self._handlers: dict[str, list[Callable[[dict[str, Any], str, str], Any]]] = {}
            self._export_dir = export_dir
            self.content = content
            self.theme = theme
            self.aggrid_theme = aggrid_theme
            self.width = width
            self.height = height
            self.grid_config = grid_config
            self.grid_id = grid_id or self._label  # Use label as default grid_id
            self.observe(self._handle_js_event, names=["_js_event"])

            # Automatically register CSV export handler
            self._register_csv_export_handler()

        @property
        def label(self) -> str:
            """Get widget label."""
            return self._label

        def _handle_js_event(self, change: dict[str, Any]) -> None:
            """Handle events from JavaScript."""
            if not change["new"]:
                return
            try:
                event = json.loads(change["new"])
                event_type = event.get("type", "")
                event_data = event.get("data", {})
                for handler in self._handlers.get(event_type, []):
                    handler(event_data, event_type, self._label)
            except Exception as e:
                print(f"[PyWry] Error handling JS event: {e}")

        def on(
            self, event_type: str, callback: Callable[[dict[str, Any], str, str], Any]
        ) -> PyWryAgGridWidget:
            """Register a callback for events from JavaScript.

            Parameters
            ----------
            event_type : str
                Event name (e.g., 'cell_click', 'row_selected').
            callback : Callable[[dict[str, Any], str, str], Any]
                Handler function receiving (data, event_type, label).

            Returns
            -------
            PyWryAgGridWidget
                Self for method chaining.
            """
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(callback)
            return self

        def emit(self, event_type: str, data: dict) -> None:
            """Send an event from Python to JavaScript.

            Parameters
            ----------
            event_type : str
                Event name that JS listeners can subscribe to.
            data : dict
                JSON-serializable payload to send to JavaScript.
            """
            # Include grid_id for scoped event handling
            payload = data.copy() if data else {}
            payload["gridId"] = self.grid_id
            event = json.dumps({"type": event_type, "data": payload, "ts": uuid.uuid4().hex})
            self._py_event = event

        def update(self, html: str) -> None:
            """Update the widget's HTML content.

            Parameters
            ----------
            html : str
                New HTML content to render.
            """
            self.content = html

        def set_content(self, content: str) -> None:
            """Alias for update()."""
            self.update(content)

        def update_data(self, data: Any) -> None:
            """Update the grid's row data.

            Parameters
            ----------
            data : DataFrame | list[dict] | dict[str, list]
                New data to display. Can be pandas DataFrame, list of row dicts,
                or dict of columns.

            Examples
            --------
            >>> widget.update_data(new_df)
            >>> widget.update_data([{"a": 1}, {"a": 2}])
            """
            row_data = self._normalize_data(data)
            self.emit("pywry:update_rows", {"rows": row_data})

        def update_columns(self, columns: list[dict[str, Any]]) -> None:
            """Update the grid's column definitions.

            Parameters
            ----------
            columns : list[dict]
                List of AG Grid column definitions.

            Examples
            --------
            >>> widget.update_columns(
            ...     [
            ...         {"field": "name", "headerName": "Name"},
            ...         {"field": "value", "headerName": "Value", "type": "numericColumn"},
            ...     ]
            ... )
            """
            self.emit("pywry:update_columns", {"columnDefs": columns})

        def update_grid(
            self,
            data: Any = None,
            columns: list[dict[str, Any]] | None = None,
            preserve_state: bool = True,
        ) -> None:
            """Update both row data and column definitions atomically.

            Parameters
            ----------
            data : DataFrame | list[dict] | dict[str, list], optional
                New row data.
            columns : list[dict], optional
                New column definitions.
            preserve_state : bool, default True
                If True, preserve column visibility, pinning, width, and order
                for columns that exist in both old and new definitions.

            Examples
            --------
            >>> widget.update_grid(new_df, new_columns)
            >>> widget.update_grid(new_df, new_columns, preserve_state=False)  # Reset state
            """
            payload: dict[str, Any] = {"preserveState": preserve_state}
            if data is not None:
                payload["rows"] = self._normalize_data(data)
            if columns is not None:
                payload["columnDefs"] = columns
            if payload:
                self.emit("pywry:update_grid", payload)

        def save_state(self) -> None:
            """Request the grid to save its current state.

            The grid will emit a 'grid_state_saved' event with the state data.
            Register a callback for 'grid_state_saved' to receive the state.
            """
            self.emit("pywry:save_state", {})

        def restore_state(self, state: dict[str, Any]) -> None:
            """Restore a previously saved grid state.

            Parameters
            ----------
            state : dict
                State object from a previous 'grid_state_saved' event.
            """
            self.emit("pywry:restore_state", {"state": state})

        def reset_state(self) -> None:
            """Reset grid to its default state.

            Clears all column customizations (width, order, visibility, pinning)
            and removes all filters.
            """
            self.emit("pywry:reset_state", {})

        def _register_csv_export_handler(self) -> None:
            """Register automatic CSV export handler for context menu exports."""
            from datetime import datetime
            from pathlib import Path

            def handle_export(data: dict[str, Any], _event_type: str, _label: str) -> None:
                csv_content = data.get("csvContent", "")
                suggested_name = data.get("fileName", "export.csv")
                export_type = data.get("exportType", "unknown")

                # Normalize line endings - AG Grid uses \r\n, convert to \n
                csv_content = csv_content.replace("\r\n", "\n").replace("\r", "\n")

                # Use configured export dir or current directory
                save_dir = Path(self._export_dir) if self._export_dir else Path.cwd()

                # Generate unique filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_name = suggested_name.rsplit(".", 1)[0]
                filename = f"{base_name}_{timestamp}.csv"
                filepath = save_dir / filename

                try:
                    save_dir.mkdir(parents=True, exist_ok=True)
                    filepath.write_text(csv_content, encoding="utf-8")
                    # Show notification in the grid
                    self.emit(
                        "pywry:show_notification",
                        {"message": f"Saved: {filepath}", "duration": 3000},
                    )
                    print(f"[PyWry] CSV exported ({export_type}): {filepath}")
                except Exception as e:
                    self.emit(
                        "pywry:show_notification",
                        {"message": f"Export failed: {e}", "duration": 4000},
                    )
                    print(f"[PyWry] Failed to save CSV: {e}")

            self.on("grid_export_csv", handle_export)

        @property
        def export_dir(self) -> str | None:
            """Get the export directory for CSV files."""
            return self._export_dir

        @export_dir.setter
        def export_dir(self, value: str | None) -> None:
            """Set the export directory for CSV files."""
            self._export_dir = value

        def _normalize_data(self, data: Any) -> list[dict[str, Any]]:
            """Convert various data formats to list of row dicts.

            Parameters
            ----------
            data : DataFrame | list[dict] | dict[str, list]
                Input data in any supported format.

            Returns
            -------
            list[dict]
                Normalized row data as list of dictionaries.
            """
            # Handle pandas DataFrame (duck typing)
            if hasattr(data, "to_dict") and hasattr(data, "columns"):
                result: list[dict[str, Any]] = data.to_dict(orient="records")
                return result
            # Handle list of dicts
            if isinstance(data, list):
                return data
            # Handle dict of lists
            if isinstance(data, dict):
                columns = list(data.keys())
                if columns:
                    length = len(data[columns[0]])
                    return [{col: data[col][i] for col in columns} for i in range(length)]
            return []

        def display(self) -> None:
            """Display the widget in the current output context."""
            from IPython.display import display as ipy_display

            ipy_display(self)

else:

    class PyWryWidget:  # type: ignore[no-redef]
        """Fallback when anywidget is not available."""

        def __init__(self, **kwargs: Any) -> None:
            """Initialize fallback widget."""
            self._label = f"w-{uuid.uuid4().hex[:8]}"
            self.content = kwargs.get("content", "")
            self._handlers: dict[str, list[Callable[..., Any]]] = {}

        @property
        def label(self) -> str:
            """Get widget label."""
            return self._label

        def on(self, event_type: str, callback: Callable[..., Any]) -> None:
            """Register an event handler (no-op in fallback)."""

        def emit(self, event_type: str, data: dict[str, Any] | None = None) -> None:
            """Send an event (no-op in fallback)."""

        def set_content(self, content: str) -> None:
            """Set content."""
            self.content = content

        def _repr_html_(self) -> str:
            """HTML representation."""
            return (
                "<div style='padding:20px;background:#ff6b6b;color:#fff;"
                "border-radius:8px'><b>anywidget not installed. "
                "Run: pip install anywidget</b></div>"
            )

    class PyWryPlotlyWidget(PyWryWidget):  # type: ignore[no-redef]
        """Fallback Plotly widget when anywidget is not available."""

    class PyWryAgGridWidget(PyWryWidget):  # type: ignore[no-redef]
        """Fallback AG Grid widget when anywidget is not available."""

        def update_data(self, data: Any) -> None:
            """Update grid data (no-op in fallback)."""

        def update_columns(self, columns: list[dict[str, Any]]) -> None:
            """Update columns (no-op in fallback)."""

        def update_grid(
            self, data: Any = None, columns: list[dict[str, Any]] | None = None
        ) -> None:
            """Update grid (no-op in fallback)."""
