"""USDA ERS Cost Estimates of Foodborne Illnesses Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_cost_estimates_of_foodborne_illnesses import (
    COST_ESTIMATES_TABLES,
)
from openbb_government_us.utils.serializers import NullTokenMixin

DEFAULT_TABLE = "cases_and_cost"


class CostEstimatesOfFoodborneIllnessesQueryParams(QueryParams):
    """USDA ERS Cost Estimates of Foodborne Illnesses Query Parameters.

    Source: https://www.ers.usda.gov/data-products/cost-estimates-of-foodborne-illnesses
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
                    for key, config in COST_ESTIMATES_TABLES.items()
                ],
                "style": {"popupWidth": 480},
            },
        },
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Cost-estimates table to retrieve. Each table is already"
        + " one row per pathogen, with its cost measures spread across the"
        + " value columns; pathogen classification and pathogen stay as pinned"
        + " row columns. Valid tables are:\n    "
        + ", ".join(COST_ESTIMATES_TABLES)
        + "\n",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        table = v.strip() if isinstance(v, str) else v
        if table not in COST_ESTIMATES_TABLES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: "
                + ", ".join(COST_ESTIMATES_TABLES)
            )
        return table


class CostEstimatesOfFoodborneIllnessesData(NullTokenMixin, Data):
    """USDA ERS Cost Estimates of Foodborne Illnesses.

    One selected table in its native wide layout: one row per pathogen, with
    the table's cost measures as value columns whose set varies by table. All
    monetary values are in 2023 U.S. dollars.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Cost Estimates of Foodborne Illnesses",
                "$.description": "Estimated annual number of cases and the"
                " economic burden of foodborne illnesses acquired in the United"
                " States, by pathogen and by health outcome, in 2023 U.S."
                " dollars, published by the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    pathogen_classification: str = Field(
        description="Pathogen classification, as published: 'Bacteria',"
        + " 'Parasites', 'Viruses', or an aggregate row's grouping such as"
        + " 'Illnesses from major foodborne pathogens', 'Other foodborne"
        + " gastroenteritis', or 'All pathogens'.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Classification",
                "pinned": "left",
            }
        },
    )
    pathogen: str = Field(
        description="Pathogen name, as published, e.g. 'Campylobacter spp.',"
        + " or an aggregate row label such as 'Subtotal' or 'Total'.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Pathogen",
                "pinned": "left",
            }
        },
    )


class CostEstimatesOfFoodborneIllnessesFetcher(
    Fetcher[
        CostEstimatesOfFoodborneIllnessesQueryParams,
        list[CostEstimatesOfFoodborneIllnessesData],
    ]
):
    """Fetch USDA ERS Cost Estimates of Foodborne Illnesses."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> CostEstimatesOfFoodborneIllnessesQueryParams:
        """Transform the query params."""
        return CostEstimatesOfFoodborneIllnessesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CostEstimatesOfFoodborneIllnessesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's wide per-pathogen rows."""
        from openbb_government_us.usda.utils import (
            ers_cost_estimates_of_foodborne_illnesses,
        )

        return await ers_cost_estimates_of_foodborne_illnesses.afetch_table(query.table)

    @staticmethod
    def transform_data(
        query: CostEstimatesOfFoodborneIllnessesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[CostEstimatesOfFoodborneIllnessesData]:
        """Emit the wide rows in source order, dropping temporary keys."""
        results = sorted(data, key=lambda row: row["_order"])
        return [
            CostEstimatesOfFoodborneIllnessesData.model_validate(
                {k: v for k, v in row.items() if not k.startswith("_")}
            )
            for row in results
        ]
