"""JODI Oil Demand By Product Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator

from openbb_jodi.utils.constants import (
    COUNTRY_SCHEMA_SINGLE,
    COUNTRY_SINGLE_DESCRIPTION,
    OIL_PRODUCT_DEFINITIONS,
    OIL_PRODUCT_FIELDS,
    OIL_UNIT_DESCRIPTION,
    OIL_UNIT_LABELS,
    OIL_UNITS,
    USE_CACHE_DESCRIPTION,
    OilUnitType,
)


class JodiOilDemandByProductQueryParams(QueryParams):
    """JODI Oil Demand By Product Query.

    Source: https://www.jodidata.org/oil/database/data-downloads.aspx
    """

    __json_schema_extra__ = {
        "country": COUNTRY_SCHEMA_SINGLE,
        "unit": {"choices": list(OIL_UNITS)},
    }

    country: str = Field(
        default="united_states",
        description=COUNTRY_SINGLE_DESCRIPTION,
    )
    unit: OilUnitType = Field(
        default="kbd",
        description=OIL_UNIT_DESCRIPTION,
    )
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " Defaults to the first data period, 2002-01-01.",
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )
    use_cache: bool = Field(default=True, description=USE_CACHE_DESCRIPTION)

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def _validate_country(cls, v):
        """Validate country."""
        from openbb_jodi.utils.helpers import validate_country_param

        return validate_country_param(v, multiple=False, default="united_states")

    @field_validator("unit", mode="before", check_fields=False)
    @classmethod
    def _normalize_unit(cls, v):
        """Normalize unit."""
        from openbb_jodi.utils.helpers import normalize_token

        return normalize_token(v, "kbd")


class JodiOilDemandByProductData(Data):
    """JODI Oil Demand By Product Data.

    One column per refined product, in published order. Demand is deliveries
    or sales to the inland market (domestic consumption) plus refinery fuel
    plus international marine and aviation bunkers.
    """

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    lpg: float | None = Field(
        default=None,
        description="LPG demand. " + OIL_PRODUCT_DEFINITIONS["lpg"],
    )
    naphtha: float | None = Field(
        default=None,
        description="Naphtha demand. " + OIL_PRODUCT_DEFINITIONS["naphtha"],
    )
    gasoline: float | None = Field(
        default=None,
        description="Gasoline demand. " + OIL_PRODUCT_DEFINITIONS["gasoline"],
    )
    kerosene: float | None = Field(
        default=None,
        description="Kerosenes demand. " + OIL_PRODUCT_DEFINITIONS["kerosene"],
    )
    jet_fuel: float | None = Field(
        default=None,
        description="Jet fuel demand. " + OIL_PRODUCT_DEFINITIONS["jet_fuel"],
    )
    gas_diesel_oil: float | None = Field(
        default=None,
        description="Gas/diesel oil demand. "
        + OIL_PRODUCT_DEFINITIONS["gas_diesel_oil"],
    )
    fuel_oil: float | None = Field(
        default=None,
        description="Fuel oil demand. " + OIL_PRODUCT_DEFINITIONS["fuel_oil"],
    )
    other_products: float | None = Field(
        default=None,
        description="Other oil products demand. "
        + OIL_PRODUCT_DEFINITIONS["other_products"]
        + " Includes direct use of crude oil, NGL, and other primary hydrocarbons.",
    )
    total_products: float | None = Field(
        default=None,
        description="Total oil products demand. "
        + OIL_PRODUCT_DEFINITIONS["total_products"],
    )


class JodiOilDemandByProductFetcher(
    Fetcher[JodiOilDemandByProductQueryParams, list[JodiOilDemandByProductData]]
):
    """JODI Oil Demand By Product Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> JodiOilDemandByProductQueryParams:
        """Transform the query params."""
        return JodiOilDemandByProductQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: JodiOilDemandByProductQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the JODI-Oil annual CSV files."""
        from openbb_jodi.utils.constants import COUNTRIES, OIL_START_YEAR
        from openbb_jodi.utils.helpers import get_filtered_oil, resolve_date_range

        start_date, end_date = resolve_date_range(
            query.start_date, query.end_date, OIL_START_YEAR
        )
        return await get_filtered_oil(
            tables=["secondary"],
            countries={COUNTRIES[query.country]},
            product_codes=set(OIL_PRODUCT_FIELDS),
            flow_codes={"TOTDEMO"},
            unit_codes={OIL_UNITS[query.unit]},
            start_date=start_date,
            end_date=end_date,
            use_cache=query.use_cache,
        )

    @staticmethod
    def transform_data(
        query: JodiOilDemandByProductQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> AnnotatedResult[list[JodiOilDemandByProductData]]:
        """Transform the raw data into the by-product table."""
        from openbb_jodi.utils.constants import COUNTRY_LABELS
        from openbb_jodi.utils.helpers import build_assessments, build_field_table

        rows = build_field_table(data, "ENERGY_PRODUCT", OIL_PRODUCT_FIELDS)
        code = data[0]["REF_AREA"]
        metadata = {
            "country": COUNTRY_LABELS.get(code, code),
            "flow": "Demand",
            "unit": OIL_UNIT_LABELS[query.unit],
            "assessments": build_assessments(
                data, "ENERGY_PRODUCT", OIL_PRODUCT_FIELDS
            ),
            "source": "JODI-Oil World Database (www.jodidata.org)",
        }
        return AnnotatedResult(
            result=[JodiOilDemandByProductData.model_validate(r) for r in rows],
            metadata=metadata,
        )
