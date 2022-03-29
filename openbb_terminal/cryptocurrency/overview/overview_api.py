"""Overview context API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from .blockchaincenter_view import display_altcoin_index as altindex
from .withdrawalfees_view import display_overall_withdrawal_fees as wf
from .withdrawalfees_view import display_overall_exchange_withdrawal_fees as ewf
from .withdrawalfees_view import display_crypto_withdrawal_fees as wfpe
from .pycoingecko_view import display_holdings_overview as cghold
from .pycoingecko_view import display_categories as cgcategories
from .pycoingecko_view import display_stablecoins as cgstables
from .pycoingecko_view import display_products as cgproducts
from .pycoingecko_view import display_platforms as cgplatforms
from .pycoingecko_view import display_exchanges as cgexchanges
from .pycoingecko_view import display_exchange_rates as cgexrates
from .pycoingecko_view import display_indexes as cgindexes
from .pycoingecko_view import display_derivatives as cgderivatives
from .pycoingecko_view import display_global_market_info as cgglobal
from .pycoingecko_view import display_global_defi_info as cgdefi
from .coinpaprika_view import display_global_market as cpglobal
from .coinpaprika_view import display_all_coins_market_info as cpmarkets
from .coinpaprika_view import display_exchange_markets as cpexmarkets
from .coinpaprika_view import display_all_coins_info as cpinfo
from .coinpaprika_view import display_all_exchanges as cpexchanges
from .coinpaprika_view import display_all_platforms as cpplatforms
from .coinpaprika_view import display_contracts as cpcontracts
from .coinbase_view import display_trading_pairs as cbpairs
from .cryptopanic_view import display_news as news


# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
