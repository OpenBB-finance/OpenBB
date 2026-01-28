/**
 * PyWry Toolbar Handlers
 */

var __pywryTooltipContainers = new WeakMap();

function initTooltipManager(container) {
    if (__pywryTooltipContainers.has(container)) return;
    __pywryTooltipContainers.set(container, true);

    var tooltip = null;
    var currentTarget = null;
    var hideTimeout = null;
    var showTimeout = null;
    var tooltipRoot = container;
    // Handle document vs Element - document doesn't have .closest()
    var widgetEl;
    if (container === document || container.nodeType === 9) {
        // container is document - find widget element or use body
        widgetEl = document.querySelector('.pywry-widget') || document.querySelector('.pywry-container') || document.body;
    } else if (typeof container.closest === 'function') {
        widgetEl = container.closest('.pywry-widget') || container.closest('.pywry-container') || container;
    } else {
        widgetEl = container;
    }
    tooltipRoot = widgetEl;

    function createTooltip() {
        if (tooltip) return tooltip;
        tooltip = document.createElement('div');
        tooltip.id = 'pywry-tooltip-' + Math.random().toString(36).substr(2, 9);
        tooltip.className = 'pywry-tooltip';
        tooltipRoot.appendChild(tooltip);
        return tooltip;
    }

    function showTooltip(target, text) {
        if (!text) return;
        createTooltip();

        tooltip.textContent = text;
        tooltip.classList.remove('visible', 'arrow-top', 'arrow-bottom');

        var rect = target.getBoundingClientRect();
        var containerRect = tooltipRoot.getBoundingClientRect();
        var tooltipRect;

        tooltip.style.left = '-9999px';
        tooltip.style.top = '-9999px';
        tooltip.style.visibility = 'hidden';
        tooltip.style.opacity = '0';
        tooltip.classList.add('visible');
        tooltipRect = tooltip.getBoundingClientRect();

        var gap = 8;
        var arrowHeight = 6;
        var spaceAbove = rect.top - containerRect.top;
        var spaceBelow = containerRect.bottom - rect.bottom;
        var tooltipHeight = tooltipRect.height + arrowHeight + gap;

        var top, arrowClass;

        if (spaceAbove >= tooltipHeight || spaceAbove > spaceBelow) {
            top = rect.top - containerRect.top - tooltipRect.height - arrowHeight - gap;
            arrowClass = 'arrow-bottom';
        } else {
            top = rect.bottom - containerRect.top + arrowHeight + gap;
            arrowClass = 'arrow-top';
        }
        var left = rect.left - containerRect.left + (rect.width / 2) - (tooltipRect.width / 2);
        var rightEdge = left + tooltipRect.width;
        var containerWidth = containerRect.width;

        if (left < 8) {
            left = 8;
        } else if (rightEdge > containerWidth - 8) {
            left = containerWidth - tooltipRect.width - 8;
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
        clearTimeout(showTimeout);
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
        clearTimeout(showTimeout);
        var text = target.getAttribute('data-tooltip');
        if (text) {
            // Delay tooltip display by 500ms
            showTimeout = setTimeout(function() {
                showTooltip(target, text);
            }, 500);
        }
    }

    function handleMouseOut(e) {
        var target = e.target.closest('[data-tooltip]');
        if (!target) return;

        var relatedTarget = e.relatedTarget;
        if (relatedTarget && target.contains(relatedTarget)) return;

        currentTarget = null;
        hideTimeout = setTimeout(hideTooltip, 100);
    }
    container.addEventListener('mouseover', handleMouseOver, false);
    container.addEventListener('mouseout', handleMouseOut, false);
    container.addEventListener('scroll', hideTooltip, true);
}

function initToolbarHandlers(container, pywry) {
    initTooltipManager(container);
    container.querySelectorAll('.pywry-dropdown').forEach(function(dropdown) {
        var selected = dropdown.querySelector('.pywry-dropdown-selected');
        var menu = dropdown.querySelector('.pywry-dropdown-menu');
        var textEl = dropdown.querySelector('.pywry-dropdown-text');

        if (!selected || !menu || !textEl) return;

        selected.addEventListener('click', function(e) {
            e.stopPropagation();
            container.querySelectorAll('.pywry-dropdown.pywry-open').forEach(function(other) {
                if (other !== dropdown) {
                    other.classList.remove('pywry-open');
                    var otherMenu = other.querySelector('.pywry-dropdown-menu');
                    if (otherMenu) otherMenu.style.cssText = '';
                }
            });

            var isOpening = !dropdown.classList.contains('pywry-open');
            dropdown.classList.toggle('pywry-open');

            if (isOpening) {
                var rect = selected.getBoundingClientRect();
                var menuHeight = menu.offsetHeight || 200;
                var viewportHeight = window.innerHeight;
                var openUp = dropdown.classList.contains('pywry-dropdown-up') ||
                             (rect.bottom + menuHeight > viewportHeight && rect.top > menuHeight);

                menu.style.position = 'fixed';
                menu.style.left = rect.left + 'px';
                menu.style.minWidth = rect.width + 'px';

                if (openUp) {
                    menu.style.bottom = (viewportHeight - rect.top + 2) + 'px';
                    menu.style.top = 'auto';
                } else {
                    menu.style.top = (rect.bottom + 2) + 'px';
                    menu.style.bottom = 'auto';
                }
            } else {
                menu.style.cssText = '';
            }
        });
        if (!dropdown.classList.contains('pywry-multiselect')) {
            var selectSearchInput = dropdown.querySelector('.pywry-search-input');
            if (selectSearchInput) {
                selectSearchInput.addEventListener('input', function(e) {
                    var query = e.target.value.toLowerCase();
                    dropdown.querySelectorAll('.pywry-dropdown-option').forEach(function(opt) {
                        var text = opt.textContent.toLowerCase();
                        opt.style.display = text.includes(query) ? '' : 'none';
                    });
                });
                selectSearchInput.addEventListener('click', function(e) {
                    e.stopPropagation();
                });
            }

            dropdown.querySelectorAll('.pywry-dropdown-option').forEach(function(option) {
                option.addEventListener('click', function(e) {
                    e.stopPropagation();
                    var value = option.getAttribute('data-value');
                    dropdown.querySelectorAll('.pywry-dropdown-option').forEach(function(opt) {
                        opt.classList.remove('pywry-selected');
                    });
                    option.classList.add('pywry-selected');
                    textEl.textContent = option.textContent;
                    dropdown.classList.remove('pywry-open');
                    menu.style.cssText = '';

                    if (selectSearchInput) {
                        selectSearchInput.value = '';
                        dropdown.querySelectorAll('.pywry-dropdown-option').forEach(function(opt) {
                            opt.style.display = '';
                        });
                    }
                    var eventName = dropdown.getAttribute('data-event');
                    if (eventName && pywry) {
                        pywry.emit(eventName, { value: value, componentId: dropdown.id });
                    }
                });
            });
        }
        if (dropdown.classList.contains('pywry-multiselect')) {
            var optionsContainer = dropdown.querySelector('.pywry-multiselect-options');
            var searchInput = dropdown.querySelector('.pywry-search-input');

            function updateMultiSelectState(emit) {
                var values = [];
                var labels = [];
                dropdown.querySelectorAll('.pywry-multiselect-checkbox:checked').forEach(function(cb) {
                    values.push(cb.value);
                    var lbl = cb.closest('.pywry-multiselect-option').querySelector('.pywry-multiselect-label');
                    if (lbl) labels.push(lbl.textContent);
                });

                if (values.length === 0) {
                    textEl.textContent = 'Select...';
                } else if (values.length <= 2) {
                    textEl.textContent = labels.join(', ');
                } else {
                    textEl.textContent = values.length + ' selected';
                }

                if (emit) {
                    var eventName = dropdown.getAttribute('data-event');
                    if (eventName && pywry) {
                        pywry.emit(eventName, { values: values, componentId: dropdown.id });
                    }
                }
            }
            function reorderOptions() {
                if (!optionsContainer) return;
                var selectedOpts = [];
                var unselectedOpts = [];
                optionsContainer.querySelectorAll('.pywry-multiselect-option').forEach(function(opt) {
                    var cb = opt.querySelector('.pywry-multiselect-checkbox');
                    if (cb && cb.checked) {
                        selectedOpts.push(opt);
                    } else {
                        unselectedOpts.push(opt);
                    }
                });
                selectedOpts.forEach(function(opt) { optionsContainer.appendChild(opt); });
                unselectedOpts.forEach(function(opt) { optionsContainer.appendChild(opt); });
            }
            if (searchInput) {
                searchInput.addEventListener('input', function(e) {
                    var query = e.target.value.toLowerCase();
                    dropdown.querySelectorAll('.pywry-multiselect-option').forEach(function(opt) {
                        var lbl = opt.querySelector('.pywry-multiselect-label');
                        var text = lbl ? lbl.textContent.toLowerCase() : '';
                        opt.style.display = text.includes(query) ? '' : 'none';
                    });
                });
                searchInput.addEventListener('click', function(e) {
                    e.stopPropagation();
                });
            }
            dropdown.querySelectorAll('.pywry-multiselect-action').forEach(function(btn) {
                btn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    var action = btn.getAttribute('data-action');
                    var checkAll = action === 'all';
                    dropdown.querySelectorAll('.pywry-multiselect-option').forEach(function(opt) {
                        if (opt.style.display === 'none') return;
                        var cb = opt.querySelector('.pywry-multiselect-checkbox');
                        if (cb) {
                            cb.checked = checkAll;
                            if (checkAll) {
                                opt.classList.add('pywry-selected');
                            } else {
                                opt.classList.remove('pywry-selected');
                            }
                        }
                    });
                    reorderOptions();
                    updateMultiSelectState(true);
                });
            });
            dropdown.querySelectorAll('.pywry-multiselect-option').forEach(function(msOption) {
                msOption.addEventListener('click', function(e) {
                    e.stopPropagation();
                    var checkbox = msOption.querySelector('.pywry-multiselect-checkbox');
                    if (checkbox && e.target !== checkbox) {
                        e.preventDefault();
                        checkbox.checked = !checkbox.checked;
                    }
                    setTimeout(function() {
                        if (checkbox && checkbox.checked) {
                            msOption.classList.add('pywry-selected');
                        } else {
                            msOption.classList.remove('pywry-selected');
                        }
                        reorderOptions();
                        updateMultiSelectState(true);
                    }, 0);
                });
            });
        }
    });
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.pywry-dropdown')) {
            container.querySelectorAll('.pywry-dropdown.pywry-open').forEach(function(dropdown) {
                dropdown.classList.remove('pywry-open');
                var menu = dropdown.querySelector('.pywry-dropdown-menu');
                if (menu) menu.style.cssText = '';
            });
        }
    });
    var buttons = container.querySelectorAll('.pywry-toolbar-button');
    buttons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            if (btn.classList.contains('pywry-disabled')) return;
            var eventName = btn.getAttribute('data-event');
            var data = { componentId: btn.id };
            try {
                if (btn.getAttribute('data-data')) {
                    var customData = JSON.parse(btn.getAttribute('data-data'));
                    Object.assign(data, customData);
                }
            } catch (err) {}
            if (eventName && pywry) {
                pywry.emit(eventName, data);
            }
        });
    });

    // Marquee click handlers (for clickable marquees)
    container.querySelectorAll('.pywry-marquee.pywry-marquee-clickable').forEach(function(marquee) {
        marquee.addEventListener('click', function(e) {
            if (marquee.classList.contains('pywry-disabled')) return;
            var eventName = marquee.getAttribute('data-event');
            var text = marquee.getAttribute('data-text') || '';
            if (eventName && pywry) {
                pywry.emit(eventName, { value: text, componentId: marquee.id });
            }
        });
    });

    // Static marquee auto-cycling (when items are provided)
    container.querySelectorAll('.pywry-marquee.pywry-marquee-static[data-items]').forEach(function(marquee) {
        try {
            var items = JSON.parse(marquee.getAttribute('data-items'));
            var speed = parseFloat(marquee.getAttribute('data-speed')) || 5;
            if (!Array.isArray(items) || items.length === 0) return;

            var currentIndex = 0;
            var contentSpan = marquee.querySelector('.pywry-marquee-content');
            if (!contentSpan) return;

            // Set initial content
            contentSpan.innerHTML = items[0];

            // Auto-cycle through items
            setInterval(function() {
                currentIndex = (currentIndex + 1) % items.length;
                contentSpan.innerHTML = items[currentIndex];
            }, speed * 1000);
        } catch (err) {
            console.warn('[toolbar] Failed to initialize static marquee auto-cycle:', err);
        }
    });

    var inputDebounceTimers = {};
    container.querySelectorAll('.pywry-input-text, .pywry-input-number, .pywry-input-date').forEach(function(input) {
        input.addEventListener('input', function(e) {
            var eventName = input.getAttribute('data-event');
            var debounce = parseInt(input.getAttribute('data-debounce') || '0', 10);
            var inputId = input.id || input.getAttribute('data-event');

            if (inputDebounceTimers[inputId]) {
                clearTimeout(inputDebounceTimers[inputId]);
            }

            var sendValue = function() {
                var value = input.value;
                if (input.type === 'number') value = parseFloat(value);
                if (eventName && pywry) {
                    pywry.emit(eventName, { value: value, componentId: input.id });
                }
            };

            if (debounce > 0) {
                inputDebounceTimers[inputId] = setTimeout(sendValue, debounce);
            } else {
                sendValue();
            }
        });
    });
    container.querySelectorAll('.pywry-input-date').forEach(function(input) {
        if (!input.value) {
            input.classList.add('pywry-date-empty');
        }

        input.addEventListener('change', function() {
            if (input.value) {
                input.classList.remove('pywry-date-empty');
            } else {
                input.classList.add('pywry-date-empty');
            }

            var eventName = input.getAttribute('data-event');
            if (eventName && pywry) {
                pywry.emit(eventName, { value: input.value, componentId: input.id });
            }
        });
    });
    container.querySelectorAll('.pywry-input-slider, .pywry-input-range').forEach(function(slider) {
        slider.addEventListener('input', function(e) {
            var eventName = slider.getAttribute('data-event');
            var value = parseFloat(slider.value);
            var display = slider.parentElement && slider.parentElement.querySelector('.pywry-slider-value');
            if (display) display.textContent = value;
            if (eventName && pywry) {
                pywry.emit(eventName, { value: value, componentId: slider.id });
            }
        });
    });
    container.querySelectorAll('.pywry-toolbar[data-collapsible="true"]').forEach(function(toolbar) {
        var componentId = toolbar.getAttribute('data-component-id');
        var storageKey = 'pywry-toolbar-collapsed-' + componentId;
        var savedState = sessionStorage.getItem(storageKey);
        if (savedState === 'true') {
            toolbar.classList.add('pywry-collapsed');
            toolbar.setAttribute('aria-expanded', 'false');
        }
    });
    container.querySelectorAll('.pywry-toolbar-toggle').forEach(function(toggleBtn) {
        toggleBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            var toolbarId = toggleBtn.getAttribute('data-toolbar-id');
            var toolbar = document.getElementById(toolbarId);
            if (toolbar) {
                var isCollapsed = toolbar.classList.toggle('pywry-collapsed');
                toolbar.setAttribute('aria-expanded', !isCollapsed);
                var storageKey = 'pywry-toolbar-collapsed-' + toolbarId;
                sessionStorage.setItem(storageKey, isCollapsed);
                if (window.pywry && window.pywry.emit) {
                    var eventName = isCollapsed ? 'toolbar:collapse' : 'toolbar:expand';
                    window.pywry.emit(eventName, { componentId: toolbarId, collapsed: isCollapsed }, toolbar);
                }
            }
        });
    });
    var resizeState = { active: false, toolbar: null, startX: 0, startY: 0, startWidth: 0, startHeight: 0, position: null };
    container.querySelectorAll('.pywry-toolbar[data-resizable="true"]').forEach(function(toolbar) {
        var componentId = toolbar.getAttribute('data-component-id');
        var position = toolbar.getAttribute('data-position');
        var savedWidth = sessionStorage.getItem('pywry-toolbar-width-' + componentId);
        var savedHeight = sessionStorage.getItem('pywry-toolbar-height-' + componentId);
        if (savedWidth && (position === 'left' || position === 'right')) toolbar.style.width = savedWidth;
        if (savedHeight && (position === 'top' || position === 'bottom')) toolbar.style.height = savedHeight;
    });
    container.querySelectorAll('.pywry-resize-handle').forEach(function(handle) {
        handle.addEventListener('mousedown', function(e) {
            var toolbarId = handle.getAttribute('data-toolbar-id');
            var toolbar = document.getElementById(toolbarId);
            if (toolbar) {
                resizeState.active = true;
                resizeState.toolbar = toolbar;
                resizeState.startX = e.clientX;
                resizeState.startY = e.clientY;
                resizeState.startWidth = toolbar.offsetWidth;
                resizeState.startHeight = toolbar.offsetHeight;
                resizeState.position = toolbar.getAttribute('data-position');
                document.body.style.cursor = (resizeState.position === 'left' || resizeState.position === 'right') ? 'ew-resize' : 'ns-resize';
                document.body.style.userSelect = 'none';
                e.preventDefault();
            }
        });
    });
    document.addEventListener('mousemove', function(e) {
        if (!resizeState.active || !resizeState.toolbar) return;
        var dx = e.clientX - resizeState.startX;
        var dy = e.clientY - resizeState.startY;
        var toolbar = resizeState.toolbar;
        var position = resizeState.position;
        if (position === 'top') { toolbar.style.height = Math.max(20, resizeState.startHeight + dy) + 'px'; toolbar.style.flexShrink = '0'; }
        else if (position === 'bottom') { toolbar.style.height = Math.max(20, resizeState.startHeight - dy) + 'px'; toolbar.style.flexShrink = '0'; }
        else if (position === 'left') { toolbar.style.width = Math.max(20, resizeState.startWidth + dx) + 'px'; toolbar.style.flexShrink = '0'; }
        else if (position === 'right') { toolbar.style.width = Math.max(20, resizeState.startWidth - dx) + 'px'; toolbar.style.flexShrink = '0'; }
    });
    document.addEventListener('mouseup', function(e) {
        if (!resizeState.active || !resizeState.toolbar) return;
        var toolbar = resizeState.toolbar;
        var componentId = toolbar.getAttribute('data-component-id');
        var position = resizeState.position;
        if (position === 'left' || position === 'right') sessionStorage.setItem('pywry-toolbar-width-' + componentId, toolbar.style.width);
        if (position === 'top' || position === 'bottom') sessionStorage.setItem('pywry-toolbar-height-' + componentId, toolbar.style.height);
        if (window.pywry && window.pywry.emit) {
            window.pywry.emit('toolbar:resize', { componentId: componentId, position: position, width: toolbar.offsetWidth, height: toolbar.offsetHeight }, toolbar);
        }
        resizeState.active = false;
        resizeState.toolbar = null;
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
    });
    container.querySelectorAll('.pywry-toolbar-bottom .pywry-dropdown, .pywry-toolbar-footer .pywry-dropdown').forEach(function(dropdown) {
        dropdown.classList.add('pywry-dropdown-up');
    });

    // toolbar:marquee-set-content - Update marquee content (handles duplicated spans)
    // toolbar:marquee-set-item - Update individual items within a marquee
    if (pywry && pywry.on) {
        // Update entire marquee content
        pywry.on('toolbar:marquee-set-content', function(data) {
            var marquee = data.id ? document.getElementById(data.id) :
                          data.selector ? container.querySelector(data.selector) : null;
            if (!marquee || !marquee.classList.contains('pywry-marquee')) {
                console.warn('[toolbar] toolbar:marquee-set-content - no marquee found for', data.id || data.selector);
                return;
            }
            // Update all content spans (there are 2 for seamless scrolling)
            var contentSpans = marquee.querySelectorAll('.pywry-marquee-content');
            if (data.html !== undefined || data.text !== undefined) {
                var newContent = data.html !== undefined ? data.html :
                    (data.text ? data.text.replace(/</g, '&lt;').replace(/>/g, '&gt;') : '');
                contentSpans.forEach(function(span) {
                    span.innerHTML = newContent;
                });
            }
            // Update data-text attribute for click events
            if (data.text !== undefined) {
                marquee.setAttribute('data-text', data.text);
            }
            // Optionally update separator
            if (data.separator !== undefined) {
                var separators = marquee.querySelectorAll('.pywry-marquee-separator');
                separators.forEach(function(sep) {
                    sep.innerHTML = data.separator.replace(/</g, '&lt;').replace(/>/g, '&gt;');
                });
            }
            // Optionally update speed
            if (data.speed !== undefined) {
                marquee.style.setProperty('--pywry-marquee-speed', data.speed + 's');
            }
            // Optionally pause/resume
            if (data.paused !== undefined) {
                var track = marquee.querySelector('.pywry-marquee-track');
                if (track) {
                    track.style.animationPlayState = data.paused ? 'paused' : 'running';
                }
            }
        });

        // Update individual ticker items within a marquee
        pywry.on('toolbar:marquee-set-item', function(data) {
            // data.ticker: the ticker symbol (matches data-ticker attribute)
            // data.selector: alternative CSS selector to match elements
            // data.text/html: new content
            // data.styles: optional inline styles to apply
            // data.class_add/class_remove: optional class modifications
            var selector = data.ticker ? '[data-ticker="' + data.ticker + '"]' :
                           data.selector ? data.selector : null;
            if (!selector) {
                console.warn('[toolbar] toolbar:marquee-set-item - no ticker or selector provided');
                return;
            }
            var elements = container.querySelectorAll(selector);
            if (!elements.length) {
                console.warn('[toolbar] toolbar:marquee-set-item - no elements found for', selector);
                return;
            }
            elements.forEach(function(el) {
                // Update content
                if (data.html !== undefined) {
                    el.innerHTML = data.html;
                } else if (data.text !== undefined) {
                    el.textContent = data.text;
                }
                // Apply styles
                if (data.styles) {
                    Object.keys(data.styles).forEach(function(prop) {
                        el.style[prop] = data.styles[prop];
                    });
                }
                // Add/remove classes
                if (data.class_add) {
                    var adds = Array.isArray(data.class_add) ? data.class_add : [data.class_add];
                    adds.forEach(function(c) { el.classList.add(c); });
                }
                if (data.class_remove) {
                    var removes = Array.isArray(data.class_remove) ? data.class_remove : [data.class_remove];
                    removes.forEach(function(c) { el.classList.remove(c); });
                }
            });
        });
    }
}
