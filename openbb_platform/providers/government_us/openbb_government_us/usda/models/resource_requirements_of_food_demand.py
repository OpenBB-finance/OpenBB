"""USDA ERS Resource Requirements of Food Demand Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_resource_requirements_of_food_demand import (
    TABLES,
)
from openbb_government_us.utils.serializers import NullTokenMixin

DEFAULT_TABLE = "Xf0000"


def _number(header: str, hide: bool = False) -> dict:
    """Build a numeric column config for one measure field."""
    config: dict = {"headerName": header, "cellDataType": "number"}
    if hide:
        config["hide"] = True
    return {"x-widget_config": config}


class ResourceRequirementsOfFoodDemandQueryParams(QueryParams):
    """USDA ERS Resource Requirements of Food Demand Query Parameters.

    Source: https://www.ers.usda.gov/data-products/resource-requirements-of-food-demand
    """

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "label": "Food group",
                "value": DEFAULT_TABLE,
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": f"{code} - {label}", "value": code}
                    for code, label in TABLES.items()
                ],
                "style": {"popupWidth": 520},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Food group, commodity, or aggregate table to retrieve,"
        + " identified by its Xf table number. Each table holds the"
        + " employment, freshwater withdrawal, and energy resources embodied"
        + " across the food supply chain to meet final demand for that"
        + " category; the resource-and-source measures become the wide value"
        + " columns while year and supply-chain stage stay as pinned rows."
        + " Valid tables are:\n    "
        + ", ".join(f"{code} ({label})" for code, label in TABLES.items())
        + "\n",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data, compared against the"
        + " observation year. If None, returns from the beginning of the"
        + " series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data, compared against the"
        + " observation year. If None, returns up to the most recent year.",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        table = v.strip() if isinstance(v, str) else v
        if table not in TABLES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: " + ", ".join(TABLES)
            )
        return table


class ResourceRequirementsOfFoodDemandData(NullTokenMixin, Data):
    """USDA ERS Resource Requirements of Food Demand Data.

    One selected food group pivoted to a wide layout: year and supply-chain
    stage stay in the rows while the resource-and-source measures spread into
    value columns, with the energy total and its by-source breakdown.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Resource Requirements of Food Demand",
                "$.description": "Employment, freshwater withdrawals, and energy"
                " use, total and by source, embodied across the U.S. food supply"
                " chain to meet final consumer demand for each food, beverage, and"
                " food-related category, published by the USDA Economic Research"
                " Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    year: int = Field(
        description="Year of the observation.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Year",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 90,
            }
        },
    )
    stage: str | None = Field(
        default=None,
        description="Supply-chain stage the resources are attributed to, as"
        + " published, e.g. 'Total', 'Crops', 'Food retail', or a household"
        + " home-kitchen stage.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Supply chain stage", "pinned": "left"}
        },
    )
    employment: float | None = Field(
        default=None,
        description="Full- or part-time employees per year embodied at the" + " stage.",
        json_schema_extra=_number("Employment (employees/yr)"),
    )
    water: float | None = Field(
        default=None,
        description="Freshwater withdrawals embodied at the stage, in million"
        + " gallons per year.",
        json_schema_extra=_number("Water withdrawals (Mgal/yr)"),
    )
    energy_total: float | None = Field(
        default=None,
        description="Total energy from all sources embodied at the stage, in"
        + " billion British thermal units per year.",
        json_schema_extra=_number("Energy: Total (bBtu/yr)"),
    )
    energy_pa: float | None = Field(
        default=None,
        description="Energy from all petroleum products embodied at the stage,"
        + " in billion British thermal units per year.",
        json_schema_extra=_number("Energy: Petroleum products (bBtu/yr)", hide=True),
    )
    energy_ng: float | None = Field(
        default=None,
        description="Energy from natural gas, including supplemental gaseous"
        + " fuels, embodied at the stage, in billion British thermal units per"
        + " year.",
        json_schema_extra=_number("Energy: Natural gas (bBtu/yr)", hide=True),
    )
    energy_es: float | None = Field(
        default=None,
        description="Energy from electricity sales embodied at the stage, in"
        + " billion British thermal units per year.",
        json_schema_extra=_number("Energy: Electricity sales (bBtu/yr)", hide=True),
    )
    energy_cl: float | None = Field(
        default=None,
        description="Energy from coal embodied at the stage, in billion British"
        + " thermal units per year.",
        json_schema_extra=_number("Energy: Coal (bBtu/yr)", hide=True),
    )
    energy_lo: float | None = Field(
        default=None,
        description="Electrical system energy losses embodied at the stage, in"
        + " billion British thermal units per year.",
        json_schema_extra=_number(
            "Energy: Electrical system losses (bBtu/yr)", hide=True
        ),
    )
    energy_bf: float | None = Field(
        default=None,
        description="Energy from biofuel embodied at the stage, in billion"
        + " British thermal units per year.",
        json_schema_extra=_number("Energy: Biofuel (bBtu/yr)", hide=True),
    )
    energy_ww: float | None = Field(
        default=None,
        description="Energy from wood and biomass waste embodied at the stage,"
        + " in billion British thermal units per year.",
        json_schema_extra=_number(
            "Energy: Wood and biomass waste (bBtu/yr)", hide=True
        ),
    )
    energy_wd: float | None = Field(
        default=None,
        description="Energy from wood embodied at the stage, in billion British"
        + " thermal units per year.",
        json_schema_extra=_number("Energy: Wood (bBtu/yr)", hide=True),
    )
    energy_hy: float | None = Field(
        default=None,
        description="Energy from hydroelectric power embodied at the stage, in"
        + " billion British thermal units per year.",
        json_schema_extra=_number("Energy: Hydroelectric (bBtu/yr)", hide=True),
    )
    energy_ge: float | None = Field(
        default=None,
        description="Energy from geothermal power embodied at the stage, in"
        + " billion British thermal units per year.",
        json_schema_extra=_number("Energy: Geothermal (bBtu/yr)", hide=True),
    )
    energy_so: float | None = Field(
        default=None,
        description="Energy from solar power embodied at the stage, in billion"
        + " British thermal units per year.",
        json_schema_extra=_number("Energy: Solar (bBtu/yr)", hide=True),
    )
    energy_wy: float | None = Field(
        default=None,
        description="Energy from wind power embodied at the stage, in billion"
        + " British thermal units per year.",
        json_schema_extra=_number("Energy: Wind (bBtu/yr)", hide=True),
    )
    energy_cc: float | None = Field(
        default=None,
        description="Energy from coal coke embodied at the stage, in billion"
        + " British thermal units per year.",
        json_schema_extra=_number("Energy: Coal coke (bBtu/yr)", hide=True),
    )
    energy_sf: float | None = Field(
        default=None,
        description="Energy from supplemental gaseous fuels embodied at the"
        + " stage, in billion British thermal units per year.",
        json_schema_extra=_number(
            "Energy: Supplemental gaseous fuels (bBtu/yr)", hide=True
        ),
    )


