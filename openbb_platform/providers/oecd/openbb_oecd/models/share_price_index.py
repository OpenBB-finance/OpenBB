"""OECD Share Price Index Model."""

# pylint: disable=unused-argument

from datetime import date
from typing import Any, Dict, List, Optional
from warnings import warn

import xmltodict
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.share_price_index import (
    SharePriceIndexData,
    SharePriceIndexQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import check_item, make_request
from openbb_oecd.utils.constants import (
    CODE_TO_COUNTRY_CPI,
    COUNTRY_TO_CODE_CPI,
)
from openbb_oecd.utils.helpers import oecd_date_to_python_date
from pydantic import Field, field_validator

countries = tuple(CODE_TO_COUNTRY_CPI.values()) + ("all",)
CountriesList = list(countries)  # type: ignore
frequency_dict = {
    "monthly": "M",
    "quarter": "Q",
    "annual": "A",
}


class OECDSharePriceIndexQueryParams(SharePriceIndexQueryParams):
    """OECD Share Price Index Query.

    Source: https://data-explorer.oecd.org/?lc=en
    """

    __json_schema_extra__ = {"country": ["multiple_items_allowed"]}

    country: str = Field(
        description=QUERY_DESCRIPTIONS.get("country", ""),
        default="united_states",
        choices=CountriesList,
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, c):
        """Validate country."""
        result: List = []
        values = c.replace(" ", "_").split(",")
        for v in values:
            if v.upper() in CODE_TO_COUNTRY_CPI:
                result.append(CODE_TO_COUNTRY_CPI.get(v.upper()))
                continue
            try:
                check_item(v.lower(), CountriesList)
            except Exception as e:
                if len(values) == 1:
                    raise e from e
                else:
                    warn(f"Invalid country: {v}. Skipping...")
                    continue
            result.append(v.lower())
        if result:
            return ",".join(result)
        raise ValueError(f"No valid country found. -> {values}")


class OECDSharePriceIndexData(SharePriceIndexData):
    """OECD Share Price Index Data."""


class OECDSharePriceIndexFetcher(
    Fetcher[OECDSharePriceIndexQueryParams, List[OECDSharePriceIndexData]]
):
    """OECD Share Price Index Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> OECDSharePriceIndexQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        if transformed_params.get("start_date") is None:
            transformed_params["start_date"] = (
                date(2000, 1, 1)
                if transformed_params.get("country") == "all"
                else date(1958, 1, 1)
            )
        if transformed_params.get("end_date") is None:
            transformed_params["end_date"] = date(date.today().year, 12, 31)
        if transformed_params.get("country") is None:
            transformed_params["country"] = "united_states"

        return OECDSharePriceIndexQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: OECDSharePriceIndexQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the OECD endpoint."""
        frequency = frequency_dict.get(query.frequency)

        def country_string(input_str: str):
            if input_str == "all":
                return ""
            countries = input_str.split(",")
            return "+".join([COUNTRY_TO_CODE_CPI[country] for country in countries])

        country = country_string(query.country)
        start_date = query.start_date.strftime("%Y-%m") if query.start_date else ""
        end_date = query.end_date.strftime("%Y-%m") if query.end_date else ""
        url = (
            "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_FINMARK,4.0/"
            + f"{country}.{frequency}.SHARE......?"
            + f"startPeriod={start_date}&endPeriod={end_date}&dimensionAtObservation=AllDimensions"
        )
        response = make_request(url)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code}")
        xml = xmltodict.parse(response.text)
        obs = (
            xml.get("message:GenericData", {})
            .get("message:DataSet", {})
            .get("generic:Obs", [])
        )
        results: List = []
        for item in obs:
            new_item: Dict = {}
            date: str = ""
            country: str = ""
            obs_key = item.get("generic:ObsKey", {}).get("generic:Value", [])
            for key_obs in obs_key:
                if key_obs.get("@id") == "TIME_PERIOD":
                    date = key_obs.get("@value")
                    date = oecd_date_to_python_date(date) if date else ""
                elif key_obs.get("@id") == "REF_AREA":
                    country = CODE_TO_COUNTRY_CPI.get(key_obs.get("@value", ""), "")
                else:
                    continue
            obs_value = item.get("generic:ObsValue", {}).get("@value", "")
            if obs_value and ((date <= query.end_date) & (date >= query.start_date)):
                new_item["date"] = date
                new_item["country"] = country
                new_item["value"] = obs_value
                results.append(new_item)
        if not results:
            raise EmptyDataError()

        return results

    @staticmethod
    def transform_data(
        query: OECDSharePriceIndexQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[OECDSharePriceIndexData]:
        """Transform the data from the OECD endpoint."""
        return [OECDSharePriceIndexData.model_validate(d) for d in data]
