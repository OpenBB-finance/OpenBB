"""OECD Unemployment Data."""

# pylint: disable=unused-argument

from datetime import date
from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.unemployment import (
    UnemploymentData,
    UnemploymentQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import check_item
from openbb_oecd.utils.constants import (
    CODE_TO_COUNTRY_UNEMPLOYMENT,
    COUNTRY_TO_CODE_UNEMPLOYMENT,
)
from pydantic import Field, field_validator

countries = tuple(CODE_TO_COUNTRY_UNEMPLOYMENT.values()) + ("all",)
CountriesList = sorted(list(countries))  # type: ignore
AGES = [
    "total",
    "15-24",
    "25+",
]
AgesLiteral = Literal[
    "total",
    "15-24",
    "25+",
]


class OECDUnemploymentQueryParams(UnemploymentQueryParams):
    """OECD Unemployment Query.

    Source: https://data-explorer.oecd.org/?lc=en
    """

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": CountriesList,
        },
    }

    country: str = Field(
        description=QUERY_DESCRIPTIONS.get("country", ""),
        default="united_states",
    )
    sex: Literal["total", "male", "female"] = Field(
        description="Sex to get unemployment for.",
        default="total",
        json_schema_extra={"choices": ["total", "male", "female"]},
    )
    age: Literal[AgesLiteral] = Field(
        description="Age group to get unemployment for. Total indicates 15 years or over",
        default="total",
        json_schema_extra={"choices": AGES},  # type: ignore
    )
    seasonal_adjustment: bool = Field(
        description="Whether to get seasonally adjusted unemployment. Defaults to False.",
        default=False,
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, c):
        """Validate country."""
        result: List = []
        values = c.replace(" ", "_").split(",")
        for v in values:
            if v.upper() in CODE_TO_COUNTRY_UNEMPLOYMENT:
                result.append(CODE_TO_COUNTRY_UNEMPLOYMENT.get(v.upper()))
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


class OECDUnemploymentData(UnemploymentData):
    """OECD Unemployment Data."""


class OECDUnemploymentFetcher(
    Fetcher[OECDUnemploymentQueryParams, List[OECDUnemploymentData]]
):
    """Transform the query, extract and transform the data from the OECD endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> OECDUnemploymentQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        if transformed_params["start_date"] is None:
            transformed_params["start_date"] = (
                date(2010, 1, 1)
                if transformed_params.get("country") == "all"
                else date(1950, 1, 1)
            )
        if transformed_params["end_date"] is None:
            transformed_params["end_date"] = date(date.today().year, 12, 31)

        return OECDUnemploymentQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: OECDUnemploymentQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the OECD endpoint."""
        # pylint: disable=import-outside-toplevel
        from io import StringIO  # noqa
        from openbb_core.provider.utils.helpers import make_request  # noqa
        from openbb_oecd.utils import helpers  # noqa
        from pandas import read_csv  # noqa

        sex = {"total": "_T", "male": "M", "female": "F"}[query.sex]
        frequency = query.frequency[0].upper()
        age = {
            "total": "Y_GE15",
            "15-24": "Y15T24",
            "25+": "Y_GE25",
        }[query.age]
        seasonal_adjustment = "Y" if query.seasonal_adjustment else "N"

        def country_string(input_str: str):
            if input_str == "all":
                return ""
            _countries = input_str.split(",")
            return "+".join(
                [COUNTRY_TO_CODE_UNEMPLOYMENT[country] for country in _countries]
            )

        country = country_string(query.country)
        start_date = query.start_date.strftime("%Y-%m") if query.start_date else ""
        end_date = query.end_date.strftime("%Y-%m") if query.end_date else ""
        url = (
            "https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_LFS@DF_IALFS_UNE_M,1.0/"
            + f"{country}..._Z.{seasonal_adjustment}.{sex}.{age}..{frequency}"
            + f"?startPeriod={start_date}&endPeriod={end_date}"
            + "&dimensionAtObservation=TIME_PERIOD&detail=dataonly"
        )
        headers = {"Accept": "application/vnd.sdmx.data+csv; charset=utf-8"}
        response = make_request(url, headers=headers, timeout=20)
        if response.status_code != 200:
            raise OpenBBError(f"Error: {response.status_code} -> {response.text}")
        df = read_csv(StringIO(response.text)).get(
            ["REF_AREA", "TIME_PERIOD", "OBS_VALUE"]
        )
        if df.empty:
            raise EmptyDataError()
        df = df.rename(
            columns={"REF_AREA": "country", "TIME_PERIOD": "date", "OBS_VALUE": "value"}
        )
        df["value"] = df["value"].astype(float) / 100
        df["country"] = df["country"].map(CODE_TO_COUNTRY_UNEMPLOYMENT)
        df["date"] = df["date"].apply(helpers.oecd_date_to_python_date)
        df = (
            df.query("value.notnull()")
            .set_index(["date", "country"])
            .sort_index()
            .reset_index()
        )
        df = df[(df["date"] <= query.end_date) & (df["date"] >= query.start_date)]

        # in column "country" if NaN replace with "all"
        df["country"] = df["country"].fillna("all")

        return df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: OECDUnemploymentQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[OECDUnemploymentData]:
        """Transform the data from the OECD endpoint."""
        return [OECDUnemploymentData.model_validate(d) for d in data]
