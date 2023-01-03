function get_popup(data = null, type = null) {
    let popup = null;
    type = type.replace('popup_', '');

    if (type == 'title') {
        data = globals.chartDiv.layout;
        let title = 'title' in data && 'text' in data.title ? data.title.text : '';
        let xaxis = 'title' in data.xaxis && 'text' in data.xaxis.title ? data.xaxis.title.text : '';
        let yaxis = 'title' in data.yaxis && 'text' in data.yaxis.title ? data.yaxis.title.text : '';

        TITLE_DIV.innerHTML = `
        <label for="title_text">Title:</label>
        <input id="title_text" type="text" value="${title}" autofocus></input>
        <label for="title_xaxis">X axis:</label>
        <input id="title_xaxis" type="text" value="${xaxis}"></input>
        <label for="title_yaxis">Y axis:</label>
        <input id="title_yaxis" type="text" value="${yaxis}"></input>

        <button id="title_submit" onclick="on_submit('title')">Submit</button>
        <button id="title_cancel" onclick="closePopup()">Cancel</button>
        `;

        // when opening the popup, we make sure to focus on the title input
        TITLE_DIV.style.display = 'inline-block';
        TITLE_DIV.querySelector('#title_text').focus();
        popup = TITLE_DIV;
    } else if (type == 'text') {
        let has_annotation = false;
        if (data == undefined) {
            data = {
                text: '',
                font: {
                    color: '#ffffff',
                    size: 18,
                },
                bordercolor: '#ffffff',
            };
        } else {
            has_annotation = true;
        }

        // we replace <br> with \n so that the textarea can display the text properly
        data.text = data.text.replace(/<br>/g, '\n');

        let yanchor =
            TEXT_DIV.querySelector('#addtext_top') == null
                ? 'top'
                : TEXT_DIV.querySelector('#addtext_top').checked
                ? 'top'
                : 'bottom';

        TEXT_DIV.innerHTML = `
        <label for="popup_textarea"><b>Text:</b>
        <div id="popup_textarea_warning" class="popup_warning">Text is required</div></label><br>
        <textarea id="addtext_textarea" rows="4" cols="50" value="${data.text}"
            placeholder="Enter text here" autofocus>${data.text}</textarea><br>

        <div style="margin-top: 10px;">
            <label for="addtext_color"><b>Font color:</b></label>
            <input type="color" id="addtext_color" value="${data.font.color}"></input>

            <label for="addtext_border"><b>Border color:</b></label>
            <input type="color" id="addtext_border" value="${data.bordercolor}"></input>

            <label for="addtext_size"><b>Font size:</b></label>
            <input style="width: 45px;" type="number" id="addtext_size" value="${data.font.size}"></input>

            <label><b>Position:</b></label>
            <label style="margin-left: 23px !important; margin-top: 25px !important;"
                for="addtext_top"><b>Above</b></label>
            <input style="margin-top: 25px !important;" type="checkbox" id="addtext_top" name="check"
                value="top" ${yanchor == 'top' ? 'checked' : ''}></input>
        </div><br>
        `;

        if (has_annotation) {
            TEXT_DIV.innerHTML += `
            <button id="addtext_submit" onclick="on_submit('text', true)">Submit</button>
            <button id="addtext_cancel" onclick="closePopup()">Cancel</button>
            <button id="addtext_delete" onclick="on_delete('text')"
                style="margin: 10px 0px 0px 134px;">Delete</button>
            <input id="addtext_annotation" type="hidden" value='${JSON.stringify(data)}'></input>
            `;
        } else {
            TEXT_DIV.innerHTML += `
            <button id="addtext_submit" onclick="on_submit('text')">Submit</button>
            <button id="addtext_cancel" onclick="closePopup()">Cancel</button>
            `;

            if (TEXT_DIV.querySelector('#addtext_annotation') != null) {
                TEXT_DIV.querySelector('#addtext_annotation').remove();
            }
        }

        // when opening the popup, we make sure to focus on the textarea
        TEXT_DIV.style.display = 'inline-block';
        TEXT_DIV.querySelector('#addtext_textarea').focus();
        popup = TEXT_DIV;
    } else if (type == 'csv') {
        closePopup();
        CSV_DIV.style.display = 'inline-block';
        popup = CSV_DIV;
        console.log('csv');
    }

    let popup_divs = [TITLE_DIV, TEXT_DIV, CSV_DIV];
    popup_divs.forEach(function (div) {
        if (div.id != popup.id) {
            div.style.display = 'none';
        }
    });

    return popup;
}

