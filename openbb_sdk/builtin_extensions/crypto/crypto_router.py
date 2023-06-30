from openbb_sdk_core.app.model.command_output import CommandOutput
from openbb_sdk_core.app.model.item.empty import Empty
from openbb_sdk_core.app.router import Router

router = Router(prefix="")


@router.command
def load() -> CommandOutput[Empty]:  # type: ignore
    """Crypto Intraday Price."""
    return CommandOutput(item=Empty())
