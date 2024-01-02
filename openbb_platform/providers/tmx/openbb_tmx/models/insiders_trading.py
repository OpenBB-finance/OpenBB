"""TMX Insiders Trading Model"""
import json
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.helpers import to_snake_case
from openbb_tmx.utils import gql
from openbb_tmx.utils.helpers import get_data_from_gql, get_random_agent
from pydantic import Field, field_validator


class TmxInsidersTradingQueryParams(QueryParams):
    """TMX Insiders Trading Query Params"""

    symbol: str = Field(description="The ticker symbol of the company")
    summary: bool = Field(
        default=False,
        description="Return a summary of the insider activity instead of the individuals.",
    )


class TmxInsidersTradingData(Data):
    """TMX Insiders Trading Data"""

    period: str = Field(
        description="The period of the activity. Bucketed by three, six, and twelve months."
    )
    owner_name: Optional[str] = Field(
        default=None, description="The name of the insider."
    )
    acquisition_or_deposition: Optional[str] = Field(
        default=None, description="Whether the insider bought or sold the shares."
    )
    number_of_trades: Optional[int] = Field(
        default=None, description="The number of shares traded over the period."
    )
    securities_owned: Optional[int] = Field(
        default=None, description="The number of shares held by the insider."
    )
    trade_value: Optional[float] = Field(
        default=None, description="The value of the shares traded by the insider."
    )
    securities_transacted: Optional[int] = Field(
        default=None,
        description="The total number of shares traded by the insider over the period.",
    )
    securities_bought: Optional[int] = Field(
        default=None,
        description="The total number of shares bought by all insiders over the period.",
    )
    securities_sold: Optional[int] = Field(
        default=None,
        description="The total number of shares sold by all insiders over the period.",
    )
    net_activity: Optional[int] = Field(
        default=None,
        description="The total net activity by all insiders over the period.",
    )

    @field_validator("period", mode="before", check_fields=False)
    @classmethod
    def period_to_snake_case(cls, v):
        return to_snake_case(v) if v else None


class TmxInsidersTradingFetcher(
    Fetcher[
        TmxInsidersTradingQueryParams,
        List[TmxInsidersTradingData],
    ]
):
    """TMX Insiders Trading Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxInsidersTradingQueryParams:
        """Transform the query."""
        return TmxInsidersTradingQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxInsidersTradingQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""

        results = []
        user_agent = get_random_agent()
        symbol = (
            query.symbol.upper()
            .replace("-", ".")
            .replace(".TO", "")
            .replace(".TSX", "")
        )
        payload = gql.get_company_insiders_payload.copy()
        payload["variables"]["symbol"] = symbol

        url = "https://app-money.tmx.com/graphql"
        response = await get_data_from_gql(
            method="POST",
            url=url,
            data=json.dumps(payload),
            headers={
                "authority": "app-money.tmx.com",
                "referer": f"https://money.tmx.com/en/quote/{symbol}",
                "locale": "en",
                "Content-Type": "application/json",
                "User-Agent": user_agent,
                "Accept": "*/*",
            },
            timeout=5,
        )

        if response.get("data") and response["data"].get(
            "getCompanyInsidersActivities"
        ):
            results = response["data"]["getCompanyInsidersActivities"]
        return results

    @staticmethod
    def transform_data(
        query: TmxInsidersTradingQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TmxInsidersTradingData]:
        """Transform the data."""
        data = data.copy()
        results = []
        flattened_insiders = []
        for activity in data["insiderActivities"]:  # type: ignore
            for transaction_type in ["buy", "sell"]:
                for transaction in activity[transaction_type]:
                    new_transaction = {
                        "period": activity["periodkey"],
                        "acquisition_or_deposition": transaction_type,
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

        return [TmxInsidersTradingData.model_validate(d) for d in results]
