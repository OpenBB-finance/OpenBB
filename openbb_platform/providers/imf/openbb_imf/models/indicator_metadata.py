"""Miscellaneous metadata models for IMF provider."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class ImfIndicatorMetadata(Data):
    """Model representing an IMF Indicator."""

    symbol: str = Field(
        description="Concatenated series identifier for the indicator.",
        validation_alias="series_id",
        serialization_alias="symbol",
        json_schema_extra={
            "x-widget_config": {
                "renderFn": "cellOnClick",
                "renderFnParams": {
                    "actionType": "groupBy",
                    "groupBy": {
                        "paramName": "symbol",
                        "valueField": "symbol",
                    },
                },
            }
        },
    )
    label: str = Field(description="Human-readable label for the indicator.")
    description: str | None = Field(
        default=None, description="Detailed description of the indicator."
    )
    dimension_id: str = Field(
        description="The dimension ID of the indicator in the data structure."
    )
    indicator: str = Field(description="Indicator code.")
    agency_id: str = Field(description="The agency ID responsible for the indicator.")
    structure_id: str = Field(
        description="The data structure ID associated with the indicator."
    )
    dataflow_id: str = Field(
        description="The IMF dataflow ID the indicator belongs to."
    )
    dataflow_name: str = Field(description="The name of the IMF dataflow.")


class ImfTableMetadata(Data):
    """Model representing an IMF Table."""

    name: str = Field(description="The name of the IMF table.")
    symbol: str = Field(description="The table symbol.")
    description: str = Field(description="Description of the IMF table.")
    agency_id: str = Field(description="The agency ID responsible for the table.")
    dataflow_id: str = Field(description="The IMF dataflow ID the table belongs to.")
    codelist_id: str = Field(description="The codelist ID associated with the table.")


class ImfPresentationTableQuery(QueryParams):
    """Query parameters for IMF presentation table metadata."""

    dataflow: str | None = Field(
        default=None,
        description="The IMF dataflow ID. See list_dataflows() for options.",
    )
    table: str | None = Field(
        default=None, description="The IMF table ID. See list_tables() for options."
    )
    country: str | None = Field(
        default=None, description="Country code to filter the data."
    )
    frequency: str | None = Field(default=None, description="Frequency of the data.")
    dimension_values: str | None = Field(
        default=None,
        description="Dimension selection for filtering. Format: 'DIM_ID1:VAL1+VAL2.'"
        + " See presentation_table_choices() and list_dataflow_choices() for available dimensions and values.",
    )
    limit: int = Field(
        default=4, description="Maximum number of records to retrieve per series."
    )
    raw: bool = Field(
        default=False,
        description="Return presentation table as raw JSON data if True.",
    )
