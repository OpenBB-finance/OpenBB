"""JavaScript bridge scripts for PyWry."""

from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .models import WindowConfig


PYWRY_BRIDGE_JS = """
(function() {
    'use strict';

    // Create or extend window.pywry - DO NOT replace to preserve existing handlers
    if (!window.pywry) {
        window.pywry = {
            theme: 'dark',
            _handlers: {}
        };
    }

    // Ensure _handlers exists
    if (!window.pywry._handlers) {
        window.pywry._handlers = {};
    }

    // Add/update methods on existing object (preserves registered handlers)
    window.pywry.result = function(data) {
        const payload = {
            data: data,
            window_label: window.__PYWRY_LABEL__ || 'unknown'
        };
        if (window.__TAURI__ && window.__TAURI__.pytauri && window.__TAURI__.pytauri.pyInvoke) {
            window.__TAURI__.pytauri.pyInvoke('pywry_result', payload);
        }
    };

    window.pywry.openFile = function(path) {
        if (window.__TAURI__ && window.__TAURI__.pytauri && window.__TAURI__.pytauri.pyInvoke) {
            window.__TAURI__.pytauri.pyInvoke('open_file', { path: path });
        }
    };

    window.pywry.devtools = function() {
        if (window.__TAURI__ && window.__TAURI__.webview) {
            console.log('DevTools requested');
        }
    };

    window.pywry.emit = function(eventType, data) {
        // Validate event type format
        if (eventType !== '*' && !/^[a-z][a-z0-9]*:[a-z][a-z0-9-]*$/.test(eventType)) {
            console.error('Invalid event type:', eventType, 'Must match namespace:event-name pattern');
            return;
        }
        const payload = {
            label: window.__PYWRY_LABEL__ || 'main',
            event_type: eventType,
            data: data || {}
        };
        if (window.__TAURI__ && window.__TAURI__.pytauri && window.__TAURI__.pytauri.pyInvoke) {
            window.__TAURI__.pytauri.pyInvoke('pywry_event', payload);
        }
    };

    window.pywry.on = function(eventType, callback) {
        if (!this._handlers[eventType]) {
            this._handlers[eventType] = [];
        }
        this._handlers[eventType].push(callback);
    };

    window.pywry.off = function(eventType, callback) {
        if (!this._handlers[eventType]) return;
        if (!callback) {
            delete this._handlers[eventType];
        } else {
            this._handlers[eventType] = this._handlers[eventType].filter(
                function(h) { return h !== callback; }
            );
        }
    };

    window.pywry._trigger = function(eventType, data) {
        console.log('[PyWry] _trigger called:', eventType, data);
        console.log('[PyWry] registered handlers:', Object.keys(this._handlers));
        var handlers = this._handlers[eventType] || [];
        var wildcardHandlers = this._handlers['*'] || [];
        console.log('[PyWry] found', handlers.length, 'handlers for', eventType);
        handlers.concat(wildcardHandlers).forEach(function(handler) {
            try {
                handler(data, eventType);
            } catch (e) {
                console.error('Error in event handler:', e);
            }
        });
    };

    window.pywry.dispatch = function(eventType, data) {
        console.log('[PyWry] dispatch called:', eventType, data);
        this._trigger(eventType, data);
    };

    console.log('PyWry bridge initialized/updated');
})();
"""

