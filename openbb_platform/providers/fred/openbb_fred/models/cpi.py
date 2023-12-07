"""FRED Consumer Price Index Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cpi import (
    ConsumerPriceIndexData,
    ConsumerPriceIndexQueryParams,
)
from openbb_fred.utils.fred_base import Fred
from openbb_fred.utils.fred_helpers import all_cpi_options


class FREDConsumerPriceIndexQueryParams(ConsumerPriceIndexQueryParams):
    """FRED Consumer Price Index Query."""


class FREDConsumerPriceIndexData(ConsumerPriceIndexData):
    """FRED Consumer Price Index Data."""


class FREDConsumerPriceIndexFetcher(
    Fetcher[FREDConsumerPriceIndexQueryParams, List[FREDConsumerPriceIndexData]]
):
    """Transform the query, extract and transform the data from the FRED endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FREDConsumerPriceIndexQueryParams:
        """Transform query."""
        return FREDConsumerPriceIndexQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FREDConsumerPriceIndexQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Extract data."""
        api_key = credentials.get("fred_api_key") if credentials else ""

        all_options = all_cpi_options(query.harmonized)

        step_1 = [x for x in all_options if x["country"] in query.countries]
        step_2 = [x for x in step_1 if x["units"] == query.units]
        step_3 = [x for x in step_2 if x["frequency"] == query.frequency]

        series_dict = {}
        fred = Fred(api_key)
        for item in step_3:
            loc = f"{item['country']}"
            temp = fred.get_series(
                item["series_id"], query.start_date, query.end_date, **kwargs
            )
            temp = [{"date": item["date"], "value": item["value"]} for item in temp]
            series_dict[loc] = [item for item in temp if item["value"] != "."]

        return series_dict

    @staticmethod
    def transform_data(
        query: FREDConsumerPriceIndexQueryParams, data: Dict, **kwargs: Any
    ) -> List[FREDConsumerPriceIndexData]:
        """Transform data."""
        transformed_data = {}

        # Iterate over the series_dict
        for country, data_list in data.items():
            for item in data_list:
                # If the date is not in the dictionary, add it
                if item["date"] not in transformed_data:
                    transformed_data[item["date"]] = {"date": item["date"]}
                # Update the dictionary with the country's value data
                transformed_data[item["date"]].update({country: item["value"]})

        # Convert the dictionary to a list of dictionaries
        transformed_data = list(transformed_data.values())

        return [
            FREDConsumerPriceIndexData.model_validate(item) for item in transformed_data
        ]
