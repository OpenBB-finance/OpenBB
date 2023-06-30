"""FMP Historical Dividends fetcher."""
# IMPORT STANDARD
from datetime import date as dateType
from datetime import datetime
from typing import Dict, List, Optional

# IMPORT THIRD-PARTY
from pydantic import validator

from builtin_providers.fmp.helpers import create_url, get_data_many
from openbb_provider.model.abstract.data import Data

# IMPORT INTERNAL
from openbb_provider.model.data.historical_dividends import (
    HistoricalDividendsData,
    HistoricalDividendsQueryParams,
)
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer


class FMPHistoricalDividendsQueryParams(HistoricalDividendsQueryParams):
    """FMP Earnings Calendar query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Historical-Dividends

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """

    __name__ = "FMPHistoricalDividendsQueryParams"


class FMPHistoricalDividendsData(Data):
    __name__ = "FMPHistoricalDividendsData"

    date: dateType
    label: str
    adjDividend: float
    dividend: float
    recordDate: Optional[dateType]
    paymentDate: Optional[dateType]
    declarationDate: Optional[dateType]

    @validator("declarationDate", pre=True)
    def declaration_date_validate(cls, v: str):  # pylint: disable=E0213
        if v:
            return datetime.strptime(v, "%Y-%m-%d").date()
        return None

    @validator("recordDate", pre=True)
    def record_date_validate(cls, v: str):  # pylint: disable=E0213
        if v:
            return datetime.strptime(v, "%Y-%m-%d").date()
        return None

    @validator("paymentDate", pre=True)
    def payment_date_validate(cls, v: str):  # pylint: disable=E0213
        if v:
            return datetime.strptime(v, "%Y-%m-%d").date()
        return None


class FMPHistoricalDividendsFetcher(
    Fetcher[
        HistoricalDividendsQueryParams,
        HistoricalDividendsData,
        FMPHistoricalDividendsQueryParams,
        FMPHistoricalDividendsData,
    ]
):
    @staticmethod
    def transform_query(
        query: HistoricalDividendsQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPHistoricalDividendsQueryParams:
        return FMPHistoricalDividendsQueryParams(symbol=query.symbol)

    @staticmethod
    def extract_data(
        query: FMPHistoricalDividendsQueryParams, api_key: str
    ) -> List[FMPHistoricalDividendsData]:
        url = create_url(
            3, f"historical-price-full/stock_dividend/{query.symbol}", api_key
        )
        return get_data_many(url, FMPHistoricalDividendsData, "historical")

    @staticmethod
    def transform_data(
        data: List[FMPHistoricalDividendsData],
    ) -> List[HistoricalDividendsData]:
        return data_transformer(data, HistoricalDividendsData)
