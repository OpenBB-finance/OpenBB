"""Due Diligence Router."""


from openbb_core.app.model.obbject import OBBject
from openbb_core.app.model.results.empty import Empty
from openbb_core.app.router import Router

router = Router(prefix="/ins")


@router.command
def act() -> OBBject[Empty]:  # type: ignore
    """Insider activity over time."""
    return OBBject(results=Empty())


@router.command
def blcp() -> OBBject[Empty]:  # type: ignore
    """Big latest CEO/CFO purchaces ($25k+)."""
    return OBBject(results=Empty())


@router.command
def blcs() -> OBBject[Empty]:  # type: ignore
    """Big latest CEO/CFO sales ($100k+)."""
    return OBBject(results=Empty())


@router.command
def blip() -> OBBject[Empty]:  # type: ignore
    """Big latest insider purchaces ($25+)."""
    return OBBject(results=Empty())


@router.command
def blis() -> OBBject[Empty]:  # type: ignore
    """Big latest insider sales ($100k+)."""
    return OBBject(results=Empty())


@router.command
def blop() -> OBBject[Empty]:  # type: ignore
    """Big latest officer purchaces ($25k+)."""
    return OBBject(results=Empty())


@router.command
def blos() -> OBBject[Empty]:  # type: ignore
    """Big latest officer sales ($100k+)."""
    return OBBject(results=Empty())


@router.command  # Can't use filter because it's a python keyword
def filt() -> OBBject[Empty]:  # type: ignore
    """Filter insiders based on preset."""
    return OBBject(results=Empty())


@router.command
def lcb() -> OBBject[Empty]:  # type: ignore
    """Latest cluster buys."""
    return OBBject(results=Empty())


@router.command
def lins() -> OBBject[Empty]:  # type: ignore
    """Last insider trading of the company."""
    return OBBject(results=Empty())


@router.command
def lip() -> OBBject[Empty]:  # type: ignore
    """Latest insider purchaces."""
    return OBBject(results=Empty())


@router.command
def lis() -> OBBject[Empty]:  # type: ignore
    """Latest insider sales."""
    return OBBject(results=Empty())


@router.command
def lit() -> OBBject[Empty]:  # type: ignore
    """Latest insider trading (all filings)."""
    return OBBject(results=Empty())


@router.command
def lpsb() -> OBBject[Empty]:  # type: ignore
    """Latest penny stock buys."""
    return OBBject(results=Empty())


@router.command
def print_insider_data() -> OBBject[Empty]:  # type: ignore
    """Print insider data."""
    return OBBject(results=Empty())


@router.command
def stats() -> OBBject[Empty]:  # type: ignore
    """Insider stats of the company."""
    return OBBject(results=Empty())
