from openbb_terminal.config_terminal import (
    theme,
)  # noqa # pylint: disable=unused-import
from openbb_terminal.helper_classes import (
    TerminalStyle,
)  # noqa # pylint: disable=unused-import
from openbb_terminal import (
    helper_funcs as helper,
)  # noqa # pylint: disable=unused-import
from openbb_terminal.reports import (
    widget_helpers as widgets,
)  # noqa # pylint: disable=unused-import
from openbb_terminal.portfolio.portfolio_model import (
    PortfolioModel as Portfolio,
)  # noqa # pylint: disable=unused-import
from openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model import (
    Coin,
)  # noqa # pylint: disable=unused-import


from openbb_terminal.core.library.breadcrumb import Breadcrumb
from openbb_terminal.core.library.trail_map import TrailMap
from openbb_terminal.core.library.breadcrumb import MetadataBuilder

TerminalStyle().applyMPLstyle()
trail = ""
trail_map = TrailMap()
metadata = MetadataBuilder.build(trail=trail, trail_map=trail_map)

openbb = Breadcrumb(
    metadata=metadata,
    trail=trail,
    trail_map=trail_map,
)

__all__ = (
    theme,
    TerminalStyle,
    helper,
    widgets,
    Portfolio,
    Coin,
    openbb,
)