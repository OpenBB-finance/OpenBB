"""OECD Unemployment Data."""

# pylint: disable=unused-argument

from datetime import date
from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.unemployment import (
    UnemploymentData,
    UnemploymentQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_oecd.utils.constants import UNEMPLOYMENT_COUNTRIES
from pydantic import Field, field_validator

AGES = ["total", "15-24", "25+"]
AgesLiteral = Literal["total", "15-24", "25+"]

_SEX_MAP = {"total": "_T", "male": "M", "female": "F"}
_AGE_MAP = {"total": "Y_GE15", "15-24": "Y15T24", "25+": "Y_GE25"}
_FREQ_MAP = {"annual": "A", "quarter": "Q", "monthly": "M"}


class OECDUnemploymentQueryParams(UnemploymentQueryParams):
    """OECD Unemployment Query.

    Notes
    -----
    Source: https://data-explorer.oecd.org/?lc=en
    """

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": list(UNEMPLOYMENT_COUNTRIES) + ["all"],
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
        return c.replace(" ", "_").strip().lower()


class OECDUnemploymentData(UnemploymentData):
    """OECD Unemployment Data."""


class OECDUnemploymentFetcher(
    Fetcher[OECDUnemploymentQueryParams, list[OECDUnemploymentData]]
):
    """Transform the query, extract and transform the data from the OECD endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> OECDUnemploymentQueryParams:
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
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the OECD endpoint."""
        from openbb_oecd.utils.query_builder import OecdQueryBuilder

        qb = OecdQueryBuilder()
        sex = _SEX_MAP.get(query.sex, "_T")
        age = _AGE_MAP.get(query.age, "Y_GE15")
        freq_code = _FREQ_MAP.get(query.frequency, query.frequency[0].upper())
        adj = "Y" if query.seasonal_adjustment else "N"

        countries = qb.metadata.resolve_country_codes("DF_IALFS_UNE_M", query.country)
        country_str = "+".join(countries) if countries else ""

        try:
            result = qb.fetch_data(
                dataflow="DF_IALFS_UNE_M",
                start_date=(
                    query.start_date.strftime("%Y-%m") if query.start_date else None
                ),
                end_date=query.end_date.strftime("%Y-%m") if query.end_date else None,
                _skip_validation=True,
                REF_AREA=country_str,
                ADJUSTMENT=adj,
                SEX=sex,
                AGE=age,
                FREQ=freq_code,
            )
        except Exception as exc:
            raise OpenBBError(f"Error fetching OECD data: {exc}") from exc

        records = result["data"]
        if not records:
            raise EmptyDataError()

        return records

    @staticmethod
    def transform_data(
        query: OECDUnemploymentQueryParams, data: list[dict], **kwargs: Any
    ) -> list[OECDUnemploymentData]:
        """Transform the data from the OECD endpoint."""
        from openbb_oecd.utils.helpers import oecd_date_to_python_date

        output: list[OECDUnemploymentData] = []
        for row in data:
            d = oecd_date_to_python_date(row.get("TIME_PERIOD", ""))
            if d is None:
                continue
            if query.start_date and d < query.start_date:
                continue
            if query.end_date and d > query.end_date:
                continue
            value = row.get("OBS_VALUE")
            if value is None or value == "":
                continue
            output.append(
                OECDUnemploymentData(
                    date=d,
                    country=row.get("REF_AREA_label", row.get("REF_AREA", "all")),
                    value=float(value) / 100,
                )
            )

        return sorted(output, key=lambda x: (x.date, x.country or ""))
