/*PyWry AG Grid Default Configuration (Community Edition) */

// Registry of all grid instances by ID
window.__PYWRY_GRIDS__ = window.__PYWRY_GRIDS__ || {};

/**
 * Show a temporary notification toast.
 * Theme-aware, uses AG Grid CSS custom properties.
 * @param {string} message - Message to display
 * @param {number} duration - Duration in ms (default 3000)
 * @param {HTMLElement} container - Optional container for theme context
 */
window.PYWRY_SHOW_NOTIFICATION = function(message, duration, container) {
    duration = duration || 3000;
    
    // Find theme class from container or body
    var themeClass = 'ag-theme-alpine-dark';
    var el = container || document.body;
    while (el) {
        if (el.className && typeof el.className === 'string') {
            var classes = el.className.split(' ');
            for (var i = 0; i < classes.length; i++) {
                if (classes[i].indexOf('ag-theme-') === 0) {
                    themeClass = classes[i];
                    break;
                }
            }
        }
        if (themeClass !== 'ag-theme-alpine-dark') break;
        el = el.parentElement;
    }

    var wrapper = document.createElement('div');
    wrapper.className = 'pywry-notification-wrapper ' + themeClass;
    wrapper.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:2147483647;pointer-events:none;';
    
    var toast = document.createElement('div');
    toast.className = 'pywry-toast-notification';
    toast.textContent = message;
    toast.style.cssText = [
        'padding: 12px 20px',
        'background-color: var(--ag-background-color, #1e1e1e)',
        'color: var(--ag-foreground-color, #fff)',
        'border: 1px solid var(--ag-border-color, #444)',
        'border-radius: var(--ag-border-radius, 4px)',
        'box-shadow: var(--ag-popup-shadow, 0 4px 16px rgba(0, 0, 0, 0.3))',
        'font-family: var(--ag-font-family, inherit)',
        'font-size: var(--ag-font-size, 13px)',
        'opacity: 0',
        'transition: opacity 0.3s ease',
        'max-width: 500px',
        'word-break: break-all',
        'pointer-events: auto'
    ].join(';') + ';';
    
    wrapper.appendChild(toast);
    document.body.appendChild(wrapper);

    setTimeout(function() { toast.style.opacity = '1'; }, 10);

    setTimeout(function() {
        toast.style.opacity = '0';
        setTimeout(function() { wrapper.remove(); }, 300);
    }, duration);
};

window.PYWRY_AGGRID_DEFAULT_COL_DEF = {
    filter: true,
    sortable: true,
    resizable: true,
    menuTabs: ['generalMenuTab', 'filterMenuTab', 'columnsMenuTab'],
    filterParams: {
        buttons: ['apply', 'clear', 'reset'],
        closeOnApply: true,
        maxNumConditions: 10,
    },
};

/**
 * Build complete grid options from config.
 * 
 * @param {Object} config - Grid configuration (columnDefs, rowData, etc.)
 * @param {string} gridId - Unique identifier for this grid instance
 * @returns {Object} Complete AG Grid options
 */
window.PYWRY_AGGRID_BUILD_OPTIONS = function(config, gridId) {
    var id = gridId || 'default';
    
    console.log('[PyWry AG Grid ' + id + '] Building options with defaults');
    console.log('[PyWry AG Grid ' + id + '] defaultColDef:', window.PYWRY_AGGRID_DEFAULT_COL_DEF);
    
    var options = {
        columnDefs: config.columnDefs,
        rowData: config.rowData,
        rowSelection: config.rowSelection || 'multiple',
        pagination: config.pagination !== false,
        paginationPageSize: config.paginationPageSize || 100,
        paginationAutoPageSize: false,
        domLayout: config.domLayout || 'autoHeight',
        defaultColDef: Object.assign({}, window.PYWRY_AGGRID_DEFAULT_COL_DEF, config.defaultColDef || {}),
        columnMenu: 'new',
        suppressMenuHide: true,
        enableCellTextSelection: true,
        ensureDomOrder: true,

        onCellClicked: function(event) {
            if (window.pywry && window.pywry.emit) {
                window.pywry.emit('cell_click', {
                    gridId: id,
                    rowIndex: event.rowIndex,
                    colId: event.column.getColId(),
                    value: event.value,
                    data: event.data
                });
            }
        },
        onSelectionChanged: function(event) {
            if (window.pywry && window.pywry.emit) {
                var selectedRows = event.api.getSelectedRows();
                window.pywry.emit('row_selected', { gridId: id, rows: selectedRows });
            }
        },
        onGridReady: function(event) {
            console.log('[PyWry AG Grid ' + id + '] Grid ready!');
            // Auto-size columns to fit content
            event.api.autoSizeAllColumns();
        }
    };
    
    console.log('[PyWry AG Grid ' + id + '] Final options:', Object.keys(options));
    return options;
};

