"""Reportlab Helpers"""
__docformat__ = "numpy"

from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph


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
    message_style = ParagraphStyle("Normal")
    message = msg.replace("\n", "<br />")
    paragraph = Paragraph(message, style=message_style)
    _, h = paragraph.wrap(max_width, max_height)
    paragraph.drawOn(report, x, y - h)
