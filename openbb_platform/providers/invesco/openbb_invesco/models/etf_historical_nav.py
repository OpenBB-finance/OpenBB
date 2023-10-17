"""Invesco ETF Historical NAV fetcher."""

from io import StringIO
from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_invesco.utils.helpers import (
    COUNTRIES,
    America,
)
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_historical_nav import (
    EtfHistoricalNavData,
    EtfHistoricalNavQueryParams,
)
from openbb_provider.utils.helpers import make_request
from pydantic import Field


class InvescoEtfHistoricalNavQueryParams(EtfHistoricalNavQueryParams):
    """Invesco ETF Historical NAV query.

    Source: https://www.invesco.com/
    """

    country: Optional[COUNTRIES] = Field(
        description="The country the ETF is registered in.", default="america"
    )


class InvescoEtfHistoricalNavData(EtfHistoricalNavData):
    """Invesco ETF Historical NAV Data."""

    __alias_dict__ = {
        "nav": "NAV",
        "date": "Date",
    }


class InvescoEtfHistoricalNavFetcher(
    Fetcher[
        InvescoEtfHistoricalNavQueryParams,
        List[InvescoEtfHistoricalNavData],
    ]
):
    """Transform the query, extract and transform the data from the Invesco endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> InvescoEtfHistoricalNavQueryParams:
        """Transform the query."""
        return InvescoEtfHistoricalNavQueryParams(**params)

    @staticmethod
    def extract_data(
        query: InvescoEtfHistoricalNavQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Invesco endpoint."""

        etfs = pd.DataFrame()
        nav = pd.DataFrame()
        results = []
        if query.country == "america":
            etfs = America.get_all_etfs()

            if query.symbol not in etfs["Ticker"].to_list():
                raise ValueError(
                    f"Symbol is not supported, or not a valid Invesco ETF -> {query.symbol}"
                )

            url = (
                "https://www.invesco.com/us/financial-products/etfs/product-detail/"
                f"main/sidebar/0?audienceType=Investor&action=download&ticker={query.symbol}"
            )

            r = make_request(url)

            if r.status_code != 200:
                raise RuntimeError(f"HTTP Error -> {str(r.status_code)}")

            nav = pd.read_csv(StringIO(r.text))
            nav["Date"] = pd.to_datetime(nav["Date"], yearfirst=True).dt.strftime(
                "%Y-%m-%d"
            )
            nav["NAV"] = nav["NAV"].astype(float)
            results = (
                nav[["Date", "NAV"]]
                .sort_values(by="Date", ascending=True)
                .to_dict(orient="records")
            )

        return results

    @staticmethod
    def transform_data(
        data: List[Dict],
        **kwargs: Any,
    ) -> List[InvescoEtfHistoricalNavData]:
        """Transform the data."""
        return [InvescoEtfHistoricalNavData.model_validate(d) for d in data]
