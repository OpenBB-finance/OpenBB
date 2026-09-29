"""TMX Insider Trading Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.insider_trading import (
    InsiderTradingData,
    InsiderTradingQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class TmxInsiderTradingQueryParams(InsiderTradingQueryParams):
    """TMX Insider Trading Query Params."""

    summary: bool = Field(
        default=False,
        description="Return a summary of the insider activity instead of the individuals.",
    )


class TmxInsiderTradingData(InsiderTradingData):
    """TMX Insider Trading Data."""

    period: str = Field(
        description="The period of the activity. Bucketed by three, six, and twelve months."
    )
    owner_name: str | None = Field(default=None, description="The name of the insider.")
    acquisition_or_deposition: str | None = Field(
        default=None, description="Whether the insider bought or sold the shares."
    )
    number_of_trades: int | None = Field(
        default=None, description="The number of shares traded over the period."
    )
    securities_owned: int | None = Field(
        default=None, description="The number of shares held by the insider."
    )
    trade_value: float | None = Field(
        default=None, description="The value of the shares traded by the insider."
    )
    securities_transacted: int | None = Field(
        default=None,
        description="The total number of shares traded by the insider over the period.",
    )
    securities_bought: int | None = Field(
        default=None,
        description="The total number of shares bought by all insiders over the period.",
    )
    securities_sold: int | None = Field(
        default=None,
        description="The total number of shares sold by all insiders over the period.",
    )
    net_activity: int | None = Field(
        default=None,
        description="The total net activity by all insiders over the period.",
    )

    @field_validator("period", mode="before", check_fields=False)
    @classmethod
    def period_to_snake_case(cls, v):
        """Convert the period to snake case."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import to_snake_case

        return to_snake_case(v) if v else None


class TmxInsiderTradingFetcher(
    Fetcher[
        TmxInsiderTradingQueryParams,
        list[TmxInsiderTradingData],
    ]
):
    """TMX Insider Trading Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxInsiderTradingQueryParams:
        """Transform the query."""
        return TmxInsiderTradingQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxInsiderTradingQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the TMX endpoint."""
        from openbb_tmx.utils import gql
        from openbb_tmx.utils.cache import amake_gql_request
        from openbb_tmx.utils.helpers import normalize_symbol

        symbol = normalize_symbol(query.symbol)
        response = await amake_gql_request(
            "getCompanyInsidersActivities",
            gql.COMPANY_INSIDERS,
            {"symbol": symbol},
            symbol=symbol,
        )
        results = (response or {}).get("getCompanyInsidersActivities")

        if not results:
            raise EmptyDataError()

        return results

    @staticmethod
    def transform_data(
        query: TmxInsiderTradingQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxInsiderTradingData]:
        """Transform the data."""
        data = data.copy()
        results = []
        flattened_insiders = []
        for activity in data["insiderActivities"]:  # type: ignore
            for transaction_type in ["buy", "sell"]:
                for transaction in activity[transaction_type]:
                    new_transaction = {
                        "period": activity["periodkey"],
                        "acquisition_or_disposition": transaction_type,
                        "owner_name": transaction["name"],
                        "number_of_trades": transaction["trades"],
                        "securities_transacted": transaction["shares"],
                        "securities_owned": transaction["sharesHeld"],
                        "trade_value": transaction["tradeValue"],
                    }
                    flattened_insiders.append(new_transaction)
        flattened_summary = []
        for activity in data["activitySummary"]:  # type: ignore
            new_activity = {
                "period": activity["periodkey"],
                "securities_bought": activity["buyShares"],
                "securities_sold": activity["soldShares"],
                "net_activity": activity["netActivity"],
                "securities_transacted": activity["totalShares"],
            }
            flattened_summary.append(new_activity)
        if query.summary is False and len(flattened_insiders) > 0:
            results = flattened_insiders
        elif query.summary is True and len(flattened_summary) > 0:
            results = flattened_summary

        return [TmxInsiderTradingData.model_validate(d) for d in results]
