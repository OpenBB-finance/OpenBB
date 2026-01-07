// PyWry main entry point
// Listens for events from Python backend

// Read label from URL query string IMMEDIATELY before anything else
(function() {
  const params = new URLSearchParams(window.location.search);
  const label = params.get('label');
  if (label) {
    window.__PYWRY_LABEL__ = label;
  }
})();

window.pywry = {
  ready: false,
  handlers: {},
  
  setContent: function(html, theme) {
    var htmlEl = document.documentElement;
    htmlEl.classList.remove('dark', 'light');
    if (theme === 'light') {
      htmlEl.classList.add('light');
    } else {
      htmlEl.classList.add('dark');
    }
    document.getElementById('app').innerHTML = html;
    // Notify Python that content has been set
    window.pywry.sendEvent('content:ready', { timestamp: Date.now() });
  },

  // Send result back to Python
  result: function(data) {
    window.pywry.sendEvent('pywry:result', data);
  },
  
  // Register event handler
  on: function(eventType, callback) {
    if (!this.handlers[eventType]) {
      this.handlers[eventType] = [];
    }
    this.handlers[eventType].push(callback);
  },
  
  // Remove event handler
  off: function(eventType, callback) {
    if (!this.handlers[eventType]) return;
    if (callback) {
      this.handlers[eventType] = this.handlers[eventType].filter(h => h !== callback);
    } else {
      delete this.handlers[eventType];
    }
  },
  
  // Dispatch event to handlers
  dispatch: function(eventType, data) {
    const handlers = this.handlers[eventType] || [];
    const wildcardHandlers = this.handlers['*'] || [];
    handlers.forEach(h => h(data));
    wildcardHandlers.forEach(h => h({ type: eventType, data: data }));
  },
  
  // Send event to Python (alias for emit)
  sendEvent: function(eventType, data) {
    if (window.__TAURI__ && window.__TAURI__.pytauri && window.__TAURI__.pytauri.pyInvoke) {
      window.__TAURI__.pytauri.pyInvoke('pywry_event', {
        label: window.__PYWRY_LABEL__ || 'main',
        event_type: eventType,
        data: data || {}
      }).catch(function(e) {
        console.error('[pywry] sendEvent error:', e);
      });
    }
  },
  
  // Emit event to Python (preferred name, same as sendEvent)
  emit: function(eventType, data) {
    this.sendEvent(eventType, data);
  }
};

// Listen for events from Python backend
async function setupEventListeners() {
  if (window.__TAURI__ && window.__TAURI__.event) {
    const { listen } = window.__TAURI__.event;
    
    await listen('pywry:content', (event) => {
      window.pywry.setContent(event.payload.html, event.payload.theme);
      window.pywry.dispatch('content', event.payload);
    });
    
    // Listen for script execution
    await listen('pywry:eval', (event) => {
      try {
        eval(event.payload.script);
      } catch (e) {
        console.error('pywry:eval error:', e);
      }
    });
    
    // Listen for generic events from Python
    await listen('pywry:event', (event) => {
      window.pywry.dispatch(event.payload.type, event.payload.data);
    });
    
    // Listen for window label assignment
    await listen('pywry:init', (event) => {
      window.__PYWRY_LABEL__ = event.payload.label;
      window.pywry.dispatch('init', event.payload);
    });
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
  await setupEventListeners();
  window.pywry.ready = true;
  window.pywry.dispatch('ready', {});
  
  // Notify Python that frontend is ready
  window.pywry.sendEvent('window:ready', { timestamp: Date.now() });
});
