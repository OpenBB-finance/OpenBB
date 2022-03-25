"""Widgets Helper Library.

A library of `ipywidgets` wrappers for notebook based reports and voila dashboards.
The library includes both python code and html/css/js elements that can be found in the
`./widgets` folder.
"""
import os
from typing import List
from jinja2 import Template


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
    card = template.render(title=title, stylesheet=stylesheet, body=body)
    return card


def h(level: int, text: str) -> str:
    """Wrap text into an HTML `h` tag."""
    return f"<h{str(level)}>{text}</h{level}>"


def p(text: str) -> str:
    """Wrap text into an HTML `p` tag."""
    return f"<p>{text}</p>"


def row(elements: List) -> str:
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "widgets", "row.j2")
    ) as f:
        template = Template(f.read())
    return template.render(elements=elements)
