"""Widgets Helper Library.

A library of `ipywidgets` wrappers for notebook based reports and voila dashboards.
The library includes both python code and html/css/js elements that can be found in the
`./widgets` folder.
"""
import base64
import os
from typing import List

from jinja2 import Template

from openbb_terminal.core.config.paths import PACKAGE_DIRECTORY
from openbb_terminal.core.plots.backend import PLOTLYJS_PATH


def price_card_stylesheet():
    """Load a default CSS stylesheet from file."""
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "widgets", "style.css")
    ) as f:
        style = f.read()
    return style


def price_card(ticker: str, price: str, price_color: str = "neutral_color") -> str:
    """Prepare a styled HTML element of a 128 by 128 price card.

    Parameters
    ----------
    ticker : str
        Instrument ticker for the price card
    price : str
        Instrument price as a string
    price_color : str, optional
        The color of the price. Accepts "up_color", "down_color" and default "neutral_color"

    Returns
    -------
    str
        HTML code as string
    """
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "widgets", "card.j2")
    ) as f:
        template = Template(f.read())
    card = template.render(ticker=ticker, price=price, price_color=price_color)
    return card


def html_report_stylesheet():
    """Load a default CSS stylesheet from file."""
    with open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "widgets", "report.css"
        )
    ) as f:
        style = f.read()
    return style


def html_report(title: str = "", stylesheet: str = "", body: str = "") -> str:
    """Prepare a styled HTML page element.

    Parameters
    ----------
    title : str, optional
        Contents of the title tag, by default ""
    stylesheet : str, optional
        Contents of the stylesheet tag, by default ""
    body : str, optional
        Contents of the body tag, by default ""

    Returns
    -------
    str
        HTML code as string
    """
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "widgets", "report.j2")
    ) as f:
        template = Template(f.read())
    return template.render(title=title, stylesheet=stylesheet, body=body + "</html>")


def h(level: int, text: str) -> str:
    """Wrap text into an HTML `h` tag.

    Parameters
    ----------
    level : int
        HTML `h` level tag
    text : str
        Contents for `h` level tag

    Returns
    -------
    str
        HTML code as string
    """
    return f"<h{str(level)}>{text}</h{level}>"


def p(text: str, style: str = "") -> str:
    """Wrap text into an HTML `p` tag.

    Parameters
    ----------
    text : str
        Contents for HTML `p` tag
    style: str
        Div style

    Returns
    -------
    str
        HTML code as string
    """
    return f'<p style="{style}">{text}</p>'


def row(elements: List) -> str:
    """HTML code elements to add in a single row

    Parameters
    ----------
    elements : List
        List of HTML code elements to add in a row

    Returns
    -------
    str
        HTML code as string
    """
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "widgets", "row.j2")
    ) as f:
        template = Template(f.read())
    return template.render(elements=elements)


def kpi(thresholds: List[float], sentences: List[str], value: float) -> str:
    """Add new key performance indicator to main page of report

    Parameters
    ----------
    thresholds : List[float]
        List of thresholds to take into account
    sentences : List[str]
        List of sentences to take into account. len(sentences) = len(thresholds)+1
    value : float
        Current value for the KPI in question

    Returns
    -------
    str
        HTML code as string
    """
    if len(thresholds) == 1 and len(sentences) == 2:
        if value < thresholds[0]:
            return f'<p style="color:red">&#10060; {sentences[0]}. {value} < {thresholds[0]} </p>'
        return f'<p style="color:green">&#x2705; {sentences[1]}. {value} > {thresholds[0]} </p>'
    if len(thresholds) == 2 and len(sentences) == 3:
        if value < thresholds[0]:
            return f'<p style="color:red">&#10060; {sentences[0]}. {value} < {thresholds[0]} </p>'
        if value > thresholds[1]:
            return f'<p style="color:green">&#x2705; {sentences[2]}. {value} > {thresholds[1]} </p>'
        return f'<p style="color:orange">&#128993; {sentences[1]}. {thresholds[0]} < {value} < {thresholds[1]} </p>'
    print("Error. KPI condition is not correctly set")
    return ""


def add_tab(
    title: str, htmlcode: str, comment_cell: bool = True, commment_text: str = ""
) -> str:
    """Add new tab section for the report. By default adds an opinion editable box at the start.

    Parameters
    ----------
    title : str
        Title associated with this tab / section
    htmlcode : str
        All HTML code contain within this section
    comment_cell : bool
        Comment cell

    Returns
    -------
    str
        HTML code as string
    """
    html_text = f'<div id="{title}" class="tabcontent"></br>'
    if comment_cell:
        comment = commment_text if commment_text else "No comment."
        html_text += f"""<p style="border:3px; border-style:solid;
            border-color:#000000; padding: 1em; width: 1050px;" contentEditable="true">
                {comment}
        </p>"""
    html_text += f"{htmlcode}</div>"
    return html_text