function get_popup_data(type = null) {
    let data = null;

    if (type == 'title') {
        data = {
            title: TITLE_DIV.querySelector('#title_text').value,
            xaxis: TITLE_DIV.querySelector('#title_xaxis').value,
            yaxis: TITLE_DIV.querySelector('#title_yaxis').value,
        };
    } else if (type == 'text') {
        data = {
            text: TEXT_DIV.querySelector('#addtext_textarea').value,
            color: TEXT_DIV.querySelector('#addtext_color').value,
            size: TEXT_DIV.querySelector('#addtext_size').value,
            yanchor: TEXT_DIV.querySelector('#addtext_top').checked ? 'top' : 'bottom',
            bordercolor: TEXT_DIV.querySelector('#addtext_border').value,
        };
        if (TEXT_DIV.querySelector('#addtext_annotation') != null) {
            data['annotation'] = JSON.parse(TEXT_DIV.querySelector('#addtext_annotation').value);
        }

        // we replace \n with <br> so that line breaks are displayed properly on the graph
        data.text = data.text.replace(/\n/g, '<br>');
        console.log(data);
    } else if (type == 'csv') {
        let popup_type = CSV_DIV.querySelector('#csv_type').value;
        if (popup_type == 'candlestick') {
            data = {
                x: CSV_DIV.querySelector('#csv_x').value,
                open: CSV_DIV.querySelector('#csv_open').value,
                high: CSV_DIV.querySelector('#csv_high').value,
                low: CSV_DIV.querySelector('#csv_low').value,
                close: CSV_DIV.querySelector('#csv_close').value,
                increasing: CSV_DIV.querySelector('#csv_increasing').value,
                decreasing: CSV_DIV.querySelector('#csv_decreasing').value,
            };
        } else {
            data = {
                x: CSV_DIV.querySelector('#csv_x').value,
                y: CSV_DIV.querySelector('#csv_y').value,
                color: CSV_DIV.querySelector('#csv_color').value,
            };
            console.log(data);
        }
        data['name'] = CSV_DIV.querySelector('#csv_name').value;
        data['file'] = CSV_DIV.querySelector('#csv_file');
        data['type'] = popup_type;
    }
    return data;
}

