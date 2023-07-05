from openbb_sdk_core.app.model.command_output import CommandOutput
from openbb_sdk_core.app.model.results.empty import Empty
from openbb_sdk_core.app.router import Router

router = Router(prefix="/options")


@router.command
def chains() -> CommandOutput[Empty]:  # type: ignore
    """Return options chains with greeks."""
    return CommandOutput(results=Empty())


@router.command
def dte() -> CommandOutput[Empty]:  # type: ignore
    return CommandOutput(results=Empty())


@router.command
def eodchain() -> CommandOutput[Empty]:  # type: ignore
    """Gets option chain at a specific date."""
    return CommandOutput(results=Empty())


@router.command
def expirations() -> CommandOutput[Empty]:  # type: ignore
    """Return options expirations."""
    return CommandOutput(results=Empty())


@router.command
def grhist() -> CommandOutput[Empty]:  # type: ignore
    """Plot option greek history."""
    return CommandOutput(results=Empty())


@router.command
def hist() -> CommandOutput[Empty]:  # type: ignore
    """Plot option history."""
    return CommandOutput(results=Empty())


@router.command
def info() -> CommandOutput[Empty]:  # type: ignore
    """Display option information (volatility, IV rank, etc.)."""
    return CommandOutput(results=Empty())


@router.command
def last_price() -> CommandOutput[Empty]:  # type: ignore
    """Return last price of an option."""
    return CommandOutput(results=Empty())


@router.command
def oi() -> CommandOutput[Empty]:  # type: ignore
    """Plot option open interest."""
    return CommandOutput(results=Empty())


@router.command
def pcr() -> CommandOutput[Empty]:  # type: ignore
    """Display put/call ratio for ticker."""
    return CommandOutput(results=Empty())


@router.command
def price() -> CommandOutput[Empty]:  # type: ignore
    return CommandOutput(results=Empty())


@router.command
def unu() -> CommandOutput[Empty]:  # type: ignore
    """Show unusual options activity."""
    return CommandOutput(results=Empty())


@router.command
def voi() -> CommandOutput[Empty]:  # type: ignore
    """Plot volume and open interest."""
    return CommandOutput(results=Empty())


@router.command
def vol() -> CommandOutput[Empty]:  # type: ignore
    """Plot volume."""
    return CommandOutput(results=Empty())


@router.command
def vsurf() -> CommandOutput[Empty]:  # type: ignore
    """Show 3D volatility surface."""
    return CommandOutput(results=Empty())
