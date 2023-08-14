from openbb_core.app.model.obbject import Obbject
from openbb_core.app.model.results.empty import Empty
from openbb_core.app.router import Router

router = Router(prefix="/options")


@router.command
def chains() -> Obbject[Empty]:  # type: ignore
    """Return options chains with greeks."""
    return Obbject(results=Empty())


@router.command
def dte() -> Obbject[Empty]:  # type: ignore
    return Obbject(results=Empty())


@router.command
def eodchain() -> Obbject[Empty]:  # type: ignore
    """Gets option chain at a specific date."""
    return Obbject(results=Empty())


@router.command
def expirations() -> Obbject[Empty]:  # type: ignore
    """Return options expirations."""
    return Obbject(results=Empty())


@router.command
def grhist() -> Obbject[Empty]:  # type: ignore
    """Plot option greek history."""
    return Obbject(results=Empty())


@router.command
def hist() -> Obbject[Empty]:  # type: ignore
    """Plot option history."""
    return Obbject(results=Empty())


@router.command
def info() -> Obbject[Empty]:  # type: ignore
    """Display option information (volatility, IV rank, etc.)."""
    return Obbject(results=Empty())


@router.command
def last_price() -> Obbject[Empty]:  # type: ignore
    """Return last price of an option."""
    return Obbject(results=Empty())


@router.command
def oi() -> Obbject[Empty]:  # type: ignore
    """Plot option open interest."""
    return Obbject(results=Empty())


@router.command
def pcr() -> Obbject[Empty]:  # type: ignore
    """Display put/call ratio for ticker."""
    return Obbject(results=Empty())


@router.command
def price() -> Obbject[Empty]:  # type: ignore
    return Obbject(results=Empty())


@router.command
def unu() -> Obbject[Empty]:  # type: ignore
    """Show unusual options activity."""
    return Obbject(results=Empty())


@router.command
def voi() -> Obbject[Empty]:  # type: ignore
    """Plot volume and open interest."""
    return Obbject(results=Empty())


@router.command
def vol() -> Obbject[Empty]:  # type: ignore
    """Plot volume."""
    return Obbject(results=Empty())


@router.command
def vsurf() -> Obbject[Empty]:  # type: ignore
    """Show 3D volatility surface."""
    return Obbject(results=Empty())
