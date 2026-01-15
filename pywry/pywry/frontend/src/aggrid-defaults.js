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
    // Note: menuTabs removed - requires AG Grid Enterprise
    filterParams: {
        buttons: ['apply', 'clear', 'reset'],
        closeOnApply: true,
        maxNumConditions: 10,
    },
};

/**
 * Format numbers intelligently:
 * - Large integers with trailing zeros → K/M/B (75000 → "75K")
 * - Large integers without trailing zeros → commas (75123 → "75,123")
 * - Small decimals (< 1) → preserve full precision, no truncation
 * - Very small numbers (many leading zeros) → scientific notation
 * - Regular decimals → preserve full precision
 * 
 * @param {number} value - The number to format
 * @returns {string} Formatted number string
 */
window.PYWRY_FORMAT_NUMBER = function(value) {
    if (value == null || isNaN(value)) return '';
    
    var absValue = Math.abs(value);
    
    // Very small numbers (with many leading zeros after decimal) → scientific notation
    // e.g., 0.00000123 → "1.23e-6"
    if (absValue > 0 && absValue < 0.0001) {
        return value.toExponential();
    }
    
    // Small decimals (< 1) or any non-integer → preserve full precision
    if (!Number.isInteger(value)) {
        // Convert to string to preserve all significant digits
        // JavaScript's toString() preserves precision better than toLocaleString for decimals
        var str = value.toString();
        // If it's a reasonable length, return as-is
        if (str.length <= 20) {
            return str;
        }
        // For very long decimals, use toPrecision
        return value.toPrecision(15).replace(/\.?0+$/, '');
    }
    
    // From here, we're dealing with integers only
    var sign = value < 0 ? '-' : '';
    
    // Billions (1,000,000,000+)
    if (absValue >= 1e9) {
        // Only abbreviate if cleanly divisible (trailing zeros)
        if (absValue % 1e8 === 0) {
            var billions = absValue / 1e9;
            return sign + (billions % 1 === 0 ? billions.toFixed(0) : billions.toFixed(1)) + 'B';
        }
    }
    
    // Millions (1,000,000+)
    if (absValue >= 1e6) {
        if (absValue % 1e5 === 0) {
            var millions = absValue / 1e6;
            return sign + (millions % 1 === 0 ? millions.toFixed(0) : millions.toFixed(1)) + 'M';
        }
    }
    
    // Thousands (10,000+) - only abbreviate if cleanly divisible
    if (absValue >= 1e4) {
        if (absValue % 1e3 === 0) {
            return sign + (absValue / 1e3).toFixed(0) + 'K';
        }
        // For numbers like 75,500 -> 75.5K (divisible by 100)
        if (absValue % 100 === 0) {
            var thousands = absValue / 1e3;
            return sign + thousands.toFixed(1).replace(/\.0$/, '') + 'K';
        }
    }
    
    // Default for integers: use locale string for comma separators
    return value.toLocaleString();
};

/**
 * Process column definitions to convert string expressions to functions.
 * AG Grid requires valueGetter, valueFormatter, etc. to be functions.
 * 
 * @param {Array} columnDefs - Array of column definitions
 * @returns {Array} Processed column definitions with functions
 */
