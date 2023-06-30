from openbb_sdk_core.app.model.command_output import CommandOutput
from openbb_sdk_core.app.model.item.empty import Empty
from openbb_sdk_core.app.router import Router

router = Router(prefix="")


@router.command
def globalnews() -> CommandOutput[Empty]:  # type: ignore
    """Global news."""
    return CommandOutput(item=Empty())


@router.command
def sectornews() -> CommandOutput[Empty]:  # type: ignore
    """Sector news."""
    return CommandOutput(item=Empty())
