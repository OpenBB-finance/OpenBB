"""FMP Treasury Rates fetcher."""


from datetime import date as dateType
from typing import Dict, List, Optional


from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer, get_querystring
from openbb_provider.models.treasury_rates import (
    TreasuryRatesData,
    TreasuryRatesQueryParams,
)

# IMPORT THIRD-PARTY
from pydantic import Field

from openbb_fmp.utils.helpers import get_data_many


class FMPTreasuryRatesQueryParams(TreasuryRatesQueryParams):
    """FMP Stock News query.

    Source: https://site.financialmodelingprep.com/developer/docs/treasury-rates-api/

    Parameter
    ---------
    start_date : str
        The start date of the data.
    end_date : str
        The end date of the data. Default is today.
    """


class FMPTreasuryRatesData(Data):
    date: dateType
    month1: float = Field(alias="month_1")
    month2: float = Field(alias="month_2")
    month3: float = Field(alias="month_3")
    month6: float = Field(alias="month_6")
    year1: float = Field(alias="year_1")
    year2: float = Field(alias="year_2")
    year3: float = Field(alias="year_3")
    year5: float = Field(alias="year_5")
    year7: float = Field(alias="year_7")
    year10: float = Field(alias="year_10")
    year20: float = Field(alias="year_20")
    year30: float = Field(alias="year_30")


class FMPTreasuryRatesFetcher(
    Fetcher[
        TreasuryRatesQueryParams,
        TreasuryRatesData,
        FMPTreasuryRatesQueryParams,
        FMPTreasuryRatesData,
    ]
):
    @staticmethod
    def transform_query(
        query: TreasuryRatesQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPTreasuryRatesQueryParams:
        return FMPTreasuryRatesQueryParams(
            start_date=query.start_date, end_date=query.end_date
        )

    @staticmethod
    def extract_data(
        query: FMPTreasuryRatesQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPTreasuryRatesData]:
        if credentials:
            api_key = credentials.get("fmp_api_key")

        base_url = "https://financialmodelingprep.com/api/v4/"
        query_str = get_querystring(query.dict(), [])
        query_str = query_str.replace("start_date", "from").replace("end_date", "to")
        url = f"{base_url}treasury?{query_str}&apikey={api_key}"
        return get_data_many(url, FMPTreasuryRatesData)

    @staticmethod
    def transform_data(data: List[FMPTreasuryRatesData]) -> List[TreasuryRatesData]:
        return data_transformer(data, TreasuryRatesData)