window.PYWRY_AGGRID_PROCESS_COLUMN_DEFS = function(columnDefs) {
    if (!columnDefs || !Array.isArray(columnDefs)) return columnDefs;
    
    console.log('[PyWry AG Grid] Processing', columnDefs.length, 'column defs');
    
    return columnDefs.map(function(colDef) {
        var processed = Object.assign({}, colDef);
        
        // Remove undefined cellDataType to avoid AG Grid warning
        if (processed.cellDataType === undefined || processed.cellDataType === null) {
            delete processed.cellDataType;
        }
        
        // Convert valueGetter string to function
        // Expression can use: params, data, node, colDef, column, api, columnApi, context
        if (typeof processed.valueGetter === 'string') {
            var getterExpr = processed.valueGetter;
            console.log('[PyWry AG Grid] Converting valueGetter:', getterExpr);
            processed.valueGetter = function(params) {
                try {
                    var data = params.data;
                    var node = params.node;
                    var colDef = params.colDef;
                    var column = params.column;
                    var api = params.api;
                    var context = params.context;
                    // Guard against undefined data (can happen during initial render)
                    if (!data) return null;
                    return eval(getterExpr);
                } catch (e) {
                    console.error('[PyWry AG Grid] valueGetter error:', e, 'Expression:', getterExpr, 'Data:', params.data);
                    return null;
                }
            };
        }
        
        // Convert valueFormatter string to function
        // Expression can use: value, data, node, colDef, column, api, context
        if (typeof processed.valueFormatter === 'string') {
            var formatterExpr = processed.valueFormatter;
            processed.valueFormatter = function(params) {
                try {
                    var value = params.value;
                    var data = params.data;
                    var node = params.node;
                    var colDef = params.colDef;
                    var column = params.column;
                    var api = params.api;
                    var context = params.context;
                    if (value === null || value === undefined) return '';
                    return eval(formatterExpr);
                } catch (e) {
                    console.error('[PyWry AG Grid] valueFormatter error:', e, 'Expression:', formatterExpr, 'Value:', params.value);
                    return String(params.value);
                }
            };
        }
        
        // Auto-apply number formatter for number columns without custom formatter
        // This formats large numbers as 75K, 1.5M, etc.
        if (!processed.valueFormatter && processed.cellDataType === 'number') {
            processed.valueFormatter = function(params) {
                if (params.value === null || params.value === undefined) return '';
                return window.PYWRY_FORMAT_NUMBER(params.value);
            };
        }
        
        // Convert valueSetter string to function
        if (typeof processed.valueSetter === 'string') {
            var setterExpr = processed.valueSetter;
            processed.valueSetter = function(params) {
                try {
                    var newValue = params.newValue;
                    var oldValue = params.oldValue;
                    var data = params.data;
                    var node = params.node;
                    return eval(setterExpr);
                } catch (e) {
                    console.error('[PyWry AG Grid] valueSetter error:', e);
                    return false;
                }
            };
        }
        
        // Recursively process children (for column groups)
        if (processed.children && Array.isArray(processed.children)) {
            processed.children = window.PYWRY_AGGRID_PROCESS_COLUMN_DEFS(processed.children);
        }
        
        return processed;
    });
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
    
    // Determine row count for pagination decisions
    var rowCount = (config.rowData && config.rowData.length) || 0;
    
    // Server-side mode: data stays in Python, JS only has metadata
    // Used when dataset is too large for browser memory
    // Enables filtering/sorting on full dataset even when truncated
    var serverSideConfig = config.serverSide;
    var isServerSide = serverSideConfig && typeof serverSideConfig === 'object';
    
    if (isServerSide) {
        var totalRows = serverSideConfig.totalRows || 0;
        console.info('[PyWry AG Grid ' + id + '] Using Server-Side filtering for ' + 
            totalRows.toLocaleString() + ' rows (data in Python memory)');
        return window.PYWRY_AGGRID_BUILD_SERVER_SIDE_OPTIONS(config, id, serverSideConfig);
    }
    
    // Browser memory limit - AG Grid renders fine but data must fit in memory
    var MAX_SAFE_ROWS = 100000;  // 100k rows
    
    // Handle large datasets - truncate to protect browser memory
    var rowData = config.rowData;
    var truncatedRows = 0;
    
    if (rowCount > MAX_SAFE_ROWS) {
        console.warn('[PyWry AG Grid ' + id + '] Dataset has ' + rowCount + 
            ' rows, truncating to ' + MAX_SAFE_ROWS + ' to prevent browser memory issues. ' +
            'Use server_side=True for full filtering capability.');
        rowData = config.rowData.slice(0, MAX_SAFE_ROWS);
        truncatedRows = rowCount - MAX_SAFE_ROWS;
        rowCount = MAX_SAFE_ROWS;
    }
    
    // Standard client-side row model with pagination
    return window.PYWRY_AGGRID_BUILD_CLIENT_OPTIONS(config, id, rowData, rowCount, truncatedRows);
};

/**
 * Build options for standard client-side row model.
 * Best for datasets under 100K rows.
 */
