"""{{cookiecutter.router_name}} router command example."""

# pylint: disable=unused-argument

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import ExtraParams, ProviderChoices, StandardParams
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from pydantic import BaseModel

# Example dependency injection yielding a configured requests.Session object.
from {{cookiecutter.package_name}}.routers.depends import Session

# The prefix extension's prefix is determined by the `pyproject.toml` EntryPoint assignment.
# Assign a prefix only if this is a sub-router.
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


@router.command(model="Example")
async def model_example(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Example Data."""
    return await OBBject.from_query(Query(**locals()))


# If you had another provider installed that mapped to this model - i.e, `openbb-fmp`
# they will be added to this endpoint.
@router.command(model="EquityHistorical")
async def candles(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject: # results type is inferred from Fetcher annotations.
    """Example Data."""
    return await OBBject.from_query(Query(**locals()))
