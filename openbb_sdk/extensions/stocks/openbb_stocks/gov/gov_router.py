"""Due Diligence Router."""


from openbb_core.app.model.obbject import OBBject
from openbb_core.app.model.results.empty import Empty
from openbb_core.app.router import Router

router = Router(prefix="/gov")


@router.command
def contracts() -> OBBject[Empty]:  # type: ignore
    """Return government contracts."""
    return OBBject(results=Empty())


@router.command
def government_trading() -> OBBject[Empty]:  # type: ignore
    """Return government trading."""
    return OBBject(results=Empty())


@router.command  # Isn't this one the same as the one above?
def gtrades() -> OBBject[Empty]:  # type: ignore
    """Return government trades."""
    return OBBject(results=Empty())


@router.command
def histcont() -> OBBject[Empty]:  # type: ignore
    """Historical quarterly government contracts."""
    return OBBject(results=Empty())


@router.command
def lastcontracts() -> OBBject[Empty]:  # type: ignore
    """Return last government contracts given out."""
    return OBBject(results=Empty())


@router.command
def lasttrades() -> OBBject[Empty]:  # type: ignore
    """Last trades."""
    return OBBject(results=Empty())


@router.command
def lobbying() -> OBBject[Empty]:  # type: ignore
    """Corporate lobbying details."""
    return OBBject(results=Empty())


@router.command
def qtrcontracts() -> OBBject[Empty]:  # type: ignore
    """Quarterly government contracts analysis."""
    return OBBject(results=Empty())


@router.command
def topbuys() -> OBBject[Empty]:  # type: ignore
    """Show most purchased stocks."""
    return OBBject(results=Empty())


@router.command
def toplobbying() -> OBBject[Empty]:  # type: ignore
    """Top corporate lobbying tickers."""
    return OBBject(results=Empty())


@router.command
def topsells() -> OBBject[Empty]:  # type: ignore
    """Show most sold stocks."""
    return OBBject(results=Empty())
