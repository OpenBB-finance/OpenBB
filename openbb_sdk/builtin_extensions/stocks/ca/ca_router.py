from openbb_sdk_core.app.model.command_output import CommandOutput
from openbb_sdk_core.app.model.item.empty import Empty
from openbb_sdk_core.app.router import Router

router = Router(prefix="/ca")


@router.command
def get() -> CommandOutput[Empty]:  # type: ignore
    """Company peers."""
    return CommandOutput(item=Empty())


@router.command
def balance() -> CommandOutput[Empty]:  # type: ignore
    """Company balance sheet."""
    return CommandOutput(item=Empty())


@router.command
def cashflow() -> CommandOutput[Empty]:  # type: ignore
    """Company cashflow."""
    return CommandOutput(item=Empty())


@router.command
def hcorr() -> CommandOutput[Empty]:  # type: ignore
    """Company historical correlation."""
    return CommandOutput(item=Empty())


@router.command
def hist() -> CommandOutput[Empty]:  # type: ignore
    """Company historical prices."""
    return CommandOutput(item=Empty())


@router.command
def income() -> CommandOutput[Empty]:  # type: ignore
    """Company income statement."""
    return CommandOutput(item=Empty())


@router.command
def scorr() -> CommandOutput[Empty]:  # type: ignore
    """Company sector correlation."""
    return CommandOutput(item=Empty())


@router.command
def screener() -> CommandOutput[Empty]:  # type: ignore
    """Company screener."""
    return CommandOutput(item=Empty())


@router.command
def sentiment() -> CommandOutput[Empty]:  # type: ignore
    """Company sentiment."""
    return CommandOutput(item=Empty())


@router.command
def similar() -> CommandOutput[Empty]:  # type: ignore
    """Company similar."""
    return CommandOutput(item=Empty())


@router.command
def volume() -> CommandOutput[Empty]:  # type: ignore
    """Company volume."""
    return CommandOutput(item=Empty())
