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


def search(query: str = "", country: COUNTRIES = "canada", **kwagrs) -> pd.DataFrame:
    """Search Blackrock ETFs by fuzzy query."""

    etfs = pd.DataFrame()
    results = pd.DataFrame()
    if country == "canada":
        etfs = Canada.get_all_etfs()

        columns = [
            "fundName",
            "aladdinCountry",
            "totalNetAssets",
            "aladdinAssetClass",
            "aladdinSubAssetClass",
            "aladdinRegion",
            "aladdinMarketType",
            "investmentStyle",
            "aladdinStrategy",
            "premiumDiscount",
            "distYield",
            "twelveMonTrlYield",
            "weightedAvgYieldToMaturity",
            "navOneYearAnnualized",
            "navThreeYearAnnualized",
            "navFiveYearAnnualized",
            "navYearToDate",
            "navSinceInceptionAnnualized",
            "mer",
            "inceptionDate",
            "symbol",
        ]

        if not query:
            results = etfs

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

            mer = []
            nav = []
            nav1y = []
            nav3y = []
            nav5y = []
            nav_inception = []
            nav_ytd = []
            premium_discount = []
            ttm_yield = []
            dist_yield = []
            ytm = []
            inception_date = []
            for i in results.index:
                inception_date.append(dict(results.inceptionDate.loc[i]).get("r"))
                mer.append(dict(results.mer.loc[i]).get("r"))
                nav.append(dict(results.totalNetAssets.loc[i]).get("r"))
                nav1y.append(dict(results.navOneYearAnnualized.loc[i]).get("r"))
                nav3y.append(dict(results.navThreeYearAnnualized.loc[i]).get("r"))
                nav5y.append(dict(results.navFiveYearAnnualized.loc[i]).get("r"))
                nav_inception.append(
                    dict(results.navSinceInceptionAnnualized.loc[i]).get("r")
                )
                if results.navYearToDate.loc[i] is not None:
                    nav_ytd.append(dict(results.navYearToDate.loc[i]).get("r"))
                else:
                    nav_ytd.append(None)
                premium_discount.append(dict(results.premiumDiscount.loc[i]).get("r"))
                if results.twelveMonTrlYield.loc[i] is not None:
                    ttm_yield.append(dict(results.twelveMonTrlYield.loc[i]).get("r"))
                else:
                    ttm_yield.append(None)
                if results.distYield.loc[i] is not None:
                    dist_yield.append(dict(results.distYield.loc[i]).get("r"))
                else:
                    dist_yield.append(None)
                if results.weightedAvgYieldToMaturity.loc[i] is not None:
                    ytm.append(dict(results.weightedAvgYieldToMaturity.loc[i]).get("r"))
                else:
                    ytm.append(None)

            results["mer"] = mer
            results["totalNetAssets"] = nav
            results["premiumDiscount"] = premium_discount
            results["twelveMonTrlYield"] = ttm_yield
            results["distYield"] = dist_yield
            results["weightedAvgYieldToMaturity"] = ytm
            results["inceptionDate"] = inception_date
            results["navOneYearAnnualized"] = nav1y
            results["navThreeYearAnnualized"] = nav3y
            results["navFiveYearAnnualized"] = nav5y
            results["navSinceInceptionAnnualized"] = nav_inception
            results["navYearToDate"] = nav_ytd

    return results


class BlackrockEtfSearchQueryParams(EtfSearchQueryParams):
    """Blackrock ETF Search Query Params"""

    country: COUNTRIES = Field(
        description="The country the ETF is registered in.", default="canada"
    )


class BlackrockEtfSearchData(EtfSearchData):
    """Blackrock ETF Search Data."""

    name: str = Field(description="The name of the ETF.", alias="fundName")
    aum: Optional[float | None] = Field(
        description="The value of the assets under management.", alias="totalNetAssets"
    )
    asset_class: Optional[str | None] = Field(
        description="The asset class of the ETF.", alias="aladdinAssetClass"
    )
    sub_asset_class: Optional[str | None] = Field(
        description="The sub-asset class of the ETF.", alias="aladdinSubAssetClass"
    )
    region: Optional[str | None] = Field(
        description="The region of the ETF.", alias="aladdinRegion"
    )
    country: str = Field(
        description="The country the ETF is registered in.", alias="aladdinCountry"
    )
    market_type: Optional[str | None] = Field(
        description="The market type of the ETF.", alias="aladdinMarketType"
    )
    investment_style: Optional[str | None] = Field(
        description="The investment style of the ETF.", alias="investmentStyle"
    )
    investment_strategy: Optional[str | None] = Field(
        description="The investment strategy of the ETF.", alias="aladdinStrategy"
    )
    premium_discount: Optional[float | None] = Field(
        description="The premium/discount to NAV.", alias="premiumDiscount"
    )
    distribution_yield: Optional[float | None] = Field(
        description="The annualized distribution yield.", alias="distributionYield"
    )
    ttm_yield: Optional[float | None] = Field(
        description="The trailing twelve months (TTM) annualized yield.",
        alias="twelveMonTrlYield",
    )
    weighted_avg_ytm: Optional[float | None] = Field(
        description="The weighted average yield-to-maturity.",
        alias="weightedAvgYieldToMaturity",
    )
    return_1y: Optional[float | None] = Field(
        description="The one-year annualized return on net assets.",
        alias="navOneYearAnnualized",
    )
    return_3y: Optional[float | None] = Field(
        description="The three-year annualized return on net assets.",
        alias="navThreeYearAnnualized",
    )
    return_5y: Optional[float | None] = Field(
        description="The five-year annualized return on net assets.",
        alias="navFiveYearAnnualized",
    )
    return_ytd: Optional[float | None] = Field(
        description="The year-to-date annualized return on net assets.",
        alias="navYearToDate",
    )
    return_inception: Optional[float | None] = Field(
        description="The annualized return on net assets since inception.",
        alias="navSinceInceptionAnnualized",
    )
    mer: Optional[float | None] = Field(
        description="The management expense ratio.",
    )
    ineception_date: Optional[str | None] = Field(
        description="The inception date.", alias="inceptionDate"
    )


class BlackrockEtfSearchFetcher(
    Fetcher[
        BlackrockEtfSearchQueryParams,
        List[BlackrockEtfSearchData],
    ]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BlackrockEtfSearchQueryParams:
        """Transform the query."""
        return BlackrockEtfSearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BlackrockEtfSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Blackrock endpoint."""

        data = search(query=query.query, country=query.country)

        return data.reset_index().to_dict("records")

    @staticmethod
    def transform_data(data: List[Dict]) -> List[BlackrockEtfSearchData]:
        """Transform the data to the standard format."""
        return [BlackrockEtfSearchData.parse_obj(d) for d in data]
