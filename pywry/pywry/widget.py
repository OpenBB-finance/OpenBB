"""PyWry widget for inline notebook rendering using anywidget."""

# mypy: disable-error-code="import-untyped,no-untyped-call,no-untyped-def,arg-type,type-arg"
# pylint: disable=too-many-lines

from __future__ import annotations

import json
import pathlib
import uuid

from functools import lru_cache
from typing import TYPE_CHECKING, Any

from .state_mixins import EmittingWidget, GridStateMixin, PlotlyStateMixin


if TYPE_CHECKING:
    from collections.abc import Callable

try:
    import anywidget
    import traitlets

    HAS_ANYWIDGET = True
except ImportError:
    HAS_ANYWIDGET = False


# Path to the source JS directory
_SRC_DIR = pathlib.Path(__file__).parent / "frontend" / "src"


@lru_cache(maxsize=1)
def _get_toolbar_handlers_js() -> str:
    """Load the centralized toolbar handlers JavaScript.

    This is the SINGLE source of truth for all toolbar interaction handlers.
    Used by AG Grid, Plotly, and basic widget ESMs.
    """
    toolbar_handlers_file = _SRC_DIR / "toolbar-handlers.js"
    if not toolbar_handlers_file.exists():
        raise FileNotFoundError(f"Toolbar handlers JS not found: {toolbar_handlers_file}")
    return toolbar_handlers_file.read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _get_plotly_widget_esm() -> str:
    """Build the Plotly widget ESM by combining Plotly.js with the widget code."""
    from .assets import (
        get_plotly_js,
        get_plotly_templates_js,
        get_toast_notifications_js,
    )

    # Get the widget render code
    widget_js_file = _SRC_DIR / "plotly-widget.js"
    if not widget_js_file.exists():
        raise FileNotFoundError(f"Widget JS not found: {widget_js_file}")

    widget_js = widget_js_file.read_text(encoding="utf-8")

    # Load centralized toolbar handlers (SINGLE SOURCE OF TRUTH)
    toolbar_handlers_js = _get_toolbar_handlers_js()

    # Inject toolbar handlers into the widget JS
    widget_js = widget_js.replace("__TOOLBAR_HANDLERS__", toolbar_handlers_js)

    # Get Plotly.js
    plotly_js = get_plotly_js()
    if not plotly_js:
        raise RuntimeError("Plotly.js not found in bundled assets")

    # Get Plotly templates for theme switching
    templates_js = get_plotly_templates_js() or ""

    # Get toast notification system
    toast_js = get_toast_notifications_js() or ""

    # Wrap Plotly.js in IIFE to expose to window
    # Plotly 3.x UMD checks for AMD/CommonJS first, we force global export
    return f"""
// Load toast notification system first
{toast_js}

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
    from .assets import (
        get_aggrid_defaults_js,
        get_aggrid_js,
        get_toast_notifications_js,
    )

    aggrid_js = get_aggrid_js()
    if not aggrid_js:
        raise RuntimeError("AG Grid JS not found in bundled assets")

    aggrid_defaults_js = get_aggrid_defaults_js()
    if not aggrid_defaults_js:
        raise RuntimeError("AG Grid defaults JS not found in bundled assets")

    # Get toast notification system
    toast_js = get_toast_notifications_js() or ""

    # Load centralized toolbar handlers (SINGLE SOURCE OF TRUTH)
    toolbar_handlers_js = _get_toolbar_handlers_js()

    # AG Grid widget render code - with ensureAgGrid() that guarantees availability
    # Note: Uses __TOOLBAR_HANDLERS__ placeholder which is replaced below
    widget_js = r"""
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

    // Apply theme class to el (AnyWidget container) for proper theming
    // CSS rule on .pywry-theme-dark/.pywry-theme-light applies background-color
    const isDarkInitial = model.get('theme') === 'dark';
    el.classList.add(isDarkInitial ? 'pywry-theme-dark' : 'pywry-theme-light');

    const container = document.createElement('div');
    container.className = 'pywry-widget';
    // Generate unique widget ID for CSS scoping
    container.dataset.widgetId = 'pywry-' + Math.random().toString(36).substr(2, 9);
    // Theme class for CSS variable switching
    container.classList.add(isDarkInitial ? 'pywry-theme-dark' : 'pywry-theme-light');
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

    // Set toast container for this widget instance
    if (typeof PYWRY_TOAST !== 'undefined' && PYWRY_TOAST.setContainer) {
        PYWRY_TOAST.setContainer(container);
        console.log('[PyWry AG Grid Widget] PYWRY_TOAST container set');
    }

    let gridApi = null;

    function getThemeClass() {
        const isDark = model.get('theme') === 'dark';
        const baseTheme = model.get('aggrid_theme') || 'alpine';
        return 'ag-theme-' + baseTheme + (isDark ? '-dark' : '');
    }

    function applyTheme() {
        const isDark = model.get('theme') === 'dark';
        // Update el (AnyWidget container) theme class - CSS applies background
        el.classList.remove('pywry-theme-dark', 'pywry-theme-light');
        el.classList.add(isDark ? 'pywry-theme-dark' : 'pywry-theme-light');
        // Update container theme
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
    // Global emit function that routes to the correct widget based on gridId
    // This is needed for context menus and other global handlers in aggrid-defaults.js
    window.pywry.emit = function(type, data, element) {
        // Try to find widget from provided element first (for toolbar buttons)
        if (element) {
            const widget = element.closest('.pywry-widget');
            if (widget && widget._pywryModel) {
                const m = widget._pywryModel;
                const evt = JSON.stringify({ type: type, data: data, ts: Date.now() });
                m.set('_js_event', evt);
                m.save_changes();
                return;
            }
        }
        // Find the grid by gridId if provided, otherwise use most recent
        const gridId = data && data.gridId;
        let gridInfo = gridId ? (window.__PYWRY_GRIDS__ || {})[gridId] : null;
        if (!gridInfo) {
            // Fallback to most recent grid
            gridInfo = Object.values(window.__PYWRY_GRIDS__ || {}).pop();
        }
        if (gridInfo && gridInfo.div) {
            const widget = gridInfo.div.closest('.pywry-widget');
            if (widget && widget._pywryModel) {
                const m = widget._pywryModel;
                const evt = JSON.stringify({ type: type, data: data, ts: Date.now() });
                m.set('_js_event', evt);
                m.save_changes();
                return;
            }
        }
        // Last resort: find any widget on page
        const anyWidget = document.querySelector('.pywry-widget');
        if (anyWidget && anyWidget._pywryModel) {
            const m = anyWidget._pywryModel;
            const evt = JSON.stringify({ type: type, data: data, ts: Date.now() });
            m.set('_js_event', evt);
            m.save_changes();
            return;
        }
        console.warn('[PyWry] No widget found for global emit:', type, data);
    };
    // Also add global 'on' for event handlers in aggrid-defaults.js and user scripts
    if (!window.pywry._handlers) {
        window.pywry._handlers = {};
    }
    if (!window.pywry._pending) {
        window.pywry._pending = [];
    }
    // Always update on/fire to ensure pending event support
    window.pywry.on = function(type, callback) {
        if (!window.pywry._handlers[type]) window.pywry._handlers[type] = [];
        window.pywry._handlers[type].push(callback);
        // Flush any pending events for this type
        const pending = (window.pywry._pending || []).filter(p => p.type === type);
        window.pywry._pending = (window.pywry._pending || []).filter(p => p.type !== type);
        pending.forEach(p => {
            callback(p.data);
        });
    };
    window.pywry._fire = function(type, data) {
        // Check for sensitive event types - don't log data
        const isSensitive = type.includes(':reveal') || type.includes(':copy') ||
                           type.includes('secret') || type.includes('password') ||
                           type.includes('api-key') || type.includes('token');
        if (window.PYWRY_DEBUG && !isSensitive) {
            console.log('[PyWry] window.pywry._fire:', type, data);
        }
        const handlers = window.pywry._handlers[type] || [];
        if (handlers.length === 0) {
            // Queue if no handlers yet (script may not have run)
            window.pywry._pending = window.pywry._pending || [];
            window.pywry._pending.push({type: type, data: data});
        } else {
            handlers.forEach(h => h(data));
        }
    };

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

    // Handle alert/toast notifications - registered via pywry.on() for consistent handling
    pywry.on('pywry:alert', (data) => {
        console.log('[PyWry AG Grid] Alert received:', data);
        const message = data.message || data.text || '';
        const type = data.type || 'info';
        if (typeof PYWRY_TOAST !== 'undefined') {
            if (type === 'confirm') {
                PYWRY_TOAST.confirm({
                    message: message,
                    title: data.title,
                    position: data.position,
                    container: container,
                    onConfirm: () => {
                        if (data.callback_event) {
                            pywry.emit(data.callback_event, { confirmed: true });
                        }
                    },
                    onCancel: () => {
                        if (data.callback_event) {
                            pywry.emit(data.callback_event, { confirmed: false });
                        }
                    }
                });
            } else {
                PYWRY_TOAST.show({
                    message: message,
                    title: data.title,
                    type: type,
                    duration: data.duration,
                    position: data.position,
                    container: container
                });
            }
        } else {
            alert(message);
        }
    });

    // Remove old handlers to prevent duplicates on re-render
    model.off('change:_py_event');
    model.off('change:data');
    model.off('change:columns');
    model.off('change:theme');

    model.on('change:_py_event', () => {
        try {
            const event = JSON.parse(model.get('_py_event') || '{}');
            if (event.type) {
                // Handle theme updates - set model property AND apply directly
                if (event.type === 'pywry:update-theme' && event.data && event.data.theme) {
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
                // Handle CSS injection - inject or update a style element INSIDE the widget container
                // This ensures CSS isolation between multiple widgets in the same notebook
                if (event.type === 'pywry:inject-css' && event.data && event.data.css) {
                    const baseId = event.data.id || 'pywry-injected-style';
                    const widgetId = container.dataset.widgetId;
                    const scopedId = baseId + '-' + widgetId;
                    let css = event.data.css;
                    const widgetSelector = '[data-widget-id="' + widgetId + '"]';

                    // Scope ALL selectors to this widget container
                    // Replace :root with widget selector
                    css = css.replace(/:root\s*\{/g, widgetSelector + ' {');
                    // Prepend widget selector to class/element selectors (e.g., .pywry-btn-neutral)
                    // Match selectors at start of line or after closing brace
                    css = css.replace(/(\n\s*)(\.[a-zA-Z])/g, '$1' + widgetSelector + ' $2');
                    // Also handle selectors right after closing brace (for minified CSS)
                    css = css.replace(/(\}\s*)(\.[a-zA-Z])/g, '$1' + widgetSelector + ' $2');

                    // Look for existing style element INSIDE container first
                    let style = container.querySelector('style[data-pywry-style="' + scopedId + '"]');
                    if (style) {
                        style.textContent = css;
                    } else {
                        style = document.createElement('style');
                        style.setAttribute('data-pywry-style', scopedId);
                        style.textContent = css;
                        // Insert at beginning of container for proper cascade
                        container.insertBefore(style, container.firstChild);
                    }
                    console.log('[PyWry] Injected scoped CSS with id:', scopedId);
                }
                // Handle CSS removal - scoped to widget
                if (event.type === 'pywry:remove-css' && event.data && event.data.id) {
                    const baseId = event.data.id;
                    const widgetId = container.dataset.widgetId;
                    const scopedId = baseId + '-' + widgetId;
                    const style = container.querySelector('style[data-pywry-style="' + scopedId + '"]');
                    if (style) {
                        style.remove();
                        console.log('[PyWry] Removed scoped CSS with id:', scopedId);
                    }
                }
                // Handle inline style updates on elements - SCOPED to widget container
                // Usage: emit('pywry:set-style', {selector: '.my-class', styles: {fontWeight: 'bold'}})
                if (event.type === 'pywry:set-style' && event.data && event.data.styles) {
                    let elements = [];
                    if (event.data.id) {
                        // Use container.querySelector to scope to this widget only
                        const el = container.querySelector('#' + event.data.id);
                        if (el) elements.push(el);
                    } else if (event.data.selector) {
                        // Scope selector to container
                        elements = Array.from(container.querySelectorAll(event.data.selector));
                    }
                    elements.forEach(function(el) {
                        Object.keys(event.data.styles).forEach(function(prop) {
                            el.style[prop] = event.data.styles[prop];
                        });
                    });
                    console.log('[PyWry] Set styles on', elements.length, 'elements (scoped):', event.data.styles);
                }
                // Built-in handler for updating element content - SCOPED to widget container
                // Usage: emit('pywry:set-content', {id: 'my-element', html: '<b>Bold</b>'})
                if (event.type === 'pywry:set-content' && event.data) {
                    let elements = [];
                    if (event.data.id) {
                        // Use container.querySelector to scope to this widget only
                        const el = container.querySelector('#' + event.data.id);
                        if (el) elements.push(el);
                    } else if (event.data.selector) {
                        // Scope selector to container
                        elements = Array.from(container.querySelectorAll(event.data.selector));
                    }
                    elements.forEach(function(el) {
                        if ('html' in event.data) {
                            el.innerHTML = event.data.html;
                        } else if ('text' in event.data) {
                            el.textContent = event.data.text;
                        }
                    });
                    console.log('[PyWry] Set content on', elements.length, 'elements (scoped)');
                }
                // Handle grid data updates (row data)
                if (event.type === 'grid:update-data' && gridApi && event.data && event.data.data) {
                    gridApi.setGridOption('rowData', event.data.data);
                    console.log('[PyWry] Grid data updated:', event.data.data.length, 'rows');
                }
                // Handle column definition updates
                if (event.type === 'grid:update-columns' && gridApi && event.data && event.data.columnDefs) {
                    gridApi.setGridOption('columnDefs', event.data.columnDefs);
                    console.log('[PyWry] Grid columns updated:', event.data.columnDefs.length, 'columns');
                }
                // Handle generic options
                if (event.type === 'grid:update-options' && gridApi && event.data && event.data.options) {
                    const options = event.data.options;
                    if (options.columnDefs) {
                        gridApi.setGridOption('columnDefs', options.columnDefs);
                    }
                    if (options.rowData) {
                         gridApi.setGridOption('rowData', options.rowData);
                    }
                     // Apply other options
                     Object.keys(options).forEach(key => {
                         if (key !== 'columnDefs' && key !== 'rowData') {
                             gridApi.setGridOption(key, options[key]);
                         }
                     });
                    console.log('[PyWry] Grid options updated');
                }
                // Handle cell updates
                if (event.type === 'grid:update-cell' && gridApi && event.data) {
                    // grid:update-cell { rowId, colId, value }
                    // Simplest approach: find row node by ID if row IDs are used, otherwise this is hard.
                    // Assuming rowId is provided and grid uses row IDs.
                    const rowNode = gridApi.getRowNode(event.data.rowId);
                    if (rowNode) {
                        rowNode.setDataValue(event.data.colId, event.data.value);
                    }
                }
                // Handle state request
                if (event.type === 'grid:request-state' && gridApi) {
                    const state = {
                        columnState: gridApi.getColumnState(),
                        filterModel: gridApi.getFilterModel()
                    };
                    // Emit response
                    pywry.emit('grid:state-response', { state: state, gridId: event.data.gridId });
                }
                // Handle restore state
                if (event.type === 'grid:restore-state' && gridApi && event.data && event.data.state) {
                    const state = event.data.state;
                    if (state.columnState) {
                        gridApi.applyColumnState({ state: state.columnState, applyOrder: true });
                    }
                    if (state.filterModel) {
                        gridApi.setFilterModel(state.filterModel);
                    }
                }
                // Handle reset state
                if (event.type === 'grid:reset-state' && gridApi) {
                    gridApi.resetColumnState();
                    gridApi.setFilterModel(null);
                    if (event.data.hard) {
                        // Hard reset - not fully implemented in JS logic yet besides clearing state
                        gridApi.setFilterModel(null);
                        gridApi.resetColumnState();
                    }
                }

                // Handle file downloads - triggers browser save dialog
                if (event.type === 'pywry:download' && event.data && event.data.content && event.data.filename) {
                    const mimeType = event.data.mimeType || 'application/octet-stream';
                    const blob = new Blob([event.data.content], { type: mimeType });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = event.data.filename;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                    console.log('[PyWry] Downloaded:', event.data.filename);
                }

                // Handle navigation
                if (event.type === 'pywry:navigate' && event.data && event.data.url) {
                    window.location.href = event.data.url;
                }

                // Handle HTML content update
                if (event.type === 'pywry:update-html' && event.data && event.data.html) {
                    container.innerHTML = event.data.html;
                    initToolbarHandlers(container, pywry);
                }

                const inlineHandledEvents = ['pywry:update-theme', 'pywry:inject-css', 'pywry:remove-css',
                    'pywry:set-style', 'pywry:set-content', 'pywry:download', 'pywry:navigate',
                    'pywry:update-html', 'pywry:alert'];
                pywry._fire(event.type, event.data);
                if (!inlineHandledEvents.includes(event.type) && window.pywry && window.pywry._fire && window.pywry !== pywry) {
                    window.pywry._fire(event.type, event.data);
                }
            }
        } catch(e) {
            console.error('[PyWry] Failed to parse Python event:', e);
        }
    });

    __TOOLBAR_HANDLERS__

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
                // Initialize toolbar handlers (dropdowns, buttons, inputs, etc.)
                initToolbarHandlers(container, pywry);
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
        const gridConfig = model.get('grid_config');
        // Log every 10th attempt to reduce spam
        if (attempt % 10 === 0) {
            console.log('[PyWry AG Grid] waitAndRender attempt', attempt, '- agGrid:', !!agGridLib, 'gridConfig:', !!gridConfig);
        }

        if (agGridLib && gridConfig) {
            renderContent(0);
        } else if (attempt < 100) {
            setTimeout(() => waitAndRender(attempt + 1), 50);
        } else {
            console.error('[PyWry AG Grid] Timeout waiting for AG Grid/gridConfig');
            container.innerHTML = '<div style="color:#ff4444;padding:20px;font-family:monospace;">' +
                'ERROR: Timeout waiting for ' + (!agGridLib ? 'AG Grid library' : 'grid config') + '</div>';
        }
    }
    waitAndRender(0);
}
export default { render };
"""
    # Inject toolbar handlers using simple replacement (avoids escaping issues)
    widget_js = widget_js.replace("__TOOLBAR_HANDLERS__", toolbar_handlers_js)

    # AG Grid UMD checks for AMD (define) first - we must disable it temporarily
    return f"""
