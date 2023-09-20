"""Quandl SP500 Multiples Fetcher."""

from typing import Any, Dict, List, Optional

import quandl
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.sp500_multiples import (
    SP500MultiplesData,
    SP500MultiplesQueryParams,
)
from openbb_quandl.utils.series_ids import SP500MULTIPLES


class QuandlSP500MultiplesQueryParams(SP500MultiplesQueryParams):
    """SP500 Multiples query."""


class QuandlSP500MultiplesData(SP500MultiplesData):
    """SP500 Multiples data."""


class QuandlSP500MultiplesFetcher(
    Fetcher[QuandlSP500MultiplesQueryParams, List[QuandlSP500MultiplesData]]
):
    """Quandl SP500 Multiples Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> QuandlSP500MultiplesQueryParams:
        return QuandlSP500MultiplesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: QuandlSP500MultiplesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> List[Dict]:
        """Get the raw Quandl Data."""
        api_key = credentials.get("quandl_api_key") if credentials else ""

        if "Year" in query.series_name:
            query.collapse = "annual"
        if "Quarter" in query.series_name:
            query.collapse = "quarterly"

        data = (
            quandl.get(
                SP500MULTIPLES[query.series_name],
                start_date=query.start_date,
                end_date=query.end_date,
                collapse=query.collapse,
                transform=query.transform,
                api_key=api_key,
                **kwargs,
            )
            .reset_index()
            .rename(columns={"Date": "date", "Value": "value"})
        )
        data["date"] = data["date"].dt.strftime("%Y-%m-%d")

        return data.to_dict("records")

    @staticmethod
    def transform_data(
        data: List[Dict],
    ) -> List[QuandlSP500MultiplesData]:
        """Parse data into the QuandlSP500MultiplesData format."""
        return [QuandlSP500MultiplesData.parse_obj(d) for d in data]
