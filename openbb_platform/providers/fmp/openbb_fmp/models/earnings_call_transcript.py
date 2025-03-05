"""FMP Earnings Call Transcript Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.earnings_call_transcript import (
    EarningsCallTranscriptData,
    EarningsCallTranscriptQueryParams,
)
from pydantic import field_validator


class FMPEarningsCallTranscriptQueryParams(EarningsCallTranscriptQueryParams):
    """FMP Earnings Call Transcript Query.

    Source: https://site.financialmodelingprep.com/developer/docs/earning-call-transcript-api/
    """

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "year": {"multiple_items_allowed": True},
    }


class FMPEarningsCallTranscriptData(EarningsCallTranscriptData):
    """FMP Earnings Call Transcript Data."""

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")


class FMPEarningsCallTranscriptFetcher(
    Fetcher[
        FMPEarningsCallTranscriptQueryParams,
        List[FMPEarningsCallTranscriptData],
    ]
):
    """FMP Earnings Call Transcript Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEarningsCallTranscriptQueryParams:
        """Transform the query params."""
        return FMPEarningsCallTranscriptQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEarningsCallTranscriptQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_data

        api_key = credentials.get("fmp_api_key") if credentials else ""
        symbols = query.symbol.split(",")
        years = query.year.split(",") if isinstance(query.year, str) else [query.year]

        def generate_url(symbol, year):
            """Generate the URL."""
            url = (
                f"https://financialmodelingprep.com/api/v4/batch_earning_call_transcript/{symbol}?"
                + f"year={year}&apikey={api_key}"
            )
            return url

        results: list = []
        for symbol in symbols:
            for year in years:
                response = await get_data(generate_url(symbol, year), **kwargs)
                if isinstance(response, list):
                    results.extend(response)

        return results

    @staticmethod
    def transform_data(
        query: FMPEarningsCallTranscriptQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPEarningsCallTranscriptData]:
        """Return the transformed data."""
        return [FMPEarningsCallTranscriptData.model_validate(d) for d in data]
