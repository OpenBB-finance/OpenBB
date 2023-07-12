"""Due Diligence Router."""


from openbb_core.app.model.command_output import CommandOutput
from openbb_core.app.model.results.empty import Empty
from openbb_core.app.router import Router

router = Router(prefix="/ins")


@router.command
def act() -> CommandOutput[Empty]:  # type: ignore
    """Insider activity over time."""
    return CommandOutput(results=Empty())


@router.command
def blcp() -> CommandOutput[Empty]:  # type: ignore
    """Big latest CEO/CFO purchaces ($25k+)."""
    return CommandOutput(results=Empty())


@router.command
def blcs() -> CommandOutput[Empty]:  # type: ignore
    """Big latest CEO/CFO sales ($100k+)."""
    return CommandOutput(results=Empty())


@router.command
def blip() -> CommandOutput[Empty]:  # type: ignore
    """Big latest insider purchaces ($25+)."""
    return CommandOutput(results=Empty())


@router.command
def blis() -> CommandOutput[Empty]:  # type: ignore
    """Big latest insider sales ($100k+)."""
    return CommandOutput(results=Empty())


@router.command
def blop() -> CommandOutput[Empty]:  # type: ignore
    """Big latest officer purchaces ($25k+)."""
    return CommandOutput(results=Empty())


@router.command
def blos() -> CommandOutput[Empty]:  # type: ignore
    """Big latest officer sales ($100k+)."""
    return CommandOutput(results=Empty())


@router.command  # Can't use filter because it's a python keyword
def filt() -> CommandOutput[Empty]:  # type: ignore
    """Filter insiders based on preset."""
    return CommandOutput(results=Empty())


@router.command
def lcb() -> CommandOutput[Empty]:  # type: ignore
    """Latest cluster buys."""
    return CommandOutput(results=Empty())


@router.command
def lins() -> CommandOutput[Empty]:  # type: ignore
    """Last insider trading of the company."""
    return CommandOutput(results=Empty())


@router.command
def lip() -> CommandOutput[Empty]:  # type: ignore
    """Latest insider purchaces."""
    return CommandOutput(results=Empty())


@router.command
def lis() -> CommandOutput[Empty]:  # type: ignore
    """Latest insider sales."""
    return CommandOutput(results=Empty())


@router.command
def lit() -> CommandOutput[Empty]:  # type: ignore
    """Latest insider trading (all filings)."""
    return CommandOutput(results=Empty())


@router.command
def lpsb() -> CommandOutput[Empty]:  # type: ignore
    """Latest penny stock buys."""
    return CommandOutput(results=Empty())


@router.command
def print_insider_data() -> CommandOutput[Empty]:  # type: ignore
    """Print insider data."""
    return CommandOutput(results=Empty())


@router.command
def stats() -> CommandOutput[Empty]:  # type: ignore
    """Insider stats of the company."""
    return CommandOutput(results=Empty())
