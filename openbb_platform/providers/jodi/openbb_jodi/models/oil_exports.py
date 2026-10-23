"""JODI Oil Exports Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator

from openbb_jodi.models.country_data import JodiCountryData
from openbb_jodi.utils.constants import (
    COUNTRY_MULTI_DESCRIPTION,
    COUNTRY_SCHEMA_MULTI,
    OIL_PRODUCT_CHOICES_DESCRIPTION,
    OIL_PRODUCT_LABELS,
    OIL_PRODUCTS,
    OIL_UNIT_DESCRIPTION,
    OIL_UNIT_LABELS,
    OIL_UNITS,
    USE_CACHE_DESCRIPTION,
    OilProductType,
    OilUnitType,
)


class JodiOilExportsQueryParams(QueryParams):
    """JODI Oil Exports Query.

    Source: https://www.jodidata.org/oil/database/data-downloads.aspx
    """

    __json_schema_extra__ = {
        "country": COUNTRY_SCHEMA_MULTI,
        "product": {"choices": list(OIL_PRODUCTS)},
        "unit": {"choices": list(OIL_UNITS)},
    }

    country: str | None = Field(
        default=None,
        description=COUNTRY_MULTI_DESCRIPTION,
    )
    product: OilProductType = Field(
        default="crude_oil",
        description="The petroleum product to get exports of."
        + " JODI questionnaire definitions:\n"
        + OIL_PRODUCT_CHOICES_DESCRIPTION,
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

        return validate_country_param(v, multiple=True, default=None)

    @field_validator("product", "unit", mode="before", check_fields=False)
    @classmethod
    def _normalize_tokens(cls, v, info):
        """Normalize token parameters."""
        from openbb_jodi.utils.helpers import normalize_token

        defaults = {"product": "crude_oil", "unit": "kbd"}
        return normalize_token(v, defaults[str(info.field_name)])


class JodiOilExportsData(JodiCountryData):
    """JODI Oil Exports Data.

    One column per reporting country. Exports are goods having physically
    crossed the international boundaries, excluding transit trade and
    international marine and aviation bunkers.
    """


class JodiOilExportsFetcher(
    Fetcher[JodiOilExportsQueryParams, list[JodiOilExportsData]]
):
    """JODI Oil Exports Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> JodiOilExportsQueryParams:
        """Transform the query params."""
        return JodiOilExportsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: JodiOilExportsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the JODI-Oil annual CSV files."""
        from openbb_jodi.utils.constants import COUNTRIES, OIL_START_YEAR
        from openbb_jodi.utils.helpers import get_filtered_oil, resolve_date_range

        start_date, end_date = resolve_date_range(
            query.start_date, query.end_date, OIL_START_YEAR
        )
        product_code, table = OIL_PRODUCTS[query.product]
        countries = (
            {COUNTRIES[country] for country in query.country.split(",")}
            if query.country
            else None
        )
        return await get_filtered_oil(
            tables=[table],
            countries=countries,
            product_codes={product_code},
            flow_codes={"TOTEXPSB"},
            unit_codes={OIL_UNITS[query.unit]},
            start_date=start_date,
            end_date=end_date,
            use_cache=query.use_cache,
        )

    @staticmethod
    def transform_data(
        query: JodiOilExportsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> AnnotatedResult[list[JodiOilExportsData]]:
        """Transform the raw data into the by-country table."""
        from openbb_jodi.utils.constants import CODE_TO_COUNTRY
        from openbb_jodi.utils.helpers import build_assessments, build_country_table

        rows = build_country_table(data)
        metadata = {
            "product": OIL_PRODUCT_LABELS[OIL_PRODUCTS[query.product][0]],
            "flow": "Exports",
            "unit": OIL_UNIT_LABELS[query.unit],
            "assessments": build_assessments(data, "REF_AREA", CODE_TO_COUNTRY),
            "source": "JODI-Oil World Database (www.jodidata.org)",
        }
        return AnnotatedResult(
            result=[JodiOilExportsData.model_validate(r) for r in rows],
            metadata=metadata,
        )
