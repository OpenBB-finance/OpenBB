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
    window.pywry = {
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

    model.off('change:_py_event');
    model.off('change:content');
    model.off('change:theme');    
    model.on('change:_py_event', () => {
        try {
            const event = JSON.parse(model.get('_py_event') || '{}');
            if (event.type) window.pywry._fire(event.type, event.data);
        } catch(e) {}
    });

    function applyTheme() {
        const isDark = model.get('theme') === 'dark';
        container.classList.remove('pywry-theme-dark', 'pywry-theme-light');
        container.classList.add(isDark ? 'pywry-theme-dark' : 'pywry-theme-light');

        const plotDiv = container.querySelector('.js-plotly-plot');
        if (plotDiv && window.Plotly) {
            const template = isDark ? 'plotly_dark' : 'plotly_white';
            window.Plotly.relayout(plotDiv, { template: template });
        }
    }
    
    function renderContent() {
        const content = model.get('content');
        console.log('[PyWry Plotly] renderContent(), content:', content ? content.length + ' chars' : 'null');
        
        if (!content) {
            container.innerHTML = '<div style="padding:20px;color:#888;font-family:monospace;">Waiting for content...</div>';
            return;
        }
        
        container.innerHTML = content;
        applyTheme();
        
        // Execute embedded scripts
        container.querySelectorAll('script').forEach(oldScript => {
            if (oldScript.src) return;
            try {
                const fn = new Function(oldScript.textContent);
                fn();
            } catch(e) {
                console.error('[PyWry Plotly] Script error:', e);
            }
        });
        
        window.pywry._ready = true;
        console.log('[PyWry Plotly] Render complete');
    }
    model.on('change:content', renderContent);
    model.on('change:theme', applyTheme);
    renderContent();
}

export default { render };
