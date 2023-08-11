"""Due Diligence Router."""


from openbb_core.app.model.obbject import Obbject
from openbb_core.app.model.results.empty import Empty
from openbb_core.app.router import Router

router = Router(prefix="/gov")


@router.command
def contracts() -> Obbject[Empty]:  # type: ignore
    """Return government contracts."""
    return Obbject(results=Empty())


@router.command
def government_trading() -> Obbject[Empty]:  # type: ignore
    """Return government trading."""
    return Obbject(results=Empty())


@router.command  # Isn't this one the same as the one above?
def gtrades() -> Obbject[Empty]:  # type: ignore
    """Return government trades."""
    return Obbject(results=Empty())


@router.command
def histcont() -> Obbject[Empty]:  # type: ignore
    """Historical quarterly government contracts."""
    return Obbject(results=Empty())


@router.command
def lastcontracts() -> Obbject[Empty]:  # type: ignore
    """Return last government contracts given out."""
    return Obbject(results=Empty())


@router.command
def lasttrades() -> Obbject[Empty]:  # type: ignore
    """Last trades."""
    return Obbject(results=Empty())


@router.command
def lobbying() -> Obbject[Empty]:  # type: ignore
    """Corporate lobbying details."""
    return Obbject(results=Empty())


@router.command
def qtrcontracts() -> Obbject[Empty]:  # type: ignore
    """Quarterly government contracts analysis."""
    return Obbject(results=Empty())


@router.command
def topbuys() -> Obbject[Empty]:  # type: ignore
    """Show most purchased stocks."""
    return Obbject(results=Empty())


@router.command
def toplobbying() -> Obbject[Empty]:  # type: ignore
    """Top corporate lobbying tickers."""
    return Obbject(results=Empty())


@router.command
def topsells() -> Obbject[Empty]:  # type: ignore
    """Show most sold stocks."""
    return Obbject(results=Empty())
