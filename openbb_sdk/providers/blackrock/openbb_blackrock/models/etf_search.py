"""Blackrock ETF Search fetcher."""

from typing import Any, Dict, List, Literal, Optional

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_search import (
    EtfSearchData,
    EtfSearchQueryParams,
)
from pydantic import Field

from openbb_blackrock.utils.helpers import COUNTRIES, Canada


def search(query: str = "", country: Literal[COUNTRIES] = "canada", **kwagrs) -> pd.DataFrame:
    """Search Blackrock ETFs by fuzzy query."""

    etfs = pd.DataFrame()
    results = pd.DataFrame()
    if country == "canada":
        etfs = Canada.get_all_etfs()

    columns = [
        "symbol", "fundName", "aladdinAssetClass", "aladdinSubAssetClass", "aladdinRegion",
        "aladdinCountry", "aladdinMarketType", "totalNetAssets", "mer", "priceYearToDate",
        "priceOneYearAnnualized", "premiumDiscount", "distYield", "twelveMonTrlYield",
        "weightedAvgYieldToMaturity"
    ]

    if query:
        results = etfs[
            etfs["fundName"].str.contains(query, case=False)
            | etfs["aladdinSubAssetClass"].str.contains(query, case=False)
            | etfs["aladdinAssetClass"].str.contains(query, case=False)
            | etfs["aladdinRegion"].str.contains(query, case=False)
            | etfs["aladdinCountry"].str.contains(query, case=False)
            | etfs["aladdinMarketType"].str.contains(query, case=False)
        ]

        results = results[columns].set_index("symbol")
        results = results.replace("-", "")
        nav = [results["totalNetAssets"].loc[i]["r"] for i in results.index]
        results["totalNetAssets"] = nav
        #mer = [results["mer"].iloc[i]["r"] for i in results.index]
        #results["mer"] = mer
        #discount = [results["premiumDiscount"].loc[i]["r"] for i in results.index]
        #results["premiumDiscount"] = discount
        dist_yield = [results["distYield"].loc[i]["r"] for i in results.index]
        results["distYield"] = dist_yield
        #ttm_yield = [results["twelveMonTrlYield"].loc[i]["r"] for i in results.index]
        #results["twelveMonTrlYield"] = ttm_yield
        #ytm = [results.loc[i]["weightedAvgYieldToMaturity"]["r"] for i in results.index]
        #results["weightedAvgYieldToMaturity"] = ytm

    return results
