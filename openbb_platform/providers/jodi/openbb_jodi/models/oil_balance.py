"""JODI Oil Balance Model."""

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
    OIL_FLOW_DEFINITIONS,
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


class JodiOilBalanceQueryParams(QueryParams):
    """JODI Oil Balance Query.

    Source: https://www.jodidata.org/oil/database/data-downloads.aspx
    """

    __json_schema_extra__ = {
        "country": COUNTRY_SCHEMA_SINGLE,
        "product": {"choices": list(OIL_PRODUCTS)},
        "unit": {"choices": list(OIL_UNITS)},
    }

    country: str = Field(
        default="united_states",
        description=COUNTRY_SINGLE_DESCRIPTION,
    )
    product: OilProductType = Field(
        default="crude_oil",
        description="The petroleum product to get the balance for."
        + " The first four are primary products, the rest are secondary"
        + " products. JODI questionnaire definitions:\n"
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

        return validate_country_param(v, multiple=False, default="united_states")

    @field_validator("product", "unit", mode="before", check_fields=False)
    @classmethod
    def _normalize_tokens(cls, v, info):
        """Normalize token parameters."""
        from openbb_jodi.utils.helpers import normalize_token

        defaults = {"product": "crude_oil", "unit": "kbd"}
        return normalize_token(v, defaults[str(info.field_name)])


class JodiOilBalanceData(Data):
    """JODI Oil Balance Data.

    One column per flow of the JODI-Oil questionnaire, in published order.
    Primary-only flows are None for secondary products, and vice versa.
    """

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    production: float | None = Field(
        default=None,
        description="Production (primary products). "
        + OIL_FLOW_DEFINITIONS["production"],
    )
    refinery_output: float | None = Field(
        default=None,
        description="Refinery output (secondary products). "
        + OIL_FLOW_DEFINITIONS["refinery_output"],
    )
    from_other_sources: float | None = Field(
        default=None,
        description="From other sources (primary products). "
        + OIL_FLOW_DEFINITIONS["from_other_sources"],
    )
    receipts: float | None = Field(
        default=None,
        description="Receipts (secondary products). "
        + OIL_FLOW_DEFINITIONS["receipts"],
    )
    imports: float | None = Field(
        default=None,
        description="Imports. " + OIL_FLOW_DEFINITIONS["imports"],
    )
    exports: float | None = Field(
        default=None,
        description="Exports. " + OIL_FLOW_DEFINITIONS["exports"],
    )
    products_transferred: float | None = Field(
        default=None,
        description="Products transferred. "
        + OIL_FLOW_DEFINITIONS["products_transferred"],
    )
    interproduct_transfers: float | None = Field(
        default=None,
        description="Interproduct transfers (secondary products). "
        + OIL_FLOW_DEFINITIONS["interproduct_transfers"],
    )
    direct_use: float | None = Field(
        default=None,
        description="Direct use (primary products). "
        + OIL_FLOW_DEFINITIONS["direct_use"],
    )
    stock_change: float | None = Field(
        default=None,
        description="Stock change. " + OIL_FLOW_DEFINITIONS["stock_change"],
    )
    statistical_difference: float | None = Field(
        default=None,
        description="Statistical difference. "
        + OIL_FLOW_DEFINITIONS["statistical_difference"],
    )
    refinery_intake: float | None = Field(
        default=None,
        description="Refinery intake (primary products). "
        + OIL_FLOW_DEFINITIONS["refinery_intake"],
    )
    demand: float | None = Field(
        default=None,
        description="Demand (secondary products). " + OIL_FLOW_DEFINITIONS["demand"],
    )
    closing_stocks: float | None = Field(
        default=None,
        description="Closing stocks. " + OIL_FLOW_DEFINITIONS["closing_stocks"],
    )


class JodiOilBalanceFetcher(
    Fetcher[JodiOilBalanceQueryParams, list[JodiOilBalanceData]]
):
    """JODI Oil Balance Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> JodiOilBalanceQueryParams:
        """Transform the query params."""
        return JodiOilBalanceQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: JodiOilBalanceQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the JODI-Oil annual CSV files."""
        from openbb_jodi.utils.constants import (
            COUNTRIES,
            OIL_BALANCE_FIELDS,
            OIL_START_YEAR,
        )
        from openbb_jodi.utils.helpers import get_filtered_oil, resolve_date_range

        start_date, end_date = resolve_date_range(
            query.start_date, query.end_date, OIL_START_YEAR
        )
        product_code, table = OIL_PRODUCTS[query.product]
        return await get_filtered_oil(
            tables=[table],
            countries={COUNTRIES[query.country]},
            product_codes={product_code},
            flow_codes=set(OIL_BALANCE_FIELDS),
            unit_codes={OIL_UNITS[query.unit]},
            start_date=start_date,
            end_date=end_date,
            use_cache=query.use_cache,
        )

    @staticmethod
    def transform_data(
        query: JodiOilBalanceQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> AnnotatedResult[list[JodiOilBalanceData]]:
        """Transform the raw data into the balance table."""
        from openbb_jodi.utils.constants import COUNTRY_LABELS, OIL_BALANCE_FIELDS
        from openbb_jodi.utils.helpers import build_assessments, build_field_table

        rows = build_field_table(data, "FLOW_BREAKDOWN", OIL_BALANCE_FIELDS)
        code = data[0]["REF_AREA"]
        metadata = {
            "country": COUNTRY_LABELS.get(code, code),
            "product": OIL_PRODUCT_LABELS[OIL_PRODUCTS[query.product][0]],
            "unit": OIL_UNIT_LABELS[query.unit],
            "assessments": build_assessments(
                data, "FLOW_BREAKDOWN", OIL_BALANCE_FIELDS
            ),
            "source": "JODI-Oil World Database (www.jodidata.org)",
        }
        return AnnotatedResult(
            result=[JodiOilBalanceData.model_validate(r) for r in rows],
            metadata=metadata,
        )
