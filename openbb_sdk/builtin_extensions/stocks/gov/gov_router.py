"""Due Diligence Router."""


from openbb_sdk_core.app.model.command_output import CommandOutput
from openbb_sdk_core.app.model.results.empty import Empty
from openbb_sdk_core.app.router import Router

router = Router(prefix="/gov")


@router.command
def contracts() -> CommandOutput[Empty]:  # type: ignore
    """Return government contracts."""
    return CommandOutput(results=Empty())


@router.command
def government_trading() -> CommandOutput[Empty]:  # type: ignore
    """Return government trading."""
    return CommandOutput(results=Empty())


@router.command  # Isn't this one the same as the one above?
def gtrades() -> CommandOutput[Empty]:  # type: ignore
    """Return government trades."""
    return CommandOutput(results=Empty())


@router.command
def histcont() -> CommandOutput[Empty]:  # type: ignore
    """Historical quarterly government contracts."""
    return CommandOutput(results=Empty())


@router.command
def lastcontracts() -> CommandOutput[Empty]:  # type: ignore
    """Return last government contracts given out."""
    return CommandOutput(results=Empty())


@router.command
def lasttrades() -> CommandOutput[Empty]:  # type: ignore
    """Last trades."""
    return CommandOutput(results=Empty())


@router.command
def lobbying() -> CommandOutput[Empty]:  # type: ignore
    """Corporate lobbying details."""
    return CommandOutput(results=Empty())


@router.command
def qtrcontracts() -> CommandOutput[Empty]:  # type: ignore
    """Quarterly government contracts analysis."""
    return CommandOutput(results=Empty())


@router.command
def topbuys() -> CommandOutput[Empty]:  # type: ignore
    """Show most purchased stocks."""
    return CommandOutput(results=Empty())


@router.command
def toplobbying() -> CommandOutput[Empty]:  # type: ignore
    """Top corporate lobbying tickers."""
    return CommandOutput(results=Empty())


@router.command
def topsells() -> CommandOutput[Empty]:  # type: ignore
    """Show most sold stocks."""
    return CommandOutput(results=Empty())
