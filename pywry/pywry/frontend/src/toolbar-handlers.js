/**
 * PyWry Toolbar Handlers - CENTRALIZED
 * 
 * This is the SINGLE source of truth for all toolbar interaction handlers.
 * Used by all widget types (AG Grid, Plotly, basic widgets).
 * 
 * DO NOT DUPLICATE THIS CODE ELSEWHERE!
 */

function initToolbarHandlers(container, pywry) {
    console.log('[PyWry Toolbar] Initializing toolbar handlers...');

    // --- Dropdown (Select) handling ---
    container.querySelectorAll('.pywry-dropdown').forEach(function(dropdown) {
        var selected = dropdown.querySelector('.pywry-dropdown-selected');
        var menu = dropdown.querySelector('.pywry-dropdown-menu');
        var textEl = dropdown.querySelector('.pywry-dropdown-text');

        if (!selected || !menu || !textEl) return;

        // Toggle dropdown on click
        selected.addEventListener('click', function(e) {
            e.stopPropagation();
            // Close all other dropdowns in this container first
            container.querySelectorAll('.pywry-dropdown.pywry-open').forEach(function(other) {
                if (other !== dropdown) {
                    other.classList.remove('pywry-open');
                    var otherMenu = other.querySelector('.pywry-dropdown-menu');
                    if (otherMenu) otherMenu.style.cssText = '';
                }
            });

            var isOpening = !dropdown.classList.contains('pywry-open');
            dropdown.classList.toggle('pywry-open');

            // Position dropdown menu using fixed positioning to escape overflow:hidden
            if (isOpening) {
                var rect = selected.getBoundingClientRect();
                var menuHeight = menu.offsetHeight || 200;
                var viewportHeight = window.innerHeight;

                // Check if dropdown should open upward
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

        // Handle option selection (single-select only)
        if (!dropdown.classList.contains('pywry-multiselect')) {
            dropdown.querySelectorAll('.pywry-dropdown-option').forEach(function(option) {
                option.addEventListener('click', function(e) {
                    e.stopPropagation();
                    var value = option.getAttribute('data-value');

                    // Update selected state
                    dropdown.querySelectorAll('.pywry-dropdown-option').forEach(function(opt) {
                        opt.classList.remove('pywry-selected');
                    });
                    option.classList.add('pywry-selected');
                    textEl.textContent = option.textContent;
                    dropdown.classList.remove('pywry-open');
                    menu.style.cssText = '';

                    // Emit event
                    var eventName = dropdown.getAttribute('data-event');
                    if (eventName && pywry) {
                        console.log('[PyWry Toolbar] Dropdown changed:', eventName, value);
                        pywry.emit(eventName, { value: value, componentId: dropdown.id });
                    }
                });
            });
        }

        // Handle multiselect
        if (dropdown.classList.contains('pywry-multiselect')) {
            var optionsContainer = dropdown.querySelector('.pywry-multiselect-options');
            var searchInput = dropdown.querySelector('.pywry-multiselect-search');

            // Helper to update display text and emit event
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
                        console.log('[PyWry Toolbar] MultiSelect changed:', eventName, values);
                        pywry.emit(eventName, { values: values, componentId: dropdown.id });
                    }
                }
            }

            // Helper to reorder options (selected first)
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

            // Search input handler
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

            // Select All / None buttons
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

            // Option click handler - use mousedown to capture before native checkbox toggle
            dropdown.querySelectorAll('.pywry-multiselect-option').forEach(function(msOption) {
                msOption.addEventListener('click', function(e) {
                    e.stopPropagation();
                    var checkbox = msOption.querySelector('.pywry-multiselect-checkbox');
                    
                    // If clicking the label area (not the checkbox itself), toggle manually
                    if (checkbox && e.target !== checkbox) {
                        e.preventDefault();
                        checkbox.checked = !checkbox.checked;
                    }
                    // If clicking the checkbox directly, let native behavior happen first
                    // Use setTimeout to ensure we read the updated checkbox state
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

    // --- Close dropdowns when clicking outside ---
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.pywry-dropdown')) {
            container.querySelectorAll('.pywry-dropdown.pywry-open').forEach(function(dropdown) {
                dropdown.classList.remove('pywry-open');
                var menu = dropdown.querySelector('.pywry-dropdown-menu');
                if (menu) menu.style.cssText = '';
            });
        }
    });

    // --- Button handling ---
    var buttons = container.querySelectorAll('.pywry-toolbar-button');
    console.log('[PyWry Toolbar] Found', buttons.length, 'toolbar buttons');
    buttons.forEach(function(btn) {
        console.log('[PyWry Toolbar] Attaching click handler to button:', btn.textContent, 'event:', btn.getAttribute('data-event'));
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
                console.log('[PyWry Toolbar] Button clicked:', eventName, data);
                pywry.emit(eventName, data);
            }
        });
    });

    // --- Text/Number/Date Input handling (with debounce) ---
    var inputDebounceTimers = {};
    container.querySelectorAll('.pywry-text-input, .pywry-number-input, .pywry-date-input').forEach(function(input) {
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

    // --- Slider/Range Input handling ---
    container.querySelectorAll('.pywry-slider-input, .pywry-range-input').forEach(function(slider) {
        slider.addEventListener('input', function(e) {
            var eventName = slider.getAttribute('data-event');
            var value = parseFloat(slider.value);
            // Update display value if present
            var display = slider.parentElement && slider.parentElement.querySelector('.pywry-slider-value');
            if (display) display.textContent = value;
            if (eventName && pywry) {
                pywry.emit(eventName, { value: value, componentId: slider.id });
            }
        });
    });

    // --- Collapsible Toolbar Handling ---
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

    // --- Resizable Toolbar Handling ---
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

    // --- Dropdown open direction: open upward for bottom/footer toolbars ---
    container.querySelectorAll('.pywry-toolbar-bottom .pywry-dropdown, .pywry-toolbar-footer .pywry-dropdown').forEach(function(dropdown) {
        dropdown.classList.add('pywry-dropdown-up');
    });

    console.log('[PyWry Toolbar] Handlers initialized');
}
