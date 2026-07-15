"""JODI Gas Exports Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator

from openbb_jodi.models.country_data import JodiCountryData
from openbb_jodi.utils.constants import (
    COUNTRY_MULTI_DESCRIPTION,
    COUNTRY_SCHEMA_MULTI,
    GAS_FLOW_DEFINITIONS,
    GAS_UNIT_DESCRIPTION,
    GAS_UNIT_LABELS,
    GAS_UNITS,
    USE_CACHE_DESCRIPTION,
    GasUnitType,
)

FLOW_CODES = {"total": "TOTEXPSB", "pipeline": "EXPPIP", "lng": "EXPLNG"}
FLOW_LABELS = {
    "total": "Exports",
    "pipeline": "Pipeline exports",
    "lng": "LNG exports",
}


class JodiGasExportsQueryParams(QueryParams):
    """JODI Gas Exports Query.

    Natural gas is a mixture of gaseous hydrocarbons, primarily methane,
    but generally also including ethane, propane, and higher hydrocarbons
    in much smaller amounts, and some non-combustible gases such as
    nitrogen and carbon dioxide. It includes both non-associated and
    associated gas. Colliery gas, coal seam gas, and shale gas are
    included, while manufactured gas and biogas are excluded except when
    blended with natural gas for final consumption. Natural gas liquids
    are excluded.

    Source: https://www.jodidata.org/gas/database/data-downloads.aspx
    """

    __json_schema_extra__ = {
        "country": COUNTRY_SCHEMA_MULTI,
        "flow": {"choices": list(FLOW_CODES)},
        "unit": {"choices": list(GAS_UNITS)},
    }

    country: str | None = Field(
        default=None,
        description=COUNTRY_MULTI_DESCRIPTION,
    )
    flow: Literal["total", "pipeline", "lng"] = Field(
        default="total",
        description="The exports breakdown. JODI questionnaire definitions:\n"
        + "    total: "
        + GAS_FLOW_DEFINITIONS["exports"]
        + "\n    pipeline: "
        + GAS_FLOW_DEFINITIONS["pipeline_exports"]
        + "\n    lng: "
        + GAS_FLOW_DEFINITIONS["lng_exports"],
    )
    unit: GasUnitType = Field(
        default="m3",
        description=GAS_UNIT_DESCRIPTION,
    )
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " Defaults to the first data period, 2009-01-01.",
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

    @field_validator("flow", "unit", mode="before", check_fields=False)
    @classmethod
    def _normalize_tokens(cls, v, info):
        """Normalize token parameters."""
        from openbb_jodi.utils.helpers import normalize_token

        defaults = {"flow": "total", "unit": "m3"}
        return normalize_token(v, defaults[str(info.field_name)])


class JodiGasExportsData(JodiCountryData):
    """JODI Gas Exports Data.

    One column per reporting country. Exports are amounts that have
    crossed the physical boundaries of the country, whether customs
    clearance has taken place or not; deliveries for international
    bunkers are excluded.
    """


class JodiGasExportsFetcher(
    Fetcher[JodiGasExportsQueryParams, list[JodiGasExportsData]]
):
    """JODI Gas Exports Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> JodiGasExportsQueryParams:
        """Transform the query params."""
        return JodiGasExportsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: JodiGasExportsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the JODI-Gas world database file."""
        from openbb_jodi.utils.constants import COUNTRIES, GAS_START_YEAR
        from openbb_jodi.utils.helpers import get_filtered_gas, resolve_date_range

        start_date, end_date = resolve_date_range(
            query.start_date, query.end_date, GAS_START_YEAR
        )
        countries = (
            {COUNTRIES[country] for country in query.country.split(",")}
            if query.country
            else None
        )
        return await get_filtered_gas(
            countries=countries,
            flow_codes={FLOW_CODES[query.flow]},
            unit_codes={GAS_UNITS[query.unit]},
            start_date=start_date,
            end_date=end_date,
            use_cache=query.use_cache,
        )

    @staticmethod
    def transform_data(
        query: JodiGasExportsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> AnnotatedResult[list[JodiGasExportsData]]:
        """Transform the raw data into the by-country table."""
        from openbb_jodi.utils.constants import CODE_TO_COUNTRY
        from openbb_jodi.utils.helpers import build_assessments, build_country_table

        rows = build_country_table(data)
        metadata = {
            "product": "Natural gas",
            "flow": FLOW_LABELS[query.flow],
            "unit": GAS_UNIT_LABELS[query.unit],
            "assessments": build_assessments(data, "REF_AREA", CODE_TO_COUNTRY),
            "source": "JODI-Gas World Database (www.jodidata.org)",
        }
        return AnnotatedResult(
            result=[JodiGasExportsData.model_validate(r) for r in rows],
            metadata=metadata,
        )