class ResourceRequirementsOfFoodDemandFetcher(
    Fetcher[
        ResourceRequirementsOfFoodDemandQueryParams,
        list[ResourceRequirementsOfFoodDemandData],
    ]
):
    """Fetch USDA ERS Resource Requirements of Food Demand."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> ResourceRequirementsOfFoodDemandQueryParams:
        """Transform the query params."""
        return ResourceRequirementsOfFoodDemandQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ResourceRequirementsOfFoodDemandQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's long-format rows."""
        from openbb_government_us.usda.utils import (
            ers_resource_requirements_of_food_demand,
        )

        return await ers_resource_requirements_of_food_demand.afetch_table(query.table)

    @staticmethod
    def transform_data(
        query: ResourceRequirementsOfFoodDemandQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[ResourceRequirementsOfFoodDemandData]:
        """Pivot the resource-and-source measures into the wide layout."""
        pivoted: dict[tuple, dict] = {}
        for order, record in enumerate(data):
            year = record["year"]
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            key = (year, record["stage_ord"], record["stage"])
            row = pivoted.get(key)
            if row is None:
                row = {
                    "_order": order,
                    "_stage_ord": record["stage_ord"],
                    "_table": record["table"],
                    "year": year,
                    "stage": record["stage"],
                }
                pivoted[key] = row
            row[record["column"]] = record["value"]
        results = sorted(
            pivoted.values(),
            key=lambda row: (row["year"], row["_stage_ord"], row["_order"]),
        )
        return [
            ResourceRequirementsOfFoodDemandData.model_validate(
                {k: v for k, v in row.items() if not k.startswith("_")}
            )
            for row in results
        ]