window.PYWRY_AGGRID_BUILD_CLIENT_OPTIONS = function(config, id, rowData, rowCount, truncatedRows) {
    var LARGE_DATASET_THRESHOLD = 10000;
    
    // Pagination logic:
    // - If config.pagination === true: always enable
    // - If config.pagination === false: always disable  
    // - If config.pagination is undefined/null: auto-enable for >10 rows
    var usePagination;
    if (config.pagination === true) {
        usePagination = true;
    } else if (config.pagination === false) {
        usePagination = false;
    } else {
        // Auto-decide: enable for datasets > 10 rows
        usePagination = rowCount > 10;
    }
    
    // For large datasets, adjust page size selector to prevent loading too many rows at once
    var pageSizeSelector;
    if (rowCount > LARGE_DATASET_THRESHOLD) {
        // Limit max visible rows for large datasets
        pageSizeSelector = [25, 50, 100, 250, 500];
    } else if (rowCount > 1000) {
        // Medium datasets get full range
        pageSizeSelector = [10, 25, 50, 100, 250, 500, 1000];
    } else {
        // Small datasets - include "All" option
        pageSizeSelector = [10, 25, 50, 100, rowCount];
    }
    
    // Default page size based on dataset size
    var defaultPageSize = config.paginationPageSize || 100;
    
    // Process column defs to convert string expressions to functions
    var processedColumnDefs = window.PYWRY_AGGRID_PROCESS_COLUMN_DEFS(config.columnDefs);
    
    var options = {
        columnDefs: processedColumnDefs,
        rowData: rowData,
        // AG Grid v32.2+: rowSelection is now an object
        rowSelection: config.rowSelection || { mode: 'multiRow', enableClickSelection: false },
        pagination: usePagination,
        paginationPageSize: defaultPageSize,
        paginationPageSizeSelector: pageSizeSelector,
        domLayout: config.domLayout || 'normal',
        defaultColDef: Object.assign({}, window.PYWRY_AGGRID_DEFAULT_COL_DEF, config.defaultColDef || {}),
        // Override AG Grid's default number formatter to use our K/M/B formatting
        dataTypeDefinitions: {
            number: {
                baseDataType: 'number',
                valueFormatter: function(params) {
                    if (params.value === null || params.value === undefined) return '';
                    return window.PYWRY_FORMAT_NUMBER(params.value);
                }
            }
        },
        columnMenu: 'new',
        suppressMenuHide: true,
        ensureDomOrder: true,
        // Row spanning support (AG Grid v32+)
        enableCellSpan: config.enableCellSpan || false,

        onCellClicked: function(event) {
            // Select the row on cell click (works with row selection enabled)
            if (event.node && config.rowSelection !== false) {
                event.node.setSelected(true, true);  // select this row, clear others
            }
            
            if (window.pywry && window.pywry.emit) {
                // Emit standard event (grid:cell_click)
                window.pywry.emit('grid:cell_click', {
                    widget_type: 'grid',
                    gridId: id,
                    rowIndex: event.rowIndex,
                    colId: event.column.getColId(),
                    value: event.value,
                    data: event.data
                });
                // Emit short event for convenience
                window.pywry.emit('cell_click', {
                    widget_type: 'grid',
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
                 window.pywry.emit('grid:row_selected', { widget_type: 'grid', gridId: id, rows: selectedRows });
                 window.pywry.emit('row_selected', { widget_type: 'grid', gridId: id, rows: selectedRows });
            }
        },
        onGridReady: function(event) {
            console.log('[PyWry AG Grid ' + id + '] Grid ready (client-side)!');
            event.api.autoSizeAllColumns();
            if (truncatedRows > 0 && window.pywry && window.pywry.emit) {
                window.pywry.emit('data_truncated', {
                    widget_type: 'grid',
                    gridId: id,
                    displayedRows: rowCount,
                    truncatedRows: truncatedRows,
                    message: 'Dataset truncated: showing ' + rowCount.toLocaleString() + 
                             ' of ' + (rowCount + truncatedRows).toLocaleString() + ' rows'
                });
            }
        }
    };
    
    console.log('[PyWry AG Grid ' + id + '] Built client-side options');
    return options;
};

/**
 * Build options for Server-Side IPC Row Model.
 * Data stays in Python, JS only has metadata. Python handles sort/filter.
 * Uses Infinite Row Model with virtual scrolling (no pagination UI).
 * 
 * Config: { serverSide: { totalRows: N, blockSize: 100, ... }, columnDefs: [...] }
 * 
 * Events:
 * - JS emits 'grid:request_page' with { gridId, startRow, endRow, sortModel, filterModel }
 * - Python responds via 'grid:page_response' with { gridId, rows, totalRows, isLastPage }
 * 
 * @param {Object} config - Grid configuration
 * @param {string} id - Grid ID
 * @param {Object} serverConfig - Server-side config { totalRows, blockSize, ... }
 */
window.PYWRY_AGGRID_BUILD_SERVER_SIDE_OPTIONS = function(config, id, serverConfig) {
    var totalRows = serverConfig.totalRows || 0;
    var blockSize = serverConfig.blockSize || 500;  // Rows per block for infinite scroll
    var currentFilteredTotal = totalRows;
    
    // Pending requests
    var pendingRequests = {};
    var requestCounter = 0;
    
    // Store grid API for later use
    var gridApiRef = null;
    
    // Set up listener for page responses from Python
    if (window.pywry && window.pywry.on) {
        window.pywry.on('grid:page_response', function(response) {
            if (response.gridId !== id) return;
            
            var requestId = response.requestId;
            var pending = pendingRequests[requestId];
            
            if (pending) {
                delete pendingRequests[requestId];
                
                if (response.error) {
                    console.error('[PyWry AG Grid ' + id + '] Error fetching data:', response.error);
                    pending.failCallback();
                } else {
                    // Update total if filtered
                    if (response.totalRows !== undefined) {
                        currentFilteredTotal = response.totalRows;
                    }
                    
                    // lastRow tells grid total size (-1 = unknown/more data)
                    var lastRow = response.isLastPage ? currentFilteredTotal : -1;
                    pending.successCallback(response.rows, lastRow);
                }
            }
        });
    }
    
    // Datasource that requests data blocks from Python
    var datasource = {
        getRows: function(params) {
            var requestId = 'req_' + (++requestCounter);
            var startRow = params.startRow;
            var endRow = params.endRow;
            
            console.log('[PyWry AG Grid ' + id + '] Requesting rows ' + startRow + '-' + endRow);
            
            // Store callbacks
            pendingRequests[requestId] = {
                successCallback: params.successCallback,
                failCallback: params.failCallback
            };
            
            // Request from Python with sort/filter state
            if (window.pywry && window.pywry.emit) {
                window.pywry.emit('grid:request_page', {
                    gridId: id,
                    requestId: requestId,
                    startRow: startRow,
                    endRow: endRow,
                    sortModel: params.sortModel || [],
                    filterModel: params.filterModel || {}
                });
            } else {
                console.error('[PyWry AG Grid ' + id + '] pywry.emit not available!');
                params.failCallback();
                delete pendingRequests[requestId];
            }
            
            // Timeout fallback
            setTimeout(function() {
                if (pendingRequests[requestId]) {
                    console.warn('[PyWry AG Grid ' + id + '] Request ' + requestId + ' timed out');
                    delete pendingRequests[requestId];
                    params.failCallback();
                }
            }, 30000);
        }
    };
    
    // Process column defs to convert string expressions to functions
    var processedColumnDefs = window.PYWRY_AGGRID_PROCESS_COLUMN_DEFS(config.columnDefs);
    
    var options = {
        columnDefs: processedColumnDefs,
        rowModelType: 'infinite',
        datasource: datasource,
        cacheBlockSize: blockSize,
        cacheOverflowSize: 2,
        maxConcurrentDatasourceRequests: 1,
        maxBlocksInCache: 20,
        infiniteInitialRowCount: Math.min(blockSize, totalRows),
        
        // NO pagination - use infinite scroll only
        // AG Grid's pagination UI doesn't work properly with infinite row model
        pagination: false,
        
        // AG Grid v32.2+: rowSelection is now an object
        rowSelection: config.rowSelection || { mode: 'multiRow', enableClickSelection: false },
        domLayout: config.domLayout || 'normal',
        defaultColDef: Object.assign({}, window.PYWRY_AGGRID_DEFAULT_COL_DEF, config.defaultColDef || {}),
        // Override AG Grid's default number formatter to use our K/M/B formatting
        dataTypeDefinitions: {
            number: {
                baseDataType: 'number',
                valueFormatter: function(params) {
                    if (params.value === null || params.value === undefined) return '';
                    return window.PYWRY_FORMAT_NUMBER(params.value);
                }
            }
        },
        columnMenu: 'new',
        suppressMenuHide: true,
        enableCellTextSelection: true,
        ensureDomOrder: true,
        
        // Row ID for selection persistence
        getRowId: function(params) {
            return params.data && params.data.__rowId !== undefined 
                ? String(params.data.__rowId) 
                : (params.data && params.data.id !== undefined 
                    ? String(params.data.id) 
                    : String(params.rowIndex));
        },

        onCellClicked: function(event) {
            // Select the row on cell click (works with row selection enabled)
            if (event.node && config.rowSelection !== false) {
                event.node.setSelected(true, true);
            }
            
            if (window.pywry && window.pywry.emit) {
                // Emit standard event (grid:cell_click)
                window.pywry.emit('grid:cell_click', {
                    widget_type: 'grid',
                    gridId: id,
                    rowIndex: event.rowIndex,
                    colId: event.column.getColId(),
                    value: event.value,
                    data: event.data
                });
                // Short event for convenience
                window.pywry.emit('cell_click', {
                    widget_type: 'grid',
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
                window.pywry.emit('grid:row_selected', { widget_type: 'grid', gridId: id, rows: selectedRows });
                window.pywry.emit('row_selected', { widget_type: 'grid', gridId: id, rows: selectedRows });
            }
        },
        
        onSortChanged: function(event) {
            console.log('[PyWry AG Grid ' + id + '] Sort changed, refreshing...');
            // Infinite model handles this automatically via datasource
        },
        
        // When filter changes, need to refresh data from Python
        onFilterChanged: function(event) {
            console.log('[PyWry AG Grid ' + id + '] Filter changed, refreshing...');
            // The datasource.getRows will be called automatically
            // We also notify Python of the filter change
            if (window.pywry && window.pywry.emit && gridApiRef) {
                window.pywry.emit('grid:filter_changed', {
                    widget_type: 'grid',
                    gridId: id,
                    filterModel: gridApiRef.getFilterModel()
                });
            }
        },
        
        onGridReady: function(event) {
            gridApiRef = event.api;
            
            console.log('[PyWry AG Grid ' + id + '] Grid ready (server-side IPC)!');
            console.log('[PyWry AG Grid ' + id + '] Total rows: ' + totalRows.toLocaleString() + 
                ', block size: ' + blockSize);
            
            // Auto-size columns after first block loads
            setTimeout(function() {
                event.api.autoSizeAllColumns();
            }, 100);
            
            if (window.pywry && window.pywry.emit) {
                window.pywry.emit('grid_mode', {
                    widget_type: 'grid',
                    gridId: id,
                    mode: 'server-side',
                    serverSide: true,
                    totalRows: totalRows,
                    blockSize: blockSize,
                    message: 'Data in Python memory (' + totalRows.toLocaleString() + 
                        ' rows). Use filters to narrow down results.'
                });
            }
        }
    };
    
    console.log('[PyWry AG Grid ' + id + '] Built server-side options for ' + 
        totalRows.toLocaleString() + ' rows (block size: ' + blockSize + ')');
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

    // Handle explicit state request from Python (grid:request_state)
    window.pywry.on('grid:request_state', function(data) {
        if (data && (!data.gridId || data.gridId === id)) {
            var state = saveColumnState();
            if (state) {
                state.gridId = id;
                // Include any request correlation data
                if (data.requestId) state.requestId = data.requestId;
                if (data.context) state.context = data.context;
                window.pywry.emit('grid:state_response', state);
                console.log('[PyWry AG Grid ' + id + '] State sent to Python');
            }
        }
    });

    // --- Unified Grid State Listeners (grid: namespace) ---

    window.pywry.on('grid:update_cell', function(data) {
        if (data && (!data.gridId || data.gridId === id)) {
            var rowId = data.rowId; // Can be ID or Index
            var colId = data.colId;
            var value = data.value;
            
            if (colId != null) {
                 var rowNode;
                 // Try index if numeric
                 if (typeof rowId === 'number') {
                     rowNode = gridApi.getDisplayedRowAtIndex(rowId);
                 }
                 // Try ID if not found or not number
                 if (!rowNode && rowId != null) {
                     rowNode = gridApi.getRowNode(String(rowId));
                 }

                if (rowNode) {
                    rowNode.setDataValue(colId, value);
                    console.log('[PyWry AG Grid ' + id + '] Cell updated: row=' + rowId + ', col=' + colId + ', value=' + value);
                } else {
                    console.warn('[PyWry AG Grid ' + id + '] Row not found for update: ' + rowId);
                }
            }
        }
    });

    window.pywry.on('grid:update_data', function(data) {
        if (data && data.data && (!data.gridId || data.gridId === id)) {
            if (data.strategy === 'append') {
                gridApi.applyTransaction({ add: data.data });
            } else if (data.strategy === 'update') {
                gridApi.applyTransaction({ update: data.data });
            } else {
                // Default: set
                gridApi.setGridOption('rowData', data.data);
            }
            console.log('[PyWry AG Grid ' + id + '] Data updated (' + (data.strategy || 'set') +'):', data.data.length, 'rows');
        }
    });

    window.pywry.on('grid:update_columns', function(data) {
        if (data && data.columnDefs && (!data.gridId || data.gridId === id)) {
            var savedState = saveColumnState();
            var processedCols = window.PYWRY_AGGRID_PROCESS_COLUMN_DEFS(data.columnDefs);
            gridApi.setGridOption('columnDefs', processedCols);
            // Try to restore state if structure matches
            setTimeout(function() { restoreColumnState(savedState); }, 0);
            console.log('[PyWry AG Grid ' + id + '] Columns updated:', data.columnDefs.length, 'columns');
        }
    });

    // Combined update for view switching: updates data, columns, and restores state in one operation
    window.pywry.on('grid:update_grid', function(data) {
        if (data && (!data.gridId || data.gridId === id)) {
            var columnDefs = data.columnDefs;
            var rowData = data.data;  // Python sends 'data', also check 'rows' for compat
            var stateToApply = data.restoreState;
            
            console.log('[PyWry AG Grid ' + id + '] grid:update_grid received');
            console.log('  has columnDefs:', !!columnDefs, columnDefs ? columnDefs.length : 0);
            console.log('  has data:', !!rowData, rowData ? rowData.length : 0);
            console.log('  has restoreState:', !!stateToApply);
            
            // Update columns first
            if (columnDefs) {
                var processedCols = window.PYWRY_AGGRID_PROCESS_COLUMN_DEFS(columnDefs);
                gridApi.setGridOption('columnDefs', processedCols);
                console.log('[PyWry AG Grid ' + id + '] Set columnDefs');
            }
            
            // Update row data
            if (rowData) {
                gridApi.setGridOption('rowData', rowData);
                console.log('[PyWry AG Grid ' + id + '] Set rowData:', rowData.length, 'rows');
            }
            
            // Apply column state AFTER setting columnDefs (AG Grid needs this for column order)
            if (stateToApply && stateToApply.columnState) {
                // Use setTimeout to ensure columnDefs are applied first
                setTimeout(function() {
                    console.log('[PyWry AG Grid ' + id + '] Applying columnState:', stateToApply.columnState.map(function(c) { return c.colId; }));
                    if (gridApi.applyColumnState) {
                        gridApi.applyColumnState({
                            state: stateToApply.columnState,
                            applyOrder: true
                        });
                        console.log('[PyWry AG Grid ' + id + '] applyColumnState done');
                    }
                    if (stateToApply.filterModel && gridApi.setFilterModel) {
                        gridApi.setFilterModel(stateToApply.filterModel);
                    }
                }, 0);
            }
            
            console.log('[PyWry AG Grid ' + id + '] Grid fully updated');
        }
    });

    window.pywry.on('grid:restore_state', function(data) {
        if (data && data.state && (!data.gridId || data.gridId === id)) {
            restoreColumnState(data.state);
            console.log('[PyWry AG Grid ' + id + '] State restored');
        }
    });

    window.pywry.on('grid:reset_state', function(data) {
        if (!data || !data.gridId || data.gridId === id) {
            if (data && data.hard) {
                // Hard reset: completely reset all state
                gridApi.resetColumnState();
                gridApi.setFilterModel(null);
                if (gridApi.setSortModel) gridApi.setSortModel(null);
            } else {
                // Soft reset: just clear filters and sort
                gridApi.setFilterModel(null);
                if (gridApi.setSortModel) gridApi.setSortModel(null);
            }
            console.log('[PyWry AG Grid ' + id + '] State reset (hard=' + (data && data.hard) + ')');
        }
    });

    window.pywry.on('grid:update_theme', function(data) {
        if (data && data.theme && (!data.gridId || data.gridId === id) && gridDiv) {
            var classes = gridDiv.className.split(' ').filter(function(c) {
                return !c.startsWith('ag-theme-');
            });
            classes.push(data.theme);
            gridDiv.className = classes.join(' ');
            console.log('[PyWry AG Grid ' + id + '] Theme updated to:', data.theme);
        }
    });

    window.pywry.on('grid:show_notification', function(data) {
        if (!data.gridId || data.gridId === id) {
            window.PYWRY_SHOW_NOTIFICATION(data.message, data.duration, gridDiv);
        }
    });

    console.log('[PyWry AG Grid ' + id + '] Event listeners registered');

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
        // Use position:absolute - will be positioned relative to container
        var styles = [
            'position: absolute',
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

        var textPart = document.createElement('span');
        textPart.className = 'ag-menu-option-part ag-menu-option-text pywry-menu-text';
        textPart.textContent = item.label;
        textPart.style.cssText = 'flex: 1;';
        option.appendChild(textPart);
        var pointerPart = document.createElement('span');
        pointerPart.className = 'ag-menu-option-part ag-menu-option-popup-pointer pywry-menu-pointer';
        pointerPart.style.cssText = 'width: 16px; text-align: right; flex-shrink: 0; opacity: 0.6;';
        if (item.submenu && item.submenu.length > 0) {
            pointerPart.textContent = '>';
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
        list.style.cssText = 'padding: 4px 0;';
        
        items.forEach(function(item) {
            var menuItem = self._createMenuItem(item, context, submenu);
            list.appendChild(menuItem);
        });
        
        submenu.appendChild(list);

        // Append to wrapper (which is inside the widget container)
        if (this._currentMenu) {
            this._currentMenu.appendChild(submenu);
        } else {
            document.body.appendChild(submenu);
        }

        // Use stored container bounds for positioning
        var containerRect = this._containerRect;
        if (!containerRect && this._container) {
            containerRect = this._container.getBoundingClientRect();
        }
        if (!containerRect) {
            containerRect = { left: 0, top: 0, width: window.innerWidth, height: window.innerHeight };
        }
        
        var subRect = submenu.getBoundingClientRect();
        var parentRect = parentMenu ? parentMenu.getBoundingClientRect() : { left: x, right: x, top: y };

        // Convert to container-relative coordinates
        var parentRelLeft = parentRect.left - containerRect.left;
        var parentRelRight = parentRect.right - containerRect.left;
        var relY = y - containerRect.top;
        
        var containerWidth = containerRect.width;
        var containerHeight = containerRect.height;
        
        // Calculate available space within container
        var spaceRight = containerWidth - parentRelRight;
        var spaceLeft = parentRelLeft;
        var spaceBelow = containerHeight - relY;
        var spaceAbove = relY;
        
        // Constrain height if needed
        var availableHeight = Math.max(spaceBelow, spaceAbove) - 10;
        if (subRect.height > availableHeight && availableHeight > 100) {
            list.style.maxHeight = availableHeight + 'px';
            list.style.overflowY = 'auto';
            subRect = submenu.getBoundingClientRect();
        }

        // Position horizontally within container
        var finalX;
        if (spaceRight >= subRect.width) {
            finalX = parentRelRight - 4;
        } else if (spaceLeft >= subRect.width) {
            finalX = parentRelLeft - subRect.width + 4;
        } else {
            finalX = containerWidth - subRect.width - 5;
        }
        finalX = Math.max(5, finalX);

        // Position vertically within container
        var finalY = relY;
        if (finalY + subRect.height > containerHeight - 5) {
            finalY = containerHeight - subRect.height - 5;
        }
        finalY = Math.max(5, finalY);
        
        submenu.style.left = finalX + 'px';
        submenu.style.top = finalY + 'px';
        this._activeSubmenus.push(submenu);
        submenu.addEventListener('mouseenter', function() {
            // Don't hide
        });
        
        return submenu;
    },
    
    /**
     * Show context menu at position
     * @param {number} x - X coordinate (clientX from event)
     * @param {number} y - Y coordinate (clientY from event)
     * @param {Array} items - Menu items [{label, icon?, action?, disabled?, separator?, submenu?}]
     * @param {Object} context - Context object passed to action callbacks
     * @param {HTMLElement} container - Container element (grid div) for positioning
     */
    show: function(x, y, items, context, container) {
        this.hide();
        var self = this;
        
        // Find the pywry-widget container for proper positioning
        var widgetContainer = container;
        while (widgetContainer && !widgetContainer.classList.contains('pywry-widget')) {
            widgetContainer = widgetContainer.parentElement;
        }
        // Fallback to the grid container if no pywry-widget found
        if (!widgetContainer) {
            widgetContainer = container;
        }
        
        // Ensure container has position for absolute children
        var containerStyle = window.getComputedStyle(widgetContainer);
        if (containerStyle.position === 'static') {
            widgetContainer.style.position = 'relative';
        }
        
        // Get container bounds
        var containerRect = widgetContainer.getBoundingClientRect();
        
        // Convert click coordinates to container-relative
        var relX = x - containerRect.left;
        var relY = y - containerRect.top;
        
        // Create wrapper inside the widget container
        var wrapper = document.createElement('div');
        wrapper.className = 'pywry-context-menu-wrapper ' + this._themeClass;
        wrapper.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;z-index:2147483647;pointer-events:none;overflow:visible;';
        
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
        widgetContainer.appendChild(wrapper);
        
        // Store reference for positioning submenus
        this._container = widgetContainer;
        this._containerRect = containerRect;
        
        // Set padding first, measure natural height
        list.style.cssText = 'padding: 4px 0;';
        var menuRect = menu.getBoundingClientRect();
        var menuWidth = menuRect.width;
        var menuHeight = menuRect.height;
        
        // Available space within container from click point
        var containerWidth = containerRect.width;
        var containerHeight = containerRect.height;
        var spaceBelow = containerHeight - relY;
        var spaceAbove = relY;
        var spaceRight = containerWidth - relX;
        var spaceLeft = relX;
        
        // Determine if we need to constrain height and add scrolling
        var preferBelow = spaceBelow >= spaceAbove;
        var availableHeight = preferBelow ? spaceBelow : spaceAbove;
        var maxMenuHeight = availableHeight - 10;
        
        if (menuHeight > maxMenuHeight && maxMenuHeight > 100) {
            list.style.maxHeight = maxMenuHeight + 'px';
            list.style.overflowY = 'auto';
            menuRect = menu.getBoundingClientRect();
            menuHeight = menuRect.height;
        }

        // Position vertically within container
        var finalY;
        if (preferBelow) {
            finalY = relY;
            if (finalY + menuHeight > containerHeight - 5) {
                finalY = containerHeight - menuHeight - 5;
            }
        } else {
            finalY = relY - menuHeight;
        }
        finalY = Math.max(5, Math.min(finalY, containerHeight - menuHeight - 5));
        
        // Position horizontally within container
        var finalX;
        if (relX + menuWidth <= containerWidth - 5) {
            finalX = relX;
        } else if (spaceLeft >= menuWidth) {
            finalX = relX - menuWidth;
        } else {
            finalX = containerWidth - menuWidth - 5;
        }
        finalX = Math.max(5, finalX);
        
        menu.style.left = finalX + 'px';
        menu.style.top = finalY + 'px';
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
