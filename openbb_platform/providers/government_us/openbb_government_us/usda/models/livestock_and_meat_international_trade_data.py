"""USDA ERS Livestock and Meat International Trade Data Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_livestock_and_meat_international_trade_data import (
    DIRECTION_LABELS,
    DIRECTIONS,
    FREQUENCIES,
    FREQUENCY_LABELS,
    SPECIES,
    SPECIES_LABELS,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix

DEFAULT_TABLE = "beef_veal"
DEFAULT_DIRECTION = "imports"
DEFAULT_FREQUENCY = "annual"

DIM_KEYS = ("country", "geography_code", "month", "unit")


class LivestockAndMeatInternationalTradeDataQueryParams(QueryParams):
    """USDA ERS Livestock and Meat International Trade Data Query Parameters.

    Source: https://www.ers.usda.gov/data-products/livestock-and-meat-international-trade-data
    """

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "label": "Species",
                "value": DEFAULT_TABLE,
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": label, "value": key}
                    for key, label in SPECIES_LABELS.items()
                ],
                "style": {"popupWidth": 280},
            },
        },
        "direction": {
            "x-widget_config": {
                "label": "Direction",
                "value": DEFAULT_DIRECTION,
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": label, "value": key}
                    for key, label in DIRECTION_LABELS.items()
                ],
            },
        },
        "frequency": {
            "x-widget_config": {
                "label": "Frequency",
                "value": DEFAULT_FREQUENCY,
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": label, "value": key}
                    for key, label in FREQUENCY_LABELS.items()
                ],
            },
        },
        "product": {
            "x-widget_config": {
                "label": "Product",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/livestock_trade_products",
                "optionsParams": {"table": "$table", "direction": "$direction"},
                "style": {"popupWidth": 360},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Species workbook to retrieve. Each species publishes import"
        + " and export blocks by trading partner and time; the years become the"
        + " wide columns while the country stays as a pinned row. Valid species"
        + " are:\n    "
        + ", ".join(SPECIES)
        + "\n",
    )
    direction: str = Field(
        default=DEFAULT_DIRECTION,
        description="Trade direction to retrieve. Valid directions are:\n    "
        + ", ".join(DIRECTIONS)
        + "\n",
    )
    frequency: str = Field(
        default=DEFAULT_FREQUENCY,
        description="Reporting frequency. 'annual' spreads calendar years plus"
        + " the two cumulative year-to-date columns; 'monthly' keeps the year"
        + " columns and adds a month row dimension. Valid frequencies are:\n    "
        + ", ".join(FREQUENCIES)
        + "\n",
    )
    product: str | None = Field(
        default=None,
        description="Product block within the selected species and direction,"
        + " e.g. 'Cattle, cattle for breeding' or 'Shell-egg'. If None, the"
        + " direction's first published block is used.",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data."
        + " If None, returns from 1989, the first year of the series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data."
        + " If None, returns up to the most recent year-to-date column.",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        if value not in SPECIES:
            raise OpenBBError(
                f"Invalid table: {value}. Valid tables are: " + ", ".join(SPECIES)
            )
        return value

    @field_validator("direction", mode="before", check_fields=False)
    @classmethod
    def _validate_direction(cls, v):
        """Validate direction."""
        if not v:
            return DEFAULT_DIRECTION
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip().lower()
        if value not in DIRECTIONS:
            raise OpenBBError(
                f"Invalid direction: {value}. Valid directions are: "
                + ", ".join(DIRECTIONS)
            )
        return value

    @field_validator("frequency", mode="before", check_fields=False)
    @classmethod
    def _validate_frequency(cls, v):
        """Validate frequency."""
        if not v:
            return DEFAULT_FREQUENCY
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip().lower()
        if value not in FREQUENCIES:
            raise OpenBBError(
                f"Invalid frequency: {value}. Valid frequencies are: "
                + ", ".join(FREQUENCIES)
            )
        return value

    @field_validator("product", mode="before", check_fields=False)
    @classmethod
    def _validate_product(cls, v):
        """Normalize product to a stripped string or None."""
        if not v:
            return None
        value = v[0] if isinstance(v, (list, tuple)) else v
        return str(value).strip() or None


class LivestockAndMeatInternationalTradeDataData(NullTokenMixin, Data):
    """USDA ERS Livestock and Meat International Trade Data.

    One species-direction-product block pivoted to a wide layout: each row is a
    trading partner while the years spread into value columns, oldest first with
    the two cumulative year-to-date columns trailing. Monthly frequency adds a
    month row dimension so each row is one partner-month with a value per year.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Livestock and Meat International Trade Data",
                "$.description": "U.S. import and export trade in live cattle,"
                " hogs, sheep, and goats and in beef and veal, pork, lamb and"
                " mutton, poultry meat, and eggs, by trading partner and year,"
                " published by the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    country: str = Field(
        description="Trading-partner geography, as published, including the"
        + " 'Other geographies' residual. On the monthly frequency the month is"
        + " appended so each partner-month row is labeled, e.g. 'Canada — Jan',"
        + " and the year columns hold that month's value across years.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Country", "pinned": "left"}
        },
    )
    month: str | None = Field(
        default=None,
        description="Month of the observation for the monthly frequency, as a"
        + " three-letter abbreviation. None for the annual frequency.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Month",
                "pinned": "left",
                "hide": True,
            }
        },
    )
    geography_code: int | None = Field(
        default=None,
        description="U.S. Census Bureau geography code of the trading partner."
        + " None for the 'Other geographies' residual.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Geography code",
                "cellDataType": "number",
                "hide": True,
                "maxWidth": 130,
            }
        },
    )
    unit: str | None = Field(
        default=None,
        description="Unit shared by every value column of the selected block,"
        + " e.g. 'Carcass weight, 1,000 pounds', 'Head', or '1,000 dozen'.",
        json_schema_extra={"x-widget_config": {"headerName": "Unit", "hide": True}},
    )


