"""Finance Database view"""
__docformat__ = "numpy"

import financedatabase as fd
import pandas as pd
from tabulate import tabulate


def show_equities(
    country: str,
    sector: str,
    industry: str,
    name: str,
    description: str,
    amount: int,
    options: str,
):
    """
    Display a selection of Equities based on country, sector, industry, name and/or description filtered
    by market cap. If no arguments are given, return the equities with the highest market cap.

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
    amount : int
        Number of stocks to display, default is 10.
    options : str
        Show the country, sector or industry options.
    """
    if options is not None:
        for option in fd.show_options("equities", options):
            print(option)
        return

    if country is not None:
        country = " ".join(country)
    if sector is not None:
        sector = " ".join(sector)
    if industry is not None:
        industry = " ".join(industry)

    data = fd.select_equities(
        country=country,
        sector=sector,
        industry=industry,
    )

    if name is not None:
        data = fd.search_products(data, query=" ".join(name), search="long_name")
    if description is not None:
        data = fd.search_products(data, query=" ".join(description), search="summary")

    tabulate_data = pd.DataFrame(data).T[
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

    tabulate_data_sorted = tabulate_data.sort_values(by="market_cap", ascending=False)

    print(
        tabulate(
            tabulate_data_sorted.iloc[:amount],
            showindex=True,
            headers=[
                "Name",
                "Sector",
                "Industry",
                "Country",
                "City",
                "Website",
                "Market Cap",
            ],
            floatfmt=".2f",
            tablefmt="fancy_grid",
        )
    )
