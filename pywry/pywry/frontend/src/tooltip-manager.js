/**
 * PyWry Tooltip Manager
 * Single source of truth for tooltip functionality.
 * Used by both anywidget mode (via toolbar-handlers.js) and iframe/Tauri mode (via scripts.py).
 */
(function() {
    'use strict';

    var tooltip = null;
    var currentTarget = null;
    var hideTimeout = null;

    function createTooltip() {
        if (tooltip) return tooltip;
        tooltip = document.createElement('div');
        tooltip.id = 'pywry-tooltip';
        document.body.appendChild(tooltip);
        return tooltip;
    }

    function showTooltip(target, text) {
        if (!text) return;
        createTooltip();

        tooltip.textContent = text;
        tooltip.classList.remove('visible', 'arrow-top', 'arrow-bottom');

        // Get target position
        var rect = target.getBoundingClientRect();
        var tooltipRect;

        // Temporarily show to measure
        tooltip.style.left = '-9999px';
        tooltip.style.top = '-9999px';
        tooltip.style.visibility = 'hidden';
        tooltip.style.opacity = '0';
        tooltip.classList.add('visible');
        tooltipRect = tooltip.getBoundingClientRect();

        // Calculate position - prefer above, fall back to below
        var gap = 8;
        var arrowHeight = 6;
        var spaceAbove = rect.top;
        var spaceBelow = window.innerHeight - rect.bottom;
        var tooltipHeight = tooltipRect.height + arrowHeight + gap;

        var top, arrowClass;

        if (spaceAbove >= tooltipHeight || spaceAbove > spaceBelow) {
            // Position above
            top = rect.top - tooltipRect.height - arrowHeight - gap;
            arrowClass = 'arrow-bottom';
        } else {
            // Position below
            top = rect.bottom + arrowHeight + gap;
            arrowClass = 'arrow-top';
        }

        // Horizontal centering with edge detection
        var left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
        var rightEdge = left + tooltipRect.width;

        if (left < 8) {
            left = 8;
        } else if (rightEdge > window.innerWidth - 8) {
            left = window.innerWidth - tooltipRect.width - 8;
        }

        tooltip.style.left = left + 'px';
        tooltip.style.top = top + 'px';
        tooltip.style.visibility = '';
        tooltip.style.opacity = '';
        tooltip.classList.add(arrowClass);
        tooltip.classList.add('visible');

        currentTarget = target;
    }

    function hideTooltip() {
        if (tooltip) {
            tooltip.classList.remove('visible');
        }
        currentTarget = null;
    }

    function handleMouseOver(e) {
        var target = e.target.closest('[data-tooltip]');
        if (!target) return;
        if (target === currentTarget) return;

        clearTimeout(hideTimeout);
        var text = target.getAttribute('data-tooltip');
        if (text) {
            showTooltip(target, text);
        }
    }

    function handleMouseOut(e) {
        var target = e.target.closest('[data-tooltip]');
        if (!target) return;

        // Check if we're moving to a child element
        var relatedTarget = e.relatedTarget;
        if (relatedTarget && target.contains(relatedTarget)) return;

        currentTarget = null;
        hideTimeout = setTimeout(hideTooltip, 100);
    }

    // Use mouseover/mouseout which bubble (unlike mouseenter/mouseleave)
    document.addEventListener('mouseover', handleMouseOver, false);
    document.addEventListener('mouseout', handleMouseOut, false);

    // Also hide on scroll
    document.addEventListener('scroll', hideTooltip, true);

    console.log('PyWry tooltip manager initialized');
})();
