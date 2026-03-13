"""Example Data Integration.

The OpenBB Platform gives developers easy tools for integration.

To use it, developers should:
1. Define the request/query parameters.
2. Define the resulting data schema.
3. Define how to fetch raw data.

First 2 steps make sure developers really get to know their data.
This is called the "Know Your Data" principle.

Note: The format of the QueryParams and Data is defined by a pydantic model that can
be entirely custom, or inherit from the OpenBB standardized models.

This file shows an example of how to integrate data from a provider.
"""
# pylint: disable=unused-argument
from typing import Any, Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class ExampleQueryParams(QueryParams):
    """Example provider query.

    This is the definition of our query parameters that are specific to this provider.
    We use this class to create our own parameters that will provided as input to the
    command.
    """

    symbol: str = Field(description="Symbol to query.")


class ExampleData(Data):
    """Sample provider data.

    The fields are displayed as-is in the output of the command. In this case, its the
    Open, High, Low, Close and Volume data.
    """

    o: float = Field(description="Open price.")
    h: float = Field(description="High price.")
    l: float = Field(description="Low price.")
    c: float = Field(description="Close price.")
    v: float = Field(description="Volume.")
    d: str = Field(description="Date")


class ExampleFetcher(
    Fetcher[
        ExampleQueryParams,
        list[ExampleData],
    ]
):
    """Example Fetcher class.

    This class is responsible for the actual data retrieval.
    """

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ExampleQueryParams:
        """Define example transform_query.

        Here we can pre-process the query parameters and add any extra parameters that
        will be used inside the extract_data method.
        """
        return ExampleQueryParams(**params)

    @staticmethod
    def extract_data(
        query: ExampleQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Define example extract_data.

        Here we make the actual request to the data provider and receive the raw data.
        If you said your Provider class needs credentials you can get them here.
        """
        api_key = (
            credentials.get("{{cookiecutter.package_name}}_api_key")
            if credentials
            else ""
        )

        # Here we mock an example_response for brevity.
        example_response = [
            {
                "o": 2,
                "h": 5,
                "l": 1,
                "c": 4,
                "v": 5,
                "d": "August 23, 2023",
            },
            {
                "o": 4,
                "h": 7,
                "l": 3,
                "c": 6,
                "v": 10,
                "d": "August 24, 2023",
            },
        ]

        return example_response

    @staticmethod
    def transform_data(
        query: ExampleQueryParams, data: list[dict], **kwargs: Any
    ) -> list[ExampleData]:
        """Define example transform_data.

        Right now, we're converting the data to fit our desired format.
        You can apply other transformations to it here.
        """
        return [ExampleData(**d) for d in data]
