"""Empty Fetcher Model. This model is used in conjunction with the 'empty_router' extension."""

# pylint: disable=unused-import
# flake8: noqa: F401

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class EmptyQueryParams(QueryParams):
    """Empty Query Params"""

    some_param: Optional[str] = Field(
        default=None,
        description="Some param",
    )


class EmptyData(Data):
    """Empty Data"""

    date: Optional[dateType] = Field(
        default=None,
        description="Date of the data.",
    )
    title: Optional[str] = Field(
        default=None,
        description="Title of the data.",
    )


class EmptyFetcher(
    Fetcher[
        EmptyQueryParams,
        EmptyData,  # Change the Typing when returning a list of models - i.e, records.
    ]
):
    """Empty Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> EmptyQueryParams:
        """Transform query params."""
        transformed_params = params.copy()
        # if transformed_params.get("some_param"):
        #     do something
        #
        # This is where you can set default values for query parameters.
        # Essentially, `@model_validate(mode='before')`.
        return EmptyQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: EmptyQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:  # Typing here should match the 'data' input of 'transform_data'.
        """Extract data."""
        # pylint: disable=import-outside-toplevel
        # from openbb_core.provider.utils.helpers import (
        #    make_request,
        #    amake_request,
        #    amake_requests,
        #    get_querystring,
        # )   Use these to make HTTP requests.

        # We import here so that items are imported on execution, not on initialization.
        # Critical for modules that introduce a heavy load on the system.
        # Generally, any module required for data retrieval and parsing should be 'lazy' imported.
        # This is to ensure that the module is only imported when needed.

        print(query.some_param)  # noqa: T201
        results = {
            "date": datetime.now().date(),
            "title": "Hello from the Empty Provider extension!",
        }
        return results

    @staticmethod
    def transform_data(
        query: EmptyQueryParams,
        data: Dict,  # Typing here matches the output of '(a)extract_data'.
        **kwargs: Any,
    ) -> EmptyData:  # Typing here matches the Fetcher's definition.
        """Transform data."""
        return EmptyData.model_validate(data)
