from openbb_core.app.model.obbject import OBBject
from openbb_core.app.model.results.empty import Empty
from openbb_core.app.router import Router

router = Router(prefix="/dps")


@router.command
def psi() -> OBBject[Empty]:  # type: ignore
    """Price vs short interest volume"""
    return OBBject(results=Empty())


@router.command
def ctb() -> OBBject[Empty]:  # type: ignore
    """Cost to borrow of stocks."""
    return OBBject(results=Empty())


@router.command
def dpotc() -> OBBject[Empty]:  # type: ignore
    """Dark pools (ATS) vs OTC data."""
    return OBBject(results=Empty())


@router.command
def ftd() -> OBBject[Empty]:  # type: ignore
    """Fails-to-deliver data."""
    return OBBject(results=Empty())


@router.command
def hsi() -> OBBject[Empty]:  # type: ignore
    """Show top high short interest stocks of over 20% ratio."""
    return OBBject(results=Empty())


@router.command
def pos() -> OBBject[Empty]:  # type: ignore
    """Dark pool short position."""
    return OBBject(results=Empty())


@router.command
def prom() -> OBBject[Empty]:  # type: ignore
    """Promising tickers based on dark pool shares regression."""
    return OBBject(results=Empty())


@router.command
def psi_q() -> OBBject[Empty]:  # type: ignore
    return OBBject(results=Empty())


@router.command
def psi_sg() -> OBBject[Empty]:  # type: ignore
    return OBBject(results=Empty())


@router.command
def shorted() -> OBBject[Empty]:  # type: ignore
    """Most shorted stocks."""
    return OBBject(results=Empty())


@router.command
def sidtc() -> OBBject[Empty]:  # type: ignore
    """Short interest and days to cover."""
    return OBBject(results=Empty())


@router.command
def spos() -> OBBject[Empty]:  # type: ignore
    """Net short vs position."""
    return OBBject(results=Empty())
