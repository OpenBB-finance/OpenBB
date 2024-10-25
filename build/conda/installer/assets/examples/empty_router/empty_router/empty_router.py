"""Empty Router Extenision for OpenBB Platform."""

from datetime import datetime

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from openbb_core.provider.abstract.data import Data

router = Router(prefix="", description="An Empty OpenBB Router Extension.")

# The first function call will take longer than the rest, as modules are loaded on the first call.

# Note that all routers must return an instance of `OBBject`, where the output is the `results` attribute.


# This is a standard router "get" command.
@router.command(
    methods=["GET"],
    examples=[
        PythonEx(
            description="Say Hello.",
            code=[
                "result = obb.empty.hello()",
            ],
        ),
    ],
)
async def hello() -> (
    OBBject[dict]
):  # The output of every router command must be an instance of `OBBject`.
    """OpenBB Hello World."""
    return OBBject(
        results={
            datetime.now().strftime(
                "%Y-%m-%d"
            ): "Hello from the Empty Router extension!"
        }
    )


# This uses the Provider Interface to call the empty provider fetcher.
@router.command(
    model="Empty",
    examples=[
        APIEx(parameters={"provider": "empty"}),
        PythonEx(
            description="Say Hello.",
            code=[
                "result = obb.empty.empty_function()",
            ],
        ),
    ],
)
async def empty_function(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[Data]:
    """An empty function using the Provider Interface."""
    return await OBBject.from_query(Query(**locals()))
