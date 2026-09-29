"""USDA ERS Eating and Health Module (ATUS) Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_eating_and_health_module_atus import (
    EATING_HEALTH_TABLES,
    RELEASE_YEARS,
)

DEFAULT_TABLE = "eating_and_drinking_time"
DEFAULT_YEAR = "2023"


class EatingAndHealthModuleAtusQueryParams(QueryParams):
    """USDA ERS Eating and Health Module (ATUS) Query Parameters.

    Source: https://www.ers.usda.gov/data-products/eating-and-health-module-atus
    """

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "label": "Table",
                "value": DEFAULT_TABLE,
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": config["label"], "value": key}
                    for key, config in EATING_HEALTH_TABLES.items()
                ],
                "style": {"popupWidth": 520},
            },
        },
        "year": {
            "x-widget_config": {
                "label": "Release year",
                "value": DEFAULT_YEAR,
                "multiSelect": False,
                "multiple": False,
                "options": [{"label": year, "value": year} for year in RELEASE_YEARS],
            },
        },
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Eating and Health Module table to retrieve. Each table is a"
        + " single survey-year snapshot whose published measure-by-sex-by-statistic"
        + " series ship pre-spread as the wide value columns, while the two"
        + " leading dimensions stay as pinned row columns. Valid tables are:\n    "
        + ", ".join(EATING_HEALTH_TABLES)
        + "\n",
    )
    year: str = Field(
        default=DEFAULT_YEAR,
        description="Release year selecting which survey-year snapshot to load."
        + " Valid years are:\n    "
        + ", ".join(RELEASE_YEARS)
        + "\n",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        table = v.strip() if isinstance(v, str) else v
        if table not in EATING_HEALTH_TABLES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: "
                + ", ".join(EATING_HEALTH_TABLES)
            )
        return table

    @field_validator("year", mode="before", check_fields=False)
    @classmethod
    def _validate_year(cls, v):
        """Validate year."""
        if not v:
            return DEFAULT_YEAR
        year = str(v).strip()
        if year not in RELEASE_YEARS:
            raise OpenBBError(
                f"Invalid year: {year}. Valid years are: " + ", ".join(RELEASE_YEARS)
            )
        return year


class EatingAndHealthModuleAtusData(Data):
    """USDA ERS Eating and Health Module (ATUS) Data.

    One selected table for a single release year, kept in its published wide
    layout: the two leading survey dimensions stay as pinned row columns while
    the measure-by-sex-by-statistic series spread into value columns, whose set
    varies by table.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Eating and Health Module (ATUS)",
                "$.description": "Time spent eating and drinking, engaged in"
                " associated and secondary eating, food preparation, grocery"
                " shopping, and fast-food purchasing, by demographic, food"
                " security, and body-mass-index subgroups, from the American Time"
                " Use Survey Eating and Health Module, published by the USDA"
                " Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    category: str = Field(
        description="Leading survey dimension of the row, as published, e.g. the"
        + " activity, response level, count of fast-food purchases, or BMI"
        + " group.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Category",
                "cellDataType": "text",
                "pinned": "left",
            }
        },
    )
    subgroup: str = Field(
        description="Second survey dimension of the row, as published, e.g. the"
        + " age bracket, metropolitan status, gender, or breakdown question.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Subgroup",
                "cellDataType": "text",
                "pinned": "left",
            }
        },
    )
    measure_type: str | None = Field(
        default=None,
        description="Whether the fast-food row is an average count or a percent"
        + " of purchasers. Populated only for the fast-food purchases table and"
        + " null for every other table.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Number/percent",
                "cellDataType": "text",
                "pinned": "left",
                "hide": True,
            }
        },
    )


class EatingAndHealthModuleAtusFetcher(
    Fetcher[
        EatingAndHealthModuleAtusQueryParams,
        list[EatingAndHealthModuleAtusData],
    ]
):
    """Fetch USDA ERS Eating and Health Module (ATUS)."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EatingAndHealthModuleAtusQueryParams:
        """Transform the query params."""
        return EatingAndHealthModuleAtusQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: EatingAndHealthModuleAtusQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table and release year's long-format rows."""
        from openbb_government_us.usda.utils import ers_eating_and_health_module_atus

        return await ers_eating_and_health_module_atus.afetch_table(
            query.table, query.year
        )

    @staticmethod
    def transform_data(
        query: EatingAndHealthModuleAtusQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[EatingAndHealthModuleAtusData]:
        """Pivot the long-format cells back into the published wide layout."""
        pivoted: dict[tuple, dict] = {}
        series_order: dict[str, int] = {}
        for record in data:
            key = (
                record["category"],
                record["subgroup"],
                record["measure_type"],
            )
            row = pivoted.get(key)
            if row is None:
                row = {
                    "_row_ord": record["row_ord"],
                    "category": record["category"],
                    "subgroup": record["subgroup"],
                    "measure_type": record["measure_type"],
                }
                pivoted[key] = row
            series = record["series"]
            row[series] = record["value"]
            series_order.setdefault(series, record["series_ord"])
        ordered = sorted(series_order, key=lambda name: series_order[name])
        results = sorted(pivoted.values(), key=lambda row: row["_row_ord"])
        records: list[EatingAndHealthModuleAtusData] = []
        for row in results:
            clean = {
                "category": row["category"],
                "subgroup": row["subgroup"],
                "measure_type": row["measure_type"],
            }
            for series in ordered:
                clean[series] = row.get(series)
            records.append(EatingAndHealthModuleAtusData.model_validate(clean))
        return records
