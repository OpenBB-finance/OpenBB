"""{{cookiecutter.router_name}} router command example."""
{% set types = cookiecutter.extension_types.split(',') | map('trim') | list %}
{% set has_provider = 'provider' in types or 'all' in types %}
# pylint: disable=unused-argument
{% if has_provider %}

from openbb_core.app.model.command_context import CommandContext
{% endif %}
from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
{% if has_provider %}
from openbb_core.app.provider_interface import ExtraParams, ProviderChoices, StandardParams
from openbb_core.app.query import Query
{% endif %}
from openbb_core.app.router import Router
from pydantic import BaseModel

from {{cookiecutter.package_name}}.routers.depends import Session

router = Router(prefix="")


@router.command(
    methods=["GET"],
    examples=[
        PythonEx(
            description="Here is an example for using this endpoint.",
            code=[
                "obb.{{ cookiecutter.router_name }}.get_example(symbol='AAPL')",
            ]
        )
    ]
)
async def get_example(session: Session, symbol: str = "AAPL") -> OBBject[dict]:
    """Get options data."""
    url = f"https://www.cboe.com/education/tools/trade-optimizer/symbol-info?symbol={symbol}"
    response = session.get(url)
    response.raise_for_status()
    data = response.json()

    return OBBject(results=data["details"])


@router.command(methods=["POST"])
async def post_example(
    data: BaseModel,  # These are body parameters.
    flag: bool = False,  # These are query parameters.
) -> OBBject[dict]:
    """Calculate mid and spread."""

    bid = getattr(data, "bid_col", 0)
    ask = getattr(data, "ask_col", 0)
    mid = (bid + ask) / 2
    spread = ask - bid

    return OBBject(results={"mid": mid, "spread": spread, "flag": flag})
{% if has_provider %}


@router.command(model="Example")
async def model_example(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Example Data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EquityHistorical")
async def candles(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Example Data."""
    return await OBBject.from_query(Query(**locals()))
{% endif %}
