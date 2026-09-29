{%- set provider_class = cookiecutter.provider_name.replace('_', ' ').title().replace(' ', '') -%}
"""{{ provider_class }} Equity Historical model built on the standard model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
from pydantic import Field, field_validator


class {{ provider_class }}EquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """{{ provider_class }} Equity Historical query parameters."""

    custom_param: str | None = Field(
        default=None, description="An optional provider-specific parameter."
    )


class {{ provider_class }}EquityHistoricalData(EquityHistoricalData):
    """{{ provider_class }} Equity Historical data."""

    __alias_dict__ = {
        "date": "d",
        "open": "o",
        "high": "h",
        "low": "l",
        "close": "c",
        "volume": "v",
        "custom_field": "f",
    }

    custom_field: str | None = Field(
        default=None, description="An optional provider-specific field."
    )

    @field_validator("custom_field", mode="before", check_fields=False)
    @classmethod
    def _default_custom_field(cls, v: str | None) -> str:
        """Replace a missing custom field with a default value."""
        return v or "Data validator replaced None."


class {{ provider_class }}EquityHistoricalFetcher(
    Fetcher[
        {{ provider_class }}EquityHistoricalQueryParams,
        list[{{ provider_class }}EquityHistoricalData],
    ]
):
    """{{ provider_class }} Equity Historical fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> {{ provider_class }}EquityHistoricalQueryParams:
        """Transform the query parameters.

        Parameters
        ----------
        params : dict[str, Any]
            The raw query parameters.

        Returns
        -------
        {{ provider_class }}EquityHistoricalQueryParams
            The validated query.
        """
        return {{ provider_class }}EquityHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: {{ provider_class }}EquityHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw rows for the query.

        Parameters
        ----------
        query : {{ provider_class }}EquityHistoricalQueryParams
            The validated query.
        credentials : dict[str, str] | None
            The provider credentials.
        **kwargs : Any
            Additional keyword arguments.

        Returns
        -------
        list[dict]
            The raw rows.
        """
        return [
            {
                "d": "2023-08-23",
                "o": 2,
                "h": 5,
                "l": 1,
                "c": 4,
                "v": 5,
                "f": query.custom_param,
            },
            {
                "d": "2023-08-24",
                "o": 4,
                "h": 7,
                "l": 3,
                "c": 6,
                "v": 10,
                "f": None,
            },
        ]

    @staticmethod
    def transform_data(
        query: {{ provider_class }}EquityHistoricalQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[{{ provider_class }}EquityHistoricalData]:
        """Validate the raw rows into the data model.

        Parameters
        ----------
        query : {{ provider_class }}EquityHistoricalQueryParams
            The validated query.
        data : list[dict]
            The raw rows.
        **kwargs : Any
            Additional keyword arguments.

        Returns
        -------
        list[{{ provider_class }}EquityHistoricalData]
            The validated rows.
        """
        return [{{ provider_class }}EquityHistoricalData.model_validate(row) for row in data]
