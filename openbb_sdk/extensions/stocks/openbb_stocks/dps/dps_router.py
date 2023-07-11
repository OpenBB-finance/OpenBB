from openbb_sdk_core.app.model.command_output import CommandOutput
from openbb_sdk_core.app.model.results.empty import Empty
from openbb_sdk_core.app.router import Router

router = Router(prefix="/dps")


@router.command
def psi() -> CommandOutput[Empty]:  # type: ignore
    """Price vs short interest volume"""
    return CommandOutput(results=Empty())


@router.command
def ctb() -> CommandOutput[Empty]:  # type: ignore
    """Cost to borrow of stocks."""
    return CommandOutput(results=Empty())


@router.command
def dpotc() -> CommandOutput[Empty]:  # type: ignore
    """Dark pools (ATS) vs OTC data."""
    return CommandOutput(results=Empty())


@router.command
def ftd() -> CommandOutput[Empty]:  # type: ignore
    """Fails-to-deliver data."""
    return CommandOutput(results=Empty())


@router.command
def hsi() -> CommandOutput[Empty]:  # type: ignore
    """Show top high short interest stocks of over 20% ratio."""
    return CommandOutput(results=Empty())


@router.command
def pos() -> CommandOutput[Empty]:  # type: ignore
    """Dark pool short position."""
    return CommandOutput(results=Empty())


@router.command
def prom() -> CommandOutput[Empty]:  # type: ignore
    """Promising tickers based on dark pool shares regression."""
    return CommandOutput(results=Empty())


@router.command
def psi_q() -> CommandOutput[Empty]:  # type: ignore
    return CommandOutput(results=Empty())


@router.command
def psi_sg() -> CommandOutput[Empty]:  # type: ignore
    return CommandOutput(results=Empty())


@router.command
def shorted() -> CommandOutput[Empty]:  # type: ignore
    """Most shorted stocks."""
    return CommandOutput(results=Empty())


@router.command
def sidtc() -> CommandOutput[Empty]:  # type: ignore
    """Short interest and days to cover."""
    return CommandOutput(results=Empty())


@router.command
def spos() -> CommandOutput[Empty]:  # type: ignore
    """Net short vs position."""
    return CommandOutput(results=Empty())
