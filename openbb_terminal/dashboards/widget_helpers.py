"""Widgets Helper Library.

A library of `ipywidgets` wrappers for notebook based reports and voila dashboards.
The library includes both python code and html/css/js elements that can be found in the
`./widgets` folder.
"""
import os

from jinja2 import Template


def stylesheet():
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
