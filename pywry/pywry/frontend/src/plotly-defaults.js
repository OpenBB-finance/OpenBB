/* PyWry Plotly Defaults & Registry */

// Registry for all Plotly charts on the page
if (!window.__PYWRY_CHARTS__) {
    window.__PYWRY_CHARTS__ = {};
}

/**
 * Register a Plotly chart instance with PyWry.
 * @param {string} chartId - The unique ID for this chart.
 * @param {object} plotDiv - The DOM element containing the Plotly chart.
 * @param {object} bridge - The PyWry event bridge (optional, will look for window.pywry).
 */
function registerPyWryChart(chartId, plotDiv, bridge) {
    console.log('[PyWry Plotly] Registering chart:', chartId);
    window.__PYWRY_CHARTS__[chartId] = plotDiv;

    const pywry = bridge || window.pywry;
    if (!pywry) {
        console.warn('[PyWry Plotly] No bridge found for chart:', chartId);
        return;
    }

    // Attach basic event handlers
    if (plotDiv.on) {
        // Click
        plotDiv.on('plotly_click', (data) => {
            pywry.emit('plotly:click', {
                widget_type: 'chart',
                points: (data.points || []).map(p => ({
                    curveNumber: p.curveNumber,
                    pointNumber: p.pointNumber,
                    x: p.x,
                    y: p.y,
                    text: p.text,
                    data: p.data,
                    trace_name: p.data.name
                })),
                event: data.event,
                chartId: chartId
            });
        });

        // Hover
        plotDiv.on('plotly_hover', (data) => {
            pywry.emit('plotly:hover', {
                widget_type: 'chart',
                points: (data.points || []).map(p => ({
                    curveNumber: p.curveNumber,
                    pointNumber: p.pointNumber,
                    x: p.x,
                    y: p.y
                })),
                chartId: chartId
            });
        });

        // Selected
        plotDiv.on('plotly_selected', (data) => {
            if (!data) {
                pywry.emit('plotly:selected', { widget_type: 'chart', points: [], chartId: chartId });
                return;
            }
            pywry.emit('plotly:selected', {
                widget_type: 'chart',
                points: (data.points || []).map(p => ({
                    curveNumber: p.curveNumber,
                    pointNumber: p.pointNumber,
                    x: p.x,
                    y: p.y
                })),
                range: data.range,
                lassoPoints: data.lassoPoints,
                chartId: chartId
            });
        });

        // Relayout
        plotDiv.on('plotly_relayout', (data) => {
            pywry.emit('plotly:relayout', {
                widget_type: 'chart',
                layout: data,
                chartId: chartId
            });
        });
    }
}

// Expose globally
window.registerPyWryChart = registerPyWryChart;
