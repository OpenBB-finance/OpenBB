"""FRED Consumer Price Index Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional, Union

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.consumer_price_index import (
    ConsumerPriceIndexData,
    ConsumerPriceIndexQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import check_item
from openbb_fred.models.series import FredSeriesFetcher
from openbb_fred.utils.fred_helpers import CPI_COUNTRIES, CpiCountries, all_cpi_options
from pydantic import Field, field_validator


class FREDConsumerPriceIndexQueryParams(ConsumerPriceIndexQueryParams):
    """FRED Consumer Price Index Query."""

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": CPI_COUNTRIES,
        },
    }

    country: Union[CpiCountries, str] = Field(
        description=QUERY_DESCRIPTIONS.get("country"),
        default="united_states",
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, c: str):
        """Validate country."""
        result: List = []
        values = c.replace(" ", "_").split(",")
        for v in values:
            check_item(v.lower(), CPI_COUNTRIES)
            result.append(v.lower())
        return ",".join(result)


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
    async def aextract_data(
        query: FREDConsumerPriceIndexQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Extract data."""
        frequency = "quarterly" if query.frequency == "quarter" else query.frequency

        # Convert the params to series IDs.
        all_options = all_cpi_options(query.harmonized)
        units_dict = {
            "period": "growth_previous",
            "yoy": "growth_same",
            "index": "index_2015",
        }
        units = (
            "growth_same"
            if query.transform == "period" and frequency == "annual"
            else units_dict.get(query.transform)
        )
        step_1 = [x for x in all_options if x["country"] in query.country]
        step_2 = [x for x in step_1 if x["units"] == units]
        step_3 = [x for x in step_2 if x["frequency"] == frequency]
        ids = [item["series_id"] for item in step_3]
        country_map = {item["series_id"]: item["country"] for item in step_3}
        item_query = dict(
            symbol=",".join(ids),
            start_date=query.start_date,
            end_date=query.end_date,
        )
        results: Dict = {}
        temp = await FredSeriesFetcher.fetch_data(item_query, credentials)
        result = [d.model_dump() for d in temp.result]
        results["metadata"] = {country_map.get(k): v for k, v in temp.metadata.items()}
        results["data"] = [
            {country_map.get(k, k): v for k, v in d.items()} for d in result
        ]

        return results

    @staticmethod
    def transform_data(
        query: FREDConsumerPriceIndexQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> AnnotatedResult[List[FREDConsumerPriceIndexData]]:
        """Transform data and validate the model."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        df = DataFrame.from_records(data["data"])
        if df.empty:
            raise EmptyDataError(
                "No data found for the given query. Try adjusting the parameters."
            )
        # Flatten the data as a pivot table.
        df = (
            df.melt(id_vars="date", var_name="country", value_name="value")
            .query("value.notnull()")
            .set_index(["date", "country"])
            .sort_index()
            .reset_index()
        )
        # Normalize the percent values.
        if query.transform in ("period", "yoy"):
            df["value"] = df["value"] / 100

        records = df.to_dict(orient="records")
        metadata = data.get("metadata", {})
        return AnnotatedResult(
            result=[FREDConsumerPriceIndexData.model_validate(r) for r in records],
            metadata=metadata,
        )
