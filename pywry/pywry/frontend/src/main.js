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

  // Initialize custom scrollbars for macOS WebKit - ONLY in native windows
  if (document.documentElement.classList.contains('pywry-native')) {
    initCustomScrollbars();
  }

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

// Custom scrollbar implementation for macOS WebKit
// Native overlay scrollbars ignore CSS, so we create our own
function initCustomScrollbars() {
  // Selectors for scroll containers we handle
  var scrollSelectors = '.pywry-scroll-container';

  // Use MutationObserver to catch dynamically added scroll containers
  var observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      mutation.addedNodes.forEach(function(node) {
        if (node.nodeType === 1) {
          // Check if node matches any scroll selector
          if (node.matches && node.matches(scrollSelectors)) {
            setupCustomScrollbar(node);
          }
          // Check children for scroll containers
          var containers = node.querySelectorAll ? node.querySelectorAll(scrollSelectors) : [];
          containers.forEach(setupCustomScrollbar);
        }
      });
    });
  });

  observer.observe(document.body, { childList: true, subtree: true });

  // Also setup any existing scroll containers
  document.querySelectorAll(scrollSelectors).forEach(setupCustomScrollbar);
}

function setupCustomScrollbar(scrollContainer) {
  // Skip if already set up
  if (scrollContainer.dataset.customScrollbar) return;

  // Skip Plotly containers only - they have their own responsive layout
  if (scrollContainer.querySelector('.pywry-plotly') ||
      scrollContainer.querySelector('.js-plotly-plot')) {
    scrollContainer.dataset.customScrollbar = 'skipped';
    return;
  }

  scrollContainer.dataset.customScrollbar = 'true';

  // Standard pywry-scroll-container handling
  var wrapper;
  var parent = scrollContainer.parentElement;

  if (parent && parent.classList.contains('pywry-scroll-wrapper')) {
    wrapper = parent;
  } else {
    wrapper = document.createElement('div');
    wrapper.className = 'pywry-scroll-wrapper';
    scrollContainer.parentNode.insertBefore(wrapper, scrollContainer);
    wrapper.appendChild(scrollContainer);
  }

  // Create vertical scrollbar track and thumb
  var trackV = document.createElement('div');
  trackV.className = 'pywry-scrollbar-track-v';
  wrapper.appendChild(trackV);

  var thumbV = document.createElement('div');
  thumbV.className = 'pywry-scrollbar-thumb-v';
  trackV.appendChild(thumbV);

  // Create horizontal scrollbar track and thumb
  var trackH = document.createElement('div');
  trackH.className = 'pywry-scrollbar-track-h';
  wrapper.appendChild(trackH);

  var thumbH = document.createElement('div');
  thumbH.className = 'pywry-scrollbar-thumb-h';
  trackH.appendChild(thumbH);

  var isDraggingV = false;
  var isDraggingH = false;
  var startY = 0;
  var startX = 0;
  var startScrollTop = 0;
  var startScrollLeft = 0;
  var scrollTimeout = null;
  var trackPadding = 6; // Padding inside the track for the thumb

  function updateScrollbars() {
    var scrollHeight = scrollContainer.scrollHeight;
    var clientHeight = scrollContainer.clientHeight;
    var scrollWidth = scrollContainer.scrollWidth;
    var clientWidth = scrollContainer.clientWidth;

    var hasVertical = scrollHeight > clientHeight;
    var hasHorizontal = scrollWidth > clientWidth;

    // Update wrapper class for corner handling
    wrapper.classList.toggle('has-both-scrollbars', hasVertical && hasHorizontal);

    // Vertical scrollbar
    if (!hasVertical) {
      trackV.style.display = 'none';
      scrollContainer.classList.remove('has-scrollbar-v');
    } else {
      trackV.style.display = 'block';
      scrollContainer.classList.add('has-scrollbar-v');

      // Calculate available track height - use wrapper dimensions for positioning
      var wrapperHeight = wrapper.clientHeight;
      var trackVBottom = (hasHorizontal ? 22 : 4); // Account for horizontal scrollbar
      var trackVHeight = wrapperHeight - 4 - trackVBottom;
      var availableHeightV = trackVHeight - (trackPadding * 2);

      var thumbHeightV = Math.max(30, (clientHeight / scrollHeight) * availableHeightV);
      var maxScrollV = scrollHeight - clientHeight;
      var scrollRatioV = scrollContainer.scrollTop / maxScrollV;
      var maxThumbTopV = availableHeightV - thumbHeightV;
      var thumbTopV = trackPadding + (scrollRatioV * maxThumbTopV);

      thumbV.style.height = thumbHeightV + 'px';
      thumbV.style.top = thumbTopV + 'px';
    }

    // Horizontal scrollbar
    if (!hasHorizontal) {
      trackH.style.display = 'none';
      scrollContainer.classList.remove('has-scrollbar-h');
    } else {
      trackH.style.display = 'block';
      scrollContainer.classList.add('has-scrollbar-h');

      // Calculate available track width - use wrapper dimensions for positioning
      var wrapperWidth = wrapper.clientWidth;
      var trackHRight = (hasVertical ? 22 : 4); // Account for vertical scrollbar
      var trackHWidth = wrapperWidth - 4 - trackHRight;
      var availableWidthH = trackHWidth - (trackPadding * 2);

      var thumbWidthH = Math.max(30, (clientWidth / scrollWidth) * availableWidthH);
      var maxScrollH = scrollWidth - clientWidth;
      var scrollRatioH = scrollContainer.scrollLeft / maxScrollH;
      var maxThumbLeftH = availableWidthH - thumbWidthH;
      var thumbLeftH = trackPadding + (scrollRatioH * maxThumbLeftH);

      thumbH.style.width = thumbWidthH + 'px';
      thumbH.style.left = thumbLeftH + 'px';
    }
  }

  // Update on scroll
  scrollContainer.addEventListener('scroll', function() {
    updateScrollbars();

    // Show scrollbar while scrolling
    wrapper.classList.add('is-scrolling');
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(function() {
      wrapper.classList.remove('is-scrolling');
    }, 1000);
  });

  // Vertical drag handling
  thumbV.addEventListener('mousedown', function(e) {
    isDraggingV = true;
    startY = e.clientY;
    startScrollTop = scrollContainer.scrollTop;
    thumbV.classList.add('is-dragging');
    document.body.style.userSelect = 'none';
    e.preventDefault();
  });

  // Horizontal drag handling
  thumbH.addEventListener('mousedown', function(e) {
    isDraggingH = true;
    startX = e.clientX;
    startScrollLeft = scrollContainer.scrollLeft;
    thumbH.classList.add('is-dragging');
    document.body.style.userSelect = 'none';
    e.preventDefault();
  });

  document.addEventListener('mousemove', function(e) {
    if (isDraggingV) {
      var deltaY = e.clientY - startY;
      var scrollHeight = scrollContainer.scrollHeight;
      var clientHeight = scrollContainer.clientHeight;
      var thumbHeightV = Math.max(30, (clientHeight / scrollHeight) * clientHeight);
      var maxThumbTopV = clientHeight - thumbHeightV;
      var maxScrollV = scrollHeight - clientHeight;

      var scrollDeltaV = (deltaY / maxThumbTopV) * maxScrollV;
      scrollContainer.scrollTop = startScrollTop + scrollDeltaV;
    }

    if (isDraggingH) {
      var deltaX = e.clientX - startX;
      var scrollWidth = scrollContainer.scrollWidth;
      var clientWidth = scrollContainer.clientWidth;
      var thumbWidthH = Math.max(30, (clientWidth / scrollWidth) * clientWidth);
      var maxThumbLeftH = clientWidth - thumbWidthH;
      var maxScrollH = scrollWidth - clientWidth;

      var scrollDeltaH = (deltaX / maxThumbLeftH) * maxScrollH;
      scrollContainer.scrollLeft = startScrollLeft + scrollDeltaH;
    }
  });

  document.addEventListener('mouseup', function() {
    if (isDraggingV) {
      isDraggingV = false;
      thumbV.classList.remove('is-dragging');
      document.body.style.userSelect = '';
    }
    if (isDraggingH) {
      isDraggingH = false;
      thumbH.classList.remove('is-dragging');
      document.body.style.userSelect = '';
    }
  });

  // Click on vertical track to jump
  trackV.addEventListener('click', function(e) {
    if (e.target === thumbV) return;

    var trackRect = trackV.getBoundingClientRect();
    var clickY = e.clientY - trackRect.top;
    var scrollHeight = scrollContainer.scrollHeight;
    var clientHeight = scrollContainer.clientHeight;
    var maxScrollV = scrollHeight - clientHeight;

    scrollContainer.scrollTop = (clickY / trackRect.height) * maxScrollV;
  });

  // Click on horizontal track to jump
  trackH.addEventListener('click', function(e) {
    if (e.target === thumbH) return;

    var trackRect = trackH.getBoundingClientRect();
    var clickX = e.clientX - trackRect.left;
    var scrollWidth = scrollContainer.scrollWidth;
    var clientWidth = scrollContainer.clientWidth;
    var maxScrollH = scrollWidth - clientWidth;

    scrollContainer.scrollLeft = (clickX / trackRect.width) * maxScrollH;
  });

  // Initial update
  updateScrollbars();

  // Update on resize
  window.addEventListener('resize', updateScrollbars);

  // Re-observe for content changes
  var contentObserver = new MutationObserver(updateScrollbars);
  contentObserver.observe(scrollContainer, { childList: true, subtree: true, characterData: true });
}