/**
 * Register Python event listeners on a specific grid instance.
 * Events are scoped by gridId - each grid only responds to its own events.
 * 
 * @param {Object} gridApi - The AG Grid API instance
 * @param {HTMLElement} gridDiv - The grid container element (for theme updates)
 * @param {string} gridId - Unique identifier for this grid instance
 */
window.PYWRY_AGGRID_REGISTER_LISTENERS = function(gridApi, gridDiv, gridId) {
    var id = gridId || 'default';
    window.__PYWRY_GRIDS__[id] = {
        api: gridApi,
        div: gridDiv
    };

    if (!window.__PYWRY_GRID_API__) {
        window.__PYWRY_GRID_API__ = gridApi;
    }

    if (!window.pywry || !window.pywry.on) {
        console.warn('[PyWry AG Grid ' + id + '] pywry bridge not available, skipping listener registration');
        return;
    }

    function saveColumnState() {
        try {
            return {
                columnState: gridApi.getColumnState ? gridApi.getColumnState() : null,
                filterModel: gridApi.getFilterModel ? gridApi.getFilterModel() : null,
                sortModel: gridApi.getSortModel ? gridApi.getSortModel() : null
            };
        } catch(e) {
            console.warn('[PyWry AG Grid ' + id + '] Failed to save state:', e);
            return null;
        }
    }

    function restoreColumnState(state) {
        if (!state) return;
        try {
            if (state.columnState && gridApi.applyColumnState) {
                gridApi.applyColumnState({
                    state: state.columnState,
                    applyOrder: true
                });
                console.log('[PyWry AG Grid ' + id + '] Column state restored');
            }
            if (state.filterModel && gridApi.setFilterModel) {
                gridApi.setFilterModel(state.filterModel);
            }
        } catch(e) {
            console.warn('[PyWry AG Grid ' + id + '] Failed to restore state:', e);
        }
    }

    window.__PYWRY_GRIDS__[id].saveState = saveColumnState;
    window.__PYWRY_GRIDS__[id].restoreState = restoreColumnState;
    window.pywry.on('pywry:update_rows', function(data) {

        if (data && data.rows && (!data.gridId || data.gridId === id)) {
            gridApi.setGridOption('rowData', data.rows);
            console.log('[PyWry AG Grid ' + id + '] Rows updated:', data.rows.length, 'rows');
        }
    });

    window.pywry.on('pywry:update_columns', function(data) {
        if (data && data.columnDefs && (!data.gridId || data.gridId === id)) {
            var savedState = data.preserveState !== false ? saveColumnState() : null;
            gridApi.setGridOption('columnDefs', data.columnDefs);
            if (savedState && data.preserveState !== false) {
                setTimeout(function() { restoreColumnState(savedState); }, 0);
            }
            console.log('[PyWry AG Grid ' + id + '] Columns updated:', data.columnDefs.length, 'columns');
        }
    });

    window.pywry.on('pywry:update_grid', function(data) {
        if (data && (!data.gridId || data.gridId === id)) {
            var savedState = data.preserveState !== false ? saveColumnState() : null;
            
            if (data.columnDefs) {
                gridApi.setGridOption('columnDefs', data.columnDefs);
            }
            if (data.rows) {
                gridApi.setGridOption('rowData', data.rows);
            }
            
            if (savedState && data.preserveState !== false) {
                setTimeout(function() { restoreColumnState(savedState); }, 0);
            }
            console.log('[PyWry AG Grid ' + id + '] Grid fully updated');
        }
    });

    window.pywry.on('pywry:update_theme', function(data) {
        if (data && data.theme && (!data.gridId || data.gridId === id) && gridDiv) {
            var classes = gridDiv.className.split(' ').filter(function(c) {
                return !c.startsWith('ag-theme-');
            });
            classes.push(data.theme);
            gridDiv.className = classes.join(' ');
            console.log('[PyWry AG Grid ' + id + '] Theme updated to:', data.theme);
        }
    });

    window.pywry.on('pywry:save_state', function(data) {
        if (!data.gridId || data.gridId === id) {
            var state = saveColumnState();
            if (window.pywry && window.pywry.emit) {
                window.pywry.emit('grid_state_saved', {
                    gridId: id,
                    state: state
                });
            }
        }
    });

    window.pywry.on('pywry:restore_state', function(data) {
        if (data && data.state && (!data.gridId || data.gridId === id)) {
            restoreColumnState(data.state);
        }
    });

    window.pywry.on('pywry:reset_state', function(data) {
        if (!data.gridId || data.gridId === id) {
            gridApi.resetColumnState();
            gridApi.setFilterModel(null);
            console.log('[PyWry AG Grid ' + id + '] State reset');
        }
    });

    window.pywry.on('pywry:show_notification', function(data) {
        if (!data.gridId || data.gridId === id) {
            window.PYWRY_SHOW_NOTIFICATION(data.message, data.duration, gridDiv);
        }
    });

    console.log('[PyWry AG Grid ' + id + '] Python event listeners registered');

    if (window.PYWRY_AGGRID_SETUP_CONTEXT_MENU) {
        window.PYWRY_AGGRID_SETUP_CONTEXT_MENU(gridApi, gridDiv, id);
    }
};

