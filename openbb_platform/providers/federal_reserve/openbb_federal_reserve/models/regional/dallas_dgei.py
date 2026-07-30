"""Federal Reserve Bank of Dallas Global Economic Indicators Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

BASE_URL = "https://www.dallasfed.org/-/media/Documents/research/international/dgei"

_INDICATORS = {
    "gdp": "gdp.xlsx",
    "cpi": "cpi.xlsx",
    "core_cpi": "core.xlsx",
    "exports": "exp.xlsx",
    "imports": "imp.xlsx",
    "industrial_production": "ip.xlsx",
    "long_term_rates": "ltrates.xlsx",
    "nominal_exchange_rate": "ner.xlsx",
    "policy_rates": "policy.xlsx",
}

_WEIGHTS = {
    "us_trade": "US Trade Weights",
    "world_trade": "World Trade Weights",
    "ppp_gdp": "PPP GDP Weights",
    "nominal_gdp": "Nominal GDP Weights",
}


class FederalReserveDallasDgeiQueryParams(QueryParams):
    """Dallas Fed Global Economic Indicators Query Parameters."""

    __json_schema_extra__ = {
        "indicator": {
            "x-widget_config": {
                "options": [
                    {"label": "Real GDP", "value": "gdp"},
                    {"label": "CPI", "value": "cpi"},
                    {"label": "Core CPI", "value": "core_cpi"},
                    {"label": "Exports", "value": "exports"},
                    {"label": "Imports", "value": "imports"},
                    {
                        "label": "Industrial Production",
                        "value": "industrial_production",
                    },
                    {"label": "Long-Term Interest Rates", "value": "long_term_rates"},
                    {
                        "label": "Nominal Exchange Rate",
                        "value": "nominal_exchange_rate",
                    },
                    {"label": "Policy Rates", "value": "policy_rates"},
                ]
            }
        },
        "weighting": {
            "x-widget_config": {
                "options": [
                    {"label": label, "value": code} for code, label in _WEIGHTS.items()
                ]
            }
        },
    }

    indicator: Literal[
        "gdp",
        "cpi",
        "core_cpi",
        "exports",
        "imports",
        "industrial_production",
        "long_term_rates",
        "nominal_exchange_rate",
        "policy_rates",
    ] = Field(
        default="gdp",
        description="The global indicator: real GDP, CPI, core CPI, exports,"
        " imports, industrial production, long-term interest rates, the nominal"
        " exchange rate, or policy rates.",
    )
    weighting: Literal["us_trade", "world_trade", "ppp_gdp", "nominal_gdp"] = Field(
        default="world_trade",
        description="The country-aggregation weighting scheme.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveDallasDgeiData(Data):
    """Dallas Fed Global Economic Indicators Data."""

    date: dateType = Field(description="The observation date.")


class FederalReserveDallasDgeiFetcher(
    Fetcher[
        FederalReserveDallasDgeiQueryParams,
        list[FederalReserveDallasDgeiData],
    ]
):
    """Dallas Fed Global Economic Indicators Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveDallasDgeiQueryParams:
        """Transform the query params."""
        return FederalReserveDallasDgeiQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveDallasDgeiQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the requested DGEI indicator workbook from the Dallas Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        filename = _INDICATORS[query.indicator]

        def _producer() -> bytes:
            """Fetch the raw indicator workbook bytes."""
            response = make_request(f"{BASE_URL}/{filename}")
            response.raise_for_status()
            return response.content

        content = cached(
            ("dallas_dgei", query.indicator),
            lambda: seconds_until_next_release("monthly"),
            _producer,
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveDallasDgeiQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveDallasDgeiData]:
        """Melt the indicator's weighting sheet, then pivot series to wide rows."""
        from openbb_federal_reserve.utils.dallas import parse_dgei
        from openbb_federal_reserve.utils.workbook import pivot_wide

        records = parse_dgei(
            data[0]["_raw"],
            _WEIGHTS[query.weighting],
            start_date=query.start_date,
            end_date=query.end_date,
        )
        rows = pivot_wide(records, index="date", column="series", value="value")
        return [FederalReserveDallasDgeiData.model_validate(record) for record in rows]
