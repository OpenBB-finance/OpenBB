"""Reportlab Helpers"""
__docformat__ = "numpy"

from datetime import datetime
from typing import List

from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle


def base_format(report: canvas.Canvas, header: str) -> None:
    """Applies a base page format to each page

    Parameters
    ----------
    report : canvas.Canvas
        The report to be formatted
    header : str
        The header for the page
    """
    report.setLineWidth(0.3)
    report.setFont("Helvetica", 12)
    report.drawString(30, 760, "Gamestonk Terminal")
    report.drawString(500, 760, datetime.now().strftime("%Y/%m/%d"))
    report.drawString(275, 750, "Annual Report")
    report.line(50, 730, 580, 730)
    report.setFont("Helvetica", 20)
    report.drawString(50, 705, header)
    report.setFont("Helvetica", 12)


def draw_paragraph(
    report: canvas.Canvas, msg: str, x: int, y: int, max_width: int, max_height: int
) -> None:
    """Draws a given paragraph

    Parameters
    ----------
    report : canvas.Canvas
        The report to be formatted
    msg : str
        The contents of the paragraph
    x : int
        The x coordinate for the paragraph
    y : int
        The y coordinate for the paragraph
    max_width : int
        The maximum width allowed for the paragraph
    max_height : int
        The maximum height allowed for the paragraph
    """
    message_style = ParagraphStyle("Normal")
    message = msg.replace("\n", "<br />")
    paragraph = Paragraph(message, style=message_style)
    _, h = paragraph.wrap(max_width, max_height)
    paragraph.drawOn(report, x, y - h)


def draw_table(
    report: canvas.Canvas,
    header_txt: str,
    aW: int,
    aH: int,
    x: int,
    data: List[List[str]],
) -> None:
    """Draw a table at given coordinates

    Parameters
    ----------
    report : canvas.Canvas
        The report to be formatted
    header_txt : str
        The header for the table
    aW : int
        The width for the table
    aH : int
        The height for the table
    x : int
        The x coordinate for the table
    data : List[List[str]]
        Data to show
    """
    style = getSampleStyleSheet()["BodyText"]
    header = Paragraph(f"<bold><font size=14>{header_txt}</font></bold>", style)

    t = Table(data)
    t.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
            ]
        )
    )

    for each in range(len(data)):
        bg_color = colors.whitesmoke if each % 2 == 0 else colors.lightgrey
        t.setStyle(TableStyle([("BACKGROUND", (0, each), (-1, each), bg_color)]))

    _, h = header.wrap(aW, aH)
    header.drawOn(report, x, aH)
    aH = aH - h
    _, h = t.wrap(aW, aH)
    t.drawOn(report, x, aH - h)
