"""FMP Earnings Call Transcript fetcher."""

# IMPORT STANDARD
from typing import Dict, List, Optional

# IMPORT INTERNAL
from openbb_provider.model.data.earnings_call_transcript import (
    EarningsCallTranscriptData,
    EarningsCallTranscriptQueryParams,
)
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer

# IMPORT THIRD-PARTY
from builtin_providers.fmp.helpers import create_url, get_data_many


class FMPEarningsCallTranscriptQueryParams(EarningsCallTranscriptQueryParams):
    """FMP Earnings Calendar query.

    Source: https://site.financialmodelingprep.com/developer/docs/earnings-calendar-api/

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """

    __name__ = "FMPEarningsCallTranscriptQueryParams"


class FMPEarningsCallTranscriptData(EarningsCallTranscriptData):
    __name__ = "FMPEarningsCallTranscriptData"


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
        query: FMPEarningsCallTranscriptQueryParams, api_key: str
    ) -> List[FMPEarningsCallTranscriptData]:
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
