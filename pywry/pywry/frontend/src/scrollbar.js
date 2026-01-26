// Custom scrollbar implementation for macOS WebKit
// Native overlay scrollbars ignore CSS, so we create our own
// This script works in both native windows and widget/iframe contexts

// Expose globally for use by widget ESM
window.PYWRY_SCROLLBARS = (function() {
  'use strict';

  // Selectors for scroll containers we handle
  var scrollSelectors = '.pywry-scroll-container';

  function initCustomScrollbars(root) {
    // Use provided root or find default
    root = root || document.querySelector('.pywry-widget') || document.body;

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

    observer.observe(root, { childList: true, subtree: true });

    // Also setup any existing scroll containers
    root.querySelectorAll(scrollSelectors).forEach(setupCustomScrollbar);
  }

  function setupCustomScrollbar(scrollContainer) {
    // Skip if already set up
    if (scrollContainer.dataset.customScrollbar) return;

    // Skip Plotly containers - they have their own responsive layout
    if (scrollContainer.querySelector('.pywry-plotly') ||
        scrollContainer.querySelector('.js-plotly-plot')) {
      scrollContainer.dataset.customScrollbar = 'skipped';
      return;
    }

    // Skip AG Grid containers - AG Grid has its own scrolling implementation
    if (scrollContainer.querySelector('.pywry-grid') ||
        scrollContainer.querySelector('.ag-root-wrapper') ||
        scrollContainer.closest('.ag-root-wrapper')) {
      scrollContainer.dataset.customScrollbar = 'skipped';
      return;
    }

    scrollContainer.dataset.customScrollbar = 'true';

    // CRITICAL: Hide native scrollbar via inline style - CSS rules may not work in iframe/widget contexts
    // This ensures native scrollbar is hidden regardless of CSS cascade issues
    scrollContainer.style.scrollbarWidth = 'none';  // Firefox
    scrollContainer.style.msOverflowStyle = 'none';  // IE/Edge

    // For WebKit: We need to inject a <style> element since ::-webkit-scrollbar can't be set via JS
    // Generate unique ID for this scroll container
    var scrollId = 'pywry-scroll-' + Math.random().toString(36).substr(2, 9);
    scrollContainer.id = scrollId;

    // Inject WebKit scrollbar hiding style into the CORRECT document context
    // In iframe/widget contexts, document.head may be the parent - use ownerDocument
    var styleId = 'pywry-scrollbar-style-' + scrollId;
    var ownerDoc = scrollContainer.ownerDocument || document;
    var styleTarget = ownerDoc.head || ownerDoc.documentElement || document.head;
    if (!ownerDoc.getElementById(styleId)) {
      var style = ownerDoc.createElement('style');
      style.id = styleId;
      style.textContent = '#' + scrollId + '::-webkit-scrollbar { display: none !important; width: 0 !important; height: 0 !important; }';
      styleTarget.appendChild(style);
    }

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

      // Use a threshold to avoid false positives from sub-pixel rendering
      var hasVertical = scrollHeight > clientHeight + 2;
      var hasHorizontal = scrollWidth > clientWidth + 2;

      // Update wrapper class for corner handling
      wrapper.classList.toggle('has-both-scrollbars', hasVertical && hasHorizontal);

      // Vertical scrollbar
      if (!hasVertical) {
        trackV.style.display = 'none';
        scrollContainer.classList.remove('has-scrollbar-v');
        // Reset thumb to top when not needed
        thumbV.style.top = trackPadding + 'px';
        thumbV.style.height = '30px';
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
        // Protect against division by zero
        var scrollRatioV = maxScrollV > 0 ? (scrollContainer.scrollTop / maxScrollV) : 0;
        // Clamp ratio to valid range
        scrollRatioV = Math.max(0, Math.min(1, scrollRatioV));
        var maxThumbTopV = availableHeightV - thumbHeightV;
        var thumbTopV = trackPadding + (scrollRatioV * maxThumbTopV);

        thumbV.style.height = thumbHeightV + 'px';
        thumbV.style.top = thumbTopV + 'px';
      }

      // Horizontal scrollbar
      if (!hasHorizontal) {
        trackH.style.display = 'none';
        scrollContainer.classList.remove('has-scrollbar-h');
        // Reset thumb to left when not needed
        thumbH.style.left = trackPadding + 'px';
        thumbH.style.width = '30px';
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
        // Protect against division by zero
        var scrollRatioH = maxScrollH > 0 ? (scrollContainer.scrollLeft / maxScrollH) : 0;
        // Clamp ratio to valid range
        scrollRatioH = Math.max(0, Math.min(1, scrollRatioH));
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

    // Use ResizeObserver to track size changes - observe ALL descendants AND toolbars
    if (typeof ResizeObserver !== 'undefined') {
      var resizeObserver = new ResizeObserver(function() {
        updateScrollbars();
      });

      // Observe wrapper and scroll container
      resizeObserver.observe(wrapper);
      resizeObserver.observe(scrollContainer);

      // CRITICAL: Also observe toolbars - when TextArea or other toolbar elements resize,
      // it changes the available space for the scroll container
      var widgetRoot = scrollContainer.closest('.pywry-widget') || scrollContainer.closest('.pywry-container') || scrollContainer.ownerDocument.body;
      var toolbars = widgetRoot.querySelectorAll('.pywry-toolbar');
      toolbars.forEach(function(toolbar) {
        resizeObserver.observe(toolbar);
        // Observe all children of toolbars (TextArea, etc.)
        toolbar.querySelectorAll('*').forEach(function(el) {
          resizeObserver.observe(el);
        });
      });

      // Observe ALL child elements - any child resizing affects scrollHeight
      function observeAllChildren(parent) {
        var children = parent.querySelectorAll('*');
        children.forEach(function(el) {
          resizeObserver.observe(el);
        });
      }
      observeAllChildren(scrollContainer);

      // Watch for new elements and observe them too (including new toolbars)
      var elementObserver = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
          mutation.addedNodes.forEach(function(node) {
            if (node.nodeType === 1) {
              resizeObserver.observe(node);
              // Also observe children of new nodes
              if (node.querySelectorAll) {
                var children = node.querySelectorAll('*');
                children.forEach(function(child) {
                  resizeObserver.observe(child);
                });
              }
              // If new node is a toolbar, observe all its children
              if (node.classList && node.classList.contains('pywry-toolbar')) {
                node.querySelectorAll('*').forEach(function(el) {
                  resizeObserver.observe(el);
                });
              }
            }
          });
        });
      });
      // Observe both the scroll container AND the widget root for toolbar changes
      elementObserver.observe(scrollContainer, { childList: true, subtree: true });
      if (widgetRoot !== scrollContainer) {
        elementObserver.observe(widgetRoot, { childList: true, subtree: true });
      }
    } else {
      // Fallback for older browsers
      window.addEventListener('resize', updateScrollbars);
    }
  }

  // Return public API
  return {
    init: initCustomScrollbars,
    setup: setupCustomScrollbar
  };
})();

// Also auto-initialize for IFrame contexts (not ESM widget)
// ESM widgets will call PYWRY_SCROLLBARS.init(container) explicitly
if (typeof module === 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      window.PYWRY_SCROLLBARS.init();
    });
  } else {
    window.PYWRY_SCROLLBARS.init();
  }
}
