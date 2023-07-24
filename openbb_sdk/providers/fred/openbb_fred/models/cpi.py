"""FRED CPI Fetcher."""


from typing import Dict, List, Optional

from openbb_fred.utils.fred_base import Fred
from openbb_fred.utils.fred_helpers import all_cpi_options
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer

# IMPORT THIRD-PARTY

from openbb_provider.models.cpi import CPIData, CPIDataPoint, CPIQueryParams


class FREDCPIQueryParams(CPIQueryParams):
    """CPI query.
    When other provders are added, this will probably need less strict types

    Parameter
    ---------
    countries: List[CPI_COUNTRIES]
        The country or countries you want to see.
    units: List[CPI_UNITS]
        The units you want to see, can be "growth_previous", "growth_same" or "index_2015".
    frequency: List[CPI_FREQUENCY]
        The frequency you want to see, either "annual", monthly" or "quarterly".
    harmonized: bool
        Whether you wish to obtain harmonized data.
    start_date: Optional[date]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[date]
        End date, formatted YYYY-MM-DD
    """


class FREDCPIData(CPIData):
    """CPI data."""


class FREDCPIFetcher(Fetcher[CPIQueryParams, CPIData, FREDCPIQueryParams, FREDCPIData]):
    @staticmethod
    def transform_query(
        query: CPIQueryParams, extra_params: Optional[Dict] = None
    ) -> FREDCPIQueryParams:
        return FREDCPIQueryParams(
            countries=query.countries,
            units=query.units,
            frequency=query.frequency,
            harmonized=query.harmonized,
            start_date=query.start_date,
            end_date=query.end_date,
            **extra_params if extra_params else {},
        )

    @staticmethod
    def extract_data(
        query: FREDCPIQueryParams, credentials: Optional[Dict[str, str]]
    ) -> FREDCPIData:
        if credentials:
            api_key = credentials.get("fred_api_key")

        all_options = all_cpi_options(query.harmonized)

        step_1 = [x for x in all_options if x["country"] in query.countries]
        step_2 = [x for x in step_1 if x["units"] == query.units]
        step_3 = [x for x in step_2 if x["frequency"] == query.frequency]

        if not step_3:
            FREDCPIData(data={})

        series_dict = {}

        fred = Fred(api_key)
        for item in step_3:
            loc = f"{item['country']}-{item['frequency']}-{item['units']}"
            temp = fred.get_series(item["series_id"], query.start_date, query.end_date)
            clean_temp = [CPIDataPoint(**x) for x in temp]
            series_dict[loc] = clean_temp

        return FREDCPIData(data=series_dict)

    @staticmethod
    def transform_data(data: List[FREDCPIData]) -> List[CPIData]:
        return data_transformer(data, CPIData)
