"""Deribit Expirations Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_deribit.utils.constants import ExpirationCurrencies, ExpirationKinds


class DeribitExpirationsQueryParams(QueryParams):
    """Deribit Expirations Query.

    Source: https://docs.deribit.com/api-reference/market-data/public-get_expirations
    """

    currency: ExpirationCurrencies = Field(
        default="grouped",
        description="The currency to list expirations for. 'any' pools every"
        + " currency together, and 'grouped' keeps them apart.",
    )
    kind: ExpirationKinds = Field(default="any", description="The kind of instrument.")
    currency_pair: str | None = Field(
        default=None,
        description="Narrow the listing to one currency pair, such as 'btc_usd'.",
    )


class DeribitExpirationsData(Data):
    """Deribit Expirations Data."""

    currency: str = Field(
        description="The currency the contracts settle in.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded", "pinned": "left"}
        },
    )
    kind: str = Field(
        description="The kind of instrument.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    code: str = Field(
        description="The expiration as it appears in instrument names.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    expiration: dateType | None = Field(
        default=None,
        description="The expiration date. Perpetual contracts carry none.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )


class DeribitExpirationsFetcher(
    Fetcher[DeribitExpirationsQueryParams, list[DeribitExpirationsData]]
):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitExpirationsQueryParams:
        """Transform the query."""
        return DeribitExpirationsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitExpirationsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        EmptyDataError
            If the exchange lists no expirations for the query.
        """
        from openbb_deribit.utils.helpers import get_expirations

        data = await get_expirations(query.currency, query.kind, query.currency_pair)

        if not data:
            raise EmptyDataError("Deribit lists no expirations matching the query.")

        return data

    @staticmethod
    def transform_data(
        query: DeribitExpirationsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[DeribitExpirationsData]:
        """Transform the data to the model.

        Raises
        ------
        EmptyDataError
            If every currency in the response listed nothing.
        """
        from pandas import to_datetime

        by_currency = (
            {query.currency: data}
            if all(isinstance(value, list) for value in data.values())
            else data
        )
        records: list[dict] = []

        for currency, kinds in by_currency.items():
            for kind, codes in kinds.items():
                for code in codes:
                    records.append(
                        {
                            "currency": currency.upper(),
                            "kind": kind,
                            "code": code,
                            "expiration": (
                                None
                                if code == "PERPETUAL"
                                else to_datetime(code).date()
                            ),
                        }
                    )

        if not records:
            raise EmptyDataError("Deribit lists no expirations matching the query.")

        return [
            DeribitExpirationsData.model_validate(record)
            for record in sorted(
                records,
                key=lambda d: (
                    d["currency"],
                    d["kind"],
                    d["expiration"] or dateType.max,
                ),
            )
        ]