THEME_MANAGER_JS = """
(function() {
    'use strict';

    if (window.__TAURI__ && window.__TAURI__.event) {
        window.__TAURI__.event.listen('pywry:theme-update', function(event) {
            var mode = event.payload.mode;
            updateTheme(mode);
        });
    }

    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
            var html = document.documentElement;
            if (html.dataset.themeMode === 'system') {
                updateTheme('system');
            }
        });
    }

    function updateTheme(mode) {
        var html = document.documentElement;
        var resolvedMode = mode;

        html.dataset.themeMode = mode;

        if (mode === 'system') {
            var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            resolvedMode = prefersDark ? 'dark' : 'light';
        }

        html.classList.remove('light', 'dark');
        html.classList.add(resolvedMode);
        window.pywry.theme = resolvedMode;

        var isDark = resolvedMode === 'dark';

        if (window.Plotly && window.__PYWRY_PLOTLY_DIV__) {
            Plotly.relayout(window.__PYWRY_PLOTLY_DIV__, {
                template: isDark ? 'plotly_dark' : 'plotly_white'
            });
        }

        var gridDiv = document.querySelector('[class*="ag-theme-"]');
        if (gridDiv) {
            var classList = Array.from(gridDiv.classList);
            classList.forEach(function(cls) {
                if (cls.startsWith('ag-theme-')) {
                    var baseTheme = cls.replace('-dark', '');
                    gridDiv.classList.remove(cls);
                    gridDiv.classList.add(isDark ? baseTheme + '-dark' : baseTheme);
                }
            });
        }

        window.pywry._trigger('pywry:theme-update', { mode: resolvedMode, original: mode });
    }

    // Register handler for pywry:update_theme events IMMEDIATELY (not in DOMContentLoaded)
    // because content is injected via JavaScript after the page loads
    console.log('[PyWry] Registering pywry:update_theme handler');
    window.pywry.on('pywry:update_theme', function(data) {
        console.log('[PyWry] pywry:update_theme handler called with:', data);
        var theme = data.theme || 'plotly_dark';
        var isDark = theme.includes('dark');
        var mode = isDark ? 'dark' : 'light';
        updateTheme(mode);

        // Also update Plotly with full template if available
        if (window.Plotly && window.__PYWRY_PLOTLY_DIV__) {
            var templateName = theme;
            var template = window.PYWRY_PLOTLY_TEMPLATES && window.PYWRY_PLOTLY_TEMPLATES[templateName];
            if (template) {
                var plotDiv = window.__PYWRY_PLOTLY_DIV__;
                var newLayout = Object.assign({}, plotDiv.layout || {}, { template: template });
                window.Plotly.newPlot(plotDiv, plotDiv.data, newLayout, plotDiv._fullLayout?._config || {});
            }
        }

        // Update AG Grid theme if present
        if (data.theme && data.theme.startsWith('ag-theme-')) {
            var gridDiv = document.querySelector('[class*="ag-theme-"]');
            if (gridDiv) {
                var classList = Array.from(gridDiv.classList);
                classList.forEach(function(cls) {
                    if (cls.startsWith('ag-theme-')) {
                        gridDiv.classList.remove(cls);
                    }
                });
                gridDiv.classList.add(data.theme);
            }
        }
    });

    // Initialize theme on DOMContentLoaded (for initial page load)
    document.addEventListener('DOMContentLoaded', function() {
        var html = document.documentElement;
        var currentTheme = html.classList.contains('dark') ? 'dark' : 'light';
        window.pywry.theme = currentTheme;
    });
})();
"""

# =============================================================================
# Event Bridge - Generic event handling
# =============================================================================

EVENT_BRIDGE_JS = """
(function() {
    'use strict';

    // Listen for all pywry:* events from Python
    if (window.__TAURI__ && window.__TAURI__.event) {
        window.__TAURI__.event.listen('pywry:event', function(event) {
            var eventType = event.payload.event_type;
            var data = event.payload.data;
            window.pywry._trigger(eventType, data);
        });
    }

    console.log('Event bridge initialized');
})();
"""

# =============================================================================
# Toolbar Bridge - Toolbar state management
# =============================================================================

