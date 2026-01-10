/*PyWry Plotly Widget*/

console.log('[PyWry Plotly] Widget module loaded');

function render({ model, el }) {
    console.log('[PyWry Plotly] render() called');

    el.innerHTML = '';

    const container = document.createElement('div');
    container.className = 'pywry-widget pywry-plotly';
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
    container.style.overflow = 'visible';
    el.appendChild(container);

    // Attach model to container for global dispatch lookup
    container._pywryModel = model;

    // Initialize global dispatcher if not present
    if (!window.pywry) {
        window.pywry = {};
    }
    if (!window.pywry.emitButton) {
        window.pywry.emitButton = function(btnEl, type, data) {
            const widget = btnEl.closest('.pywry-widget');
            if (widget && widget._pywryModel) {
                 const m = widget._pywryModel;
                 const evt = JSON.stringify({ type: type, data: data, ts: Date.now() });
                 m.set('_js_event', evt);
                 m.save_changes();
            } else {
                 console.warn('[PyWry] Could not find widget model for element', btnEl);
            }
        };
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
    
    // Attach local pywry to container for debugging if needed
    container._pywryInstance = pywry;

    pywry.on('pywry:update_plotly', (data) => {
        const plotDiv = container.querySelector('.js-plotly-plot');
        if (plotDiv && window.Plotly && data.figure) {
            console.log('[PyWry Plotly] Updating figure via event');
            const fig = data.figure;
            window.Plotly.react(plotDiv, fig.data, fig.layout, data.config || fig.config || {});
        }
    });

    // Handle theme updates from Python
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
            pywry.emit('plotly_click', { points: points });
        });
        chartEl.on('plotly_hover', function(data) {
            const points = data.points.map(p => ({
                curveNumber: p.curveNumber,
                pointNumber: p.pointNumber,
                x: p.x,
                y: p.y
            }));
            pywry.emit('plotly_hover', { points: points });
        });
        chartEl.on('plotly_selected', function(data) {
            if (data) {
                const points = data.points.map(p => ({
                    curveNumber: p.curveNumber,
                    pointNumber: p.pointNumber,
                    x: p.x,
                    y: p.y
                }));
                pywry.emit('plotly_selected', { points: points, range: data.range });
            }
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
                const finalConfig = Object.assign({responsive: true}, config);
                
                console.log('[PyWry Plotly] Rendering chart from figure_json');
                window.Plotly.newPlot(chartEl, figData.data, figData.layout, finalConfig).then(function() {
                    setupPlotlyEvents(chartEl);
                    console.log('[PyWry Plotly] Chart rendered successfully');
                }).catch(function(err) {
                    console.error('[PyWry Plotly] Plotly.newPlot failed:', err);
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
