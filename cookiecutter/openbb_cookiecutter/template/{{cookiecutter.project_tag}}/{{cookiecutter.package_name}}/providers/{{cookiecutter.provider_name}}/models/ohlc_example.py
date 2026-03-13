"""Example Data Integration With Standard Model.

This file shows an example of how to integrate this provider with ends available to other providers.
"""

# pylint: disable=unused-argument
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
from pydantic import Field, field_validator


class {{cookiecutter.provider_name.replace('_', ' ').capitalize().replace(' ', '')}}EquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """Example provider query.

    The standard model here comes with parameters for symbol, start_date, and end_date.
    """

    custom_param: str | None = Field(
        default=None, description="Some optional parameter"
    )


class {{cookiecutter.provider_name.replace('_', ' ').capitalize().replace(' ', '')}}EquityHistoricalData(EquityHistoricalData):
    """Sample provider data.

    The standard model has these fields,
    so we use __alias_dict__ to map them.
    We only need to add fields not in the inherited model, or to override.
    """

    __alias_dict__ = {
        "date": "d",
        "open": "o",
        "high": "h",
        "low": "l",
        "close": "c",
        "volume": "v",
        "custom_field": "f",
    }
    custom_field: str | None = Field(default=None, description="Some optional field")

    @field_validator("custom_field", mode="before", check_fields=False)
    @classmethod
    def _validate_custom_field(cls, v):
        """Validate the custom field."""
        return v if v else "Data validator replaced None."


class {{cookiecutter.provider_name.replace('_', ' ').capitalize().replace(' ', '')}}EquityHistoricalFetcher(
    Fetcher[
        {{cookiecutter.provider_name.replace('_', ' ').capitalize().replace(' ', '')}}EquityHistoricalQueryParams,
        list[{{cookiecutter.provider_name.replace('_', ' ').capitalize().replace(' ', '')}}EquityHistoricalData],
    ]
):
    """Example Fetcher class.

    This class is responsible for the actual data retrieval.
    """

    @staticmethod
    def transform_query(params: dict[str, Any]) -> {{cookiecutter.provider_name.replace('_', ' ').capitalize().replace(' ', '')}}EquityHistoricalQueryParams:
        """Define example transform_query.

        Here we can pre-process the query parameters and add any extra parameters that
        will be used inside the extract_data method.
        """
        return {{cookiecutter.provider_name.replace('_', ' ').capitalize().replace(' ', '')}}EquityHistoricalQueryParams(**params)

    # Note the use of async here. Make the Fetcher async with this small change.
    @staticmethod
    async def aextract_data(
        query: {{cookiecutter.provider_name.replace('_', ' ').capitalize().replace(' ', '')}}EquityHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Define example extract_data.

        Here we make the actual request to the data provider and receive the raw data.
        If you said your Provider class needs credentials you can get them here.
        """
        api_key = (
            credentials.get("{{ cookiecutter.provider_name }}_api_key") if credentials else ""
        )

        # Here we mock an example_response for brevity.
        # Show model validation by only returning one row of custom_field
        # Show model validation by only returning one row of custom_field
        example_response = [
            {
                "o": 2,
                "h": 5,
                "l": 1,
                "c": 4,
                "v": 5,
                "d": "August 23, 2023",
                "f": query.custom_param,
            },
            {
                "o": 4,
                "h": 7,
                "l": 3,
                "c": 6,
                "v": 10,
                "d": "August 24, 2023",
                "f": None,
            },
        ]

        return example_response

    @staticmethod
    def transform_data(
        query: {{cookiecutter.provider_name.replace('_', ' ').capitalize().replace(' ', '')}}EquityHistoricalQueryParams,
        data: list[dict],
        **kwargs: Any
    ) -> list[{{cookiecutter.provider_name.replace('_', ' ').capitalize().replace(' ', '')}}EquityHistoricalData]:
        """Define example transform_data.

        Right now, we're converting the data to fit our desired format.
        You can apply other transformations to it here.
        """
        return [{{cookiecutter.provider_name.replace('_', ' ').capitalize().replace(' ', '')}}EquityHistoricalData.model_validate(d) for d in data]
