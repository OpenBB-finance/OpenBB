let globals = { dark_mode: false };

TITLE_DIV = undefined;
TEXT_DIV = undefined;
CSV_DIV = undefined;

let check_divs = setInterval(function () {
    let div_ids = ['popup_title', 'popup_text', 'popup_csv'];
    let divs = div_ids.map(function (id) {
        return document.getElementById(id);
    });

    if (
        divs.every(function (div) {
            return div != null;
        })
    ) {
        TITLE_DIV = document.getElementById('popup_title');
        TEXT_DIV = document.getElementById('popup_text');
        CSV_DIV = document.getElementById('popup_csv');
        console.log('popup divs found');
        clearInterval(check_divs);
    }
}, 100);

function OpenBBMain(plotly_figure) {
    let CHART_DIV = document.getElementById('openbb_chart');
    globals.chartDiv = CHART_DIV;
    let graphs = plotly_figure;

    CONFIG = {
        scrollZoom: true,
        responsive: true,
        displaylogo: false,
        toImageButtonOptions: {
            format: 'png',
            filename: openbbFilename(graphs),
            height: CHART_DIV.clientHeight,
            width: CHART_DIV.clientWidth,
        },
        modeBarButtonsToRemove: ['lasso2d', 'select2d'],
        modeBarButtons: [
            [
                'drawline',
                'drawopenpath',
                'drawcircle',
                'drawrect',
                'eraseshape',
                {
                    name: 'Download Data (Ctrl+S)',
                    icon: Plotly.Icons.disk,
                    click: function (gd) {
                        downloadData(gd);
                    },
                },
                'toImage',
            ],
            ['zoomIn2d', 'zoomOut2d', 'resetScale2d', 'zoom2d', 'pan2d'],
            [
                {
                    name: 'Add Text (Ctrl+T)',
                    icon: ICONS.addText,
                    click: function () {
                        openPopup('popup_text');
                    },
                },
                {
                    name: 'Change Titles (Ctrl+Shift+T)',
                    icon: ICONS.changeTitle,
                    click: function () {
                        openPopup('popup_title');
                    },
                },
                {
                    name: 'Plot CSV (Ctrl+Shift+C)',
                    icon: ICONS.plotCsv,
                    click: function () {
                        closePopup();
                        openPopup('popup_csv');
                    },
                },
                {
                    name: 'Edit Color (Ctrl+E)',
                    icon: ICONS.changeColor,
                    click: function () {
                        let title = 'Edit Color (Ctrl+E)';
                        let button = globals.barButtons[title];
                        let active = true;
                        if (button.style.border == 'transparent') {
                            active = false;
                        }
                        button_pressed(title, active);
                        changeColor();
                    },
                },
                {
                    name: 'Auto Scale (Ctrl+Shift+A)',
                    icon: Plotly.Icons.autoscale,
                    click: function () {
                        let title = 'Auto Scale (Ctrl+Shift+A)';
                        let button = globals.barButtons[title];
                        let active = true;
                        if (button.style.border == 'transparent') {
                            active = false;
                            CHART_DIV.on('plotly_relayout', function (eventdata) {
                                autoScaling(eventdata, graphs);
                            });
                        } else {
                            CHART_DIV.removeAllListeners('plotly_relayout');
                        }
                        button_pressed(title, active);
                    },
                },
                'hoverClosestCartesian',
                'hoverCompareCartesian',
                'toggleSpikelines',
            ],
        ],
    };

    if (!('font' in graphs.layout)) {
        graphs.layout['font'] = {
            family: 'Fira Code, monospace, Arial Black',
            size: 18,
        };
    }
    graphs.layout.annotations = !graphs.layout.annotations ? [] : graphs.layout.annotations;
    graphs.layout.height = !graphs.layout.height ? 586 : graphs.layout.height;
    graphs.layout.width = !graphs.layout.width ? 800 : graphs.layout.width;

    if (!('margin' in graphs.layout)) {
        graphs.layout['margin'] = {
            l: 0,
            r: 0,
            b: 0,
            t: 0,
            pad: 2,
        };
    }

    // We setup keyboard shortcuts custom to OpenBB
    window.document.addEventListener('keydown', function (e) {
        if (e.ctrlKey && (e.key == 't' || e.key == 'T')) {
            openPopup('popup_text');
        }
        if (e.ctrlKey && (e.key == 'e' || e.key == 'E')) {
            changeColor();
        }
        if (e.ctrlKey && e.shiftKey && (e.key == 't' || e.key == 'T')) {
            openPopup('popup_title');
        }
        if (e.ctrlKey && (e.key == 's' || e.key == 'S')) {
            downloadData(CHART_DIV);
        }
        if (e.ctrlKey && e.shiftKey && (e.key == 'c' || e.key == 'C')) {
            openPopup('popup_csv');
        }
        if (e.key == 'Escape') {
            closePopup();
        }
    });

    graphs.layout.autosize = true;
    delete graphs.layout.height;
    delete graphs.layout.width;

    if (graphs.layout.annotations != undefined) {
        graphs.layout.annotations.forEach(function (annotation) {
            if (!('font' in annotation) || !('size' in annotation.font)) {
                annotation['font'] = {
                    family: 'Fira Code, monospace, Arial Black',
                    size: 18,
                };
            }
            annotation.font.size = Math.min(CHART_DIV.clientWidth / 50, annotation.font.size);
        });
    }

    // We add spaces to all trace names, due to Fira Code font width issues
    // to make sure that the legend is not cut off
    graphs.data.forEach(function (trace) {
        if (trace.name != undefined) {
            trace.name = trace.name + '   ';
        }
    });

    graphs.layout.dragmode = 'pan';
    graphs.layout.font.size = Math.min(CHART_DIV.clientWidth / 50, graphs.layout.font.size);

    // We check for the dark mode
    if (graphs.layout.template.layout.mapbox.style == 'dark') {
        let style = document.createElement('style');
        style.innerHTML = `
        .updatemenu-item-rect {
            fill: transparent !important;
        }
        .updatemenu-item-rect:hover {
            fill: #00ACFF !important;
            background-color: transparent !important;

        }
        .updatemenu-item-text:hover {
            fill: #d1030d !important;
        }
        `;
        document.getElementsByTagName('head')[0].appendChild(style);
        document.body.style.backgroundColor = '#000000';
        graphs.layout.template.layout.paper_bgcolor = '#000000';
        graphs.layout.template.layout.plot_bgcolor = '#000000';
    }

    Plotly.setPlotConfig(CONFIG);
    Plotly.newPlot(CHART_DIV, graphs, { responsive: true });

    // Create global variables to for use later
    let modebar = document.getElementsByClassName('modebar-container');
    let modebar_buttons = modebar[0].getElementsByClassName('modebar-btn');
    globals.barButtons = {};

    for (let i = 0; i < modebar_buttons.length; i++) {
        let button = modebar_buttons[i];
        button.style.border = 'transparent';
        globals.barButtons[button.getAttribute('data-title')] = button;
    }

    // send a relayout event to trigger the initial zoom
    Plotly.relayout(CHART_DIV, {
        'xaxis.range[0]': graphs.layout.xaxis.range[0],
        'xaxis.range[1]': graphs.layout.xaxis.range[1],
    });

    // We add the event listeners for csv file/type changes
    CSV_DIV.querySelector('#csv_file').addEventListener('change', function () {
        checkFile(CSV_DIV);
    });
    CSV_DIV.querySelector('#csv_type').addEventListener('change', function () {
        console.log('type changed');
        checkFile(CSV_DIV, true);
    });
}