function on_submit(type, on_annotation = null) {
    let popup_data = get_popup_data(type);
    let gd = globals.chartDiv;
    Plotly.relayout(gd, 'hovermode', 'closest');

    if (type == 'text') {
        if (!popup_data.text == '') {
            if ('annotation' in popup_data) {
                let current_text = popup_data.annotation.text;
                let data = {
                    x: popup_data.annotation.x,
                    y: popup_data.annotation.y,
                    yref: popup_data.annotation.yref,
                };
                plot_text(data, popup_data, current_text);
                return;
            }

            gd.on('plotly_clickannotation', function (eventData) {
                let annotation = eventData.annotation;
                openPopup('popup_text');
                get_popup(annotation, (type = 'text'));

                if (on_annotation != null) {
                    let data = {
                        x: popup_data.annotation.x,
                        y: popup_data.annotation.y,
                        yref: popup_data.annotation.yref,
                    };
                    plot_text(data, popup_data, popup_data.annotation.text);
                }
                Plotly.relayout(gd, 'hovermode', 'x');
            });

            let clickHandler = function (eventData) {
                let x = eventData.points[0].x;
                let yaxis = eventData.points[0].data.yaxis;
                let y = 0;

                // We need to check if the trace is a candlestick or not
                // this is because the y value is stored in the high or low
                if (eventData.points[0].y != undefined) {
                    y = eventData.points[0].y;
                } else if (eventData.points[0].low != undefined) {
                    if (popup_data.yanchor == 'bottom') {
                        y = eventData.points[0].low;
                    } else {
                        y = eventData.points[0].high;
                    }
                }
                let data = {
                    x: x,
                    y: y,
                    yref: yaxis,
                };
                plot_text(data, popup_data);
                Plotly.relayout(gd, 'hovermode', 'x');
            };

            Plotly.relayout(gd, { dragmode: 'select' });
            gd.on('plotly_click', clickHandler);
        } else {
            let textarea = TEXT_DIV.querySelector('#addtext_textarea');
            document.getElementById('popup_textarea_warning').style.display = 'block';
            textarea.style.border = '1px solid red';
            textarea.focus();

            TEXT_DIV.style.display = 'inline-block';
            return;
        }
    } else if (type == 'title') {
        Plotly.relayout(gd, {
            title: popup_data.title,
            'xaxis.title': popup_data.xaxis,
            'yaxis.title': popup_data.yaxis,
            'yaxis.type': 'linear',
        });
    } else if (type == 'csv') {
        console.log('got popup file');
        let popup_file = popup_data.file;

        if (popup_file.files.length > 0) {
            console.log('file selected');

            let file = popup_file.files[0];
            let popup_file_reader = new FileReader();
            popup_file_reader.onload = function (e) {
                let lines = e.target.result.split('\n');
                let data = [];
                let headers = lines[0].split(',');
                let trace = {};

                for (let i = 1; i < lines.length; i++) {
                    let obj = {};
                    let currentline = lines[i].split(',');
                    for (let j = 0; j < headers.length; j++) {
                        obj[headers[j]] = currentline[j];
                    }
                    data.push(obj);
                }

                if (popup_data.type == 'candlestick') {
                    trace = {
                        x: data.map(function (row) {
                            return row[popup_data.x];
                        }),
                        open: data.map(function (row) {
                            return row[popup_data.open];
                        }),
                        high: data.map(function (row) {
                            return row[popup_data.high];
                        }),
                        low: data.map(function (row) {
                            return row[popup_data.low];
                        }),
                        close: data.map(function (row) {
                            return row[popup_data.close];
                        }),
                        type: popup_data.type,
                        name: popup_data.name,
                        increasing: { line: { color: popup_data.increasing } },
                        decreasing: { line: { color: popup_data.decreasing } },
                    };
                } else {
                    trace = {
                        x: data.map(function (row) {
                            return row[popup_data.x];
                        }),
                        y: data.map(function (row) {
                            return row[popup_data.y];
                        }),
                        type: popup_data.type,
                        mode: 'lines',
                        name: popup_data.name,
                        line: { color: popup_data.color },
                        xaxis: 'x',
                        yaxis: 'y',
                    };
                }

                Plotly.addTraces(gd, trace);
                Plotly.relayout(gd, { 'yaxis.type': 'linear' });
                Plotly.react(gd, gd.data, gd.layout);

                // We empty the fields and innerHTML after the plot is made
                CSV_DIV.querySelector('#csv_colors').innerHTML = '';
                CSV_DIV.querySelector('#csv_columns').innerHTML = '';

                CSV_DIV.querySelectorAll('input').forEach(function (input) {
                    input.value = '';
                });
            };
            popup_file_reader.readAsText(file);
        }
    }
    closePopup();
}

function on_cancel() {
    closePopup();
}

function on_delete(type) {
    let gd = globals.chartDiv;
    closePopup();

    if (type == 'text') {
        let annotation = JSON.parse(TEXT_DIV.querySelector('#addtext_annotation').value);
        gd.layout.annotations.splice(gd.layout.annotations.indexOf(annotation), 1);

        Plotly.react(gd, gd.data, gd.layout);
        Plotly.relayout(gd, 'dragmode', 'pan');

        TEXT_DIV.style.display = 'none';
    }
}

function closePopup() {
    var popup = document.getElementById('popup_overlay');
    popup.style.display = 'none';
}

function openPopup(popup_id) {
    closePopup();
    get_popup(null, popup_id);
    var overlay = document.getElementById('popup_overlay');
    overlay.style.display = 'block';
}
