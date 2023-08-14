from openbb_core.app.model.obbject import OBBject
from openbb_core.app.model.results.empty import Empty
from openbb_core.app.router import Router

router = Router(prefix="/disc")


@router.command
def active() -> OBBject[Empty]:  # type: ignore
    """Most active stocks by intraday trade volumes."""
    return OBBject(results=Empty())


@router.command
def arkord() -> OBBject[Empty]:  # type: ignore
    """Order by ARK INvestment Management LLC."""
    return OBBject(results=Empty())


@router.command
def asc() -> OBBject[Empty]:  # type: ignore
    """Small cap stocks with revenue and earnings growth more than 25%."""
    return OBBject(results=Empty())


@router.command
def dividends() -> OBBject[Empty]:  # type: ignore
    return OBBject(results=Empty())


@router.command
def filings() -> OBBject[Empty]:  # type: ignore
    """The most-recent form submissions to the SEC."""
    return OBBject(results=Empty())


@router.command
def fipo() -> OBBject[Empty]:  # type: ignore
    """Future IPOs dates."""
    return OBBject(results=Empty())


@router.command
def gainers() -> OBBject[Empty]:  # type: ignore
    """Show latest top gainers."""
    return OBBject(results=Empty())


@router.command
def gtech() -> OBBject[Empty]:  # type: ignore
    """Tech stocks with revenue and earnings growth more than 25%."""
    return OBBject(results=Empty())


@router.command
def hotpenny() -> OBBject[Empty]:  # type: ignore
    """Today's hot penny stocks."""
    return OBBject(results=Empty())


@router.command
def ipo() -> OBBject[Empty]:  # type: ignore
    return OBBject(results=Empty())


@router.command
def losers() -> OBBject[Empty]:  # type: ignore
    """Show latest top losers."""
    return OBBject(results=Empty())


@router.command
def lowfloat() -> OBBject[Empty]:  # type: ignore
    """Low float stocks under 10M shares float."""
    return OBBject(results=Empty())


@router.command
def pipo() -> OBBject[Empty]:  # type: ignore
    """Past IPOs dates."""
    return OBBject(results=Empty())


@router.command
def rtat() -> OBBject[Empty]:  # type: ignore
    """Top 10 retail traded stocks per day."""
    return OBBject(results=Empty())


@router.command
def trending() -> OBBject[Empty]:  # type: ignore
    """Trending news."""
    return OBBject(results=Empty())


@router.command
def ugs() -> OBBject[Empty]:  # type: ignore
    """Undervalued stocks with revenue and earnings growth above 25%."""
    return OBBject(results=Empty())


@router.command
def ulc() -> OBBject[Empty]:  # type: ignore
    """Potentially undervalued large cap stocks."""
    return OBBject(results=Empty())


@router.command
def upcoming() -> OBBject[Empty]:  # type: ignore
    """Upcoming earnings release dates."""
    return OBBject(results=Empty())
