"""JODI Gas Balance Model."""

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
    GAS_BALANCE_FIELDS,
    GAS_FLOW_DEFINITIONS,
    GAS_UNIT_DESCRIPTION,
    GAS_UNIT_LABELS,
    GAS_UNITS,
    USE_CACHE_DESCRIPTION,
    GasUnitType,
)


class JodiGasBalanceQueryParams(QueryParams):
    """JODI Gas Balance Query.

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
        "country": COUNTRY_SCHEMA_SINGLE,
        "unit": {"choices": list(GAS_UNITS)},
    }

    country: str = Field(
        default="united_states",
        description=COUNTRY_SINGLE_DESCRIPTION,
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

        return validate_country_param(v, multiple=False, default="united_states")

    @field_validator("unit", mode="before", check_fields=False)
    @classmethod
    def _normalize_unit(cls, v):
        """Normalize unit."""
        from openbb_jodi.utils.helpers import normalize_token

        return normalize_token(v, "m3")


class JodiGasBalanceData(Data):
    """JODI Gas Balance Data.

    One column per flow of the JODI-Gas questionnaire, in published order.
    """

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    production: float | None = Field(
        default=None,
        description="Production. " + GAS_FLOW_DEFINITIONS["production"],
    )
    from_other_sources: float | None = Field(
        default=None,
        description="Receipts from other sources. "
        + GAS_FLOW_DEFINITIONS["from_other_sources"],
    )
    imports: float | None = Field(
        default=None,
        description="Total imports. " + GAS_FLOW_DEFINITIONS["imports"],
    )
    pipeline_imports: float | None = Field(
        default=None,
        description="Of which: pipeline imports. "
        + GAS_FLOW_DEFINITIONS["pipeline_imports"],
    )
    lng_imports: float | None = Field(
        default=None,
        description="Of which: LNG imports. " + GAS_FLOW_DEFINITIONS["lng_imports"],
    )
    exports: float | None = Field(
        default=None,
        description="Total exports. " + GAS_FLOW_DEFINITIONS["exports"],
    )
    pipeline_exports: float | None = Field(
        default=None,
        description="Of which: pipeline exports. "
        + GAS_FLOW_DEFINITIONS["pipeline_exports"],
    )
    lng_exports: float | None = Field(
        default=None,
        description="Of which: LNG exports. " + GAS_FLOW_DEFINITIONS["lng_exports"],
    )
    stock_change: float | None = Field(
        default=None,
        description="Stock change. " + GAS_FLOW_DEFINITIONS["stock_change"],
    )
    demand_calculated: float | None = Field(
        default=None,
        description=GAS_FLOW_DEFINITIONS["demand_calculated"],
    )
    statistical_difference: float | None = Field(
        default=None,
        description="Statistical difference. "
        + GAS_FLOW_DEFINITIONS["statistical_difference"],
    )
    demand: float | None = Field(
        default=None,
        description=GAS_FLOW_DEFINITIONS["demand"],
    )
    electricity_and_heat_generation: float | None = Field(
        default=None,
        description="Of which: electricity and heat generation. "
        + GAS_FLOW_DEFINITIONS["electricity_and_heat_generation"],
    )
    closing_stocks: float | None = Field(
        default=None,
        description="Closing stocks. " + GAS_FLOW_DEFINITIONS["closing_stocks"],
    )


class JodiGasBalanceFetcher(
    Fetcher[JodiGasBalanceQueryParams, list[JodiGasBalanceData]]
):
    """JODI Gas Balance Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> JodiGasBalanceQueryParams:
        """Transform the query params."""
        return JodiGasBalanceQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: JodiGasBalanceQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the JODI-Gas world database file."""
        from openbb_jodi.utils.constants import COUNTRIES, GAS_START_YEAR
        from openbb_jodi.utils.helpers import get_filtered_gas, resolve_date_range

        start_date, end_date = resolve_date_range(
            query.start_date, query.end_date, GAS_START_YEAR
        )
        return await get_filtered_gas(
            countries={COUNTRIES[query.country]},
            flow_codes=set(GAS_BALANCE_FIELDS),
            unit_codes={GAS_UNITS[query.unit]},
            start_date=start_date,
            end_date=end_date,
            use_cache=query.use_cache,
        )

    @staticmethod
    def transform_data(
        query: JodiGasBalanceQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> AnnotatedResult[list[JodiGasBalanceData]]:
        """Transform the raw data into the balance table."""
        from openbb_jodi.utils.constants import COUNTRY_LABELS
        from openbb_jodi.utils.helpers import build_assessments, build_field_table

        rows = build_field_table(data, "FLOW_BREAKDOWN", GAS_BALANCE_FIELDS)
        code = data[0]["REF_AREA"]
        metadata = {
            "country": COUNTRY_LABELS.get(code, code),
            "product": "Natural gas",
            "unit": GAS_UNIT_LABELS[query.unit],
            "assessments": build_assessments(
                data, "FLOW_BREAKDOWN", GAS_BALANCE_FIELDS
            ),
            "source": "JODI-Gas World Database (www.jodidata.org)",
        }
        return AnnotatedResult(
            result=[JodiGasBalanceData.model_validate(r) for r in rows],
            metadata=metadata,
        )
