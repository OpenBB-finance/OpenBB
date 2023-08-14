from openbb_core.app.modelobbject import OBBject
from openbb_core.app.model.results.empty import Empty
from openbb_core.app.router import Router

router = Router(prefix="/options")


@router.command
def chains() -> OBBject[Empty]:  # type: ignore
    """Return options chains with greeks."""
    return OBBject(results=Empty())


@router.command
def dte() -> OBBject[Empty]:  # type: ignore
    return OBBject(results=Empty())


@router.command
def eodchain() -> OBBject[Empty]:  # type: ignore
    """Gets option chain at a specific date."""
    return OBBject(results=Empty())


@router.command
def expirations() -> OBBject[Empty]:  # type: ignore
    """Return options expirations."""
    return OBBject(results=Empty())


@router.command
def grhist() -> OBBject[Empty]:  # type: ignore
    """Plot option greek history."""
    return OBBject(results=Empty())


@router.command
def hist() -> OBBject[Empty]:  # type: ignore
    """Plot option history."""
    return OBBject(results=Empty())


@router.command
def info() -> OBBject[Empty]:  # type: ignore
    """Display option information (volatility, IV rank, etc.)."""
    return OBBject(results=Empty())


@router.command
def last_price() -> OBBject[Empty]:  # type: ignore
    """Return last price of an option."""
    return OBBject(results=Empty())


@router.command
def oi() -> OBBject[Empty]:  # type: ignore
    """Plot option open interest."""
    return OBBject(results=Empty())


@router.command
def pcr() -> OBBject[Empty]:  # type: ignore
    """Display put/call ratio for ticker."""
    return OBBject(results=Empty())


@router.command
def price() -> OBBject[Empty]:  # type: ignore
    return OBBject(results=Empty())


@router.command
def unu() -> OBBject[Empty]:  # type: ignore
    """Show unusual options activity."""
    return OBBject(results=Empty())


@router.command
def voi() -> OBBject[Empty]:  # type: ignore
    """Plot volume and open interest."""
    return OBBject(results=Empty())


@router.command
def vol() -> OBBject[Empty]:  # type: ignore
    """Plot volume."""
    return OBBject(results=Empty())


@router.command
def vsurf() -> OBBject[Empty]:  # type: ignore
    """Show 3D volatility surface."""
    return OBBject(results=Empty())
