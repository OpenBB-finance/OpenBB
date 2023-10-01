"""Blackrock ETF Info fetcher."""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_info import (
    EtfInfoData,
    EtfInfoQueryParams,
)
from pydantic import Field

from openbb_blackrock.utils.helpers import COUNTRIES, America, Canada


class BlackrockEtfInfoQueryParams(EtfInfoQueryParams):
    """Blackrock ETF Info Query Params"""

    country: COUNTRIES = Field(
        description="The country the ETF is registered in. '.TO' acts as a proxy to 'canada'.",
        default="america",
    )


class BlackrockEtfInfoData(EtfInfoData):
    """Blackrock ETF Search Data."""

    name: str = Field(description="The name of the ETF.")

    asset_class: Optional[str] = Field(
        description="The asset class of the ETF.", default=None
    )
    sub_asset_class: Optional[str] = Field(
        description="The sub-asset class of the ETF.", default=None
    )
    country: Optional[str] = Field(
        description="The country the ETF is registered in.", default=None
    )
    region: Optional[str] = Field(description="The region of the ETF.", default=None)
    investment_style: Optional[str] = Field(
        description="The investment style of the ETF.",
        alias="investment_style",
        default=None,
    )
    yield_ttm: Optional[float] = Field(
        description="The TTM yield of the ETF.", default=None
    )
    aum: Optional[float] = Field(
        description="The value of the assets under management.",
        alias="aum",
        default=None,
    )


class BlackrockEtfInfoFetcher(
    Fetcher[
        BlackrockEtfInfoQueryParams,
        List[BlackrockEtfInfoData],
    ]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BlackrockEtfInfoQueryParams:
        """Transform the query."""
        return BlackrockEtfInfoQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BlackrockEtfInfoQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Blackrock endpoint."""

        query.symbol = query.symbol.upper()
        symbols = query.symbol.split(",") if "," in query.symbol else [query.symbol]
        results = pd.DataFrame()

        canada_etfs = Canada.get_all_etfs()
        america_etfs = America.get_all_etfs()

        def get_one(symbol: str, country: str = "america") -> pd.Series:
            COLUMNS = [
                "symbol",
                "inceptionDate",
                "fundName",
                "aladdinAssetClass",
                "aladdinSubAssetClass",
                "aladdinCountry",
                "aladdinRegion",
                "investmentStyle",
                "weightedAvgYieldToMaturity",
                "twelveMonTrlYield",
                "totalNetAssets",
            ]

            COUNTRY_COLUMNS = {
                "canada": [
                    "navYearToDate",
                    "navOneYearAnnualized",
                    "distYield",
                    "premiumDiscount",
                    "mer",
                ],
                "america": [
                    "navAmount",
                    "navYearToDate",
                    "navOneYearAnnualized",
                    "fees",
                    "yieldToWorst",
                    "cleanDuration",
                    "effectiveDuration",
                    "esgMsciQualityScore",
                    "esgRating",
                    "wtdAvgCarbonIntensity",
                    "cusip",
                    "isin",
                ],
            }

            COLS_DICT = {
                "navAmount": "nav",
                "totalNetAssets": "aum",
                "inceptionDate": "inception_date",
                "fundName": "name",
                "aladdinAssetClass": "asset_class",
                "aladdinSubAssetClass": "sub_asset_class",
                "aladdinCountry": "country",
                "aladdinRegion": "region",
                "investmentStyle": "investment_style",
                "distYield": "yield",
                "twelveMonTrlYield": "yield_ttm",
                "navYearToDate": "nav_ytd",
                "navOneYearAnnualized": "nav_1y",
                "premiumDiscount": "premium_discount",
                "weightedAvgYieldToMaturity": "avg_ytm",
                "esgRating": "esg_rating",
                "esgMsciQualityScore": "esg_msci_quality_score",
                "wtdAvgCarbonIntensity": "avg_carbon_intensity",
                "yieldToWorst": "yield_to_worst",
                "effectiveDuration": "duration",
                "mer": "fees",
            }

            data = pd.Series(dtype="object")
            if ".TO" in symbol or country == "canada":
                symbol = symbol.replace(".TO", "")  # noqa
                country = "canada"

            _etfs = america_etfs if country == "america" else canada_etfs
            if symbol in _etfs["symbol"].to_list():
                data = _etfs[_etfs["symbol"] == symbol][
                    COLUMNS + COUNTRY_COLUMNS[country]
                ]

                data.rename(columns=COLS_DICT, inplace=True)

                data = data.transpose().iloc[:, 0].rename(symbol)
                data["inception_date"] = pd.to_datetime(
                    data["inception_date"], format="%Y%m%d"
                ).strftime("%Y-%m-%d")

            return data

        for symbol in symbols:
            results = pd.concat([results, get_one(symbol).transpose()], axis=1)

        return (
            results.transpose()
            .reset_index(drop=True)
            .dropna(how="all")
            .to_dict("records")
        )

    @staticmethod
    def transform_data(data: List[Dict]) -> List[BlackrockEtfInfoData]:
        """Transform the data to the standard format."""
        return [BlackrockEtfInfoData.parse_obj(d) for d in data]