// Load toast notification system first
{toast_js}

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
    console.log('[PyWry AG Grid ESM] After load - self.agGrid:', typeof self.agGrid, 'window.agGrid:', typeof window.agGrid);

    // AG Grid should be available now - check multiple locations
    if (typeof self.agGrid !== 'undefined' && self.agGrid.createGrid) {{
        _agGridLib = self.agGrid;
        window.agGrid = self.agGrid;
        window._pywryAgGrid = self.agGrid; // Extra persistence
        console.log('[PyWry AG Grid ESM] SUCCESS - loaded AG Grid from self.agGrid');
    }} else if (typeof window.agGrid !== 'undefined' && window.agGrid.createGrid) {{
        _agGridLib = window.agGrid;
        window._pywryAgGrid = window.agGrid;
        console.log('[PyWry AG Grid ESM] SUCCESS - loaded AG Grid from window.agGrid');
    }} else if (typeof agGrid !== 'undefined' && agGrid.createGrid) {{
        _agGridLib = agGrid;
        window.agGrid = agGrid;
        window._pywryAgGrid = agGrid;
        console.log('[PyWry AG Grid ESM] SUCCESS - loaded AG Grid from global agGrid');
    }} else {{
        console.error('[PyWry AG Grid ESM] FAILED - AG Grid not found in self, window, or global scope after loading');
    }}
}} else {{
    console.log('[PyWry AG Grid ESM] AG Grid already loaded, reusing existing instance from:',
        _agGridLib ? 'cache' : 'unknown');
}}

