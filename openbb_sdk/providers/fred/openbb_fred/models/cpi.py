"""FRED CPI Fetcher."""


from typing import Any, Dict, List, Optional

from openbb_fred.utils.fred_base import Fred
from openbb_fred.utils.fred_helpers import all_cpi_options
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.cpi import CPIData, CPIQueryParams


class FREDCPIQueryParams(CPIQueryParams):
    """CPI query."""


class FREDCPIData(CPIData):
    """CPI data."""


class FREDCPIFetcher(Fetcher[CPIQueryParams, CPIData, FREDCPIQueryParams, FREDCPIData]):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FREDCPIQueryParams:
        return FREDCPIQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FREDCPIQueryParams, credentials: Optional[Dict[str, str]]
    ) -> Dict[str, List[CPIData]]:
        if credentials:
            api_key = credentials.get("fred_api_key")

        all_options = all_cpi_options(query.harmonized)

        step_1 = [x for x in all_options if x["country"] in query.countries]
        step_2 = [x for x in step_1 if x["units"] == query.units]
        step_3 = [x for x in step_2 if x["frequency"] == query.frequency]

        series_dict = {}

        fred = Fred(api_key)
        for item in step_3:
            loc = f"{item['country']}-{item['frequency']}-{item['units']}"
            temp = fred.get_series(item["series_id"], query.start_date, query.end_date)
            clean_temp = [FREDCPIData(**x) for x in temp]
            series_dict[loc] = clean_temp

        return series_dict

    @staticmethod
    def transform_data(data: Dict[str, List[CPIData]]) -> Dict[str, List[CPIData]]:
        return data
