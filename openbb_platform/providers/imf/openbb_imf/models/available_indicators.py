"""IMF Available Indicators."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.available_indicators import (
    AvailableIndicatorsData,
    AvailableIndicesQueryParams,
)
from pydantic import Field


class ImfAvailableIndicatorsQueryParams(AvailableIndicesQueryParams):
    """IMF Available Indicators Query Parameters."""


class ImfAvailableIndicatorsData(AvailableIndicatorsData):
    """IMF Available Indicators Data."""

    __alias_dict__ = {
        "symbol_root": "parent",
        "description": "title",
    }

    table: Optional[str] = Field(
        default=None,
        description="The name of the table associated with the symbol.",
    )
    level: Optional[int] = Field(
        default=None,
        description="The indentation level of the data, relative to the table and symbol_root",
    )
    order: Optional[int] = Field(
        default=None,
        description="Order of the data, relative to the table.",
    )


class ImfAvailableIndicatorsFetcher(
    Fetcher[ImfAvailableIndicatorsQueryParams, List[ImfAvailableIndicatorsData]]
):
    """IMF Available Indicators Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> ImfAvailableIndicatorsQueryParams:
        """Transform the query."""
        return ImfAvailableIndicatorsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: ImfAvailableIndicatorsQueryParams,
        credentials: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> List[Dict]:
        """Fetch the data."""
        # pylint: disable=import-outside-toplevel
        from openbb_imf.utils.irfcl_helpers import load_irfcl_symbols

        try:
            irfcl_symbols = load_irfcl_symbols()
        except OpenBBError as e:
            raise OpenBBError(f"Failed to load IMF IRFCL symbols: {e}") from e

        records: List = []
        for key, value in irfcl_symbols.items():
            value["symbol"] = key
            records.append(value)

        return records

    @staticmethod
    def transform_data(
        query: ImfAvailableIndicatorsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[ImfAvailableIndicatorsData]:
        """Transform the data."""
        return [ImfAvailableIndicatorsData.model_validate(d) for d in data]
