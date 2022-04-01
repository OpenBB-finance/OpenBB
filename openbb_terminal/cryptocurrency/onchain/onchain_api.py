"""Onchain context API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from .ethgasstation_view import display_gwei_fees as gwei
from .whale_alert_view import display_whales_transactions as whales
from .ethplorer_view import display_address_info as balance
from .ethplorer_view import display_address_history as hist
from .ethplorer_view import display_top_token_holders as holders
from .ethplorer_view import display_top_tokens as top
from .ethplorer_view import display_token_info as info
from .ethplorer_view import display_token_history as th
from .ethplorer_view import display_tx_info as tx
from .ethplorer_view import display_token_historical_prices as prices
from .bitquery_view import display_dex_trades as lt
from .bitquery_view import display_daily_volume_for_given_pair as dvcp
from .bitquery_view import display_dex_volume_for_token as tv
from .bitquery_view import display_ethereum_unique_senders as ueat
from .bitquery_view import display_most_traded_pairs as ttcp
from .bitquery_view import display_spread_for_crypto_pair as baas


# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