TOOLBAR_BRIDGE_JS = """
(function() {
    'use strict';

    // Collect state from all toolbar components
    function getToolbarState(toolbarId) {
        var state = { toolbars: {}, components: {}, timestamp: Date.now() };

        // Find all toolbars (or specific one)
        var toolbars = toolbarId
            ? [document.getElementById(toolbarId)]
            : document.querySelectorAll('.pywry-toolbar');

        toolbars.forEach(function(toolbar) {
            if (!toolbar) return;
            var tbId = toolbar.id;
            if (!tbId) return;

            state.toolbars[tbId] = {
                position: Array.from(toolbar.classList)
                    .find(function(c) { return c.startsWith('pywry-toolbar-'); })
                    ?.replace('pywry-toolbar-', '') || 'top',
                components: []
            };

            // Collect all input values within this toolbar
            toolbar.querySelectorAll('[id]').forEach(function(el) {
                var id = el.id;
                var value = null;
                var type = null;

                if (el.tagName === 'BUTTON') {
                    type = 'button';
                    value = { disabled: el.disabled };
                } else if (el.tagName === 'SELECT') {
                    type = 'select';
                    value = el.value;
                } else if (el.tagName === 'INPUT') {
                    var inputType = el.type;
                    if (inputType === 'checkbox') {
                        // Part of multiselect - handled by parent
                        return;
                    } else if (inputType === 'range') {
                        type = 'range';
                        value = parseFloat(el.value);
                    } else if (inputType === 'number') {
                        type = 'number';
                        value = parseFloat(el.value) || 0;
                    } else if (inputType === 'date') {
                        type = 'date';
                        value = el.value;
                    } else {
                        type = 'text';
                        value = el.value;
                    }
                } else if (el.classList.contains('pywry-multiselect')) {
                    type = 'multiselect';
                    value = Array.from(el.querySelectorAll('input:checked'))
                        .map(function(i) { return i.value; });
                }

                if (type) {
                    state.components[id] = { type: type, value: value };
                    state.toolbars[tbId].components.push(id);
                }
            });
        });

        return state;
    }

    // Get value of a specific component
    function getComponentValue(componentId) {
        var el = document.getElementById(componentId);
        if (!el) return null;

        if (el.tagName === 'SELECT') {
            return el.value;
        } else if (el.tagName === 'INPUT') {
            var inputType = el.type;
            if (inputType === 'range' || inputType === 'number') {
                return parseFloat(el.value);
            }
            return el.value;
        } else if (el.classList.contains('pywry-multiselect')) {
            return Array.from(el.querySelectorAll('input:checked'))
                .map(function(i) { return i.value; });
        }
        return null;
    }

    // Set value of a specific component
    function setComponentValue(componentId, value) {
        var el = document.getElementById(componentId);
        if (!el) return false;

        if (el.tagName === 'SELECT' || el.tagName === 'INPUT') {
            el.value = value;
            return true;
        } else if (el.classList.contains('pywry-multiselect')) {
            var values = Array.isArray(value) ? value : [value];
            el.querySelectorAll('input[type="checkbox"]').forEach(function(cb) {
                cb.checked = values.includes(cb.value);
            });
            return true;
        }
        return false;
    }

    // Handle toolbar state request from Python
    window.pywry.on('toolbar:request_state', function(data) {
        var toolbarId = data && data.toolbarId;
        var componentId = data && data.componentId;
        var context = data && data.context;

        var response;
        if (componentId) {
            // Single component value
            response = {
                componentId: componentId,
                value: getComponentValue(componentId),
                context: context
            };
        } else {
            // Full toolbar state
            response = getToolbarState(toolbarId);
            response.context = context;
            if (toolbarId) response.toolbarId = toolbarId;
        }

        window.pywry.emit('toolbar:state_response', response);
    });

    // Handle toolbar update from Python
    window.pywry.on('toolbar:set_value', function(data) {
        if (data && data.componentId && data.value !== undefined) {
            setComponentValue(data.componentId, data.value);
        }
    });

    // Handle bulk update
    window.pywry.on('toolbar:set_values', function(data) {
        if (data && data.values) {
            Object.keys(data.values).forEach(function(id) {
                setComponentValue(id, data.values[id]);
            });
        }
    });

    // Expose for manual access
    window.__PYWRY_TOOLBAR__ = {
        getState: getToolbarState,
        getValue: getComponentValue,
        setValue: setComponentValue
    };

    console.log('Toolbar bridge initialized');
})();
"""

# =============================================================================
# Plotly Bridge - Hooks Plotly events to PyWry
# =============================================================================