// Load PyWry AG Grid defaults (single source of truth for all grid config)
{aggrid_defaults_js}

{widget_js}
"""


@lru_cache(maxsize=1)
def _get_widget_esm() -> str:
    """Build the basic widget ESM with centralized toolbar handlers."""
    from .assets import get_scrollbar_js, get_toast_notifications_js

    # Load centralized toolbar handlers (SINGLE SOURCE OF TRUTH)
    toolbar_handlers_js = _get_toolbar_handlers_js()

    # Get toast notification system
    toast_js = get_toast_notifications_js() or ""

    # Get custom scrollbar JS
    scrollbar_js = get_scrollbar_js() or ""

    # Prepend toast JS and scrollbar JS to the widget ESM
    esm_with_libs = toast_js + "\n\n" + scrollbar_js + "\n\n" + _WIDGET_ESM

    return esm_with_libs.replace("__TOOLBAR_HANDLERS__", toolbar_handlers_js)


# Basic widget ESM without Plotly
_WIDGET_ESM = r"""
function render({ model, el }) {
    // Inject CSS into the main document to fix Jupyter output cell backgrounds
    // This must be done here because _css only applies inside the widget shadow DOM
    const JUPYTER_FIX_ID = 'pywry-jupyter-fix-css';
    if (!document.getElementById(JUPYTER_FIX_ID)) {
        const style = document.createElement('style');
        style.id = JUPYTER_FIX_ID;
        style.textContent = `
            .cell-output-ipywidget-background {
                background-color: transparent !important;
            }
            .jp-OutputArea-output {
                background-color: transparent !important;
            }
        `;
        document.head.appendChild(style);
    }

    let modelHeight = model.get('height');
    let modelWidth = model.get('width');

    // Helper to ensure units (e.g. "200" -> "200px")
    const toCss = (v) => {
        if (!v) return v;
        const s = String(v).trim();
        return /^\d+$/.test(s) ? s + 'px' : s;
    };

    modelHeight = toCss(modelHeight);
    modelWidth = toCss(modelWidth);

    // CRITICAL: Set height on el (AnyWidget's container) to constrain output size
    if (modelHeight) {
        el.style.height = modelHeight;
        // Ensure el is displayed as block/inline-block to respect height
        if (!el.style.display) el.style.display = 'block';
    }
    if (modelWidth) {
        el.style.width = modelWidth;
    }

    // Apply theme class to el (AnyWidget container) for proper theming
    // CSS rule on .pywry-theme-dark/.pywry-theme-light applies background-color
    const isDarkInitial = model.get('theme') === 'dark';
    el.classList.add(isDarkInitial ? 'pywry-theme-dark' : 'pywry-theme-light');

    const container = document.createElement('div');
    container.className = 'pywry-widget pywry-custom-scrollbar';
    container.dataset.widgetId = 'pywry-' + Math.random().toString(36).substr(2, 9);
    container.classList.add(isDarkInitial ? 'pywry-theme-dark' : 'pywry-theme-light');

    // Set CSS variables - CSS rules will use these via var(--pywry-widget-height)
    if (modelHeight) {
        container.style.setProperty('--pywry-widget-height', modelHeight);
    }
    if (modelWidth) {
        container.style.setProperty('--pywry-widget-width', modelWidth);
    }

    function applyTheme() {
        const isDark = model.get('theme') === 'dark';
        // Update el (AnyWidget container) theme class - CSS applies background
        el.classList.remove('pywry-theme-dark', 'pywry-theme-light');
        el.classList.add(isDark ? 'pywry-theme-dark' : 'pywry-theme-light');
        // Update container theme
        container.classList.remove('pywry-theme-dark', 'pywry-theme-light');
        container.classList.add(isDark ? 'pywry-theme-dark' : 'pywry-theme-light');
    }
    applyTheme();
    el.appendChild(container);

    // Initialize custom scrollbars for this widget container
    if (typeof PYWRY_SCROLLBARS !== 'undefined' && PYWRY_SCROLLBARS.init) {
        PYWRY_SCROLLBARS.init(container);
        console.log('[PyWry Basic Widget] Custom scrollbars initialized');
    }

    // Set toast container for this widget instance
    if (typeof PYWRY_TOAST !== 'undefined' && PYWRY_TOAST.setContainer) {
        PYWRY_TOAST.setContainer(container);
        console.log('[PyWry Basic Widget] PYWRY_TOAST container set');
    }

    // Attach model to container for global dispatch lookup
    container._pywryModel = model;

    // Initialize global dispatcher if not present (with full API for user scripts)
    if (!window.pywry || !window.pywry._fire) {
        window.pywry = {
            _handlers: {},
            _pending: [],
            on: function(type, callback) {
                if (!this._handlers[type]) this._handlers[type] = [];
                this._handlers[type].push(callback);
                // Flush pending events for this type
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
            },
            emit: function(type, data, element) {
                // Try to find widget from provided element first (for toolbar buttons)
                if (element) {
                    const widget = element.closest('.pywry-widget');
                    if (widget && widget._pywryModel) {
                        const m = widget._pywryModel;
                        const evt = JSON.stringify({ type: type, data: data, ts: Date.now() });
                        m.set('_js_event', evt);
                        m.save_changes();
                        return;
                    }
                }
                // Fallback: find any widget on page
                const anyWidget = document.querySelector('.pywry-widget');
                if (anyWidget && anyWidget._pywryModel) {
                    const m = anyWidget._pywryModel;
                    const evt = JSON.stringify({ type: type, data: data, ts: Date.now() });
                    m.set('_js_event', evt);
                    m.save_changes();
                    return;
                }
                console.warn('[PyWry] No widget found for global emit:', type, data);
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

    // Handle alert/toast notifications - registered via pywry.on() for consistent handling
    pywry.on('pywry:alert', (data) => {
        console.log('[PyWry Basic Widget] Alert received:', data);
        const message = data.message || data.text || '';
        const type = data.type || 'info';
        if (typeof PYWRY_TOAST !== 'undefined') {
            if (type === 'confirm') {
                PYWRY_TOAST.confirm({
                    message: message,
                    title: data.title,
                    position: data.position,
                    container: container,
                    onConfirm: () => {
                        if (data.callback_event) {
                            pywry.emit(data.callback_event, { confirmed: true });
                        }
                    },
                    onCancel: () => {
                        if (data.callback_event) {
                            pywry.emit(data.callback_event, { confirmed: false });
                        }
                    }
                });
            } else {
                PYWRY_TOAST.show({
                    message: message,
                    title: data.title,
                    type: type,
                    duration: data.duration,
                    position: data.position,
                    container: container
                });
            }
        } else {
            alert(message);
        }
    });

    // =========================================================================
    // TOOLBAR HANDLERS - LOADED FROM CENTRALIZED SOURCE
    // See: frontend/src/toolbar-handlers.js
    // =========================================================================
    __TOOLBAR_HANDLERS__

    // Remove old handlers to prevent duplicates on re-render
    model.off('change:_py_event');
    model.off('change:content');
    model.off('change:theme');

    model.on('change:_py_event', () => {
        try {
            const event = JSON.parse(model.get('_py_event') || '{}');
            if (event.type) {
                // Handle theme updates - set model property AND apply directly
                if (event.type === 'pywry:update-theme' && event.data && event.data.theme) {
                    const isDark = event.data.theme.includes('dark');
                    const newTheme = isDark ? 'dark' : 'light';
                    model.set('theme', newTheme);
                    model.save_changes();
                    // Apply theme directly (model.on('change:theme') only fires for changes FROM Python)
                    applyTheme();
                    console.log('[PyWry] Model theme set to:', newTheme);
                }
                // Handle CSS injection - inject or update a style element INSIDE the widget container
                // This ensures CSS isolation between multiple widgets in the same notebook
                if (event.type === 'pywry:inject-css' && event.data && event.data.css) {
                    const baseId = event.data.id || 'pywry-injected-style';
                    const widgetId = container.dataset.widgetId;
                    const scopedId = baseId + '-' + widgetId;
                    let css = event.data.css;
                    const widgetSelector = '[data-widget-id="' + widgetId + '"]';

                    // Scope ALL selectors to this widget container
                    // Replace :root with widget selector
                    css = css.replace(/:root\s*\{/g, widgetSelector + ' {');
                    // Prepend widget selector to class/element selectors (e.g., .pywry-btn-neutral)
                    // Match selectors at start of line or after closing brace
                    css = css.replace(/(\n\s*)(\.[a-zA-Z])/g, '$1' + widgetSelector + ' $2');
                    // Also handle selectors right after closing brace (for minified CSS)
                    css = css.replace(/(\}\s*)(\.[a-zA-Z])/g, '$1' + widgetSelector + ' $2');

                    // Look for existing style element INSIDE container first
                    let style = container.querySelector('style[data-pywry-style="' + scopedId + '"]');
                    if (style) {
                        style.textContent = css;
                    } else {
                        style = document.createElement('style');
                        style.setAttribute('data-pywry-style', scopedId);
                        style.textContent = css;
                        // Insert at beginning of container for proper cascade
                        container.insertBefore(style, container.firstChild);
                    }
                    console.log('[PyWry] Injected scoped CSS with id:', scopedId);
                }
                // Handle CSS removal - scoped to widget
                if (event.type === 'pywry:remove-css' && event.data && event.data.id) {
                    const baseId = event.data.id;
                    const widgetId = container.dataset.widgetId;
                    const scopedId = baseId + '-' + widgetId;
                    const style = container.querySelector('style[data-pywry-style="' + scopedId + '"]');
                    if (style) {
                        style.remove();
                        console.log('[PyWry] Removed scoped CSS with id:', scopedId);
                    }
                }
                // Handle inline style updates on elements - SCOPED to widget container
                if (event.type === 'pywry:set-style' && event.data && event.data.styles) {
                    let elements = [];
                    if (event.data.id) {
                        // Use container.querySelector to scope to this widget only
                        const el = container.querySelector('#' + event.data.id);
                        if (el) elements.push(el);
                    } else if (event.data.selector) {
                        // Scope selector to container
                        elements = Array.from(container.querySelectorAll(event.data.selector));
                    }
                    elements.forEach(function(el) {
                        Object.keys(event.data.styles).forEach(function(prop) {
                            el.style[prop] = event.data.styles[prop];
                        });
                    });
                    console.log('[PyWry] Set styles on', elements.length, 'elements (scoped):', event.data.styles);
                }
                // Built-in handler for updating element content - SCOPED to widget container
                if (event.type === 'pywry:set-content' && event.data) {
                    let elements = [];
                    if (event.data.id) {
                        // Use container.querySelector to scope to this widget only
                        const el = container.querySelector('#' + event.data.id);
                        if (el) elements.push(el);
                    } else if (event.data.selector) {
                        // Scope selector to container
                        elements = Array.from(container.querySelectorAll(event.data.selector));
                    }
                    elements.forEach(function(el) {
                        if ('html' in event.data) {
                            el.innerHTML = event.data.html;
                        } else if ('text' in event.data) {
                            el.textContent = event.data.text;
                        }
                    });
                    console.log('[PyWry] Set content on', elements.length, 'elements');
                }

                // Handle file downloads - triggers browser save dialog
                if (event.type === 'pywry:download' && event.data && event.data.content && event.data.filename) {
                    const mimeType = event.data.mimeType || 'application/octet-stream';
                    const blob = new Blob([event.data.content], { type: mimeType });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = event.data.filename;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                    console.log('[PyWry] Downloaded:', event.data.filename);
                }

                // Handle navigation
                if (event.type === 'pywry:navigate' && event.data && event.data.url) {
                    window.location.href = event.data.url;
                }

                // Handle HTML content update
                if (event.type === 'pywry:update-html' && event.data && event.data.html) {
                    container.innerHTML = event.data.html;
                    initToolbarHandlers(container, pywry);
                }

                const inlineHandledEvents = ['pywry:update-theme', 'pywry:inject-css', 'pywry:remove-css',
                    'pywry:set-style', 'pywry:set-content', 'pywry:download', 'pywry:navigate',
                    'pywry:update-html', 'pywry:alert'];
                pywry._fire(event.type, event.data);
                if (!inlineHandledEvents.includes(event.type) && window.pywry && window.pywry._fire && window.pywry !== pywry) {
                    window.pywry._fire(event.type, event.data);
                }
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
        console.log('[PyWry Basic] renderContent() called');
        console.log('[PyWry Basic] content length:', content ? content.length : 0);
        console.log('[PyWry Basic] content preview:', content ? content.substring(0, 100) : 'EMPTY');
        if (content) {
            container.innerHTML = content;
            console.log('[PyWry Basic] container.innerHTML SET, container.children.length:', container.children.length);
            setTimeout(() => runScripts(container), 0);
            setTimeout(() => initToolbarHandlers(container, pywry), 10);
        } else {
            console.error('[PyWry Basic] NO CONTENT - model.get(content) returned empty!');
            container.innerHTML = '<div style="color:red;padding:20px;background:yellow;">ERROR: No content received from Python. content=' + JSON.stringify(content) + '</div>';
        }
    }

    model.on('change:content', renderContent);
    model.on('change:theme', applyTheme);

    // Call renderContent immediately AND after a delay to handle async trait sync
    renderContent();
    setTimeout(renderContent, 0);
    setTimeout(renderContent, 100);
}
export default { render };
"""


@lru_cache(maxsize=1)
def _get_pywry_base_css() -> str:
    """Load pywry base CSS for widget theming, including toast styles."""
    from .assets import get_pywry_css, get_toast_css

    # Fix for Jupyter notebook output cell backgrounds - must be in the widget CSS
    # to override the default white/gray backgrounds that hide the widget theme
    jupyter_fix_css = """
.cell-output-ipywidget-background {
    background-color: transparent !important;
}
.jp-OutputArea-output {
    background-color: transparent !important;
}
"""
    base_css = get_pywry_css() or ""
    toast_css = get_toast_css() or ""
    return f"{jupyter_fix_css}\n{base_css}\n{toast_css}"


if HAS_ANYWIDGET:

    class PyWryWidget(anywidget.AnyWidget, EmittingWidget):  # pylint: disable=abstract-method
        """Widget for inline notebook rendering using anywidget (no Plotly).

        Implements BaseWidget protocol for unified API.
        """

        _esm = _get_widget_esm()
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
            # Set traits BEFORE calling super().__init__() to ensure they're available when render() is called
            kwargs["content"] = content
            kwargs["theme"] = theme
            kwargs["width"] = width
            kwargs["height"] = height

            super().__init__(**kwargs)
            self._label = f"w-{uuid.uuid4().hex[:8]}"
            self._handlers: dict[str, list[Callable[[dict[str, Any], str, str], Any]]] = {}
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
                handlers = self._handlers.get(event_type, [])
                for handler in handlers:
                    handler(event_data, event_type, self._label)
            except Exception as e:
                print(f"[PyWry] Error handling JS event: {e}")
                import traceback

                traceback.print_exc()

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
            self.send_state("_py_event")  # Force sync to frontend

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

        @classmethod
        def from_html(
            cls,
            content: str,
            callbacks: (dict[str, Callable[[dict[str, Any], str, str], Any]] | None) = None,
            theme: str = "dark",
            width: str = "100%",
            height: str = "500px",
            toolbars: list | None = None,
        ) -> PyWryWidget:
            """Create a PyWryWidget from HTML content with callbacks.

            Parameters
            ----------
            content : str
                HTML content to display.
            callbacks : dict[str, Callable], optional
                Event callbacks: {event_type: handler_function}.
            theme : str
                Color theme ('dark' or 'light').
            width : str
                Widget width (CSS value).
            height : str
                Widget height (CSS value or int pixels).
            toolbars : list, optional
                List of toolbar configurations.

            Returns
            -------
            PyWryWidget
                Configured widget with callbacks registered.
            """
            from .toolbar import (
                Toolbar,
                register_secret_handlers_for_toolbar,
                wrap_content_with_toolbars,
            )

            # Always wrap content with proper container structure
            # This ensures consistent styling even without toolbars
            content = wrap_content_with_toolbars(content, toolbars)

            # Normalize height to string with px
            height_str = f"{height}px" if isinstance(height, int) else height

            # Create widget
            widget = cls(
                content=content,
                theme=theme,
                width=width,
                height=height_str,
            )

            # Register callbacks
            if callbacks:
                for event_type, handler in callbacks.items():
                    widget.on(event_type, handler)

            # Register secret handlers for all SecretInputs in toolbars
            # This enables reveal/copy functionality
            if toolbars:
                for toolbar_cfg in toolbars:
                    if isinstance(toolbar_cfg, Toolbar):
                        register_secret_handlers_for_toolbar(
                            toolbar_cfg,
                            widget.on,
                            widget.emit,
                        )

            return widget

    class PyWryPlotlyWidget(PyWryWidget, PlotlyStateMixin):  # pylint: disable=abstract-method,too-many-ancestors
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
        chart_id = traitlets.Unicode("").tag(sync=True)  # Unique ID for scoped events
        _js_event = traitlets.Unicode("").tag(sync=True)
        _py_event = traitlets.Unicode("").tag(sync=True)

        def __init__(
            self,
            content: str = "",
            theme: str = "dark",
            width: str = "100%",
            height: str = "500px",
            figure_json: str = "",
            chart_id: str = "",
            **kwargs,
        ):
            """Initialize the widget with Plotly bundled."""
            super().__init__(content=content, theme=theme, width=width, height=height, **kwargs)
            self.figure_json = figure_json
            self.chart_id = chart_id or self._label
            self.observe(self._handle_js_event, names=["_js_event"])

        def emit(self, event_type: str, data: dict[str, Any] | None = None) -> None:
            """Send an event from Python to JavaScript."""
            # Include chart_id for scoped event handling
            payload = data.copy() if data else {}
            payload.setdefault("chartId", self.chart_id)
            super().emit(event_type, payload)

    class PyWryAgGridWidget(PyWryWidget, GridStateMixin):  # pylint: disable=abstract-method,too-many-ancestors
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
            super().__init__(content=content, theme=theme, width=width, height=height, **kwargs)
            self._export_dir = export_dir
            self.aggrid_theme = aggrid_theme
            self.grid_config = grid_config
            self.grid_id = grid_id or self._label  # Use label as default grid_id
            self.observe(self._handle_js_event, names=["_js_event"])

            # Automatically register CSV export handler
            self._register_csv_export_handler()

        def emit(self, event_type: str, data: dict[str, Any] | None = None) -> None:
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
            payload.setdefault("gridId", self.grid_id)
            super().emit(event_type, payload)

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
                        "pywry:show-notification",
                        {"message": f"Saved: {filepath}", "duration": 3000},
                    )
                    print(f"[PyWry] CSV exported ({export_type}): {filepath}")
                except Exception as e:
                    self.emit(
                        "pywry:show-notification",
                        {"message": f"Export failed: {e}", "duration": 4000},
                    )
                    print(f"[PyWry] Failed to save CSV: {e}")

            self.on("grid:export-csv", handle_export)

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

    class PyWryWidget(EmittingWidget):  # type: ignore[no-redef]
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
