"""Oanda context API."""
import os
from gamestonk_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Context menus

from gamestonk_terminal.forex.oanda.oanda_view import get_fx_price as price
from gamestonk_terminal.forex.oanda.oanda_view import get_account_summary as summary
from gamestonk_terminal.forex.oanda.oanda_view import get_order_book as orderbook
from gamestonk_terminal.forex.oanda.oanda_view import get_position_book as positionbook

# Renamed due to python reserved word
from gamestonk_terminal.forex.oanda.oanda_view import list_orders as listorder
from gamestonk_terminal.forex.oanda.oanda_view import create_order as order
from gamestonk_terminal.forex.oanda.oanda_view import cancel_pending_order as cancel
from gamestonk_terminal.forex.oanda.oanda_view import get_open_positions as positions
from gamestonk_terminal.forex.oanda.oanda_view import get_pending_orders as pending
from gamestonk_terminal.forex.oanda.oanda_view import get_open_trades as trades
from gamestonk_terminal.forex.oanda.oanda_view import close_trade as closetrade
from gamestonk_terminal.forex.oanda.oanda_view import show_candles as candles
from gamestonk_terminal.forex.oanda.oanda_view import calendar

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
