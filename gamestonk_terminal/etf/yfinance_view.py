"""Yahoo Finance view"""
__docformat__ = "numpy"

import os
import pandas as pd
from matplotlib import pyplot as plt
from tabulate import tabulate
from gamestonk_terminal.etf import yfinance_model
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale, export_data


def display_etf_weightings(
    name: str,
    raw: bool = False,
    min_pct_to_display: float = 5,
    export: str = "",
):
    """Display sector weightings allocation of ETF. [Source: Yahoo Finance]

    Parameters
    ----------
    name: str
        ETF name
    raw: bool
        Display sector weighting allocation
    min_pct_to_display: float
        Minimum percentage to display sector
    export: str
        Type of format to export data
    """
    sectors = yfinance_model.get_etf_sector_weightings(name)
    if not sectors:
        print("No data was found for that ETF\n")
        return

    holdings = pd.DataFrame(sectors, index=[0]).T

    title = f"Sector holdings of {name}"

    if raw:
        print(f"\n{title}")
        holdings.columns = ["% of holdings in the sector"]
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    holdings,
                    headers=holdings.columns,
                    showindex=True,
                    tablefmt="fancy_grid",
                ),
            )
        else:
            print(holdings.to_string, "\n")

    else:
        main_holdings = holdings[holdings.values > min_pct_to_display].to_dict()[
            holdings.columns[0]
        ]
        if len(main_holdings) < len(holdings):
            main_holdings["Others"] = 100 - sum(main_holdings.values())

        legend, values = zip(*main_holdings.items())
        leg = [f"{le}\n{round(v,2)}%" for le, v in zip(legend, values)]

        plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        plt.pie(
            values,
            labels=leg,
            wedgeprops={"linewidth": 0.5, "edgecolor": "white"},
            labeldistance=1.05,
            startangle=90,
        )
        plt.title(title)
        plt.tight_layout()
        if gtff.USE_ION:
            plt.ion()
        plt.show()

        print("")

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "weights", holdings)


def display_etf_description(
    name: str,
):
    """Display ETF description summary. [Source: Yahoo Finance]

    Parameters
    ----------
    name: str
        ETF name
    """
    description = yfinance_model.get_etf_summary_description(name)
    if not description:
        print("No data was found for that ETF\n")
        return

    print(description, "\n")
