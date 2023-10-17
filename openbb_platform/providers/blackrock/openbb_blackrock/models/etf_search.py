"""Blackrock ETF Search fetcher."""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_blackrock.utils.helpers import COUNTRIES, America, Canada, camel_to_snake
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_search import (
    EtfSearchData,
    EtfSearchQueryParams,
)
from pydantic import Field


class BlackrockEtfSearchQueryParams(EtfSearchQueryParams):
    """Blackrock ETF Search Query Params"""

    country: COUNTRIES = Field(
        description="The country the ETF is registered in.", default="america"
    )


class BlackrockEtfSearchData(EtfSearchData):
    """Blackrock ETF Search Data."""

    name: Optional[str] = Field(description="The name of the ETF.", alias="fund_name")

    asset_class: Optional[str] = Field(
        description="The asset class of the ETF.",
        alias="aladdin_asset_class",
        default=None,
    )
    sub_asset_class: Optional[str] = Field(
        description="The sub-asset class of the ETF.",
        alias="aladdin_sub_asset_class",
        default=None,
    )
    region: Optional[str] = Field(
        description="The region of the ETF.", alias="aladdin_region", default=None
    )
    country: Optional[str] = Field(
        description="The country the ETF is registered in.",
        alias="aladdin_country",
        default=None,
    )
    market_type: Optional[str] = Field(
        description="The market type of the ETF.",
        alias="aladdin_market_type",
        default=None,
    )
    investment_style: Optional[str] = Field(
        description="The investment style of the ETF.",
        alias="investment_style",
        default=None,
    )
    investment_strategy: Optional[str] = Field(
        description="The investment strategy of the ETF.",
        alias="aladdin_strategy",
        default=None,
    )
    nav: Optional[float] = Field(
        description="The value of the assets under management.",
        alias="total_net_assets",
        default=None,
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

        etfs = pd.DataFrame()
        results = pd.DataFrame()

        if query.country == "america":
            etfs = America.get_all_etfs().set_index("symbol")
            etfs = etfs.rename(
                columns={"aladdinEsgClassification": "EsgClassification"}
            )
        if query.country == "canada":
            etfs = Canada.get_all_etfs().set_index("symbol")

        results = etfs[
            etfs["fundName"].str.contains(query.query, case=False)  # type: ignore
            | etfs["aladdinSubAssetClass"].str.contains(query.query, case=False)  # type: ignore
            | etfs["aladdinAssetClass"].str.contains(query.query, case=False)  # type: ignore
            | etfs["aladdinRegion"].str.contains(query.query, case=False)  # type: ignore
            | etfs["aladdinCountry"].str.contains(query.query, case=False)  # type: ignore
            | etfs["aladdinMarketType"].str.contains(query.query, case=False)  # type: ignore
        ]

        results.columns = [camel_to_snake(c) for c in results.columns]
        results = results.drop(columns=["product_page_url"])

        return results.reset_index().fillna(value=0).to_dict("records")

    @staticmethod
    def transform_data(data: List[Dict], **kwargs: Any) -> List[BlackrockEtfSearchData]:
        """Transform the data to the standard format."""
        return [BlackrockEtfSearchData.model_validate(d) for d in data]
