"""FMP Earnings Call Transcript fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.earnings_call_transcript import (
    EarningsCallTranscriptData,
    EarningsCallTranscriptQueryParams,
)
from pydantic import validator

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPEarningsCallTranscriptQueryParams(EarningsCallTranscriptQueryParams):
    """FMP Earnings Calendar Query.

    Source: https://site.financialmodelingprep.com/developer/docs/earning-call-transcript-api/
    """

    @validator("year", pre=True, check_fields=False)
    def time_validate(cls, v: int):  # pylint: disable=E0213
        current_year = datetime.now().year
        return current_year if v > current_year or v < 1950 else v


class FMPEarningsCallTranscriptData(EarningsCallTranscriptData):
    """FMP Earnings Call Transcript Data."""

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v: str):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")


class FMPEarningsCallTranscriptFetcher(
    Fetcher[
        FMPEarningsCallTranscriptQueryParams,
        List[FMPEarningsCallTranscriptData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEarningsCallTranscriptQueryParams:
        return FMPEarningsCallTranscriptQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPEarningsCallTranscriptQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[FMPEarningsCallTranscriptData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            4,
            f"batch_earning_call_transcript/{query.symbol}",
            api_key,
            query,
            ["symbol"],
        )
        return get_data_many(url, FMPEarningsCallTranscriptData, **kwargs)

    @staticmethod
    def transform_data(
        data: List[FMPEarningsCallTranscriptData],
    ) -> List[FMPEarningsCallTranscriptData]:
        return data
