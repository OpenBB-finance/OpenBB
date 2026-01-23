// PyWry main entry point
// Listens for events from Python backend

(function() {
  const params = new URLSearchParams(window.location.search);
  const label = params.get('label');
  if (label) {
    window.__PYWRY_LABEL__ = label;
  }
})();

window.pywry = {
  ready: false,
  _handlers: {},

  setContent: function(html, theme) {
    var htmlEl = document.documentElement;
    // Remove all theme classes
    htmlEl.classList.remove('dark', 'light', 'pywry-theme-dark', 'pywry-theme-light');
    if (theme === 'light') {
      htmlEl.classList.add('light', 'pywry-theme-light');
    } else {
      htmlEl.classList.add('dark', 'pywry-theme-dark');
    }
    document.getElementById('app').innerHTML = html;
    window.pywry.sendEvent('content:ready', { timestamp: Date.now() });
  },

  result: function(data) {
    window.pywry.sendEvent('pywry:result', data);
  },

  on: function(eventType, callback) {
    if (!this._handlers[eventType]) {
      this._handlers[eventType] = [];
    }
    this._handlers[eventType].push(callback);
  },

  off: function(eventType, callback) {
    if (!this._handlers[eventType]) return;
    if (callback) {
      this._handlers[eventType] = this._handlers[eventType].filter(h => h !== callback);
    } else {
      delete this._handlers[eventType];
    }
  },

  dispatch: function(eventType, data) {
    const handlers = this._handlers[eventType] || [];
    const wildcardHandlers = this._handlers['*'] || [];
    handlers.forEach(h => h(data));
    wildcardHandlers.forEach(h => h({ type: eventType, data: data }));
  },

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

  emit: function(eventType, data) {
    this.sendEvent(eventType, data);
  }
};

async function setupEventListeners() {
  if (window.__TAURI__ && window.__TAURI__.event) {
    const { listen } = window.__TAURI__.event;

    await listen('pywry:content', (event) => {
      window.pywry.setContent(event.payload.html, event.payload.theme);
      window.pywry.dispatch('content', event.payload);
    });

    await listen('pywry:eval', (event) => {
      try {
        eval(event.payload.script);
      } catch (e) {
        console.error('pywry:eval error:', e);
      }
    });

    await listen('pywry:event', (event) => {
      window.pywry.dispatch(event.payload.type, event.payload.data);
    });

    await listen('pywry:init', (event) => {
      window.__PYWRY_LABEL__ = event.payload.label;
      window.pywry.dispatch('init', event.payload);
    });
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  await setupEventListeners();

  // Register built-in pywry:* handlers for Python→JS utility events
  registerBuiltinHandlers();

  window.pywry.ready = true;
  window.pywry.dispatch('ready', {});

  // Request content from Python - handles initial load and page reload
  window.pywry.sendEvent('pywry:content-request', {
    widget_type: 'window',
    window_label: window.__PYWRY_LABEL__ || 'main',
    reason: 'page_load',
    timestamp: Date.now()
  });
});

// Built-in pywry:* utility event handlers
function registerBuiltinHandlers() {
  // pywry:set-content - Update element innerHTML or textContent
  window.pywry.on('pywry:set-content', function(data) {
    var el = data.id ? document.getElementById(data.id) :
             data.selector ? document.querySelector(data.selector) : null;
    if (!el) {
      console.warn('[pywry] pywry:set-content - no element found for', data.id || data.selector);
      return;
    }
    if (data.html !== undefined) {
      el.innerHTML = data.html;
    } else if (data.text !== undefined) {
      el.textContent = data.text;
    }
  });

  // pywry:set-style - Update inline styles on element(s)
  window.pywry.on('pywry:set-style', function(data) {
    var elements = [];
    if (data.id) {
      var el = document.getElementById(data.id);
      if (el) elements.push(el);
    } else if (data.selector) {
      elements = Array.from(document.querySelectorAll(data.selector));
    }
    if (!elements.length) {
      console.warn('[pywry] pywry:set-style - no elements found for', data.id || data.selector);
      return;
    }
    var styles = data.styles || {};
    elements.forEach(function(el) {
      Object.keys(styles).forEach(function(prop) {
        el.style[prop] = styles[prop];
      });
    });
  });

  // pywry:inject-css - Inject CSS dynamically
  window.pywry.on('pywry:inject-css', function(data) {
    if (!data.css) return;
    var id = data.id || 'pywry-dynamic-css-' + Date.now();
    var existing = document.getElementById(id);
    if (existing) {
      existing.textContent = data.css;
    } else {
      var style = document.createElement('style');
      style.id = id;
      style.textContent = data.css;
      document.head.appendChild(style);
    }
  });

  // pywry:download - Trigger file download (browser/iframe mode)
  window.pywry.on('pywry:download', function(data) {
    if (!data.content || !data.filename) {
      console.warn('[pywry] pywry:download - missing content or filename');
      return;
    }
    var mimeType = data.mimeType || 'text/plain';
    var blob = new Blob([data.content], { type: mimeType });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = data.filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });

  // pywry:navigate - Navigate to URL
  window.pywry.on('pywry:navigate', function(data) {
    if (data.url) {
      window.location.href = data.url;
    }
  });

  // pywry:update-html - Replace entire widget content
  window.pywry.on('pywry:update-html', function(data) {
    if (data.html) {
      var app = document.getElementById('app');
      if (app) {
        app.innerHTML = data.html;
      } else {
        document.body.innerHTML = data.html;
      }
    }
  });

  // pywry:update-theme - Theme switching (handled in plotly-defaults.js for Plotly)
  // This is a base implementation for non-Plotly content
  window.pywry.on('pywry:update-theme', function(data) {
    if (!data.theme) return;
    var isDark = data.theme.includes('dark');
    var htmlEl = document.documentElement;
    // Update all theme classes consistently
    htmlEl.classList.remove('dark', 'light', 'pywry-theme-dark', 'pywry-theme-light');
    htmlEl.classList.add(isDark ? 'dark' : 'light');
    htmlEl.classList.add(isDark ? 'pywry-theme-dark' : 'pywry-theme-light');

    // Also update widget containers
    var containers = document.querySelectorAll('.pywry-widget, .pywry-container');
    containers.forEach(function(container) {
      container.classList.remove('pywry-theme-dark', 'pywry-theme-light');
      container.classList.add(isDark ? 'pywry-theme-dark' : 'pywry-theme-light');
    });
  });

  // pywry:refresh - Request fresh content from Python
  // Emits a content-request to Python to re-send the stored content
  window.pywry.on('pywry:refresh', function(data) {
    // Request Python to re-send content for this window
    window.pywry.sendEvent('pywry:content-request', {
      widget_type: 'window',
      window_label: window.__PYWRY_LABEL__ || 'main',
      reason: 'user_refresh',
      timestamp: Date.now()
    });
  });

  // pywry:remove-css - Remove a CSS style element by ID
  window.pywry.on('pywry:remove-css', function(data) {
    if (!data.id) return;
    var existing = document.getElementById(data.id);
    if (existing) {
      existing.remove();
    }
  });
}
