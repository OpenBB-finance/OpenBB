"""Finance Database view"""
__docformat__ = "numpy"
# pylint:disable=too-many-arguments

import logging

import financedatabase as fd
import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

equities = fd.Equities()


@log_start_end(log=logger)
def show_equities(
    country: str,
    sector: str,
    industry: str,
    name: str,
    description: str,
    marketcap: str,
    amount: int,
    include_exchanges: bool,
    options: str,
):
    """
    Display a selection of Equities based on country, sector, industry, name and/or description filtered
    by market cap. If no arguments are given, return equities categorized as Large Cap.
    [Source: Finance Database]

    Parameters
    ----------
    country: str
        Search by country to find stocks matching the criteria.
    sector : str
        Search by sector to find stocks matching the criteria.
    industry : str
        Search by industry to find stocks matching the criteria.
    name : str
        Search by name to find stocks matching the criteria.
    description : str
        Search by description to find stocks matching the criteria.
    marketcap : str
        Select stocks based on the market cap.
    amount : int
        Number of stocks to display, default is 10.
    include_exchanges: bool
        When you wish to include different exchanges use this boolean.
    options : str
        Show the country, sector or industry options.
    """
    if options is not None:
        for option in ["country", "sector", "industry_group", "industry"]:
            console.print(option.title())
            console.print(equities.options(option))
        return

    if country is not None:
        country = " ".join(country).title()
    if sector is not None:
        sector = " ".join(sector).title()
    if industry is not None:
        industry = " ".join(industry).title()

    data = equities.search(
        country=country,
        sector=sector,
        industry=industry,
        exclude_exchanges=include_exchanges,
    )

    if name is not None:
        data = equities.search(long_name=" ".join(name))
    if description is not None:
        data = equities.search(summary=" ".join(description))
    if marketcap is not None:
        data = equities.search(market_cap=f"{''.join(marketcap)} Cap")

    table_data = pd.DataFrame(data).T[
        [
            "long_name",
            "sector",
            "industry_group",
            "industry",
            "country",
            "city",
            "website",
            "market_cap",
        ]
    ]

    print_rich_table(
        table_data.iloc[:amount],
        show_index=True,
        headers=[
            "Name",
            "Sector",
            "Industry Group",
            "Industry",
            "Country",
            "City",
            "Website",
            "Market Cap",
        ],
        title="Equities",
    )
