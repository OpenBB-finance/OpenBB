"""FMP Earnings Call Transcript Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.earnings_call_transcript import (
    EarningsCallTranscriptData,
    EarningsCallTranscriptQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import field_validator


class FMPEarningsCallTranscriptQueryParams(EarningsCallTranscriptQueryParams):
    """FMP Earnings Call Transcript Query.

    Source: https://site.financialmodelingprep.com/developer/docs/earning-call-transcript-api/
    """

    @field_validator("year", mode="before", check_fields=False)
    @classmethod
    def time_validate(cls, v: int):  # pylint: disable=E0213
        """Return the year as an integer."""
        current_year = datetime.now().year
        return current_year if v > current_year or v < 1950 else v


class FMPEarningsCallTranscriptData(EarningsCallTranscriptData):
    """FMP Earnings Call Transcript Data."""

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v: str):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")


class FMPEarningsCallTranscriptFetcher(
    Fetcher[
        FMPEarningsCallTranscriptQueryParams,
        List[FMPEarningsCallTranscriptData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

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
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            4,
            f"batch_earning_call_transcript/{query.symbol}",
            api_key,
            query,
            ["symbol"],
        )

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPEarningsCallTranscriptQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPEarningsCallTranscriptData]:
        """Return the transformed data."""
        return [FMPEarningsCallTranscriptData.model_validate(d) for d in data]