def tab_clickable_and_save_evt() -> str:
    """Adds javascript code within HTML at the bottom that allows the interactivity with tabs.

    Parameters
    ----------
    report_name : str
        Report name for the file to be saved

    Returns
    -------
    str
        javascript code in HTML to process interactive tabs
    """
    return """
        <script>
        function menu(evt, menu_name) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
                tablinks[i].style.backgroundColor = "white";
                tablinks[i].style.color = "black";
            }
            document.getElementById(menu_name).style.display = "block";

            evt.currentTarget.className += " active";
            evt.currentTarget.style.backgroundColor = "black";
            evt.currentTarget.style.color = "white";
        }

        function saveReport() {
            const markup = document.documentElement.innerHTML;
            var bl = new Blob([markup], { type: "text/html" });
            var a = document.createElement("a");
            a.href = URL.createObjectURL(bl);
            a.download =  "openbb_report.html";
            a.hidden = true;
            document.body.appendChild(a);
            a.innerHTML = "Download";
            a.click();
        }

        function readCommentsAndUpdateValues() {
            var inputs, index;

            inputs = document.getElementsByTagName('input');
            for (index = 0; index < inputs.length; ++index) {
                const elem = inputs[index];
                elem.addEventListener('input', (e) => {
                    console.log(elem.name, elem.value, e.target.value);
                    elem.setAttribute("value", e.target.value)
                });
            }
        }

        window.onload=function(){
            readCommentsAndUpdateValues();
            menu(event, 'SUMMARY');
        };
        </script>"""


def tablinks(tabs: List[str]) -> str:
    """Adds list of tabs/sections for the reports that are able to be clicked. For every
    6 tabs we push them onto a new line.

    Parameters
    ----------
    tabs : List[str]
        List of tabs/sections for the reports.

    Returns
    -------
    str
        HTML code for interactive tabs
    """
    htmlcode = '<div class="tab">'
    for idx, tab in enumerate(tabs):
        htmlcode += f"""<button class="tablinks" onclick="menu(event, '{tab}')">{tab}</button>"""
        if ((idx + 1) % 5) == 0:
            htmlcode += "</br>"
    htmlcode += "</div>"
    return htmlcode


def header(
    author: str,
    report_date: str,
    report_time: str,
    report_tz: str,
    title: str,
    plotly_js: bool = False,
) -> str:
    """Creates reports header

    Parameters
    ----------
    author : str
        Name of author responsible by report
    report_date : str
        Date when report is run
    report_time : str
        Time when report is run
    report_tz : str
        Timezone associated with datetime of report being run
    title : str
        Title of the report
    plotly_js : bool
        If True, then we add plotly.js to the report

    Returns
    -------
    str
        HTML code for interactive tabs
    """
    openbb_img_path = PACKAGE_DIRECTORY / "reports/templates/OpenBB_reports_logo.png"
    floppy_disk_path = PACKAGE_DIRECTORY / "reports/templates/floppy-disc.png"

    try:
        openbb_image_encoded = base64.b64encode(openbb_img_path.read_bytes())
        openbb_img = f"""
            <img src="data:image/png;base64,{openbb_image_encoded.decode()}"
            alt="OpenBB" style="width:144px;">"""
    except Exception:
        openbb_img = ""

    try:
        floppy_disk_encoded = base64.b64encode(floppy_disk_path.read_bytes())
        flask_disk_save = f"""
            <center><img src="data:image/png;base64,{floppy_disk_encoded.decode()}"
            alt="OpenBB" style="width:40px;"></center>"""
    except Exception:
        flask_disk_save = ""

    plotly_script = ""

    if plotly_js:
        plotly_script = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
        body {
            font-family: 'Fira Code', monospace;
            font-weight: 400 700;
            font-stretch: 50%;
        }
        </style>
        """
        try:
            plotly_script += (
                f"""<script>{PLOTLYJS_PATH.read_text(encoding="utf-8")}</script>"""
            )
        except Exception:
            plotly_script += (
                "<script src='https://cdn.plot.ly/plotly-2.24.2.min.js'></script>"
            )

    return f"""
            <html lang="en" class="" data-lt-installed="true">
            <head>
                <meta charset="UTF-8">
                <title>OpenBB Terminal Report</title>
                <meta name="robots" content="noindex">
            </head>
            {plotly_script}
            <div style="display:flex; margin-bottom:1cm;">
                {openbb_img}
                <div style="margin-left:2em">
                    <p><b>Analyst:</b> {author}</p>
                    <p><b>Date   :</b> {report_date}</p>
                    <p><b>Time   :</b> {report_time} {report_tz}</p>
                    <br/>
                    <p>{title}</p>
                </div>
                <button style="margin-left:7em; border:0px solid black;
                    background-color: transparent;" onclick="saveReport()">
                        {flask_disk_save}Save changes
                </button>
            </div>
        """


def add_external_fig(figloc: str, style: str = "") -> str:
    """Add external figure to HTML

    Parameters
    ----------
    figloc : str
        Relative figure location
    style: str
        Div style

    Returns
    -------
    str
        HTML code for figure
    """
    try:
        with open(figloc, "rb") as image_file:
            img = base64.b64encode(image_file.read()).decode()
            return f'<img src="data:image/{figloc.split(".")[1]};base64,{img}"style="{style}">'
    except Exception:
        return ""