class LivestockAndMeatInternationalTradeDataFetcher(
    Fetcher[
        LivestockAndMeatInternationalTradeDataQueryParams,
        list[LivestockAndMeatInternationalTradeDataData],
    ]
):
    """Fetch USDA ERS Livestock and Meat International Trade Data."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> LivestockAndMeatInternationalTradeDataQueryParams:
        """Transform the query params."""
        return LivestockAndMeatInternationalTradeDataQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: LivestockAndMeatInternationalTradeDataQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected species-direction-product block's long records."""
        from openbb_government_us.usda.utils import (
            ers_livestock_and_meat_international_trade_data,
        )

        return await ers_livestock_and_meat_international_trade_data.afetch_records(
            query.table, query.direction, query.frequency, query.product
        )

    @staticmethod
    def transform_data(
        query: LivestockAndMeatInternationalTradeDataQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[LivestockAndMeatInternationalTradeDataData]:
        """Pivot the long records into wide rows with years as columns."""
        monthly = any(record["month"] for record in data)
        pivoted: dict[tuple, dict] = {}
        col_meta: dict[str, tuple] = {}
        for record in data:
            year = record["year"]
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            col_meta[record["col_key"]] = (record["is_ytd"], year)
            key = (record["country"], record["month"])
            row = pivoted.get(key)
            if row is None:
                row = {
                    "_rank": record["rank"],
                    "_month_ord": record["month_ord"],
                    "country": (
                        f"{record['country']} — {record['month']}"
                        if monthly and record["month"]
                        else record["country"]
                    ),
                    "geography_code": record["geography_code"],
                    "month": record["month"],
                    "unit": record["unit"],
                }
                pivoted[key] = row
            row[record["col_key"]] = record["value"]
        if not pivoted:
            raise EmptyDataError("No records match the given filters.")
        column_order = sorted(col_meta, key=lambda col: col_meta[col])
        results = sorted(
            pivoted.values(),
            key=lambda row: (row["_rank"], row["_month_ord"], row["country"]),
        )
        validated: list[LivestockAndMeatInternationalTradeDataData] = []
        for row in results:
            payload = {key: row[key] for key in DIM_KEYS}
            for col in column_order:
                payload[col] = row.get(col)
            validated.append(
                LivestockAndMeatInternationalTradeDataData.model_validate(payload)
            )
        return validated