/**
 * Get a grid instance by ID.
 * @param {string} gridId - The grid ID
 * @returns {Object|null} Object with {api, div} or null if not found
 */
window.PYWRY_AGGRID_GET_GRID = function(gridId) {
    return window.__PYWRY_GRIDS__[gridId] || null;
};

/**
 * Destroy a grid instance and remove from registry.
 * @param {string} gridId - The grid ID to destroy
 */
window.PYWRY_AGGRID_DESTROY_GRID = function(gridId) {
    var grid = window.__PYWRY_GRIDS__[gridId];
    if (grid && grid.api) {
        grid.api.destroy();
        delete window.__PYWRY_GRIDS__[gridId];
        console.log('[PyWry AG Grid ' + gridId + '] Destroyed');
    }
};

/**
 * Custom Context Menu (Community Edition alternative)
 * Creates a right-click menu styled like AG Grid's native menu.
 * Menu elements inherit from the AG Grid theme class wrapper.
 */
window.PYWRY_AGGRID_CONTEXT_MENU = {
    _currentMenu: null,
    _activeSubmenus: [],
    _themeClass: 'ag-theme-alpine-dark',
    
    /**
     * Hide any visible context menu and submenus
     */
    hide: function() {
        // Hide all submenus
        this._activeSubmenus.forEach(function(sub) {
            if (sub && sub.parentNode) sub.remove();
        });
        this._activeSubmenus = [];
        
        // Hide main menu
        if (this._currentMenu) {
            this._currentMenu.remove();
            this._currentMenu = null;
        }
    },
    
    /**
     * Set theme for menu styling
     * @param {string} themeClass - The AG Grid theme class (e.g., 'ag-theme-alpine-dark')
     */
    setTheme: function(themeClass) {
        this._themeClass = themeClass || 'ag-theme-alpine-dark';
    },
    
    /**
     * Get menu styles - uses CSS custom properties from AG Grid theme
     */
    _getMenuStyles: function() {
        // Core positioning and layout - no colors here, colors come from CSS vars
        var styles = [
            'position: fixed',
            'z-index: 2147483647',
            'min-width: 200px',
            'max-width: 300px',
            'pointer-events: auto',
            'overflow: visible',
            'background-color: var(--ag-background-color, var(--ag-header-background-color))',
            'border: 1px solid var(--ag-border-color)',
            'border-radius: var(--ag-border-radius, 4px)',
            'box-shadow: var(--ag-popup-shadow, 0 4px 16px rgba(0, 0, 0, 0.3))',
            'color: var(--ag-foreground-color)',
            'font-family: var(--ag-font-family, inherit)',
            'font-size: var(--ag-font-size, 13px)',
        ];
        
        return styles.join(';') + ';';
    },
    
    /**
     * Create a menu item element - fully CSS-selectable, no inline colors
     */
    _createMenuItem: function(item, context, parentMenu) {
        var self = this;
        
        if (item.separator) {
            var sep = document.createElement('div');
            sep.className = 'ag-menu-separator pywry-menu-separator';
            // Separator uses CSS vars
            sep.style.cssText = 'height: 1px; background-color: var(--ag-border-color); margin: 4px 8px;';
            return sep;
        }
        
        var option = document.createElement('div');
        option.className = 'ag-menu-option pywry-menu-option' + (item.disabled ? ' ag-menu-option-disabled pywry-menu-option-disabled' : '');
        option.setAttribute('role', 'treeitem');
        option.setAttribute('tabindex', '-1');
    
        var optionStyles = [
            'display: flex',
            'align-items: center',
            'padding: 8px 12px',
            'cursor: pointer',
            'transition: background-color 0.15s ease',
            'position: relative',
            'background-color: transparent',
        ];
        
        if (item.disabled) {
            optionStyles.push('opacity: 0.5');
            optionStyles.push('cursor: default');
        }
        
        option.style.cssText = optionStyles.join(';') + ';';

        var iconPart = document.createElement('span');
        iconPart.className = 'ag-menu-option-part ag-menu-option-icon pywry-menu-icon';
        iconPart.style.cssText = 'width: 20px; margin-right: 8px; text-align: center; flex-shrink: 0;';
        if (item.icon) {
            var iconMap = {
                'copy': '📋',
                'csv': '📄',
                'columns': '▤',
                'filter': '🔍',
                'tick': '✓',
                'cross': '✕',
                'menu': '☰',
                'eye': '👁',
                'eye-slash': '◌',
                'pin': '📌',
                'unpin': '⊘',
                'left': '⬅',
                'right': '➡'
            };
            iconPart.textContent = iconMap[item.icon] || item.icon;
        } else if (item.checked !== undefined) {
            // Show check mark for checked items - color from CSS var
            iconPart.textContent = item.checked ? '✓' : '';
            iconPart.style.color = item.checked ? 'var(--ag-input-focus-border-color, #4CAF50)' : 'transparent';
        }
        option.appendChild(iconPart);

        var textPart = document.createElement('span');
        textPart.className = 'ag-menu-option-part ag-menu-option-text pywry-menu-text';
        textPart.textContent = item.label;
        textPart.style.cssText = 'flex: 1;';
        option.appendChild(textPart);
        var pointerPart = document.createElement('span');
        pointerPart.className = 'ag-menu-option-part ag-menu-option-popup-pointer pywry-menu-pointer';
        pointerPart.style.cssText = 'width: 16px; text-align: right; flex-shrink: 0; opacity: 0.6;';
        if (item.submenu && item.submenu.length > 0) {
            pointerPart.textContent = '▶';
        }
        option.appendChild(pointerPart);

        var submenuTimeout = null;
        
        if (!item.disabled) {
            option.addEventListener('mouseenter', function() {
                // Use AG Grid's hover color variable
                this.style.backgroundColor = 'var(--ag-row-hover-color, var(--ag-range-selection-background-color, rgba(128,128,128,0.2)))';
                
                // Show submenu after small delay
                if (item.submenu && item.submenu.length > 0) {
                    submenuTimeout = setTimeout(function() {
                        // Hide any existing submenus at this level
                        self._hideSubmenusAfter(parentMenu);
                        
                        var rect = option.getBoundingClientRect();
                        self._showSubmenu(rect.right - 4, rect.top, item.submenu, context, parentMenu);
                    }, 150);
                }
            });
            
            option.addEventListener('mouseleave', function() {
                this.style.backgroundColor = 'transparent';
                if (submenuTimeout) {
                    clearTimeout(submenuTimeout);
                    submenuTimeout = null;
                }
            });
            
            // Click action (only if no submenu)
            if (item.action && !item.submenu) {
                option.addEventListener('click', function() {
                    self.hide();
                    item.action(context);
                });
            }
        }
        
        return option;
    },
    
    /**
     * Hide submenus that are children of the given parent
     */
    _hideSubmenusAfter: function(parentMenu) {
        var parentIndex = this._activeSubmenus.indexOf(parentMenu);
        if (parentIndex === -1) parentIndex = -1; // Main menu
        
        // Remove all submenus after this level
        while (this._activeSubmenus.length > parentIndex + 1) {
            var sub = this._activeSubmenus.pop();
            if (sub && sub.parentNode) sub.remove();
        }
    },
    
    /**
     * Show a submenu
     */
    _showSubmenu: function(x, y, items, context, parentMenu) {
        var self = this;
        
        // Create submenu - inherits theme from wrapper
        var submenu = document.createElement('div');
        submenu.className = 'ag-popup ag-menu ag-ltr ag-popup-child pywry-context-submenu';
        submenu.style.cssText = this._getMenuStyles();
        
        var list = document.createElement('div');
        list.className = 'ag-menu-list pywry-menu-list';
        list.setAttribute('role', 'tree');
        list.style.cssText = 'padding: 4px 0; max-height: 400px; overflow-y: auto;';
        
        items.forEach(function(item) {
            var menuItem = self._createMenuItem(item, context, submenu);
            list.appendChild(menuItem);
        });
        
        submenu.appendChild(list);

        if (this._currentMenu) {
            this._currentMenu.appendChild(submenu);
        } else {
            document.body.appendChild(submenu);
        }

        var viewportWidth = window.innerWidth;
        var viewportHeight = window.innerHeight;
        var subRect = submenu.getBoundingClientRect();

        if (x + subRect.width > viewportWidth) {
            var parentRect = parentMenu ? parentMenu.getBoundingClientRect() : { left: x };
            x = parentRect.left - subRect.width + 4;
        }

        if (y + subRect.height > viewportHeight) {
            y = viewportHeight - subRect.height - 5;
        }
        if (y < 5) y = 5;
        
        submenu.style.left = x + 'px';
        submenu.style.top = y + 'px';
        this._activeSubmenus.push(submenu);
        submenu.addEventListener('mouseenter', function() {
            // Don't hide
        });
        
        return submenu;
    },
    
    /**
     * Show context menu at position
     * @param {number} x - X coordinate
     * @param {number} y - Y coordinate
     * @param {Array} items - Menu items [{label, icon?, action?, disabled?, separator?, submenu?}]
     * @param {Object} context - Context object passed to action callbacks
     * @param {HTMLElement} container - Optional container element for positioning context
     */
    show: function(x, y, items, context, container) {
        this.hide();
        var self = this;
        var containerRect = null;
        if (container) {
            containerRect = container.getBoundingClientRect();
        }
        var wrapper = document.createElement('div');
        wrapper.className = 'pywry-context-menu-wrapper ' + this._themeClass;
        wrapper.style.cssText = 'position:fixed;top:0;left:0;width:0;height:0;z-index:2147483647;pointer-events:none;';
        var menu = document.createElement('div');
        menu.className = 'ag-popup ag-menu ag-ltr ag-popup-child pywry-context-menu';
        menu.style.cssText = this._getMenuStyles();
        var list = document.createElement('div');
        list.className = 'ag-menu-list pywry-menu-list';
        list.setAttribute('role', 'tree');
        items.forEach(function(item) {
            var menuItem = self._createMenuItem(item, context, menu);
            list.appendChild(menuItem);
        });
        menu.appendChild(list);
        wrapper.appendChild(menu);
        document.body.appendChild(wrapper);
        var menuRect = menu.getBoundingClientRect();
        var viewportWidth = window.innerWidth;
        var viewportHeight = window.innerHeight;
        var maxBottom = viewportHeight;
        var maxRight = viewportWidth;
        if (containerRect) {
            maxBottom = Math.min(viewportHeight, containerRect.bottom);
            maxRight = Math.min(viewportWidth, containerRect.right);
        }
        var spaceBelow = maxBottom - y;
        var spaceAbove = y - (containerRect ? containerRect.top : 0);
        var maxMenuHeight = Math.max(spaceBelow, spaceAbove) - 10;
        list.style.cssText = 'padding: 4px 0; max-height: ' + maxMenuHeight + 'px; overflow-y: auto;';
        menuRect = menu.getBoundingClientRect();

        if (menuRect.height > spaceBelow && spaceAbove > spaceBelow) {
            y = Math.max(5, y - menuRect.height);
        } else if (y + menuRect.height > maxBottom) {
            y = Math.max(5, maxBottom - menuRect.height - 5);
        }
        
        if (x + menuRect.width > maxRight) {
            x = Math.max(5, maxRight - menuRect.width - 5);
        }
        if (x < 5) x = 5;
        if (y < 5) y = 5;
        
        menu.style.left = x + 'px';
        menu.style.top = y + 'px';
        this._currentMenu = wrapper;

        var closeHandler = function(e) {
            var isInside = wrapper.contains(e.target);
            if (!isInside) {
                self.hide();
                document.removeEventListener('click', closeHandler);
            }
        };
        setTimeout(function() {
            document.addEventListener('click', closeHandler);
        }, 0);

        var escHandler = function(e) {
            if (e.key === 'Escape') {
                self.hide();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
    }
};

/**
 * Setup right-click context menu for a grid.
 * @param {Object} gridApi - The AG Grid API
 * @param {HTMLElement} gridDiv - The grid container element
 * @param {string} gridId - Grid ID for events
 * @param {Array} customItems - Optional custom menu items
 */
window.PYWRY_AGGRID_SETUP_CONTEXT_MENU = function(gridApi, gridDiv, gridId, customItems) {
    var id = gridId || 'default';
    
    // Detect theme class from grid div
    var themeClass = 'ag-theme-alpine-dark';
    if (gridDiv && gridDiv.className) {
        var classes = gridDiv.className.split(' ');
        for (var i = 0; i < classes.length; i++) {
            if (classes[i].indexOf('ag-theme-') === 0) {
                themeClass = classes[i];
                break;
            }
        }
    }
    window.PYWRY_AGGRID_CONTEXT_MENU.setTheme(themeClass);
    
    gridDiv.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        
        // Update theme each time in case it changed
        if (gridDiv.className) {
            var classes = gridDiv.className.split(' ');
            for (var i = 0; i < classes.length; i++) {
                if (classes[i].indexOf('ag-theme-') === 0) {
                    window.PYWRY_AGGRID_CONTEXT_MENU.setTheme(classes[i]);
                    break;
                }
            }
        }

        var cellInfo = null;
        var target = e.target;

        while (target && target !== gridDiv) {
            if (target.classList && target.classList.contains('ag-cell')) {
                var rowNode = null;
                var colId = target.getAttribute('col-id');
                
                // Try to get row node
                var rowElement = target.closest('.ag-row');
                if (rowElement) {
                    var rowIndex = parseInt(rowElement.getAttribute('row-index'), 10);
                    rowNode = gridApi.getDisplayedRowAtIndex(rowIndex);
                }
                
                cellInfo = {
                    colId: colId,
                    rowNode: rowNode,
                    data: rowNode ? rowNode.data : null,
                    value: target.textContent
                };
                break;
            }
            target = target.parentElement;
        }

        var menuItems = [];

        menuItems.push({
            label: 'Copy',
            icon: 'copy',
            action: function(ctx) {
                if (ctx.value) {
                    navigator.clipboard.writeText(ctx.value).then(function() {
                        console.log('[PyWry] Copied to clipboard');
                    });
                }
            }
        });

        menuItems.push({
            label: 'Copy Row',
            icon: 'copy',
            action: function(ctx) {
                if (ctx.data) {
                    var text = Object.values(ctx.data).join('\t');
                    navigator.clipboard.writeText(text).then(function() {
                        console.log('[PyWry] Row copied to clipboard');
                    });
                }
            }
        });
        
        menuItems.push({ separator: true });

        async function saveWithFilePicker(csvContent, suggestedName) {
            if (window.__TAURI__) {
                try {
                    var dialog = window.__TAURI__.dialog;
                    var fs = window.__TAURI__.fs;
                    var filePath = await dialog.save({
                        defaultPath: suggestedName,
                        filters: [{
                            name: 'CSV Files',
                            extensions: ['csv']
                        }]
                    });
                    
                    if (filePath) {
                        await fs.writeTextFile(filePath, csvContent);
                        console.log('[PyWry] CSV saved via Tauri:', filePath);
                        return true;
                    }
                    return false;
                } catch (err) {
                    console.warn('[PyWry] Tauri file save failed:', err);
                }
            }
            
            // Fallback: Try modern File System Access API (browser)
            // Note: This shows "this site can see edits" warning in non-Tauri contexts
            if (window.showSaveFilePicker) {
                try {
                    var fileHandle = await window.showSaveFilePicker({
                        suggestedName: suggestedName,
                        types: [{
                            description: 'CSV Files',
                            accept: { 'text/csv': ['.csv'] }
                        }]
                    });
                    var writable = await fileHandle.createWritable();
                    await writable.write(csvContent);
                    await writable.close();
                    console.log('[PyWry] CSV saved via file picker');
                    return true;
                } catch (err) {
                    if (err.name !== 'AbortError') {
                        console.warn('[PyWry] File picker failed:', err);
                    }
                    return false;
                }
            }
            return false;
        }

        function emitToPython(csvContent, fileName, exportType) {
            if (window.pywry && window.pywry.emit) {
                window.pywry.emit('grid_export_csv', {
                    gridId: id,
                    fileName: fileName,
                    exportType: exportType,  // 'grid_state' or 'raw'
                    csvContent: csvContent
                });
                console.log('[PyWry] CSV emitted to Python for saving');
                return true;
            }
            return false;
        }

        function downloadCsv(csvContent, fileName) {
            var blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            var url = URL.createObjectURL(blob);
            var link = document.createElement('a');
            link.href = url;
            link.download = fileName;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            console.log('[PyWry] CSV downloaded:', fileName);

            if (window.PYWRY_SHOW_NOTIFICATION) {
                window.PYWRY_SHOW_NOTIFICATION('Downloaded: ' + fileName, 3000, gridDiv);
            }
        }
        

        menuItems.push({
            label: 'Export CSV (Grid State)',
            icon: 'csv',
            action: async function() {
                var csvContent = gridApi.getDataAsCsv({
                    suppressQuotes: true
                });
                var saved = await saveWithFilePicker(csvContent, 'export_filtered.csv');
                if (saved && window.PYWRY_SHOW_NOTIFICATION) {
                    window.PYWRY_SHOW_NOTIFICATION('CSV saved successfully', 3000, gridDiv);
                } else if (!saved) {
                    // In notebooks, emit to Python (Python will show notification); otherwise download
                    if (!emitToPython(csvContent, 'export_filtered.csv', 'grid_state')) {
                        downloadCsv(csvContent, 'export_filtered.csv');
                    }
                }
            }
        });

        menuItems.push({
            label: 'Export CSV (Raw Data)',
            icon: 'csv',
            action: async function() {
                var csvContent = gridApi.getDataAsCsv({
                    allColumns: true,           // Include hidden columns
                    onlySelected: false,        // All rows, not just selected
                    skipColumnGroupHeaders: true,
                    skipRowGroups: true,
                    suppressQuotes: true,       // Don't quote all values
                    // Export all data ignoring filters
                    exportedRows: 'all'         // 'all' = ignore filters, 'filteredAndSorted' = respect filters
                });

                var saved = await saveWithFilePicker(csvContent, 'export_raw.csv');
                if (saved && window.PYWRY_SHOW_NOTIFICATION) {
                    window.PYWRY_SHOW_NOTIFICATION('CSV saved successfully', 3000, gridDiv);
                } else if (!saved) {
                    if (!emitToPython(csvContent, 'export_raw.csv', 'raw')) {
                        downloadCsv(csvContent, 'export_raw.csv');
                    }
                }
            }
        });
        
        menuItems.push({ separator: true });

        if (cellInfo && cellInfo.colId) {
            var clickedCol = gridApi.getColumn ? gridApi.getColumn(cellInfo.colId) : null;
            if (clickedCol) {
                var clickedColDef = clickedCol.getColDef();
                var clickedHeaderName = clickedColDef.headerName || clickedColDef.field || cellInfo.colId;
                var clickedPinned = clickedCol.getPinned();
                

                menuItems.push({
                    label: 'Pin "' + clickedHeaderName + '"',
                    icon: 'pin',
                    submenu: [
                        {
                            label: 'Pin Left',
                            icon: '⬅',
                            checked: clickedPinned === 'left',
                            action: function() {
                                gridApi.setColumnsPinned([cellInfo.colId], 'left');
                            }
                        },
                        {
                            label: 'Pin Right',
                            icon: '➡',
                            checked: clickedPinned === 'right',
                            action: function() {
                                gridApi.setColumnsPinned([cellInfo.colId], 'right');
                            }
                        },
                        {
                            label: 'No Pin',
                            icon: '⊘',
                            checked: clickedPinned === null,
                            action: function() {
                                gridApi.setColumnsPinned([cellInfo.colId], null);
                            }
                        }
                    ]
                });
                
                menuItems.push({
                    label: 'Hide "' + clickedHeaderName + '"',
                    icon: 'eye-slash',
                    action: function() {
                        gridApi.setColumnsVisible([cellInfo.colId], false);
                    }
                });
                
                menuItems.push({ separator: true });
            }
        }
        
        var allColumns = gridApi.getColumns ? gridApi.getColumns() : [];
        if (allColumns.length > 0) {
            var columnSubmenuItems = [];

            columnSubmenuItems.push({
                label: 'Show All',
                icon: 'eye',
                action: function() {
                    var colIds = allColumns.map(function(c) { return c.getColId(); });
                    gridApi.setColumnsVisible(colIds, true);
                }
            });
            
            columnSubmenuItems.push({ separator: true });
            allColumns.forEach(function(col) {
                var colDef = col.getColDef();
                var colId = col.getColId();
                var headerName = colDef.headerName || colDef.field || colId;
                var isVisible = col.isVisible();
                
                columnSubmenuItems.push({
                    label: headerName,
                    checked: isVisible,
                    action: function() {
                        gridApi.setColumnsVisible([colId], !isVisible);
                    }
                });
            });
            
            menuItems.push({
                label: 'Columns',
                icon: 'columns',
                submenu: columnSubmenuItems
            });
        }
        
        menuItems.push({
            label: 'Reset Columns',
            icon: 'columns',
            action: function() {
                gridApi.resetColumnState();
                console.log('[PyWry] Columns reset');
            }
        });
        
        menuItems.push({
            label: 'Auto-size Columns',
            icon: 'columns',
            action: function() {
                gridApi.autoSizeAllColumns();
                console.log('[PyWry] Columns auto-sized');
            }
        });
        
        menuItems.push({ separator: true });
        
        menuItems.push({
            label: 'Clear All Filters',
            icon: 'filter',
            action: function() {
                gridApi.setFilterModel(null);
                console.log('[PyWry] All filters cleared');
            }
        });
        
        if (customItems && customItems.length > 0) {
            menuItems.push({ separator: true });
            customItems.forEach(function(item) {
                menuItems.push({
                    label: item.label,
                    icon: item.icon,
                    action: function(ctx) {
                        if (window.pywry && window.pywry.emit) {
                            window.pywry.emit(item.event || 'context_menu_action', {
                                gridId: id,
                                action: item.event || item.label,
                                cellInfo: ctx
                            });
                        }
                    }
                });
            });
        }
        
        window.PYWRY_AGGRID_CONTEXT_MENU.show(e.clientX, e.clientY, menuItems, cellInfo || {}, gridDiv);
    });
    
    console.log('[PyWry AG Grid ' + id + '] Context menu enabled');
};

console.log('[PyWry] AG Grid defaults loaded');
