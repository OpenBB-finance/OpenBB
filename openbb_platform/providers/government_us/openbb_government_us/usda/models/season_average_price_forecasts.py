"""Season-Average Price Forecasts Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_season_average_price_forecasts import (
    COMMODITIES,
)
from openbb_government_us.utils.serializers import NullTokenMixin

DEFAULT_COMMODITY = "Corn"


def _number(header: str, hide: bool = False) -> dict:
    """Build a numeric column config for one measure field."""
    config: dict = {"headerName": header, "cellDataType": "number"}
    if hide:
        config["hide"] = True
    return {"x-widget_config": config}


class SeasonAveragePriceForecastsQueryParams(QueryParams):
    """Season-Average Price Forecasts Query Parameters.

    Source: https://www.ers.usda.gov/data-products/season-average-price-forecasts
    """

    __json_schema_extra__ = {
        "commodity": {
            "x-widget_config": {
                "label": "Commodity",
                "value": DEFAULT_COMMODITY,
                "multiSelect": False,
                "multiple": False,
                "options": [{"label": name, "value": name} for name in COMMODITIES],
                "style": {"popupWidth": 280},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
        "latest": {"x-widget_config": {"label": "Latest vintage only"}},
    }

    commodity: str = Field(
        default=DEFAULT_COMMODITY,
        description="Commodity to retrieve. Valid commodities are:\n    "
        + ", ".join(COMMODITIES)
        + "\n",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data, compared against the"
        + " marketing year. If None, returns from the beginning of the series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data, compared against the"
        + " marketing year. If None, returns up to the most recent year.",
    )
    latest: bool = Field(
        default=False,
        description="Return only the most recent weekly model forecast vintage."
        + " If False, every historical vintage is returned.",
    )

    @field_validator("commodity", mode="before", check_fields=False)
    @classmethod
    def _validate_commodity(cls, v):
        """Validate commodity."""
        if not v:
            return DEFAULT_COMMODITY
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        canonical = {name.casefold(): name for name in COMMODITIES}.get(
            value.casefold()
        )
        if canonical is None:
            raise OpenBBError(
                f"Invalid commodity: {value}. Valid commodities are: "
                + ", ".join(COMMODITIES)
            )
        return canonical


class SeasonAveragePriceForecastsData(NullTokenMixin, Data):
    """Season-Average Price Forecasts Data.

    One row per weekly model forecast vintage and marketing year, with the
    USDA ERS season-average price forecast measures spread across columns.
    """

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Season-Average Price Forecasts",
                "$.description": "Weekly ERS model and monthly WASDE season-average"
                " price forecasts for corn, soybeans, wheat, and cotton, with the"
                " farm-bill Price Loss Coverage and Agriculture Risk Coverage"
                " benchmarks, published by the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        },
    )

    model_forecast_date: str = Field(
        description="Weekly forecast vintage date the model was run, as"
        + " published (YYYY-MM-DD).",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Forecast date",
                "cellDataType": "date",
                "pinned": "left",
                "maxWidth": 130,
            }
        },
    )
    marketing_year: str = Field(
        description="Marketing year of the forecast, as published.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Marketing year",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 130,
            }
        },
    )
    commodity: str = Field(
        description="Commodity name, as published.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Commodity", "hide": True}
        },
    )
    futures_model_type: str = Field(
        description="Futures model type: 'Single contract' or 'Three contract"
        + " aggregate'. Wheat publishes both on the same date.",
        json_schema_extra={"x-widget_config": {"headerName": "Model type"}},
    )
    futures_exchange: str = Field(
        description="Futures exchange the model prices reference, as published.",
        json_schema_extra={"x-widget_config": {"headerName": "Exchange"}},
    )
    mya_price_model_forecast: float | None = Field(
        default=None,
        description="ERS model forecast of the marketing-year average price.",
        json_schema_extra=_number("MYA price (model)"),
    )
    mya_price_wasde_forecast: float | None = Field(
        default=None,
        description="WASDE forecast of the marketing-year average price.",
        json_schema_extra=_number("MYA price (WASDE)"),
    )
    wasde_forecast_date: str | None = Field(
        default=None,
        description="Date of the WASDE forecast, as published.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "WASDE forecast date",
                "cellDataType": "text",
            }
        },
    )
    target_price: float | None = Field(
        default=None,
        description="Farm-bill target price for the marketing year.",
        json_schema_extra=_number("Target price", hide=True),
    )
    national_loan_rate: float | None = Field(
        default=None,
        description="Farm-bill national loan rate for the marketing year.",
        json_schema_extra=_number("National loan rate", hide=True),
    )
    direct_payment_rate: float | None = Field(
        default=None,
        description="Farm-bill direct payment rate for the marketing year.",
        json_schema_extra=_number("Direct payment rate", hide=True),
    )
    reference_price: float | None = Field(
        default=None,
        description="Farm-bill statutory reference price for the marketing year.",
        json_schema_extra=_number("Reference price", hide=True),
    )
    ccp_effective_price_model_forecast: float | None = Field(
        default=None,
        description="Counter-cyclical payment effective price, model forecast.",
        json_schema_extra=_number("CCP effective price (model)", hide=True),
    )
    ccp_rate_model_forecast: float | None = Field(
        default=None,
        description="Counter-cyclical payment rate, model forecast.",
        json_schema_extra=_number("CCP rate (model)", hide=True),
    )
    ccp_effective_price_wasde_forecast: float | None = Field(
        default=None,
        description="Counter-cyclical payment effective price, WASDE forecast.",
        json_schema_extra=_number("CCP effective price (WASDE)", hide=True),
    )
    ccp_rate_wasde_forecast: float | None = Field(
        default=None,
        description="Counter-cyclical payment rate, WASDE forecast.",
        json_schema_extra=_number("CCP rate (WASDE)", hide=True),
    )
    historical_mya_price_year1: float | None = Field(
        default=None,
        description="Marketing-year average price of the first historical year"
        + " in the five-year benchmark window.",
        json_schema_extra=_number("Historical MYA price yr 1", hide=True),
    )
    historical_mya_price_year2: float | None = Field(
        default=None,
        description="Marketing-year average price of the second historical year"
        + " in the five-year benchmark window.",
        json_schema_extra=_number("Historical MYA price yr 2", hide=True),
    )
    historical_mya_price_year3: float | None = Field(
        default=None,
        description="Marketing-year average price of the third historical year"
        + " in the five-year benchmark window.",
        json_schema_extra=_number("Historical MYA price yr 3", hide=True),
    )
    historical_mya_price_year4: float | None = Field(
        default=None,
        description="Marketing-year average price of the fourth historical year"
        + " in the five-year benchmark window.",
        json_schema_extra=_number("Historical MYA price yr 4", hide=True),
    )
    historical_mya_price_year5: float | None = Field(
        default=None,
        description="Marketing-year average price of the fifth historical year"
        + " in the five-year benchmark window.",
        json_schema_extra=_number("Historical MYA price yr 5", hide=True),
    )
    historical_mya_5year_range: str | None = Field(
        default=None,
        description="Range of years spanned by the five-year benchmark window,"
        + " as published, e.g. '2019-2023'.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Historical MYA 5-year range",
                "hide": True,
            }
        },
    )
    historical_mya_price_5year_olympic_average: float | None = Field(
        default=None,
        description="Olympic average of the five historical marketing-year"
        + " average prices.",
        json_schema_extra=_number("Historical MYA 5-year Olympic avg", hide=True),
    )
    effective_reference_price: float | None = Field(
        default=None,
        description="Farm-bill effective reference price for the marketing year.",
        json_schema_extra=_number("Effective reference price"),
    )
    effective_price_model_forecast: float | None = Field(
        default=None,
        description="Price Loss Coverage effective price, model forecast.",
        json_schema_extra=_number("Effective price (model)", hide=True),
    )
    plc_payment_rate_model_forecast: float | None = Field(
        default=None,
        description="Price Loss Coverage payment rate, model forecast.",
        json_schema_extra=_number("PLC payment rate (model)", hide=True),
    )
    effective_price_wasde_forecast: float | None = Field(
        default=None,
        description="Price Loss Coverage effective price, WASDE forecast.",
        json_schema_extra=_number("Effective price (WASDE)", hide=True),
    )
    plc_payment_rate_wasde_forecast: float | None = Field(
        default=None,
        description="Price Loss Coverage payment rate, WASDE forecast.",
        json_schema_extra=_number("PLC payment rate (WASDE)", hide=True),
    )
    maximum_plc_payment_rate: float | None = Field(
        default=None,
        description="Maximum Price Loss Coverage payment rate for the year.",
        json_schema_extra=_number("Maximum PLC payment rate", hide=True),
    )
    arc_annual_benchmark_price_year1: float | None = Field(
        default=None,
        description="Agriculture Risk Coverage annual benchmark price of the"
        + " first historical year in the window.",
        json_schema_extra=_number("ARC benchmark price yr 1", hide=True),
    )
    arc_annual_benchmark_price_year2: float | None = Field(
        default=None,
        description="Agriculture Risk Coverage annual benchmark price of the"
        + " second historical year in the window.",
        json_schema_extra=_number("ARC benchmark price yr 2", hide=True),
    )
    arc_annual_benchmark_price_year3: float | None = Field(
        default=None,
        description="Agriculture Risk Coverage annual benchmark price of the"
        + " third historical year in the window.",
        json_schema_extra=_number("ARC benchmark price yr 3", hide=True),
    )
    arc_annual_benchmark_price_year4: float | None = Field(
        default=None,
        description="Agriculture Risk Coverage annual benchmark price of the"
        + " fourth historical year in the window.",
        json_schema_extra=_number("ARC benchmark price yr 4", hide=True),
    )
    arc_annual_benchmark_price_year5: float | None = Field(
        default=None,
        description="Agriculture Risk Coverage annual benchmark price of the"
        + " fifth historical year in the window.",
        json_schema_extra=_number("ARC benchmark price yr 5", hide=True),
    )
    arc_annual_benchmark_price_5year_range: str | None = Field(
        default=None,
        description="Range of years spanned by the ARC five-year benchmark"
        + " window, as published, e.g. '2008-2012'.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "ARC benchmark 5-year range",
                "hide": True,
            }
        },
    )
    arc_co_benchmark_price: float | None = Field(
        default=None,
        description="Agriculture Risk Coverage county-option benchmark price.",
        json_schema_extra=_number("ARC-CO benchmark price", hide=True),
    )
    arc_co_price_model_forecast: float | None = Field(
        default=None,
        description="Agriculture Risk Coverage county-option price, model"
        + " forecast.",
        json_schema_extra=_number("ARC-CO price (model)", hide=True),
    )
    arc_co_price_wasde_forecast: float | None = Field(
        default=None,
        description="Agriculture Risk Coverage county-option price, WASDE"
        + " forecast.",
        json_schema_extra=_number("ARC-CO price (WASDE)", hide=True),
    )
    arc_ic_price_model_forecast: float | None = Field(
        default=None,
        description="Agriculture Risk Coverage individual-coverage price, model"
        + " forecast.",
        json_schema_extra=_number("ARC-IC price (model)", hide=True),
    )
    arc_ic_price_wasde_forecast: float | None = Field(
        default=None,
        description="Agriculture Risk Coverage individual-coverage price, WASDE"
        + " forecast.",
        json_schema_extra=_number("ARC-IC price (WASDE)", hide=True),
    )
    actual_mya_price: float | None = Field(
        default=None,
        description="Actual realized marketing-year average price, once known.",
        json_schema_extra=_number("Actual MYA price"),
    )
    price_unit: str = Field(
        description="Unit of the price columns, as published, e.g. 'U.S. dollars"
        + " per bushel' or 'U.S. dollars per pound'.",
        json_schema_extra={"x-widget_config": {"headerName": "Price unit"}},
    )


class SeasonAveragePriceForecastsFetcher(
    Fetcher[
        SeasonAveragePriceForecastsQueryParams,
        list[SeasonAveragePriceForecastsData],
    ]
):
    """Fetch USDA ERS Season-Average Price Forecasts."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> SeasonAveragePriceForecastsQueryParams:
        """Transform the query params."""
        return SeasonAveragePriceForecastsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SeasonAveragePriceForecastsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the output-forecast rows for the selected commodity."""
        from openbb_government_us.usda.utils import ers_season_average_price_forecasts

        records = await ers_season_average_price_forecasts.afetch_output_forecast()
        return [record for record in records if record["commodity"] == query.commodity]

    @staticmethod
    def transform_data(
        query: SeasonAveragePriceForecastsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[SeasonAveragePriceForecastsData]:
        """Filter by year and vintage, then emit newest-first wide rows."""
        latest_date = (
            max(record["model_forecast_date"] for record in data) if data else None
        )
        selected: list[dict] = []
        for record in data:
            if query.latest and record["model_forecast_date"] != latest_date:
                continue
            year = int(record["marketing_year"])
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            selected.append(record)
        selected.sort(
            key=lambda record: (
                record["commodity"],
                record["model_forecast_date"],
                int(record["marketing_year"]),
            ),
            reverse=True,
        )
        return [
            SeasonAveragePriceForecastsData.model_validate(record)
            for record in selected
        ]
