"""IMF Available Indicators."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.available_indicators import (
    AvailableIndicatorsData,
    AvailableIndicesQueryParams,
)
from pydantic import ConfigDict, Field


class ImfAvailableIndicatorsQueryParams(AvailableIndicesQueryParams):
    """IMF Available Indicators Query Parameters."""

    __json_schema_extra__ = {
        "query": {"multiple_items_allowed": True},
        "dataflows": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": "/api/v1/imf_utils/list_dataflow_choices",
                "multiSelect": False,
                "style": {"popupWidth": 950},
            },
        },
        "symbol": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "text",
                "multiSelect": False,
                "style": {"width": 400},
                "multiple": True,
            },
        },
        "keywords": {"multiple_items_allowed": True},
    }

    query: str | None = Field(
        default=None,
        description="The search query string. Multiple search phrases can be separated by semicolons."
        + " Each phrase can use AND (+) and OR (|) operators, as well as quoted phrases."
        + " Semicolon separation allows commas to be used within search phrases.",
    )
    dataflows: str | list[str] | None = Field(
        default=None,
        description="List of IMF dataflow IDs to filter the indicators."
        + " Use semicolons to separate multiple dataflow IDs.",
    )
    keywords: str | list[str] | None = Field(
        default=None,
        description="List of keywords to filter results. Each keyword is a single word that must"
        + " appear in the indicator's label or description. Keywords prefixed with 'not'"
        + " will exclude indicators containing that word (e.g., 'not USD' excludes indicators"
        + " with 'USD' in them).",
    )
    symbol: str | None = Field(
        default=None,
        exclude=True,
        description="Dummy field to allow grouping by symbol.",
    )


class ImfAvailableIndicatorsData(AvailableIndicatorsData):
    """IMF Available Indicators Data."""

    __alias_dict__ = {
        "description": "label",
        "symbol": "series_id",
        "symbol_root": "indicator",
        "long_description": "description",
    }

    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "symbol": {
                "x-widget_config": {
                    "renderFn": "cellOnClick",
                    "renderFnParams": {
                        "actionType": "groupBy",
                        "groupByParamName": "symbol",
                    },
                }
            }
        },
    )

    agency_id: str = Field(description="The agency ID responsible for the indicator.")
    dataflow_id: str = Field(
        description="The IMF dataflow ID associated with the indicator."
    )
    dataflow_name: str = Field(
        description="The name of the IMF dataflow (symbol root)."
    )
    structure_id: str = Field(
        description="The data structure ID associated with the indicator."
    )
    dimension_id: str = Field(
        description="The dimension ID of the indicator in the data structure."
    )
    long_description: str | None = Field(
        default=None, description="Detailed description of the indicator."
    )
    member_of: list[str] = Field(
        default_factory=list,
        description="List of table symbols (dataflow_id::table_id) this indicator belongs to.",
    )


class ImfAvailableIndicatorsFetcher(
    Fetcher[ImfAvailableIndicatorsQueryParams, list[ImfAvailableIndicatorsData]]
):
    """IMF Available Indicators Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ImfAvailableIndicatorsQueryParams:
        """Transform the query."""
        return ImfAvailableIndicatorsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: ImfAvailableIndicatorsQueryParams,
        credentials: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch the data."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.errors import EmptyDataError
        from openbb_imf.utils.metadata import ImfMetadata

        metadata = ImfMetadata()

        if isinstance(query.dataflows, str):
            dataflows = query.dataflows.split(",")
        elif isinstance(query.dataflows, list):
            dataflows = query.dataflows
        else:
            dataflows = None

        if isinstance(query.keywords, str):
            keywords = query.keywords.split(",")
        elif isinstance(query.keywords, list):
            keywords = query.keywords
        else:
            keywords = None

        try:
            results = metadata.search_indicators(
                query=query.query.replace(",", ", ") if query.query else "",
                dataflows=dataflows,
                keywords=keywords,
            )
        except Exception as e:  # pylint: disable=broad-except
            raise OpenBBError(e) from e

        if not results:
            raise EmptyDataError("No indicators found for the given query.")

        return results

    @staticmethod
    def transform_data(
        query: ImfAvailableIndicatorsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[ImfAvailableIndicatorsData]:
        """Transform the data."""
        results = []
        for d in data:
            # Build the ready-to-use symbol: dataflow_id::indicator_code
            dataflow_id = d.get("dataflow_id", "")
            indicator_code = d.get("indicator", "")
            d["symbol"] = f"{dataflow_id}::{indicator_code}"
            results.append(ImfAvailableIndicatorsData.model_validate(d))
        return results
