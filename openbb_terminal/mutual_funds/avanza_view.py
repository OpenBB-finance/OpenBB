"""Avanza View"""
__docformat__ = "numpy"

import logging

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console
from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.mutual_funds import avanza_model

logger = logging.getLogger(__name__)

sector_dict = {
    "Industri": "Industry",
    "Konsument, cyklisk": "Consumer goods, cyclical",
    "Finans": "Finance",
    "Konsument, stabil": "Consumer goods, stable",
    "Sjukvård": "Health Care",
    "Teknik": "Technology",
    "Fastigheter": "Real Estate",
    "Råvaror": "Commodities",
    "Kommunikation": "Telecommunication",
    "Allmännyttigt": "Utilities",
    "Energi": "Energy",
}


@log_start_end(log=logger)
def display_allocation(fund_name: str, focus: str):
    """Displays the allocation of the selected swedish fund

    Parameters
    ----------
    fund_name: str
        Full name of the fund
    focus: str
        The focus of the displayed allocation/exposure of the fund
    """
    # Code mostly taken from: https://github.com/northern-64bit/Portfolio-Report-Generator/tree/main
    fund_data = avanza_model.get_data(fund_name.upper())
    if focus in ["holding", "all"]:
        table_row = []
        console.print("")
        for data in fund_data["holdingChartData"]:
            table_row_temp = []
            table_row_temp.append(data["name"])
            table_row_temp.append(str(data["y"]))
            table_row_temp.append(data["countryCode"])
            table_row.append(table_row_temp)
        header = ["Holding", "Allocation in %", "Country"]
        holding_data = pd.DataFrame(table_row, columns=header)
        print_rich_table(holding_data, title=f"{fund_name}'s Holdings", headers=header)
    if focus in ["sector", "all"]:
        table_row = []
        console.print("")
        for data in fund_data["sectorChartData"]:
            table_row_temp = []
            table_row_temp.append(sector_dict[data["name"]])
            table_row_temp.append(str(data["y"]))
            table_row.append(table_row_temp)
        header = ["Sector", "Allocation in %"]
        sector_data = pd.DataFrame(table_row, columns=header)
        print_rich_table(
            sector_data, title=f"{fund_name}'s Sector Weighting", headers=header
        )
    if focus in ["country", "all"]:
        table_row = []
        console.print("")
        for data in fund_data["countryChartData"]:
            table_row_temp = []
            table_row_temp.append(data["countryCode"])
            table_row_temp.append(str(data["y"]))
            table_row.append(table_row_temp)
        header = ["Country", "Allocation in %"]
        country_data = pd.DataFrame(table_row, columns=header)
        print_rich_table(
            country_data, title=f"{fund_name}'s Country Weighting", headers=header
        )


@log_start_end(log=logger)
def display_info(fund_name: str):
    """Displays info of swedish funds

    Parameters
    ----------
    fund_name: str
        Full name of the fund
    """
    fund_data = avanza_model.get_data(fund_name.upper())
    text = f"\nSwedish Description:\n\n{fund_data['description']}\n\nThe fund is managed by:\n"
    for manager in fund_data["fundManagers"]:
        text = text + f"\t- {manager['name']} since {manager['startDate']}\n"
    text = (
        text
        + f"from {fund_data['adminCompany']['name']}.\nThe currency of the fund is {fund_data['currency']}"
        f" and it the fund started {fund_data['startDate']}."
    )
    if fund_data["indexFund"]:
        text = text + " It is a index fund."
    else:
        text = text + " It is not a index fund."
    text = (
        text
        + f" The fund manages {str(fund_data['capital'])} {fund_data['currency']}. The "
        f"standard deviation of the fund is {str(fund_data['standardDeviation'])} and the sharpe "
        f"ratio is {str(fund_data['sharpeRatio'])}.\n"
    )
    console.print(text)
