"""Due Diligence API."""
import os

from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

from .binance_view import display_balance as balance, display_order_book as book
from .coinbase_view import (
    display_order_book as cbbook,
    display_stats as stats,
    display_trades as trades,
)
from .coinglass_view import display_open_interest as oi
from .coinpaprika_view import (
    display_basic as basic,
    display_events as events,
    display_exchanges as ex,
    display_markets as mkt,
    display_price_supply as ps,
    display_twitter as twitter,
)
from .cryptopanic_view import display_news as news

# Menu commands
from .glassnode_view import (
    display_active_addresses as active,
    display_exchange_balances as eb,
    display_exchange_net_position_change as change,
    display_hashrate as hr,
    display_non_zero_addresses as nonzero,
)
from .messari_view import (
    display_fundraising as fr,
    display_governance as gov,
    display_investors as inv,
    display_links as links,
    display_marketcap_dominance as mcapdom,
    display_messari_timeseries as mt,
    display_messari_timeseries_list as get_mt,
    display_project_info as pi,
    display_roadmap as rm,
    display_team as team,
    display_tokenomics as tk,
)
from .pycoingecko_view import (
    display_ath as ath,
    display_atl as atl,
    display_bc as bc,
    display_dev as dev,
    display_info as info,
    display_market as market,
    display_score as score,
    display_social as social,
    display_web as web,
)
from .santiment_view import display_github_activity as gh
from .tokenterminal_view import (
    display_description as desc,
    display_fundamental_metric_from_project_over_time as funot,
)

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
