"""FMP ETF Holdings Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_holdings_date import (
    EtfHoldingsDateData,
    EtfHoldingsDateQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import Field


class FMPEtfHoldingsDateQueryParams(EtfHoldingsDateQueryParams):
    """FMP ETF Holdings Query.

    Source: https://site.financialmodelingprep.com/developer/docs#Historical-ETF-Holdings
    """

    cik: Optional[str] = Field(
        description=QUERY_DESCRIPTIONS.get("cik", "")
        + "The CIK of the filing entity. Overrides symbol.",
        default=None,
    )


class FMPEtfHoldingsDateData(EtfHoldingsDateData):
    """FMP ETF Holdings Data."""


class FMPEtfHoldingsDateFetcher(
    Fetcher[
        FMPEtfHoldingsDateQueryParams,
        List[FMPEtfHoldingsDateData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEtfHoldingsDateQueryParams:
        """Transform the query."""
        return FMPEtfHoldingsDateQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEtfHoldingsDateQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            version=4,
            endpoint="etf-holdings/portfolio-date",
            api_key=api_key,
            query=query,
        )

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPEtfHoldingsDateQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FMPEtfHoldingsDateData]:
        """Return the transformed data."""
        return [FMPEtfHoldingsDateData.model_validate(d) for d in data]
