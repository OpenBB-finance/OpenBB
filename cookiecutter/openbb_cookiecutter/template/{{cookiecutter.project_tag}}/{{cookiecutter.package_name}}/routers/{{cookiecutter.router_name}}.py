{%- set types = cookiecutter.extension_types.split(',') | map('trim') | list -%}
{%- set has_provider = 'provider' in types or 'all' in types -%}
"""{{ cookiecutter.router_name }} router."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
{% if has_provider -%}
from openbb_core.app.model.command_context import CommandContext
{% endif -%}
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
{% if has_provider -%}
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
{% endif -%}
from openbb_core.app.router import Router
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.helpers import amake_request
from pydantic import Field

router = Router(prefix="", description="{{ cookiecutter.project_name }} commands.")

SYMBOL_INFO_URL = "https://www.cboe.com/education/tools/trade-optimizer/symbol-info"


class QuoteQueryParams(QueryParams):
    """Bid and ask prices to measure."""

    bid: float = Field(description="Bid price.")
    ask: float = Field(description="Ask price.")
    flag: bool = Field(default=False, description="A flag echoed in the results.")


@router.command(
    methods=["GET"],
    examples=[APIEx(parameters={"symbol": "AAPL"})],
)
async def get_example(symbol: str = "AAPL") -> OBBject[dict[str, Any]]:
    """Get the Cboe symbol details for a ticker."""
    response = await amake_request(f"{SYMBOL_INFO_URL}?symbol={symbol}")
    if not isinstance(response, dict):
        raise OpenBBError(f"Unexpected response for {symbol}: {response}")
    return OBBject(results=response["details"])


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"bid": 1.0, "ask": 3.0})],
)
async def post_example(params: QuoteQueryParams) -> OBBject[dict[str, Any]]:
    """Calculate the mid price and spread of a quote."""
    return OBBject(
        results={
            "mid": (params.bid + params.ask) / 2,
            "spread": params.ask - params.bid,
            "flag": params.flag,
        }
    )
{%- if has_provider %}


@router.command(
    model="Example",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "{{ cookiecutter.provider_name }}"})],
)
async def model_example(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get example OHLCV data from a provider."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EquityHistorical",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "{{ cookiecutter.provider_name }}"})],
)
async def candles(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get historical equity prices from a provider."""
    return await OBBject.from_query(Query(**locals()))
{%- endif %}
