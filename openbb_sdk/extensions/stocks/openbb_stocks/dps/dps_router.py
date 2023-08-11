from openbb_core.app.model.obbject import Obbject
from openbb_core.app.model.results.empty import Empty
from openbb_core.app.router import Router

router = Router(prefix="/dps")


@router.command
def psi() -> Obbject[Empty]:  # type: ignore
    """Price vs short interest volume"""
    return Obbject(results=Empty())


@router.command
def ctb() -> Obbject[Empty]:  # type: ignore
    """Cost to borrow of stocks."""
    return Obbject(results=Empty())


@router.command
def dpotc() -> Obbject[Empty]:  # type: ignore
    """Dark pools (ATS) vs OTC data."""
    return Obbject(results=Empty())


@router.command
def ftd() -> Obbject[Empty]:  # type: ignore
    """Fails-to-deliver data."""
    return Obbject(results=Empty())


@router.command
def hsi() -> Obbject[Empty]:  # type: ignore
    """Show top high short interest stocks of over 20% ratio."""
    return Obbject(results=Empty())


@router.command
def pos() -> Obbject[Empty]:  # type: ignore
    """Dark pool short position."""
    return Obbject(results=Empty())


@router.command
def prom() -> Obbject[Empty]:  # type: ignore
    """Promising tickers based on dark pool shares regression."""
    return Obbject(results=Empty())


@router.command
def psi_q() -> Obbject[Empty]:  # type: ignore
    return Obbject(results=Empty())


@router.command
def psi_sg() -> Obbject[Empty]:  # type: ignore
    return Obbject(results=Empty())


@router.command
def shorted() -> Obbject[Empty]:  # type: ignore
    """Most shorted stocks."""
    return Obbject(results=Empty())


@router.command
def sidtc() -> Obbject[Empty]:  # type: ignore
    """Short interest and days to cover."""
    return Obbject(results=Empty())


@router.command
def spos() -> Obbject[Empty]:  # type: ignore
    """Net short vs position."""
    return Obbject(results=Empty())
