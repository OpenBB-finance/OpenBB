from openbb_sdk_core.app.model.command_output import CommandOutput
from openbb_sdk_core.app.model.item.empty import Empty
from openbb_sdk_core.app.router import Router

router = Router(prefix="/disc")


@router.command
def active() -> CommandOutput[Empty]:  # type: ignore
    """Most active stocks by intraday trade volumes."""
    return CommandOutput(item=Empty())


@router.command
def arkord() -> CommandOutput[Empty]:  # type: ignore
    """Order by ARK INvestment Management LLC."""
    return CommandOutput(item=Empty())


@router.command
def asc() -> CommandOutput[Empty]:  # type: ignore
    """Small cap stocks with revenue and earnings growth more than 25%."""
    return CommandOutput(item=Empty())


@router.command
def dividends() -> CommandOutput[Empty]:  # type: ignore
    return CommandOutput(item=Empty())


@router.command
def filings() -> CommandOutput[Empty]:  # type: ignore
    """The most-recent form submissions to the SEC."""
    return CommandOutput(item=Empty())


@router.command
def fipo() -> CommandOutput[Empty]:  # type: ignore
    """Future IPOs dates."""
    return CommandOutput(item=Empty())


@router.command
def gainers() -> CommandOutput[Empty]:  # type: ignore
    """Show latest top gainers."""
    return CommandOutput(item=Empty())


@router.command
def gtech() -> CommandOutput[Empty]:  # type: ignore
    """Tech stocks with revenue and earnings growth more than 25%."""
    return CommandOutput(item=Empty())


@router.command
def hotpenny() -> CommandOutput[Empty]:  # type: ignore
    """Today's hot penny stocks."""
    return CommandOutput(item=Empty())


@router.command
def ipo() -> CommandOutput[Empty]:  # type: ignore
    return CommandOutput(item=Empty())


@router.command
def losers() -> CommandOutput[Empty]:  # type: ignore
    """Show latest top losers."""
    return CommandOutput(item=Empty())


@router.command
def lowfloat() -> CommandOutput[Empty]:  # type: ignore
    """Low float stocks under 10M shares float."""
    return CommandOutput(item=Empty())


@router.command
def pipo() -> CommandOutput[Empty]:  # type: ignore
    """Past IPOs dates."""
    return CommandOutput(item=Empty())


@router.command
def rtat() -> CommandOutput[Empty]:  # type: ignore
    """Top 10 retail traded stocks per day."""
    return CommandOutput(item=Empty())


@router.command
def trending() -> CommandOutput[Empty]:  # type: ignore
    """Trending news."""
    return CommandOutput(item=Empty())


@router.command
def ugs() -> CommandOutput[Empty]:  # type: ignore
    """Undervalued stocks with revenue and earnings growth above 25%."""
    return CommandOutput(item=Empty())


@router.command
def ulc() -> CommandOutput[Empty]:  # type: ignore
    """Potentially undervalued large cap stocks."""
    return CommandOutput(item=Empty())


@router.command
def upcoming() -> CommandOutput[Empty]:  # type: ignore
    """Upcoming earnings release dates."""
    return CommandOutput(item=Empty())
