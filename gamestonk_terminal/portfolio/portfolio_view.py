"""Portfolio View"""
__docformat__ = "numpy"

from datetime import datetime
import os

import pandas as pd
from tabulate import tabulate
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from gamestonk_terminal import feature_flags as gtff


def load_info():
    """Prints instructions to load a CSV"""
    text = """
In order to load a CSV do the following:

1. Add headers to the first row, below is data for each column:\n
\t1. Identifier for the asset (such as a stock ticker)
\t2. Type of asset (stock, bond, option, crypto)
\t3. The volume of the asset transacted
\t4. The buy date in yyyy/mm/dd
\t5. The Price paid for the asset
\t6. Any fees paid during the transaction
\t7. A premium paid or received if this was an option
\t8. Whether the asset was bought (covered) or sold (shorted)\n
2. Place this file in gamestonk_terminal/portfolio/portfolios\n
        """
    print(text)


def show_df(df: pd.DataFrame, show: bool) -> None:
    """
    Shows the given dataframe

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to be shown
    show : bool
        Whether to show the dataframe index
    """

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=show,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df.to_string, "\n")


def annual_report() -> None:
    """Generates an annual report"""
    dire = os.path.dirname(os.path.abspath(__file__)).replace(
        "gamestonk_terminal", "exports"
    )

    now = datetime.now()
    path = os.path.abspath(
        os.path.join(
            dire,
            f"ar_{now.strftime('%Y%m%d_%H%M%S')}.pdf",
        )
    )
    report = canvas.Canvas(path, pagesize=letter)
    report.setLineWidth(0.3)
    report.setFont("Helvetica", 12)
    report.drawString(30, 750, "Gamestonk Terminal")
    report.drawString(500, 750, now.strftime("%Y/%m/%d"))
    report.drawString(275, 725, "Annual Report")
    report.setFillColorRGB(255, 0, 0)
    report.drawString(
        100,
        710,
        "Warning: currently only analyzes stocks, currently excludes dividends and interest",
    )
    report.setFillColorRGB(0, 0, 0)
    report.line(50, 700, 580, 700)
    report.save()
