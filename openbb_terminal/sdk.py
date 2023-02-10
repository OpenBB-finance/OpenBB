# pylint: disable=unused-import
from openbb_terminal import helper_funcs as helper  # noqa: F401
from openbb_terminal.config_terminal import theme
from openbb_terminal.core.config.paths import load_dotenv_and_reload  # noqa: F401
from openbb_terminal.core.library.breadcrumb import Breadcrumb, MetadataBuilder
from openbb_terminal.core.library.trail_map import TrailMap
from openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model import (  # noqa: F401
    Coin,
)
from openbb_terminal.helper_classes import TerminalStyle
from openbb_terminal.reports import widget_helpers as widgets  # noqa: F401
from openbb_terminal.session.user import User

if User.is_guest():
    load_dotenv_and_reload()

TerminalStyle().applyMPLstyle()
trail = ""
trail_map = TrailMap()
metadata = MetadataBuilder.build(trail=trail, trail_map=trail_map)

openbb = Breadcrumb(
    metadata=metadata,
    trail=trail,
    trail_map=trail_map,
)
