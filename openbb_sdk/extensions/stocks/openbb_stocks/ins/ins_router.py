"""Due Diligence Router."""


from openbb_core.app.model.obbject import Obbject
from openbb_core.app.model.results.empty import Empty
from openbb_core.app.router import Router

router = Router(prefix="/ins")


@router.command
def act() -> Obbject[Empty]:  # type: ignore
    """Insider activity over time."""
    return Obbject(results=Empty())


@router.command
def blcp() -> Obbject[Empty]:  # type: ignore
    """Big latest CEO/CFO purchaces ($25k+)."""
    return Obbject(results=Empty())


@router.command
def blcs() -> Obbject[Empty]:  # type: ignore
    """Big latest CEO/CFO sales ($100k+)."""
    return Obbject(results=Empty())


@router.command
def blip() -> Obbject[Empty]:  # type: ignore
    """Big latest insider purchaces ($25+)."""
    return Obbject(results=Empty())


@router.command
def blis() -> Obbject[Empty]:  # type: ignore
    """Big latest insider sales ($100k+)."""
    return Obbject(results=Empty())


@router.command
def blop() -> Obbject[Empty]:  # type: ignore
    """Big latest officer purchaces ($25k+)."""
    return Obbject(results=Empty())


@router.command
def blos() -> Obbject[Empty]:  # type: ignore
    """Big latest officer sales ($100k+)."""
    return Obbject(results=Empty())


@router.command  # Can't use filter because it's a python keyword
def filt() -> Obbject[Empty]:  # type: ignore
    """Filter insiders based on preset."""
    return Obbject(results=Empty())


@router.command
def lcb() -> Obbject[Empty]:  # type: ignore
    """Latest cluster buys."""
    return Obbject(results=Empty())


@router.command
def lins() -> Obbject[Empty]:  # type: ignore
    """Last insider trading of the company."""
    return Obbject(results=Empty())


@router.command
def lip() -> Obbject[Empty]:  # type: ignore
    """Latest insider purchaces."""
    return Obbject(results=Empty())


@router.command
def lis() -> Obbject[Empty]:  # type: ignore
    """Latest insider sales."""
    return Obbject(results=Empty())


@router.command
def lit() -> Obbject[Empty]:  # type: ignore
    """Latest insider trading (all filings)."""
    return Obbject(results=Empty())


@router.command
def lpsb() -> Obbject[Empty]:  # type: ignore
    """Latest penny stock buys."""
    return Obbject(results=Empty())


@router.command
def print_insider_data() -> Obbject[Empty]:  # type: ignore
    """Print insider data."""
    return Obbject(results=Empty())


@router.command
def stats() -> Obbject[Empty]:  # type: ignore
    """Insider stats of the company."""
    return Obbject(results=Empty())
