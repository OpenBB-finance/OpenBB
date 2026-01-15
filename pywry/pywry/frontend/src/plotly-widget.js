/*PyWry Plotly Widget*/

console.log('[PyWry Plotly] Widget module loaded');

function render({ model, el }) {
    console.log('[PyWry Plotly] render() called');

    el.innerHTML = '';

    const container = document.createElement('div');
    container.className = 'pywry-widget';
    container.classList.add(model.get('theme') === 'dark' ? 'pywry-theme-dark' : 'pywry-theme-light');
    const modelHeight = model.get('height');
    const modelWidth = model.get('width');
    if (modelHeight) {
        container.style.setProperty('--pywry-widget-height', modelHeight);
    }
    if (modelWidth) {
        container.style.setProperty('--pywry-widget-width', modelWidth);
    }
    container.style.overflow = 'visible';
    el.appendChild(container);

    // Attach model to container for global dispatch lookup
    container._pywryModel = model;

    // Initialize global dispatcher if not present
    if (!window.pywry) {
        window.pywry = {};
    }

    // Local bridge - specialized for this widget instance
    const pywry = {
        _ready: false,
        _handlers: {},
        _pending: [],
        emit: function(type, data) {
            model.set('_js_event', JSON.stringify({ type, data, ts: Date.now() }));
            model.save_changes();
        },
        on: function(type, cb) {
            if (!this._handlers[type]) this._handlers[type] = [];
            this._handlers[type].push(cb);
            const pending = this._pending.filter(p => p.type === type);
            this._pending = this._pending.filter(p => p.type !== type);
            pending.forEach(p => cb(p.data));
        },
        _fire: function(type, data) {
            const handlers = this._handlers[type] || [];
            if (handlers.length === 0) {
                this._pending.push({ type, data });
            } else {
                handlers.forEach(h => h(data));
            }
        }
    };

    container._pywryInstance = pywry;
    window.pywry = pywry;

    // =========================================================================
    // TOOLBAR HANDLERS - LOADED FROM CENTRALIZED SOURCE
    // See: frontend/src/toolbar-handlers.js
    // =========================================================================
    __TOOLBAR_HANDLERS__
    // Helper function to trigger CSV download from data sent by Python
    function downloadCsv(csvContent, filename) {
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename || 'data.csv';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        console.log('[PyWry Export] Downloaded:', filename);
    }
    
    // Listen for CSV data from Python
    pywry.on('pywry:download_csv', (data) => {
        console.log('[PyWry Export] Received CSV from Python, length:', data.csv?.length);
        downloadCsv(data.csv, data.filename);
    });
    
    // Listen for toolbar:set_value to update a single component's value/options
    pywry.on('toolbar:set_value', (data) => {
        console.log('[PyWry] toolbar:set_value:', data.componentId, data.value);
        const componentId = data.componentId;
        
        // Find component by ID
        const component = container.querySelector(`#${componentId}`);
        if (!component) {
            console.warn('[PyWry] Component not found:', componentId);
            return;
        }
        
        // Handle dropdown - can update options OR selected value
        if (component.classList.contains('pywry-dropdown')) {
            const menu = component.querySelector('.pywry-dropdown-menu');
            const textEl = component.querySelector('.pywry-dropdown-text');
            
            // If options array provided, rebuild the dropdown options
            if (data.options && Array.isArray(data.options)) {
                menu.innerHTML = '';
                const selected = data.value || data.selected;
                
                data.options.forEach(opt => {
                    const optEl = document.createElement('div');
                    optEl.className = 'pywry-dropdown-option';
                    if (opt.value === selected) {
                        optEl.classList.add('pywry-selected');
                        textEl.textContent = opt.label;
                    }
                    optEl.setAttribute('data-value', opt.value);
                    optEl.textContent = opt.label;
                    
                    // Add click handler
                    optEl.addEventListener('click', function(e) {
                        e.stopPropagation();
                        menu.querySelectorAll('.pywry-dropdown-option').forEach(o => o.classList.remove('pywry-selected'));
                        optEl.classList.add('pywry-selected');
                        textEl.textContent = opt.label;
                        component.classList.remove('pywry-open');
                        
                        const eventName = component.getAttribute('data-event');
                        if (eventName) {
                            pywry.emit(eventName, { value: opt.value, componentId: componentId });
                        }
                    });
                    
                    menu.appendChild(optEl);
                });
            } else if (data.value !== undefined) {
                // Just update selected value (find matching option)
                const options = menu.querySelectorAll('.pywry-dropdown-option');
                options.forEach(opt => {
                    opt.classList.remove('pywry-selected');
                    if (opt.getAttribute('data-value') === data.value) {
                        opt.classList.add('pywry-selected');
                        textEl.textContent = opt.textContent;
                    }
                });
            }
        }
    });

    // Helper function to process config - converts icon names to objects and event props to click handlers
    function processPlotlyConfig(config) {
        if (!config) return config;
        
        if (config.modeBarButtonsToAdd && Array.isArray(config.modeBarButtonsToAdd)) {
            console.log('[PyWry Plotly] Processing', config.modeBarButtonsToAdd.length, 'custom buttons');
            config.modeBarButtonsToAdd = config.modeBarButtonsToAdd.map(function(btn, idx) {
                console.log('[PyWry Plotly] Button', idx, ':', btn.name, 'icon:', btn.icon, 'event:', btn.event);
                
                // Handle icon - could be string (Plotly icon name) or object (custom SVG)
                if (typeof btn.icon === 'string') {
                    // String icon name - look up in Plotly.Icons
                    var iconName = btn.icon;
                    if (window.Plotly && window.Plotly.Icons && window.Plotly.Icons[iconName]) {
                        btn.icon = window.Plotly.Icons[iconName];
                        console.log('[PyWry Plotly] Icon', iconName, 'resolved to Plotly.Icons');
                    } else {
                        // Fallback: use question mark icon if the named icon doesn't exist
                        console.warn('[PyWry Plotly] Unknown icon:', iconName, '- using fallback');
                        if (window.Plotly && window.Plotly.Icons && window.Plotly.Icons.question) {
                            btn.icon = window.Plotly.Icons.question;
                        } else {
                            btn.icon = {
                                width: 857.1,
                                height: 1000,
                                path: 'm500 82v107q0 8-5 13t-13 5h-107q-8 0-13-5t-5-13v-107q0-8 5-13t13-5h107q8 0 13 5t5 13z m143 375q0 49-31 91t-77 65-95 23q-136 0-207-119-9-14 4-24l74-55q4-4 10-4 9 0 14 7 30 38 48 51 19 14 48 14 27 0 48-15t21-33q0-21-11-34t-38-25q-35-16-65-48t-29-70v-20q0-8 5-13t13-5h107q8 0 13 5t5 13q0 10 12 27t30 28q18 10 28 16t25 19 25 27 16 34 7 45z m214-107q0-117-57-215t-156-156-215-58-216 58-155 156-58 215 58 215 155 156 216 58 215-58 156-156 57-215z',
                                transform: 'matrix(1 0 0 -1 0 850)'
                            };
                        }
                    }
                } else if (btn.icon && typeof btn.icon === 'object') {
                    // Object icon - custom SVG definition from Python SvgIcon
                    // Ensure it has required properties for Plotly
                    if (!btn.icon.width) btn.icon.width = 1000;
                    if (!btn.icon.height) btn.icon.height = 1000;
                    console.log('[PyWry Plotly] Using custom SVG icon for', btn.name);
                }
                
                // Convert 'event' property to 'click' function
                if (btn.event) {
                    var eventName = btn.event;
                    var eventData = btn.data || {};
                    btn.click = function(gd) {
                        console.log('[PyWry Plotly] Button clicked, emitting:', eventName);
                        // Just emit to Python - Python will send back CSV data
                        pywry.emit(eventName, eventData);
                    };
                    delete btn.event;
                    delete btn.data;
                    console.log('[PyWry Plotly] Button', btn.name, 'click handler set for event:', eventName);
                }
                
                return btn;
            });
        }
        
        return config;
    }

    pywry.on('plotly:update_figure', (data) => {
        const plotDiv = container.querySelector('.js-plotly-plot');
        if (plotDiv && window.Plotly) {
            console.log('[PyWry Plotly] Updating figure via event, data keys:', Object.keys(data));
            // Python sends {data: [...], layout: {...}} directly, not nested in figure
            const figData = data.figure ? data.figure.data : data.data;
            const figLayout = data.figure ? data.figure.layout : data.layout;
            // Process config to convert icon names and event properties, always hide logo
            const config = Object.assign({displaylogo: false}, processPlotlyConfig(data.config || {}));
            if (figData) {
                window.Plotly.react(plotDiv, figData, figLayout || {}, config);
            }
        }
    });

    pywry.on('plotly:update_layout', (data) => {
        const plotDiv = container.querySelector('.js-plotly-plot');
        if (plotDiv && window.Plotly && data.layout) {
            window.Plotly.relayout(plotDiv, data.layout);
        }
    });

    pywry.on('plotly:update_traces', (data) => {
        const plotDiv = container.querySelector('.js-plotly-plot');
        if (plotDiv && window.Plotly && data.update) {
            window.Plotly.restyle(plotDiv, data.update, data.indices);
        }
    });

    pywry.on('plotly:reset_zoom', () => {
        const plotDiv = container.querySelector('.js-plotly-plot');
        if (plotDiv && window.Plotly) {
            window.Plotly.relayout(plotDiv, {
                'xaxis.autorange': true,
                'yaxis.autorange': true
            });
        }
    });

    pywry.on('plotly:request_state', () => {
        const plotDiv = container.querySelector('.js-plotly-plot');
        if (plotDiv && window.Plotly) {
            pywry.emit('plotly:state_response', {
                layout: plotDiv.layout,
                data: plotDiv.data,
                chartId: model.get('chart_id')
            });
        }
    });

    // Also allow export to be triggered from Python
    pywry.on('plotly:export_data', () => {
        const plotDiv = container.querySelector('.js-plotly-plot');
        if (plotDiv) doExportData(plotDiv);
    });

    pywry.on('pywry:update_theme', (data) => {
        if (data && data.theme) {
            const isDark = data.theme.includes('dark');
            const newTheme = isDark ? 'dark' : 'light';
            console.log('[PyWry Plotly] Theme update received:', data.theme, '-> model.theme:', newTheme);
            model.set('theme', newTheme);
            model.save_changes();
            applyTheme();
        }
    });

    model.off('change:_py_event');
    model.off('change:content');
    model.off('change:figure_json');
    model.off('change:theme');
    
    model.on('change:_py_event', () => {
        try {
            const event = JSON.parse(model.get('_py_event') || '{}');
            if (event.type) pywry._fire(event.type, event.data);
        } catch(e) {}
    });

    function applyTheme() {
        const isDark = model.get('theme') === 'dark';
        container.classList.remove('pywry-theme-dark', 'pywry-theme-light');
        container.classList.add(isDark ? 'pywry-theme-dark' : 'pywry-theme-light');

        const plotDiv = container.querySelector('.js-plotly-plot');
        if (plotDiv && window.Plotly && plotDiv.data) {
            const templateName = isDark ? 'plotly_dark' : 'plotly_white';
            const template = window.PYWRY_PLOTLY_TEMPLATES?.[templateName];
            if (template) {
                const newLayout = Object.assign({}, plotDiv.layout || {}, { template: template });
                window.Plotly.newPlot(plotDiv, plotDiv.data, newLayout, plotDiv._fullLayout?._config || {});
            }
        }
    }

    function setupPlotlyEvents(chartEl) {
        // Get chartId from model for event payloads
        const chartId = model.get('chart_id') || 'default';
        
        chartEl.on('plotly_click', function(data) {
            const points = data.points.map(p => ({
                curveNumber: p.curveNumber,
                pointNumber: p.pointNumber,
                pointIndex: p.pointIndex,
                x: p.x,
                y: p.y,
                text: p.text,
                customdata: p.customdata
            }));
            // Emit with colon format for consistency with native windows
            pywry.emit('plotly:click', { chartId: chartId, widget_type: 'chart', points: points });
        });
        chartEl.on('plotly_hover', function(data) {
            const points = data.points.map(p => ({
                curveNumber: p.curveNumber,
                pointNumber: p.pointNumber,
                x: p.x,
                y: p.y
            }));
            pywry.emit('plotly:hover', { chartId: chartId, widget_type: 'chart', points: points });
        });
        chartEl.on('plotly_selected', function(data) {
            if (data) {
                const points = data.points.map(p => ({
                    curveNumber: p.curveNumber,
                    pointNumber: p.pointNumber,
                    x: p.x,
                    y: p.y
                }));
                pywry.emit('plotly:select', { chartId: chartId, widget_type: 'chart', points: points, range: data.range });
            }
        });
        chartEl.on('plotly_relayout', function(data) {
            pywry.emit('plotly:relayout', { chartId: chartId, widget_type: 'chart', relayout_data: data });
        });
    }
    
    function renderContent() {
        const content = model.get('content');
        const figureJson = model.get('figure_json');
        
        console.log('[PyWry Plotly] renderContent(), content:', content ? content.length + ' chars' : 'null',
                    ', figure_json:', figureJson ? figureJson.length + ' chars' : 'null');
        
        if (!content) {
            container.innerHTML = '<div style="padding:20px;color:#888;font-family:monospace;">Waiting for content...</div>';
            return;
        }
        
        // Set content HTML (toolbar + chart container)
        container.innerHTML = content;
        
        // Initialize toolbar handlers using centralized function
        // This handles all component types: Button, Select, MultiSelect, Toggle, Checkbox, etc.
        setTimeout(() => initToolbarHandlers(container, pywry), 10);
        
        applyTheme();
        
        // Find chart element within our container (NOT document.getElementById!)
        const chartEl = container.querySelector('#chart');
        
        if (!chartEl) {
            console.error('[PyWry Plotly] No #chart element found in content');
            return;
        }
        
        if (!window.Plotly) {
            console.error('[PyWry Plotly] Plotly library not available');
            chartEl.innerHTML = '<div style="background:#ff4444;color:white;padding:20px;">Plotly not loaded</div>';
            return;
        }
        
        // Use figure_json from model if available
        if (figureJson) {
            try {
                const figData = JSON.parse(figureJson);
                const config = figData.config || {};
                
                console.log('[PyWry Plotly] Config from figure_json:', JSON.stringify(config, null, 2));
                
                // Process modebar buttons using shared helper
                processPlotlyConfig(config);
                
                if (config.modeBarButtonsToRemove) {
                    console.log('[PyWry Plotly] Buttons to remove:', config.modeBarButtonsToRemove);
                }
                
                const finalConfig = Object.assign({responsive: true, displaylogo: false}, config);
                
                console.log('[PyWry Plotly] Final config for Plotly.newPlot:', Object.keys(finalConfig));
                console.log('[PyWry Plotly] Rendering chart from figure_json');
                window.Plotly.newPlot(chartEl, figData.data, figData.layout, finalConfig).then(function() {
                    setupPlotlyEvents(chartEl);
                    console.log('[PyWry Plotly] Chart rendered successfully');
                }).catch(function(err) {
                    console.error('[PyWry Plotly] Plotly.newPlot failed:', err);
                    chartEl.innerHTML = '<div style="background:#ff4444;color:white;padding:20px;">Plotly error: ' + err.message + '</div>';
                });
            } catch(e) {
                console.error('[PyWry Plotly] Failed to parse figure_json:', e);
            }
        } else {
            console.warn('[PyWry Plotly] No figure_json provided, chart will be empty');
        }
        
        pywry._ready = true;
    }
    
    model.on('change:content', renderContent);
    model.on('change:figure_json', renderContent);
    model.on('change:theme', applyTheme);
    renderContent();
}

export default { render };