PLOTLY_BRIDGE_JS = """
(function() {
    'use strict';

    // Wait for Plotly and graph to be ready
    function initPlotlyBridge() {
        var plotDiv = document.querySelector('.plotly-graph-div, [data-plotly]');
        if (!plotDiv || !window.Plotly) {
            setTimeout(initPlotlyBridge, 100);
            return;
        }

        window.__PYWRY_PLOTLY_DIV__ = plotDiv;

        // Click event
        plotDiv.on('plotly_click', function(data) {
            if (!data || !data.points) return;
            var points = data.points.map(function(pt) {
                return {
                    curveNumber: pt.curveNumber,
                    pointIndex: pt.pointIndex,
                    x: pt.x,
                    y: pt.y,
                    data: pt.data ? { name: pt.data.name } : {}
                };
            });
            window.pywry.emit('plotly:click', {
                points: points,
                point_indices: data.points.map(function(pt) { return pt.pointIndex; }),
                curve_number: data.points[0] ? data.points[0].curveNumber : 0
            });
        });

        // Hover event
        plotDiv.on('plotly_hover', function(data) {
            if (!data || !data.points) return;
            window.pywry.emit('plotly:hover', {
                points: data.points.map(function(pt) {
                    return { x: pt.x, y: pt.y, curveNumber: pt.curveNumber };
                })
            });
        });

        // Selection event
        plotDiv.on('plotly_selected', function(data) {
            if (!data) {
                window.pywry.emit('plotly:select', { points: [], range: null });
                return;
            }
            window.pywry.emit('plotly:select', {
                points: (data.points || []).map(function(pt) {
                    return { x: pt.x, y: pt.y, pointIndex: pt.pointIndex };
                }),
                range: data.range || null
            });
        });

        // Relayout event (zoom, pan)
        plotDiv.on('plotly_relayout', function(data) {
            window.pywry.emit('plotly:relayout', { relayout_data: data });
        });

        console.log('Plotly bridge initialized');
    }

    // Listen for plotly data updates from Python
    if (window.__TAURI__ && window.__TAURI__.event) {
        window.__TAURI__.event.listen('pywry:plotly-data', function(event) {
            var data = event.payload;
            if (window.__PYWRY_PLOTLY_DIV__ && window.Plotly) {
                Plotly.react(
                    window.__PYWRY_PLOTLY_DIV__,
                    data.data || [],
                    data.layout || {},
                    data.config || {}
                );
            }
        });
    }

    initPlotlyBridge();
})();
"""

AGGRID_BRIDGE_JS = """
(function() {
    'use strict';

    // Wait for grid to be ready
    function initGridBridge() {
        if (!window.__PYWRY_GRID_API__) {
            setTimeout(initGridBridge, 100);
            return;
        }

        var gridApi = window.__PYWRY_GRID_API__;

        // Selection changed
        gridApi.addEventListener('selectionChanged', function() {
            var selectedRows = gridApi.getSelectedRows();
            var selectedNodes = gridApi.getSelectedNodes();
            window.pywry.emit('grid:select', {
                selected_rows: selectedRows,
                selected_row_ids: selectedNodes.map(function(n) { return n.id || String(n.rowIndex); })
            });
        });

        // Cell value changed
        gridApi.addEventListener('cellValueChanged', function(event) {
            window.pywry.emit('grid:cell-edit', {
                row_id: event.node.id || String(event.rowIndex),
                row_index: event.rowIndex,
                column: event.colDef.field,
                old_value: event.oldValue,
                new_value: event.newValue
            });
        });

        // Row clicked
        gridApi.addEventListener('rowClicked', function(event) {
            window.pywry.emit('grid:row-click', {
                row_data: event.data,
                row_id: event.node.id || String(event.rowIndex),
                row_index: event.rowIndex
            });
        });

        console.log('AG Grid bridge initialized');
    }

    initGridBridge();
})();
"""


