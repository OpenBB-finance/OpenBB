from openbb_core.app.model.obbject import Obbject
from openbb_core.app.model.results.empty import Empty
from openbb_core.app.router import Router

router = Router(prefix="/disc")


@router.command
def active() -> Obbject[Empty]:  # type: ignore
    """Most active stocks by intraday trade volumes."""
    return Obbject(results=Empty())


@router.command
def arkord() -> Obbject[Empty]:  # type: ignore
    """Order by ARK INvestment Management LLC."""
    return Obbject(results=Empty())


@router.command
def asc() -> Obbject[Empty]:  # type: ignore
    """Small cap stocks with revenue and earnings growth more than 25%."""
    return Obbject(results=Empty())


@router.command
def dividends() -> Obbject[Empty]:  # type: ignore
    return Obbject(results=Empty())


@router.command
def filings() -> Obbject[Empty]:  # type: ignore
    """The most-recent form submissions to the SEC."""
    return Obbject(results=Empty())


@router.command
def fipo() -> Obbject[Empty]:  # type: ignore
    """Future IPOs dates."""
    return Obbject(results=Empty())


@router.command
def gainers() -> Obbject[Empty]:  # type: ignore
    """Show latest top gainers."""
    return Obbject(results=Empty())


@router.command
def gtech() -> Obbject[Empty]:  # type: ignore
    """Tech stocks with revenue and earnings growth more than 25%."""
    return Obbject(results=Empty())


@router.command
def hotpenny() -> Obbject[Empty]:  # type: ignore
    """Today's hot penny stocks."""
    return Obbject(results=Empty())


@router.command
def ipo() -> Obbject[Empty]:  # type: ignore
    return Obbject(results=Empty())


@router.command
def losers() -> Obbject[Empty]:  # type: ignore
    """Show latest top losers."""
    return Obbject(results=Empty())


@router.command
def lowfloat() -> Obbject[Empty]:  # type: ignore
    """Low float stocks under 10M shares float."""
    return Obbject(results=Empty())


@router.command
def pipo() -> Obbject[Empty]:  # type: ignore
    """Past IPOs dates."""
    return Obbject(results=Empty())


@router.command
def rtat() -> Obbject[Empty]:  # type: ignore
    """Top 10 retail traded stocks per day."""
    return Obbject(results=Empty())


@router.command
def trending() -> Obbject[Empty]:  # type: ignore
    """Trending news."""
    return Obbject(results=Empty())


@router.command
def ugs() -> Obbject[Empty]:  # type: ignore
    """Undervalued stocks with revenue and earnings growth above 25%."""
    return Obbject(results=Empty())


@router.command
def ulc() -> Obbject[Empty]:  # type: ignore
    """Potentially undervalued large cap stocks."""
    return Obbject(results=Empty())


@router.command
def upcoming() -> Obbject[Empty]:  # type: ignore
    """Upcoming earnings release dates."""
    return Obbject(results=Empty())
