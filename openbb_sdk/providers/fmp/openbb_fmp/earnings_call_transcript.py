"""FMP Earnings Call Transcript fetcher."""

# IMPORT STANDARD
from typing import Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer

# IMPORT INTERNAL
from openbb_provider.models.earnings_call_transcript import (
    EarningsCallTranscriptData,
    EarningsCallTranscriptQueryParams,
)

# IMPORT THIRD-PARTY
from .helpers import create_url, get_data_many


class FMPEarningsCallTranscriptQueryParams(EarningsCallTranscriptQueryParams):
    """FMP Earnings Calendar query.

    Source: https://site.financialmodelingprep.com/developer/docs/earnings-calendar-api/

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """


class FMPEarningsCallTranscriptData(EarningsCallTranscriptData):
    """FMP Earnings Call Transcript data."""


class FMPEarningsCallTranscriptFetcher(
    Fetcher[
        EarningsCallTranscriptQueryParams,
        EarningsCallTranscriptData,
        FMPEarningsCallTranscriptQueryParams,
        FMPEarningsCallTranscriptData,
    ]
):
    @staticmethod
    def transform_query(
        query: EarningsCallTranscriptQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPEarningsCallTranscriptQueryParams:
        return FMPEarningsCallTranscriptQueryParams.parse_obj(query)

    @staticmethod
    def extract_data(
        query: FMPEarningsCallTranscriptQueryParams,
        credentials: Optional[Dict[str, str]],
    ) -> List[FMPEarningsCallTranscriptData]:
        if credentials:
            api_key = credentials.get("FMP_API_KEY")

        url = create_url(
            4,
            f"batch_earning_call_transcript/{query.symbol}",
            api_key,
            query,
            ["symbol"],
        )
        return get_data_many(url, FMPEarningsCallTranscriptData)

    @staticmethod
    def transform_data(
        data: List[FMPEarningsCallTranscriptData],
    ) -> List[EarningsCallTranscriptData]:
        return data_transformer(data, EarningsCallTranscriptData)
