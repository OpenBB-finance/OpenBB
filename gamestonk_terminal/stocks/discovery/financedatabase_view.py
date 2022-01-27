"""Finance Database view"""
__docformat__ = "numpy"
# pylint:disable=too-many-arguments

import financedatabase as fd
import pandas as pd
from gamestonk_terminal.helper_funcs import print_rich_table
from gamestonk_terminal.rich_config import console


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
        for option in fd.show_options("equities", options):
            console.print(option)
        return

    if country is not None:
        country = " ".join(country).title()
    if sector is not None:
        sector = " ".join(sector).title()
    if industry is not None:
        industry = " ".join(industry).title()

    data = fd.select_equities(
        country=country,
        sector=sector,
        industry=industry,
        exclude_exchanges=include_exchanges,
    )

    if name is not None:
        data = fd.search_products(data, query=" ".join(name), search="long_name")
    if description is not None:
        data = fd.search_products(data, query=" ".join(description), search="summary")
    if marketcap is not None:
        data = fd.search_products(
            data, query=f"{''.join(marketcap)} Cap", search="market_cap"
        )

    table_data = pd.DataFrame(data).T[
        [
            "long_name",
            "sector",
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
            "Industry",
            "Country",
            "City",
            "Website",
            "Market Cap",
        ],
        title="Equities",
    )
    console.print("")
