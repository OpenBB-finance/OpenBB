"""OECD Immediate Interest Rate Data."""

# pylint: disable=unused-argument

from datetime import date
from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.immediate_interest_rate import (
    ImmediateInterestRateData,
    ImmediateInterestRateQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import check_item
from openbb_oecd.utils.constants import CODE_TO_COUNTRY_IR, COUNTRY_TO_CODE_IR
from pydantic import Field, field_validator

countries = tuple(CODE_TO_COUNTRY_IR.values()) + ("all",)
CountriesList = list(countries)
frequency_dict = {
    "monthly": "M",
    "quarter": "Q",
    "annual": "A",
}


class OECDImmediateInterestRateQueryParams(ImmediateInterestRateQueryParams):
    """OECD Immediate Interest Rate Query.

    Source: https://data-explorer.oecd.org/?lc=en
    """

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": CountriesList,
        }
    }

    country: str = Field(
        description=QUERY_DESCRIPTIONS.get("country", ""),
        default="united_states",
    )
    frequency: Literal["monthly", "quarter", "annual"] = Field(
        description=QUERY_DESCRIPTIONS.get("frequency", ""),
        default="monthly",
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, c):
        """Validate country."""
        result: List = []
        values = c.replace(" ", "_").split(",")
        for v in values:
            if v.upper() in CODE_TO_COUNTRY_IR:
                result.append(CODE_TO_COUNTRY_IR.get(v.upper()))
                continue
            try:
                check_item(v.lower(), CountriesList)
            except Exception as e:
                if len(values) == 1:
                    raise e from e
                warn(f"Invalid country: {v}. Skipping...")
                continue
            result.append(v.lower())
        if result:
            return ",".join(result)
        raise OpenBBError(f"No valid country found. -> {values}")


class OECDImmediateInterestRateData(ImmediateInterestRateData):
    """OECD Immediate Interest Rate Data."""


class OECDImmediateInterestRateFetcher(
    Fetcher[OECDImmediateInterestRateQueryParams, List[OECDImmediateInterestRateData]]
):
    """Transform the query, extract and transform the data from the OECD endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> OECDImmediateInterestRateQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        if transformed_params.get("start_date") is None:
            transformed_params["start_date"] = (
                date(2020, 1, 1)
                if transformed_params.get("country") == "all"
                else date(1954, 1, 1)
            )
        if transformed_params.get("end_date") is None:
            transformed_params["end_date"] = date(date.today().year, 12, 31)
        if transformed_params.get("country") is None:
            transformed_params["country"] = "united_states"

        return OECDImmediateInterestRateQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: OECDImmediateInterestRateQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the OECD endpoint."""
        # pylint: disable=import-outside-toplevel
        from io import StringIO  # noqa
        from openbb_oecd.utils.helpers import oecd_date_to_python_date  # noqa
        from pandas import read_csv  # noqa
        from openbb_core.provider.utils.helpers import make_request  # noqa

        frequency = frequency_dict.get(query.frequency, "Q")

        def country_string(input_str: str):
            if input_str == "all":
                return ""
            _countries = input_str.split(",")
            return "+".join([COUNTRY_TO_CODE_IR[country] for country in _countries])

        country = country_string(query.country) if query.country else ""
        start_date = query.start_date.strftime("%Y-%m") if query.start_date else ""
        end_date = query.end_date.strftime("%Y-%m") if query.end_date else ""
        url = (
            "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_FINMARK,4.0/"
            + f"{country}.{frequency}.IRSTCI.PA.....?"
            + f"startPeriod={start_date}&endPeriod={end_date}"
            + "&dimensionAtObservation=TIME_PERIOD&detail=dataonly"
        )
        headers = {"Accept": "application/vnd.sdmx.data+csv; charset=utf-8"}
        response = make_request(url, headers=headers, timeout=20)
        if response.status_code != 200:
            raise Exception(f"Error with the OECD request: {response.status_code}")
        df = read_csv(StringIO(response.text)).get(
            ["REF_AREA", "TIME_PERIOD", "OBS_VALUE"]
        )
        if df.empty:
            raise EmptyDataError()
        df = df.rename(
            columns={"REF_AREA": "country", "TIME_PERIOD": "date", "OBS_VALUE": "value"}
        )
        df.country = [CODE_TO_COUNTRY_IR.get(d, d) for d in df.country]
        df.date = df.date.apply(oecd_date_to_python_date)
        df.value = df.value.astype(float) / 100
        df = (
            df.query("value.notnull()")
            .set_index(["date", "country"])
            .sort_index()
            .reset_index()
        )

        return df.to_dict("records")

    @staticmethod
    def transform_data(
        query: OECDImmediateInterestRateQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[OECDImmediateInterestRateData]:
        """Transform the data from the OECD endpoint."""
        return [OECDImmediateInterestRateData.model_validate(d) for d in data]