CLEANUP_JS = """
(function() {
    'use strict';

    // Listen for cleanup signal before window destruction
    if (window.__TAURI__ && window.__TAURI__.event) {
        window.__TAURI__.event.listen('pywry:cleanup', function() {
            console.log('Cleanup requested, releasing resources...');

            // Clear Plotly
            if (window.Plotly && window.__PYWRY_PLOTLY_DIV__) {
                try { Plotly.purge(window.__PYWRY_PLOTLY_DIV__); } catch(e) {}
                window.__PYWRY_PLOTLY_DIV__ = null;
            }

            // Clear AG Grid
            if (window.__PYWRY_GRID_API__) {
                try { window.__PYWRY_GRID_API__.destroy(); } catch(e) {}
                window.__PYWRY_GRID_API__ = null;
            }

            // Clear event handlers
            if (window.pywry) {
                window.pywry._handlers = {};
            }

            console.log('Cleanup complete');
        });
    }

    console.log('Cleanup handler registered');
})();
"""

HOT_RELOAD_JS = """
(function() {
    'use strict';

    // Store scroll position in sessionStorage for preservation across refreshes
    var SCROLL_KEY = 'pywry_scroll_' + (window.__PYWRY_LABEL__ || 'main');

    /**
     * Save current scroll position to sessionStorage.
     */
    function saveScrollPosition() {
        var scrollData = {
            x: window.scrollX || window.pageXOffset,
            y: window.scrollY || window.pageYOffset,
            timestamp: Date.now()
        };
        try {
            sessionStorage.setItem(SCROLL_KEY, JSON.stringify(scrollData));
        } catch (e) {
            // sessionStorage may not be available
        }
    }

    function restoreScrollPosition() {
        try {
            var data = sessionStorage.getItem(SCROLL_KEY);
            if (data) {
                var scrollData = JSON.parse(data);
                // Only restore if saved within last 5 seconds (hot reload window)
                if (Date.now() - scrollData.timestamp < 5000) {
                    window.scrollTo(scrollData.x, scrollData.y);
                }
                sessionStorage.removeItem(SCROLL_KEY);
            }
        } catch (e) {
            // Ignore errors
        }
    }

    window.pywry.injectCSS = function(css, id) {
        var style = document.getElementById(id);
        if (style) {
            style.textContent = css;
        } else {
            style = document.createElement('style');
            style.id = id;
            style.textContent = css;
            document.head.appendChild(style);
        }
    };

    window.pywry.removeCSS = function(id) {
        var style = document.getElementById(id);
        if (style) {
            style.remove();
        }
    };

    window.pywry.refresh = function() {
        saveScrollPosition();
        window.location.reload();
    };

    if (document.readyState === 'complete') {
        restoreScrollPosition();
    } else {
        window.addEventListener('load', restoreScrollPosition);
    }

    if (window.__TAURI__ && window.__TAURI__.event) {
        window.__TAURI__.event.listen('pywry:inject-css', function(event) {
            var css = event.payload.css;
            var id = event.payload.id;
            window.pywry.injectCSS(css, id);
        });

        window.__TAURI__.event.listen('pywry:remove-css', function(event) {
            window.pywry.removeCSS(event.payload.id);
        });

        window.__TAURI__.event.listen('pywry:refresh', function() {
            window.pywry.refresh();
        });
    }

    console.log('Hot reload bridge initialized');
})();
"""


def build_init_script(
    config: WindowConfig,
    window_label: str,
    enable_hot_reload: bool = False,
) -> str:
    """Build the complete initialization script based on config.

    Parameters
    ----------
    config : WindowConfig
        The window configuration.
    window_label : str
        The label for this window.
    enable_hot_reload : bool, optional
        Whether to include hot reload functionality.

    Returns
    -------
    str
        The combined JavaScript initialization script.
    """
    scripts = [
        f"window.__PYWRY_LABEL__ = '{window_label}';",
        PYWRY_BRIDGE_JS,
        THEME_MANAGER_JS,
        EVENT_BRIDGE_JS,
        TOOLBAR_BRIDGE_JS,
        CLEANUP_JS,
    ]

    # Add hot reload bridge only when enabled
    if enable_hot_reload:
        scripts.append(HOT_RELOAD_JS)

    # Add library-specific bridges
    if config.enable_plotly:
        scripts.append(PLOTLY_BRIDGE_JS)

    if config.enable_aggrid:
        scripts.append(AGGRID_BRIDGE_JS)

    return "\n".join(scripts)
