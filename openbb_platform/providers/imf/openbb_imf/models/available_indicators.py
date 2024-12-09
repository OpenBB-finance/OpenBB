"""IMF Available Indicators."""

# pylint: disable=unused-argument

from typing import Any, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.available_indicators import (
    AvailableIndicatorsData,
    AvailableIndicesQueryParams,
)
from pydantic import Field


class ImfAvailableIndicatorsQueryParams(AvailableIndicesQueryParams):
    """IMF Available Indicators Query Parameters."""

    __json_schema_extra__ = {"query": {"multiple_items_allowed": True}}

    query: Optional[str] = Field(
        default=None,
        description="The query string to search through the available indicators."
        + " Use semicolons to separate multiple terms.",
    )


class ImfAvailableIndicatorsData(AvailableIndicatorsData):
    """IMF Available Indicators Data."""

    __alias_dict__ = {
        "symbol_root": "parent",
        "description": "title",
    }
    dataset: Optional[str] = Field(
        default=None,
        description="The IMF dataset associated with the symbol.",
    )
    table: Optional[str] = Field(
        default=None,
        description="The name of the table associated with the symbol.",
    )
    level: Optional[int] = Field(
        default=None,
        description="The indentation level of the data, relative to the table and symbol_root",
    )
    order: Optional[Union[int, float]] = Field(
        default=None,
        description="Order of the data, relative to the table.",
    )
    children: Optional[str] = Field(
        default=None,
        description="The symbol of the child data, if any.",
    )
    unit: Optional[str] = Field(
        default=None,
        description="The unit of the data.",
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
        credentials: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch the data."""
        # pylint: disable=import-outside-toplevel
        from numpy import nan
        from openbb_core.provider.utils.errors import EmptyDataError
        from openbb_imf.utils.constants import load_symbols
        from pandas import DataFrame, Series

        try:
            all_symbols = load_symbols("all")
        except OpenBBError as e:
            raise OpenBBError(f"Failed to load IMF symbols static file: {e}") from e

        terms = [term.strip() for term in query.query.split(";")] if query.query else []

        df = (
            DataFrame(all_symbols)
            .T.reset_index()
            .rename(columns={"index": "symbol"})
            .replace({nan: None})
        )

        if not terms:
            records = df.to_dict(orient="records")
        else:
            combined_mask = Series([True] * len(df))
            for term in terms:
                mask = df.apply(
                    lambda row, term=term: row.astype(str).str.contains(
                        term, case=False, regex=True, na=False
                    )
                ).any(axis=1)
                combined_mask &= mask

            matches = df[combined_mask]

            if matches.empty:
                raise EmptyDataError("No results found for the provided query.")

            records = matches.to_dict(orient="records")

        return records

    @staticmethod
    def transform_data(
        query: ImfAvailableIndicatorsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[ImfAvailableIndicatorsData]:
        """Transform the data."""
        return [ImfAvailableIndicatorsData.model_validate(d) for d in data]
