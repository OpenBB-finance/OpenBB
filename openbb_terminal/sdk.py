"""OpenBB Terminal SDK."""
# flake8: noqa
# pylint: disable=unused-import,wrong-import-order
# pylint: disable=C0302,W0611,R0902,R0903,C0412,C0301,not-callable
from datetime import datetime, timedelta
import types
import functools
from typing import (
    Any,
    Callable,
)
import logging
from traceback import format_stack
import pandas as pd

import openbb_terminal.config_terminal as cfg
from openbb_terminal.reports.reports_controller import ReportController
from openbb_terminal.dashboards.dashboards_controller import DashboardsController


from openbb_terminal.config_terminal import theme

from openbb_terminal.helper_classes import TerminalStyle  # noqa: F401
from openbb_terminal import helper_funcs as helper  # noqa: F401
from openbb_terminal.loggers import setup_logging
from openbb_terminal.decorators import log_start_end, sdk_arg_logger
from openbb_terminal.core.log.generation.settings_logger import log_all_settings
from openbb_terminal.reports import widget_helpers as widgets  # noqa: F401

from openbb_terminal.portfolio.portfolio_model import PortfolioModel as Portfolio
from openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model import Coin
import openbb_terminal.sdk_init as lib

logger = logging.getLogger(__name__)


SUPPRESS_LOGGING_CLASSES = {
    ReportController: "ReportController",
    DashboardsController: "DashboardsController",
}


def check_suppress_logging(suppress_dict: dict) -> bool:
    """
    Check if logging should be suppressed.
    If the dict contains a value that is found in the stack trace,
    the logging should be suppressed.

    Parameters
    ----------
    supress_dict: dict
        Dictionary with values that trigger log suppression

    Returns
    -------
    bool
        True if logging shall be suppressed, False otherwise
    """
    for _, value in suppress_dict.items():
        for ele in format_stack():
            if value in ele:
                return True
    return False


def copy_func(
    f: Callable,
    logging_decorator: bool = False,
    chart: bool = False,
) -> Callable:
    """Copy the contents and attributes of the entered function.

    Based on https://stackoverflow.com/a/13503277

    Parameters
    ----------
    f: Callable
        Function to be copied
    logging_decorator: bool
        If True, the copied function will be decorated with the logging decorator
    chart: bool
        If True, the copied function will log info on whether it is a view (chart)

    Returns
    -------
    g: Callable
        New function
    """
    # Removing the logging decorator
    if hasattr(f, "__wrapped__"):
        f = f.__wrapped__  # type: ignore

    g = types.FunctionType(
        f.__code__,
        f.__globals__,  # type: ignore
        name=f.__name__,
        argdefs=f.__defaults__,  # type: ignore
        closure=f.__closure__,  # type: ignore
    )
    g = functools.update_wrapper(g, f)
    g.__kwdefaults__ = f.__kwdefaults__  # type: ignore

    if logging_decorator:
        log_name = logging.getLogger(g.__module__)
        g = sdk_arg_logger(func=g, log=log_name, chart=chart)
        g = log_start_end(func=g, log=log_name)

    return g


def clean_attr_desc(attr):
    return (
        attr.__doc__.splitlines()[1].lstrip()
        if not attr.__doc__.splitlines()[0]
        else attr.__doc__.splitlines()[0].lstrip()
        if attr.__doc__
        else ""
    )


class Category:
    """The base class that all categories must inherit from."""

    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)

    def __setattr__(self, attr: str, value: Any) -> None:
        """We override setattr to apply logging decorator to Catergory attributes."""
        chart = False
        if "view" in attr:
            chart = True
        if callable(value) and not attr.startswith("_"):
            value = copy_func(value, logging_decorator=True, chart=chart)
        super().__setattr__(attr, value)

    def __repr__(self):
        """Return the representation of the class."""
        repr_docs = [
            f"    {k}: {clean_attr_desc(v)}\n"
            for k, v in self.__dict__.items()
            if v.__doc__
        ]
        return f"{self.__class__.__name__}(\n{''.join(repr_docs)}\n)"


##################################################################
#                           Crypto                               #
##################################################################


class CryptoDueDiligence(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.trading_pairs = lib.crypto_dd_binance_model._get_trading_pairs
        self.check_valid_binance_string = (
            lib.crypto_dd_binance_model.check_valid_binance_str
        )
        self.get_binance_trading_pairs = (
            lib.crypto_dd_binance_model.get_all_binance_trading_pairs
        )
        self.binance_available_quotes_for_each_coin = (
            lib.crypto_dd_binance_model.get_binance_available_quotes_for_each_coin
        )
        self.balance = lib.crypto_dd_binance_model.get_balance
        self.balance_view = lib.crypto_dd_binance_view.display_balance
        self.book = lib.crypto_dd_binance_model.get_order_book
        self.book_view = lib.crypto_dd_binance_view.display_order_book
        self.show_available_pairs_for_given_symbol = (
            lib.crypto_dd_binance_model.show_available_pairs_for_given_symbol
        )
        self.exchanges = lib.crypto_dd_ccxt_model.get_exchanges
        self.candles = lib.crypto_dd_coinbase_model.get_candles
        self.candles_view = lib.crypto_dd_coinbase_view.display_candles
        self.cbbook = lib.crypto_dd_coinbase_model.get_order_book
        self.cbbook_view = lib.crypto_dd_coinbase_view.display_order_book
        self.stats = lib.crypto_dd_coinbase_model.get_product_stats
        self.stats_view = lib.crypto_dd_coinbase_view.display_stats
        self.trades = lib.crypto_dd_coinbase_model.get_trades
        self.trades_view = lib.crypto_dd_coinbase_view.display_trades
        self.trading_pair_info = lib.crypto_dd_coinbase_model.get_trading_pair_info
        self.oi = lib.crypto_dd_coinglass_model.get_open_interest_per_exchange
        self.oi_view = lib.crypto_dd_coinglass_view.display_open_interest
        self.basic_info = lib.crypto_dd_coinpaprika_model.basic_coin_info
        self.coin = lib.crypto_dd_coinpaprika_model.get_coin
        self.events = lib.crypto_dd_coinpaprika_model.get_coin_events_by_id
        self.events_view = lib.crypto_dd_coinpaprika_view.display_events
        self.ex = lib.crypto_dd_coinpaprika_model.get_coin_exchanges_by_id
        self.ex_view = lib.crypto_dd_coinpaprika_view.display_exchanges
        self.mkt = lib.crypto_dd_coinpaprika_model.get_coin_markets_by_id
        self.mkt_view = lib.crypto_dd_coinpaprika_view.display_markets
        self.twitter = lib.crypto_dd_coinpaprika_model.get_coin_twitter_timeline
        self.twitter_view = lib.crypto_dd_coinpaprika_view.display_twitter
        self.ohlc_historical = lib.crypto_dd_coinpaprika_model.get_ohlc_historical
        self.ps = lib.crypto_dd_coinpaprika_model.get_tickers_info_for_coin
        self.ps_view = lib.crypto_dd_coinpaprika_view.display_price_supply
        self.news = lib.crypto_ov_cryptopanic_model.get_news
        self.news_view = lib.crypto_dd_cryptopanic_view.display_news
        self.headlines = lib.ba_finbrain_model.get_sentiment
        self.headlines_view = (
            lib.crypto_dd_crypto_finbrain_view.display_crypto_sentiment_analysis
        )
        self.active = lib.crypto_dd_glassnode_model.get_active_addresses
        self.active_view = lib.crypto_dd_glassnode_view.display_active_addresses
        self.close = lib.crypto_dd_glassnode_model.get_close_price
        self.btcrb = lib.crypto_dd_glassnode_model.get_btc_rainbow
        self.btcrb_view = lib.crypto_dd_glassnode_view.display_btc_rainbow
        self.eb = lib.crypto_dd_glassnode_model.get_exchange_balances
        self.eb_view = lib.crypto_dd_glassnode_view.display_exchange_balances
        self.change = lib.crypto_dd_glassnode_model.get_exchange_net_position_change
        self.change_view = (
            lib.crypto_dd_glassnode_view.display_exchange_net_position_change
        )
        self.nonzero = lib.crypto_dd_glassnode_model.get_non_zero_addresses
        self.nonzero_view = lib.crypto_dd_glassnode_view.display_non_zero_addresses
        self.get_mt = lib.crypto_dd_messari_model.get_available_timeseries
        self.get_mt_view = lib.crypto_dd_messari_view.display_messari_timeseries_list
        self.fr = lib.crypto_dd_messari_model.get_fundraising
        self.fr_view = lib.crypto_dd_messari_view.display_fundraising
        self.gov = lib.crypto_dd_messari_model.get_governance
        self.gov_view = lib.crypto_dd_messari_view.display_governance
        self.inv = lib.crypto_dd_messari_model.get_investors
        self.inv_view = lib.crypto_dd_messari_view.display_investors
        self.links = lib.crypto_dd_messari_model.get_links
        self.links_view = lib.crypto_dd_messari_view.display_links
        self.mcapdom = lib.crypto_dd_messari_model.get_marketcap_dominance
        self.mcapdom_view = lib.crypto_dd_messari_view.display_marketcap_dominance
        self.mt = lib.crypto_dd_messari_model.get_messari_timeseries
        self.mt_view = lib.crypto_dd_messari_view.display_messari_timeseries
        self.pi = lib.crypto_dd_messari_model.get_project_product_info
        self.pi_view = lib.crypto_dd_messari_view.display_project_info
        self.rm = lib.crypto_dd_messari_model.get_roadmap
        self.rm_view = lib.crypto_dd_messari_view.display_roadmap
        self.team = lib.crypto_dd_messari_model.get_team
        self.team_view = lib.crypto_dd_messari_view.display_team
        self.tk = lib.crypto_dd_messari_model.get_tokenomics
        self.tk_view = lib.crypto_dd_messari_view.display_tokenomics
        self.coin_market_chart = lib.crypto_dd_pycoingecko_model.get_coin_market_chart
        self.pr = lib.crypto_dd_pycoingecko_model.get_coin_potential_returns
        self.pr_view = lib.crypto_dd_pycoingecko_view.display_coin_potential_returns
        self.tokenomics = lib.crypto_dd_pycoingecko_model.get_coin_tokenomics
        self.gh = lib.crypto_dd_santiment_model.get_github_activity
        self.gh_view = lib.crypto_dd_santiment_view.display_github_activity


class CryptoDefi(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.swaps = lib.crypto_defi_graph_model.get_last_uni_swaps
        self.swaps_view = lib.crypto_defi_graph_view.display_last_uni_swaps
        self.pools = lib.crypto_defi_graph_model.get_uni_pools_by_volume
        self.pools_view = lib.crypto_defi_graph_view.display_uni_pools
        self.tokens = lib.crypto_defi_graph_model.get_uni_tokens
        self.tokens_view = lib.crypto_defi_graph_view.display_uni_tokens
        self.pairs = lib.crypto_defi_graph_model.get_uniswap_pool_recently_added
        self.pairs_view = lib.crypto_defi_graph_view.display_recently_added
        self.stats = lib.crypto_defi_graph_model.get_uniswap_stats
        self.stats_view = lib.crypto_defi_graph_view.display_uni_stats
        self.dtvl = lib.crypto_defi_llama_model.get_defi_protocol
        self.dtvl_view = lib.crypto_defi_llama_view.display_historical_tvl
        self.ldapps = lib.crypto_defi_llama_model.get_defi_protocols
        self.ldapps_view = lib.crypto_defi_llama_view.display_defi_protocols
        self.stvl = lib.crypto_defi_llama_model.get_defi_tvl
        self.stvl_view = lib.crypto_defi_llama_view.display_defi_tvl
        self.gdapps = lib.crypto_defi_llama_model.get_grouped_defi_protocols
        self.gdapps_view = lib.crypto_defi_llama_view.display_grouped_defi_protocols
        self.luna_supply = lib.crypto_defi_smartstake_model.get_luna_supply_stats
        self.luna_supply_view = (
            lib.crypto_defi_smartstake_view.display_luna_circ_supply_change
        )
        self.newsletters = lib.crypto_defi_substack_model.get_newsletters
        self.newsletters_view = lib.crypto_defi_substack_view.display_newsletters
        self.aterra = (
            lib.crypto_defi_terraengineer_model.get_history_asset_from_terra_address
        )
        self.aterra_view = (
            lib.crypto_defi_terraengineer_view.display_terra_asset_history
        )
        self.ayr = lib.crypto_defi_terraengineer_model.get_anchor_yield_reserve
        self.ayr_view = lib.crypto_defi_terraengineer_view.display_anchor_yield_reserve
        self.gacc = lib.crypto_defi_terramoney_fcd_model.get_account_growth
        self.gacc_view = lib.crypto_defi_terramoney_fcd_view.display_account_growth
        self.gov_proposals = lib.crypto_defi_terramoney_fcd_model.get_proposals
        self.gov_proposals_view = (
            lib.crypto_defi_terramoney_fcd_view.display_gov_proposals
        )
        self.sinfo = lib.crypto_defi_terramoney_fcd_model.get_staking_account_info
        self.sinfo_view = (
            lib.crypto_defi_terramoney_fcd_view.display_account_staking_info
        )
        self.sratio = lib.crypto_defi_terramoney_fcd_model.get_staking_ratio_history
        self.sratio_view = (
            lib.crypto_defi_terramoney_fcd_view.display_staking_ratio_history
        )
        self.sreturn = lib.crypto_defi_terramoney_fcd_model.get_staking_returns_history
        self.sreturn_view = (
            lib.crypto_defi_terramoney_fcd_view.display_staking_returns_history
        )
        self.validators = lib.crypto_defi_terramoney_fcd_model.get_validators
        self.validators_view = lib.crypto_defi_terramoney_fcd_view.display_validators


class CryptoDiscovery(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.cmctop = lib.crypto_disc_coinmarketcap_model.get_cmc_top_n
        self.cmctop_view = lib.crypto_disc_coinmarketcap_view.display_cmc_top_coins
        self.cpsearch = lib.crypto_disc_coinpaprika_model.get_search_results
        self.cpsearch_view = lib.crypto_disc_coinpaprika_view.display_search_results
        self.top_dapps = lib.crypto_disc_dappradar_model.get_top_dapps
        self.top_dapps_view = lib.crypto_disc_dappradar_view.display_top_dapps
        self.top_dexes = lib.crypto_disc_dappradar_model.get_top_dexes
        self.top_dexes_view = lib.crypto_disc_dappradar_view.display_top_dexes
        self.top_games = lib.crypto_disc_dappradar_model.get_top_games
        self.top_games_view = lib.crypto_disc_dappradar_view.display_top_games
        self.top_nfts = lib.crypto_disc_dappradar_model.get_top_nfts
        self.top_nfts_view = lib.crypto_disc_dappradar_view.display_top_nfts
        self.categories_keys = lib.crypto_disc_pycoingecko_model.get_categories_keys
        self.coin_list = lib.crypto_disc_pycoingecko_model.get_coin_list
        self.coins = lib.crypto_disc_pycoingecko_model.get_coins
        self.coins_view = lib.crypto_disc_pycoingecko_view.display_coins
        self.coins_for_given_exchange = (
            lib.crypto_disc_pycoingecko_model.get_coins_for_given_exchange
        )
        self.gainers_or_losers = lib.crypto_disc_pycoingecko_model.get_gainers_or_losers
        self.gainers = lib.crypto_disc_pycoingecko_model.get_gainers
        self.gainers_view = lib.crypto_disc_pycoingecko_view.display_gainers
        self.losers = lib.crypto_disc_pycoingecko_model.get_losers
        self.losers_view = lib.crypto_disc_pycoingecko_view.display_losers
        self.trending = lib.crypto_disc_pycoingecko_model.get_trending_coins
        self.trending_view = lib.crypto_disc_pycoingecko_view.display_trending


class CryptoOnChain(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.hr = lib.crypto_dd_glassnode_model.get_hashrate
        self.hr_view = lib.crypto_dd_glassnode_view.display_hashrate
        self.dvcp = (
            lib.crypto_onchain_bitquery_model.get_daily_dex_volume_for_given_pair
        )
        self.dvcp_view = (
            lib.crypto_onchain_bitquery_view.display_daily_volume_for_given_pair
        )
        self.lt = lib.crypto_onchain_bitquery_model.get_dex_trades_by_exchange
        self.lt_view = lib.crypto_onchain_bitquery_view.display_dex_trades
        self.dex_trades_monthly = (
            lib.crypto_onchain_bitquery_model.get_dex_trades_monthly
        )
        self.erc20_tokens = lib.crypto_onchain_bitquery_model.get_erc20_tokens
        self.ueat = lib.crypto_onchain_bitquery_model.get_ethereum_unique_senders
        self.ueat_view = (
            lib.crypto_onchain_bitquery_view.display_ethereum_unique_senders
        )
        self.ttcp = lib.crypto_onchain_bitquery_model.get_most_traded_pairs
        self.ttcp_view = lib.crypto_onchain_bitquery_view.display_most_traded_pairs
        self.baas = lib.crypto_onchain_bitquery_model.get_spread_for_crypto_pair
        self.baas_view = lib.crypto_onchain_bitquery_view.display_spread_for_crypto_pair
        self.tv = lib.crypto_onchain_bitquery_model.get_token_volume_on_dexes
        self.tv_view = lib.crypto_onchain_bitquery_view.display_dex_volume_for_token
        self.query_graph = lib.crypto_onchain_bitquery_model.query_graph
        self.btc_supply = lib.crypto_onchain_blockchain_model.get_btc_circulating_supply
        self.btc_supply_view = (
            lib.crypto_onchain_blockchain_view.display_btc_circulating_supply
        )
        self.btc_transac = (
            lib.crypto_onchain_blockchain_model.get_btc_confirmed_transactions
        )
        self.btc_transac_view = (
            lib.crypto_onchain_blockchain_view.display_btc_confirmed_transactions
        )
        self.gwei = lib.crypto_onchain_ethgasstation_model.get_gwei_fees
        self.gwei_view = lib.crypto_onchain_ethgasstation_view.display_gwei_fees
        self.hist = lib.crypto_onchain_ethplorer_model.get_address_history
        self.hist_view = lib.crypto_onchain_ethplorer_view.display_address_history
        self.balance = lib.crypto_onchain_ethplorer_model.get_address_info
        self.balance_view = lib.crypto_onchain_ethplorer_view.display_address_info
        self.token_decimals = lib.crypto_onchain_ethplorer_model.get_token_decimals
        self.prices = lib.crypto_onchain_ethplorer_model.get_token_historical_price
        self.prices_view = (
            lib.crypto_onchain_ethplorer_view.display_token_historical_prices
        )
        self.th = lib.crypto_onchain_ethplorer_model.get_token_history
        self.th_view = lib.crypto_onchain_ethplorer_view.display_token_history
        self.info = lib.crypto_onchain_ethplorer_model.get_token_info
        self.info_view = lib.crypto_onchain_ethplorer_view.display_token_info
        self.holders = lib.crypto_onchain_ethplorer_model.get_top_token_holders
        self.holders_view = lib.crypto_onchain_ethplorer_view.display_top_token_holders
        self.top = lib.crypto_onchain_ethplorer_model.get_top_tokens
        self.top_view = lib.crypto_onchain_ethplorer_view.display_top_tokens
        self.tx = lib.crypto_onchain_ethplorer_model.get_tx_info
        self.tx_view = lib.crypto_onchain_ethplorer_view.display_tx_info
        self.whales = lib.crypto_onchain_whale_alert_model.get_whales_transactions
        self.whales_view = (
            lib.crypto_onchain_whale_alert_view.display_whales_transactions
        )


class CryptoOverview(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.altindex = lib.crypto_ov_blockchaincenter_model.get_altcoin_index
        self.altindex_view = lib.crypto_ov_blockchaincenter_view.display_altcoin_index
        self.cbpairs = lib.crypto_ov_coinbase_model.get_trading_pairs
        self.cbpairs_view = lib.crypto_ov_coinbase_view.display_trading_pairs
        self.cpplatforms = lib.crypto_ov_coinpaprika_model.get_all_contract_platforms
        self.cpplatforms_view = lib.crypto_ov_coinpaprika_view.display_all_platforms
        self.cpinfo = lib.crypto_ov_coinpaprika_model.get_coins_info
        self.cpinfo_view = lib.crypto_ov_coinpaprika_view.display_all_coins_info
        self.cpmarkets = lib.crypto_ov_coinpaprika_model.get_coins_market_info
        self.cpmarkets_view = (
            lib.crypto_ov_coinpaprika_view.display_all_coins_market_info
        )
        self.cpcontracts = lib.crypto_ov_coinpaprika_model.get_contract_platform
        self.cpcontracts_view = lib.crypto_ov_coinpaprika_view.display_contracts
        self.cpexmarkets = lib.crypto_ov_coinpaprika_model.get_exchanges_market
        self.cpexmarkets_view = lib.crypto_ov_coinpaprika_view.display_exchange_markets
        self.cpglobal = lib.crypto_ov_coinpaprika_model.get_global_market
        self.cpglobal_view = lib.crypto_ov_coinpaprika_view.display_global_market
        self.list_of_coins = lib.crypto_ov_coinpaprika_model.get_list_of_coins
        self.cpexchanges = lib.crypto_ov_coinpaprika_model.get_list_of_exchanges
        self.cpexchanges_view = lib.crypto_ov_coinpaprika_view.display_all_exchanges
        self.news = lib.crypto_ov_cryptopanic_model.get_news
        self.news_view = lib.crypto_ov_cryptopanic_view.display_news
        self.cr = lib.crypto_ov_loanscan_model.get_rates
        self.cr_view = lib.crypto_ov_loanscan_view.display_crypto_rates
        self.cgderivatives = lib.crypto_ov_pycoingecko_model.get_derivatives
        self.cgderivatives_view = lib.crypto_ov_pycoingecko_view.display_derivatives
        self.cgexrates = lib.crypto_ov_pycoingecko_model.get_exchange_rates
        self.cgexrates_view = lib.crypto_ov_pycoingecko_view.display_exchange_rates
        self.exchanges = lib.crypto_ov_pycoingecko_model.get_exchanges
        self.exchanges_view = lib.crypto_ov_pycoingecko_view.display_exchanges
        self.cgproducts = lib.crypto_ov_pycoingecko_model.get_finance_products
        self.cgproducts_view = lib.crypto_ov_pycoingecko_view.display_products
        self.platforms = lib.crypto_ov_pycoingecko_model.get_financial_platforms
        self.platforms_view = lib.crypto_ov_pycoingecko_view.display_platforms
        self.cgdefi = lib.crypto_ov_pycoingecko_model.get_global_defi_info
        self.cgdefi_view = lib.crypto_ov_pycoingecko_view.display_global_defi_info
        self.global_info = lib.crypto_ov_pycoingecko_model.get_global_info
        self.cgglobal = lib.crypto_ov_pycoingecko_model.get_global_markets_info
        self.cgglobal_view = lib.crypto_ov_pycoingecko_view.display_global_market_info
        self.cghold = lib.crypto_ov_pycoingecko_model.get_holdings_overview
        self.cghold_view = lib.crypto_ov_pycoingecko_view.display_holdings_overview
        self.cgindexes = lib.crypto_ov_pycoingecko_model.get_indexes
        self.cgindexes_view = lib.crypto_ov_pycoingecko_view.display_indexes
        self.cgstables = lib.crypto_ov_pycoingecko_model.get_stable_coins
        self.cgstables_view = lib.crypto_ov_pycoingecko_view.display_stablecoins
        self.cgcategories = lib.crypto_ov_pycoingecko_model.get_top_crypto_categories
        self.cgcategories_view = lib.crypto_ov_pycoingecko_view.display_categories
        self.cgh = lib.crypto_ov_pycoingecko_model.get_coins
        self.cgh_view = lib.crypto_ov_pycoingecko_view.display_crypto_heatmap
        self.crypto_hack = lib.crypto_ov_rekt_model.get_crypto_hack
        self.crypto_hack_slugs = lib.crypto_ov_rekt_model.get_crypto_hack_slugs
        self.crypto_hacks = lib.crypto_ov_rekt_model.get_crypto_hacks
        self.crypto_hacks_view = lib.crypto_ov_rekt_view.display_crypto_hacks
        self.wfpe = lib.crypto_ov_withdrawalfees_model.get_crypto_withdrawal_fees
        self.wfpe_view = (
            lib.crypto_ov_withdrawalfees_view.display_crypto_withdrawal_fees
        )
        self.ewf = (
            lib.crypto_ov_withdrawalfees_model.get_overall_exchange_withdrawal_fees
        )
        self.ewf_view = (
            lib.crypto_ov_withdrawalfees_view.display_overall_exchange_withdrawal_fees
        )
        self.wf = lib.crypto_ov_withdrawalfees_model.get_overall_withdrawal_fees
        self.wf_view = lib.crypto_ov_withdrawalfees_view.display_overall_withdrawal_fees


class CryptoTools(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.apy = lib.crypto_tools_model.calculate_apy
        self.apy_view = lib.crypto_tools_view.display_apy
        self.il = lib.crypto_tools_model.calculate_il
        self.il_view = lib.crypto_tools_view.display_il


##################################################################
#                           Common                               #
##################################################################


class CommonQuantitativeAnalysis(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.bw = lib.common_qa_view.display_bw
        self.calculate_adjusted_var = lib.common_qa_model.calculate_adjusted_var
        self.es = lib.common_qa_model.get_es
        self.es_view = lib.common_qa_view.display_es
        self.normality = lib.common_qa_model.get_normality
        self.normality_view = lib.common_qa_view.display_normality
        self.omega = lib.common_qa_model.get_omega
        self.omega_view = lib.common_qa_view.display_omega
        self.decompose = lib.common_qa_model.get_seasonal_decomposition
        self.sharpe = lib.common_qa_model.get_sharpe
        self.sharpe_view = lib.common_qa_view.display_sharpe
        self.sortino = lib.common_qa_model.get_sortino
        self.sortino_view = lib.common_qa_view.display_sortino
        self.summary = lib.common_qa_model.get_summary
        self.summary_view = lib.common_qa_view.display_summary
        self.unitroot = lib.common_qa_model.get_unitroot
        self.unitroot_view = lib.common_qa_view.display_unitroot
        self.var = lib.common_qa_model.get_var
        self.var_view = lib.common_qa_view.display_var
        self.kurtosis = lib.common_qa_rolling_model.get_kurtosis
        self.kurtosis_view = lib.common_qa_rolling_view.display_kurtosis
        self.quantile = lib.common_qa_rolling_model.get_quantile
        self.quantile_view = lib.common_qa_rolling_view.display_quantile
        self.rolling = lib.common_qa_rolling_model.get_rolling_avg
        self.rolling_view = lib.common_qa_rolling_view.display_mean_std
        self.skew = lib.common_qa_rolling_model.get_skew
        self.skew_view = lib.common_qa_rolling_view.display_skew
        self.spread = lib.common_qa_rolling_model.get_spread
        self.spread_view = lib.common_qa_rolling_view.display_spread


class CommonTechnicalAnalysis(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.ad = lib.common_ta_volume_model.ad
        self.ad_view = lib.common_ta_volume_view.display_ad
        self.adosc = lib.common_ta_volume_model.adosc
        self.adosc_view = lib.common_ta_volume_view.display_adosc
        self.aroon = lib.common_ta_trend_indicators_model.aroon
        self.aroon_view = lib.common_ta_trend_indicators_view.display_aroon
        self.adx = lib.common_ta_trend_indicators_model.adx
        self.adx_view = lib.common_ta_trend_indicators_view.display_adx
        self.atr = lib.common_ta_volatility_model.atr
        self.atr_view = lib.common_ta_volatility_view.display_atr
        self.bbands = lib.common_ta_volatility_model.bbands
        self.bbands_view = lib.common_ta_volatility_view.display_bbands
        self.donchian = lib.common_ta_volatility_model.donchian
        self.donchian_view = lib.common_ta_volatility_view.display_donchian
        self.ema = lib.common_ta_overlap_model.ema
        self.fib = lib.common_ta_custom_indicators_model.calculate_fib_levels
        self.fib_view = lib.common_ta_custom_indicators_view.fibonacci_retracement
        self.fisher = lib.common_ta_momentum_model.fisher
        self.hma = lib.common_ta_overlap_model.hma
        self.kc = lib.common_ta_volatility_model.kc
        self.kc_view = lib.common_ta_volatility_view.view_kc
        self.ma = lib.common_ta_overlap_view.view_ma
        self.macd = lib.common_ta_momentum_model.macd
        self.macd_view = lib.common_ta_momentum_view.display_macd
        self.obv = lib.common_ta_volume_model.obv
        self.obv_view = lib.common_ta_volume_view.display_obv
        self.rsi = lib.common_ta_momentum_model.rsi
        self.rsi_view = lib.common_ta_momentum_view.display_rsi
        self.sma = lib.common_ta_overlap_model.sma
        self.stoch = lib.common_ta_momentum_model.stoch
        self.stoch_view = lib.common_ta_momentum_view.display_stoch
        self.vwap = lib.common_ta_overlap_model.vwap
        self.vwap_view = lib.common_ta_overlap_view.view_vwap
        self.wma = lib.common_ta_overlap_model.wma
        self.zlma = lib.common_ta_overlap_model.zlma


class StocksBehavioralAnalysis(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.headlines = lib.ba_finbrain_model.get_sentiment
        self.headlines_view = lib.ba_finbrain_view.display_sentiment_analysis
        self.mentions = lib.ba_google_model.get_mentions
        self.mentions_view = lib.ba_google_view.display_mentions
        self.queries = lib.ba_google_model.get_queries
        self.regions = lib.ba_google_model.get_regions
        self.regions_view = lib.ba_google_view.display_regions
        self.rise = lib.ba_google_model.get_rise
        self.rise_view = lib.ba_google_view.display_rise
        self.getdd = lib.ba_reddit_model.get_due_dilligence
        self.popular = lib.ba_reddit_model.get_popular_tickers
        self.popular_view = lib.ba_reddit_view.display_popular_tickers
        self.redditsent = lib.ba_reddit_model.get_posts_about
        self.redditsent_view = lib.ba_reddit_view.display_redditsent
        self.text_sent = lib.ba_reddit_model.get_sentiment
        self.spac = lib.ba_reddit_model.get_spac
        self.spacc = lib.ba_reddit_model.get_spac_community
        self.watchlist = lib.ba_reddit_model.get_watchlists
        self.watchlist_view = lib.ba_reddit_view.display_watchlist
        self.wsb = lib.ba_reddit_model.get_wsb_community
        self.hist = lib.ba_sentimentinvestor_model.get_historical
        self.hist_view = lib.ba_sentimentinvestor_view.display_historical
        self.trend = lib.ba_sentimentinvestor_model.get_trending
        self.trend_view = lib.ba_sentimentinvestor_view.display_trending
        self.bullbear = lib.ba_stocktwits_model.get_bullbear
        self.bullbear_view = lib.ba_stocktwits_view.display_bullbear
        self.messages = lib.ba_stocktwits_model.get_messages
        self.messages_view = lib.ba_stocktwits_view.display_messages
        self.stalker = lib.ba_stocktwits_model.get_stalker
        self.trending = lib.ba_stocktwits_model.get_trending
        self.infer = lib.ba_twitter_model.load_analyze_tweets
        self.infer_view = lib.ba_twitter_view.display_inference
        self.sentiment = lib.ba_twitter_model.get_sentiment
        self.sentiment_view = lib.ba_twitter_view.display_sentiment


##################################################################
#                         Alternative                            #
##################################################################


class Covid(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.slopes = lib.alt_covid_model.get_case_slopes
        self.slopes_view = lib.alt_covid_view.display_case_slopes
        self.global_cases = lib.alt_covid_model.get_global_cases
        self.global_deaths = lib.alt_covid_model.get_global_deaths
        self.ov = lib.alt_covid_model.get_covid_ov
        self.ov_view = lib.alt_covid_view.display_covid_ov
        self.stat = lib.alt_covid_model.get_covid_stat
        self.stat_view = lib.alt_covid_view.display_covid_stat


class OSS(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.github_data = lib.alt_oss_github_model.get_github_data
        self.summary = lib.alt_oss_github_model.get_repo_summary
        self.summary_view = lib.alt_oss_github_view.display_repo_summary
        self.history = lib.alt_oss_github_model.get_stars_history
        self.history_view = lib.alt_oss_github_view.display_star_history
        self.top = lib.alt_oss_github_model.get_top_repos
        self.top_view = lib.alt_oss_github_view.display_top_repos
        self.search = lib.alt_oss_github_model.search_repos
        self._make_request = lib.alt_oss_runa_model._make_request
        self._retry_session = lib.alt_oss_runa_model._retry_session
        self.ross = lib.alt_oss_runa_model.get_startups
        self.ross_view = lib.alt_oss_runa_view.display_rossindex


class Alternative:
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)

    @property
    def oss(self):
        """Open Source Something Module

        Submodules:
            `covid`: Covid Module
            `oss`: Open Source Something Module
        """
        return OSS()

    @property
    def covid(self):
        """Covid Module

        Submodules:
            `covid`: Covid Module
            `oss`: Open Source Something Module
        """
        return Covid()


##################################################################
#                            Stocks                              #
##################################################################


class StocksQuantitativeAnalysis(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.capm_information = lib.stocks_qa_factors_model.capm_information
        self.fama_raw = lib.stocks_qa_factors_model.get_fama_raw
        self.historical_5 = lib.stocks_qa_factors_model.get_historical_5


class StocksTechnicalAnalysis(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.summary = lib.stocks_ta_finbrain_model.get_technical_summary_report
        self.view = lib.stocks_ta_finviz_model.get_finviz_image
        self.recom = lib.stocks_ta_tradingview_model.get_tradingview_recommendation


class StocksComparisonAnalysis(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.sentiment = lib.stocks_ca_finbrain_model.get_sentiments
        self.sentiment_view = lib.stocks_ca_finbrain_view.display_sentiment_compare
        self.scorr = lib.stocks_ca_finbrain_model.get_sentiment_correlation
        self.scorr_view = lib.stocks_ca_finbrain_view.display_sentiment_correlation
        self.finnhub_peers = lib.stocks_ca_finnhub_model.get_similar_companies
        self.screener = lib.stocks_ca_finviz_compare_model.get_comparison_data
        self.finviz_peers = lib.stocks_ca_finviz_compare_model.get_similar_companies
        self.balance = lib.stocks_ca_marketwatch_model.get_balance_comparison
        self.cashflow = lib.stocks_ca_marketwatch_model.get_cashflow_comparison
        self.income = lib.stocks_ca_marketwatch_model.get_income_comparison
        self.income_view = lib.stocks_ca_marketwatch_view.display_income_comparison
        self.polygon_peers = lib.stocks_ca_polygon_model.get_similar_companies
        self.hist = lib.stocks_ca_yahoo_finance_model.get_historical
        self.hist_view = lib.stocks_ca_yahoo_finance_view.display_historical
        self.hcorr = lib.stocks_ca_yahoo_finance_model.get_correlation
        self.hcorr_view = lib.stocks_ca_yahoo_finance_view.display_correlation
        self.volume = lib.stocks_ca_yahoo_finance_model.get_volume
        self.volume_view = lib.stocks_ca_yahoo_finance_view.display_volume


class StocksDarkPoolShorts(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.prom = lib.stocks_dps_finra_model.getATSdata
        self.prom_view = lib.stocks_dps_finra_view.darkpool_otc
        self.dpotc = lib.stocks_dps_finra_model.getTickerFINRAdata
        self.dpotc_view = lib.stocks_dps_finra_view.darkpool_ats_otc
        self.ctb = lib.stocks_dps_ibkr_model.get_cost_to_borrow
        self.volexch = lib.stocks_dps_nyse_model.get_short_data_by_exchange
        self.volexch_view = lib.stocks_dps_nyse_view.display_short_by_exchange
        self.psi_q = lib.stocks_dps_quandl_model.get_short_interest
        self.psi_q_view = lib.stocks_dps_quandl_view.short_interest
        self.ftd = lib.stocks_dps_sec_model.get_fails_to_deliver
        self.ftd_view = lib.stocks_dps_sec_view.fails_to_deliver
        self.hsi = lib.stocks_dps_shortinterest_model.get_high_short_interest
        self.pos = lib.stocks_dps_stockgrid_model.get_dark_pool_short_positions
        self.spos = lib.stocks_dps_stockgrid_model.get_net_short_position
        self.spos_view = lib.stocks_dps_stockgrid_view.net_short_position
        self.sidtc = lib.stocks_dps_stockgrid_model.get_short_interest_days_to_cover
        self.psi_sg = lib.stocks_dps_stockgrid_model.get_short_interest_volume
        self.psi_sg_view = lib.stocks_dps_stockgrid_view.short_interest_volume
        self.shorted = lib.stocks_dps_yahoofinance_model.get_most_shorted
        self.ctb = lib.stocks_dps_stocksera_model.get_cost_to_borrow
        self.ctb_view = lib.stocks_dps_stocksera_view.plot_cost_to_borrow


class StocksDiscovery(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.arkord = lib.stocks_disc_ark_model.get_ark_orders
        self.ipo = lib.stocks_disc_finnhub_model.get_ipo_calendar
        self.pipo = lib.stocks_disc_finnhub_model.get_past_ipo
        self.fipo = lib.stocks_disc_finnhub_model.get_future_ipo
        self.dividends = lib.stocks_disc_nasdaq_model.get_dividend_cal
        self.rtat = lib.stocks_disc_nasdaq_model.get_retail_tickers
        self.news = lib.stocks_disc_seeking_alpha_model.get_news
        self.upcoming = lib.stocks_disc_seeking_alpha_model.get_next_earnings
        self.trending = lib.stocks_disc_seeking_alpha_model.get_trending_list
        self.lowfloat = lib.stocks_disc_shortinterest_model.get_low_float
        self.hotpenny = lib.stocks_disc_shortinterest_model.get_today_hot_penny_stocks
        self.active = lib.stocks_disc_yahoofinance_model.get_active
        self.asc = lib.stocks_disc_yahoofinance_model.get_asc
        self.gainers = lib.stocks_disc_yahoofinance_model.get_gainers
        self.gtech = lib.stocks_disc_yahoofinance_model.get_gtech
        self.losers = lib.stocks_disc_yahoofinance_model.get_losers
        self.ugs = lib.stocks_disc_yahoofinance_model.get_ugs
        self.ulc = lib.stocks_disc_yahoofinance_model.get_ulc


class StocksDueDiligence(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.arktrades = lib.stocks_dd_ark_model.get_ark_trades_by_ticker
        self.est = lib.stocks_dd_business_insider_model.get_estimates
        self.pt = lib.stocks_dd_business_insider_model.get_price_target_from_analysts
        self.pt_view = lib.stocks_dd_business_insider_view.price_target_from_analysts
        self.customer = lib.stocks_dd_csimarket_model.get_customers
        self.supplier = lib.stocks_dd_csimarket_model.get_suppliers
        self.rot = lib.stocks_dd_finnhub_model.get_rating_over_time
        self.rot_view = lib.stocks_dd_finnhub_view.rating_over_time
        self.analyst = lib.stocks_dd_finviz_model.get_analyst_data
        self.news = lib.stocks_dd_finviz_model.get_news
        self.rating = lib.stocks_dd_fmp_model.get_rating
        self.sec = lib.stocks_dd_marketwatch_model.get_sec_filings
        self.sec_view = lib.stocks_dd_marketwatch_view.sec_filings


class StocksTradingHours(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.check_if_open = lib.stocks_th_bursa_model.check_if_open
        self.all = lib.stocks_th_bursa_model.get_all
        self.all_view = lib.stocks_th_bursa_view.display_all
        self.closed = lib.stocks_th_bursa_model.get_closed
        self.closed_view = lib.stocks_th_bursa_view.display_closed
        self.open = lib.stocks_th_bursa_model.get_open
        self.open_view = lib.stocks_th_bursa_view.display_open
        self.exchange = lib.stocks_th_bursa_model.get_bursa
        self.exchange_view = lib.stocks_th_bursa_view.display_exchange


class StocksSIA(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.filter_stocks = lib.stocks_sia_financedatabase_model.filter_stocks
        self.cpci = (
            lib.stocks_sia_financedatabase_model.get_companies_per_country_in_industry
        )
        self.cpci_view = (
            lib.stocks_sia_financedatabase_view.display_companies_per_country_in_industry
        )
        self.cpcs = (
            lib.stocks_sia_financedatabase_model.get_companies_per_country_in_sector
        )
        self.cpcs_view = (
            lib.stocks_sia_financedatabase_view.display_companies_per_country_in_sector
        )
        self.cpic = (
            lib.stocks_sia_financedatabase_model.get_companies_per_industry_in_country
        )
        self.cpic_view = (
            lib.stocks_sia_financedatabase_view.display_companies_per_industry_in_country
        )
        self.cpis = (
            lib.stocks_sia_financedatabase_model.get_companies_per_industry_in_sector
        )
        self.cpis_view = (
            lib.stocks_sia_financedatabase_view.display_companies_per_industry_in_sector
        )
        self.cps = (
            lib.stocks_sia_financedatabase_model.get_companies_per_sector_in_country
        )
        self.cps_view = (
            lib.stocks_sia_financedatabase_view.display_companies_per_sector_in_country
        )
        self.countries = lib.stocks_sia_financedatabase_model.get_countries
        self.industries = lib.stocks_sia_financedatabase_model.get_industries
        self.marketcap = lib.stocks_sia_financedatabase_model.get_marketcap
        self.sectors = lib.stocks_sia_financedatabase_model.get_sectors
        self.stocks_data = lib.stocks_sia_stockanalysis_model.get_stocks_data


class StocksScreener(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.screener_data = lib.stocks_screener_finviz_model.get_screener_data
        self.screener_view = lib.stocks_screener_finviz_view.screener
        self.historical = lib.stocks_screener_yahoofinance_model.historical
        self.historical_view = lib.stocks_screener_yahoofinance_view.historical


class StocksOptionsScreen(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.check_presets = lib.stocks_options_screen_syncretism_model.check_presets
        self.screener_output = (
            lib.stocks_options_screen_syncretism_model.get_screener_output
        )
        self.screener_output_view = (
            lib.stocks_options_screen_syncretism_view.view_screener_output
        )


class StocksOptionsHedge(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.add_hedge_option = lib.stocks_options_hedge_hedge_model.add_hedge_option
        self.add_hedge_option_view = (
            lib.stocks_options_hedge_hedge_view.add_and_show_greeks
        )
        self.calc_delta = lib.stocks_options_hedge_hedge_model.calc_delta
        self.calc_gamma = lib.stocks_options_hedge_hedge_model.calc_gamma
        self.calc_hedge = lib.stocks_options_hedge_hedge_model.calc_hedge
        self.calc_hedge_view = lib.stocks_options_hedge_hedge_view.show_calculated_hedge
        self.calc_vega = lib.stocks_options_hedge_hedge_model.calc_vega


class StocksOptions(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.screen = StocksOptionsScreen()
        self.hedge = StocksOptionsHedge()
        self.pcr = lib.stocks_options_alphaquery_model.get_put_call_ratio
        self.pcr_view = lib.stocks_options_alphaquery_view.display_put_call_ratio
        self.info = lib.stocks_options_yfinance_model.get_info
        self.info_view = lib.stocks_options_barchart_view.print_options_data
        self.hist_ce = lib.stocks_options_chartexchange_model.get_option_history
        self.hist_ce_view = lib.stocks_options_chartexchange_view.display_raw
        self.unu = lib.stocks_options_fdscanner_model.unusual_options
        self.unu_view = lib.stocks_options_fdscanner_view.display_options
        self.grhist = lib.stocks_options_screen_syncretism_model.get_historical_greeks
        self.grhist_view = (
            lib.stocks_options_screen_syncretism_view.view_historical_greeks
        )
        self.hist_tr = lib.stocks_options_tradier_model.get_historical_options
        self.hist_tr_view = lib.stocks_options_tradier_view.display_historical
        self.chains_tr = lib.stocks_options_tradier_model.get_option_chains
        self.chains_tr_view = lib.stocks_options_tradier_view.display_chains
        self.chains_yf = lib.stocks_options_yfinance_model.get_option_chain
        self.chains_yf_view = lib.stocks_options_yfinance_view.display_chains
        self.chains_nasdaq = lib.stocks_options_nasdaq_model.get_chain_given_expiration
        self.chains_nasdaq_view = lib.stocks_options_nasdaq_view.display_chains
        self.last_price = lib.stocks_options_tradier_model.last_price
        self.option_expirations = lib.stocks_options_yfinance_model.option_expirations
        self.process_chains = lib.stocks_options_tradier_model.process_chains
        self.generate_data = lib.stocks_options_yfinance_model.generate_data
        self.closing = lib.stocks_options_yfinance_model.get_closing
        self.dividend = lib.stocks_options_yfinance_model.get_dividend
        self.dte = lib.stocks_options_yfinance_model.get_dte
        self.vsurf = lib.stocks_options_yfinance_model.get_iv_surface
        self.vsurf_view = lib.stocks_options_yfinance_view.display_vol_surface
        self.vol_yf = lib.stocks_options_yfinance_model.get_vol
        self.vol_yf_view = lib.stocks_options_yfinance_view.plot_vol
        self.voi_yf = lib.stocks_options_yfinance_model.get_volume_open_interest
        self.voi_yf_view = lib.stocks_options_yfinance_view.plot_volume_open_interest
        self.option_chain = lib.stocks_options_yfinance_model.get_option_chain
        self.price = lib.stocks_options_yfinance_model.get_price
        self.x_values = lib.stocks_options_yfinance_model.get_x_values
        self.y_values = lib.stocks_options_yfinance_model.get_y_values
        self.chains = get_chains


def get_chains(ticker: str, expiry: str, source: str = "tr"):
    """Gets option chain for given ticker and expiration from given source (Default: tradier)

    Parameters
    ----------
    symbol: str
        Ticker symbol to get options for
    expiry: str
        Date to get options for. YYYY-MM-DD
    source: str
        Source to get options from. Default: tradier
        Choices: tradier, yf, nasdaq

    Returns
    -------
    chains: pd.DataFrame
        Options chain
    """
    if source.lower() in ("yf", "yahoofinance"):
        chains = StocksOptions().chains_yf(ticker, expiry)
        chains = pd.concat([chains.calls.copy(), chains.puts.copy()])
    elif source.lower() in ("tr", "tradier"):
        chains = StocksOptions().chains_tr(ticker, expiry)
    elif source.lower() in ("nasdaq", "nas", "nq"):
        chains = StocksOptions().chains_nasdaq(ticker, expiry)

    return chains


class StocksInsider(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.act = lib.stocks_insider_businessinsider_model.get_insider_activity
        self.act_view = lib.stocks_insider_businessinsider_view.insider_activity
        self.lins = lib.stocks_insider_finviz_model.get_last_insider_activity
        self.lins_view = lib.stocks_insider_finviz_view.last_insider_activity
        self.print_insider_data = (
            lib.stocks_insider_openinsider_model.get_print_insider_data
        )
        self.print_insider_data_view = (
            lib.stocks_insider_openinsider_view.print_insider_data
        )


class StocksGovMenu:
    def __init__(self):
        self.qtrcontracts = lib.stocks_gov_quiverquant_model.get_qtr_contracts
        self.qtrcontracts_view = lib.stocks_gov_quiverquant_view.display_qtr_contracts
        self.gov_trading = lib.stocks_gov_quiverquant_model.get_government_trading
        self.contracts = lib.stocks_gov_quiverquant_model.get_contracts
        self.contracts_view = lib.stocks_gov_quiverquant_view.display_contracts
        self.topbuys = lib.stocks_gov_quiverquant_model.get_government_buys
        self.topbuys_view = lib.stocks_gov_quiverquant_view.display_government_buys
        self.topsells = lib.stocks_gov_quiverquant_model.get_government_sells
        self.topsells_view = lib.stocks_gov_quiverquant_view.display_government_sells
        self.gtrades = lib.stocks_gov_quiverquant_model.get_cleaned_government_trading
        self.gtrades_view = lib.stocks_gov_quiverquant_view.display_government_trading
        self.histcont = lib.stocks_gov_quiverquant_model.get_hist_contracts
        self.histcont_view = lib.stocks_gov_quiverquant_view.display_hist_contracts
        self.lastcontracts = lib.stocks_gov_quiverquant_model.get_last_contracts
        self.lastcontracts_view = lib.stocks_gov_quiverquant_view.display_last_contracts
        self.lasttrades = lib.stocks_gov_quiverquant_model.get_last_government
        self.lobbying = lib.stocks_gov_quiverquant_model.get_lobbying
        self.toplobbying = lib.stocks_gov_quiverquant_model.get_top_lobbying
        self.toplobbying_view = lib.stocks_gov_quiverquant_view.display_top_lobbying


class StocksFundamentalAnalysis(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.av_balance = lib.stocks_fa_av_model.get_balance_sheet
        self.av_cash = lib.stocks_fa_av_model.get_cash_flow
        self.av_cash_view = lib.stocks_fa_av_view.display_cash_flow
        self.dupont = lib.stocks_fa_av_model.get_dupont
        self.earnings = lib.stocks_fa_av_model.get_earnings
        self.fraud = lib.stocks_fa_av_model.get_fraud_ratios
        self.av_income = lib.stocks_fa_av_model.get_income_statements
        self.av_metrics = lib.stocks_fa_av_model.get_key_metrics
        self.av_overview = lib.stocks_fa_av_model.get_overview
        self.mgmt = lib.stocks_fa_business_insider_model.get_management
        self.fama_coe = lib.stocks_fa_dcf_model.get_fama_coe
        self.fama_raw = lib.stocks_fa_dcf_model.get_fama_raw
        self.historical_5 = lib.stocks_fa_dcf_model.get_historical_5
        self.similar_dfs = lib.stocks_fa_dcf_model.get_similar_dfs
        self.analysis = lib.stocks_fa_eclect_us_model.get_filings_analysis
        self.fmp_balance = lib.stocks_fa_fmp_model.get_balance
        self.fmp_cash = lib.stocks_fa_fmp_model.get_cash
        self.dcf = lib.stocks_fa_fmp_model.get_dcf
        self.enterprise = lib.stocks_fa_fmp_model.get_enterprise
        self.growth = lib.stocks_fa_fmp_model.get_financial_growth
        self.fmp_income = lib.stocks_fa_fmp_model.get_income
        self.fmp_metrics = lib.stocks_fa_fmp_model.get_key_metrics
        self.fmp_ratios = lib.stocks_fa_fmp_model.get_key_ratios
        self.profile = lib.stocks_fa_fmp_model.get_profile
        self.quote = lib.stocks_fa_fmp_model.get_quote
        self.score = lib.stocks_fa_fmp_model.get_score
        self.data = lib.stocks_fa_finviz_model.get_data
        self.poly_financials = lib.stocks_fa_polygon_model.get_financials
        self.poly_financials_view = lib.stocks_fa_polygon_view.display_fundamentals
        self.cal = lib.stocks_fa_yahoo_finance_model.get_calendar_earnings
        self.divs = lib.stocks_fa_yahoo_finance_model.get_dividends
        self.yf_financials = lib.stocks_fa_yahoo_finance_model.get_financials
        self.yf_financials_view = lib.stocks_fa_yahoo_finance_view.display_fundamentals
        self.hq = lib.stocks_fa_yahoo_finance_model.get_hq
        self.info = lib.stocks_fa_yahoo_finance_model.get_info
        self.mktcap = lib.stocks_fa_yahoo_finance_model.get_mktcap
        self.shrs = lib.stocks_fa_yahoo_finance_model.get_shareholders
        self.splits = lib.stocks_fa_yahoo_finance_model.get_splits
        self.splits_view = lib.stocks_fa_yahoo_finance_view.display_splits
        self.sust = lib.stocks_fa_yahoo_finance_model.get_sustainability
        self.website = lib.stocks_fa_yahoo_finance_model.get_website


##################################################################
#                           Portfolio                            #
##################################################################


class Portfolio_Optimization(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.load = lib.portfolio_optimization_excel_model.load_allocation
        self.load_bl_views = lib.portfolio_optimization_excel_model.load_bl_views
        self.maxsharpe = lib.portfolio_optimization_optimizer_model.get_max_sharpe
        self.maxsharpe_view = (
            lib.portfolio_optimization_optimizer_view.display_max_sharpe
        )
        self.minrisk = lib.portfolio_optimization_optimizer_model.get_min_risk
        self.minrisk_view = lib.portfolio_optimization_optimizer_view.display_min_risk
        self.maxutil = lib.portfolio_optimization_optimizer_model.get_max_util
        self.maxutil_view = lib.portfolio_optimization_optimizer_view.display_max_util
        self.maxret = lib.portfolio_optimization_optimizer_model.get_max_ret
        self.maxret_view = lib.portfolio_optimization_optimizer_view.display_max_ret
        self.maxdiv = (
            lib.portfolio_optimization_optimizer_model.get_max_diversification_portfolio
        )
        self.maxdiv_view = lib.portfolio_optimization_optimizer_view.display_max_div
        self.maxdecorr = (
            lib.portfolio_optimization_optimizer_model.get_max_decorrelation_portfolio
        )
        self.maxdecorr_view = (
            lib.portfolio_optimization_optimizer_view.display_max_decorr
        )
        self.blacklitterman = (
            lib.portfolio_optimization_optimizer_model.get_black_litterman_portfolio
        )
        self.blacklitterman_view = (
            lib.portfolio_optimization_optimizer_view.display_black_litterman
        )
        self.ef = lib.portfolio_optimization_optimizer_model.get_ef
        self.ef_view = lib.portfolio_optimization_optimizer_view.display_ef
        self.riskparity = (
            lib.portfolio_optimization_optimizer_model.get_risk_parity_portfolio
        )
        self.riskparity_view = (
            lib.portfolio_optimization_optimizer_view.display_risk_parity
        )
        self.relriskparity = (
            lib.portfolio_optimization_optimizer_model.get_rel_risk_parity_portfolio
        )
        self.relriskparity_view = (
            lib.portfolio_optimization_optimizer_view.display_rel_risk_parity
        )
        self.meanrisk = (
            lib.portfolio_optimization_optimizer_model.get_mean_risk_portfolio
        )
        self.meanrisk_view = lib.portfolio_optimization_optimizer_view.display_mean_risk
        self.hrp = lib.portfolio_optimization_optimizer_model.get_hrp
        self.hrp_view = lib.portfolio_optimization_optimizer_view.display_hrp
        self.herc = lib.portfolio_optimization_optimizer_model.get_herc
        self.herc_view = lib.portfolio_optimization_optimizer_view.display_herc
        self.nco = lib.portfolio_optimization_optimizer_model.get_nco
        self.nco_view = lib.portfolio_optimization_optimizer_view.display_nco
        self.hcp = lib.portfolio_optimization_optimizer_model.get_hcp_portfolio
        self.hcp_view = lib.portfolio_optimization_optimizer_view.display_hcp
        self.equal = lib.portfolio_optimization_optimizer_model.get_equal_weights
        self.property = lib.portfolio_optimization_optimizer_model.get_property_weights
        self.property_view = (
            lib.portfolio_optimization_optimizer_view.display_property_weighting
        )
        self.get_properties = lib.portfolio_optimization_optimizer_model.get_properties
        self.plot = lib.portfolio_optimization_optimizer_view.additional_plots
        self.plot_view = lib.portfolio_optimization_optimizer_view.additional_plots


class PortfolioModule(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.po = Portfolio_Optimization()
        self.holdv = lib.portfolio_model.get_holdings_value
        self.holdv_view = lib.portfolio_view.display_holdings_value
        self.holdp = lib.portfolio_model.get_holdings_percentage
        self.holdp_view = lib.portfolio_view.display_holdings_percentage
        self.yret = lib.portfolio_model.get_yearly_returns
        self.yret_view = lib.portfolio_view.display_yearly_returns
        self.mret = lib.portfolio_model.get_monthly_returns
        self.mret_view = lib.portfolio_view.display_monthly_returns
        self.dret = lib.portfolio_model.get_daily_returns
        self.dret_view = lib.portfolio_view.display_daily_returns
        self.max_drawdown_ratio = lib.portfolio_model.get_maximum_drawdown_ratio
        self.max_drawdown_ratio_view = lib.portfolio_view.display_maximum_drawdown_ratio
        self.distr = lib.portfolio_model.get_distribution_returns
        self.distr_view = lib.portfolio_view.display_distribution_returns
        self.maxdd = lib.portfolio_model.get_maximum_drawdown
        self.maxdd_view = lib.portfolio_view.display_maximum_drawdown
        self.rvol = lib.portfolio_model.get_rolling_volatility
        self.rvol_view = lib.portfolio_view.display_rolling_volatility
        self.rsharpe = lib.portfolio_model.get_rolling_sharpe
        self.rsharpe_view = lib.portfolio_view.display_rolling_sharpe
        self.rsortino = lib.portfolio_model.get_rolling_sortino
        self.rsortino_view = lib.portfolio_view.display_rolling_sortino
        self.rbeta = lib.portfolio_model.get_rolling_beta
        self.rbeta_view = lib.portfolio_view.display_rolling_beta
        self.summary = lib.portfolio_model.get_summary
        self.skew = lib.portfolio_model.get_skewness
        self.kurtosis = lib.portfolio_model.get_kurtosis
        self.volatility = lib.portfolio_model.get_volatility
        self.sharpe = lib.portfolio_model.get_sharpe_ratio
        self.sortino = lib.portfolio_model.get_sortino_ratio
        self.rsquare = lib.portfolio_model.get_r2_score
        self.maxdrawdown = lib.portfolio_model.get_maximum_drawdown_ratio
        self.gaintopain = lib.portfolio_model.get_gaintopain_ratio
        self.trackerr = lib.portfolio_model.get_tracking_error
        self.information = lib.portfolio_model.get_information_ratio
        self.tail = lib.portfolio_model.get_tail_ratio
        self.commonsense = lib.portfolio_model.get_common_sense_ratio
        self.jensens = lib.portfolio_model.get_jensens_alpha
        self.calmar = lib.portfolio_model.get_calmar_ratio
        self.kelly = lib.portfolio_model.get_kelly_criterion
        self.payoff = lib.portfolio_model.get_payoff_ratio
        self.profitfactor = lib.portfolio_model.get_profit_factor
        self.perf = lib.portfolio_model.get_performance_vs_benchmark
        self.var = lib.portfolio_model.get_var
        self.es = lib.portfolio_model.get_es
        self.om = lib.portfolio_model.get_omega


##################################################################
#                             Funds                              #
##################################################################


class Funds(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.info = lib.mutual_funds_investpy_model.get_fund_info
        self.info_view = lib.mutual_funds_investpy_view.display_fund_info
        self.overview = lib.mutual_funds_investpy_model.get_overview
        self.overview_view = lib.mutual_funds_investpy_view.display_overview
        self.search = lib.mutual_funds_investpy_model.search_funds
        self.search_view = lib.mutual_funds_investpy_view.display_search


##################################################################
#                             Forex                              #
##################################################################


class ForexOanda(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.fwd = lib.forex_fxempire_model.get_forward_rates
        self.fwd_view = lib.forex_fxempire_view.display_forward_rates
        self.summary = lib.forex_oanda_model.account_summary_request
        self.summary_view = lib.forex_oanda_view.get_account_summary
        self.cancel = lib.forex_oanda_model.cancel_pending_order_request
        self.cancel_view = lib.forex_oanda_view.cancel_pending_order
        self.close = lib.forex_oanda_model.close_trades_request
        self.close_view = lib.forex_oanda_view.close_trade
        self.order = lib.forex_oanda_model.create_order_request
        self.order_view = lib.forex_oanda_view.create_order
        self.price = lib.forex_oanda_model.fx_price_request
        self.price_view = lib.forex_oanda_view.get_fx_price
        self.calendar = lib.forex_oanda_model.get_calendar_request
        self.calendar_view = lib.forex_oanda_view.calendar
        self.candles = lib.forex_oanda_model.get_candles_dataframe
        self.candles_view = lib.forex_oanda_view.show_candles
        self.openpositions = lib.forex_oanda_model.open_positions_request
        self.openpositions_view = lib.forex_oanda_view.get_open_positions
        self.opentrades = lib.forex_oanda_model.open_trades_request
        self.opentrades_view = lib.forex_oanda_view.get_open_trades
        self.listorders = lib.forex_oanda_model.order_history_request
        self.listorders_view = lib.forex_oanda_view.list_orders
        self.orderbook = lib.forex_oanda_model.orderbook_plot_data_request
        self.orderbook_view = lib.forex_oanda_view.get_order_book
        self.pending = lib.forex_oanda_model.pending_orders_request
        self.pending_view = lib.forex_oanda_view.get_pending_orders
        self.positionbook = lib.forex_oanda_model.positionbook_plot_data_request
        self.positionbook_view = lib.forex_oanda_view.get_position_book


class Forex:
    """OpenBB SDK Forex Module"""

    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.oanda = ForexOanda()
        self.candle = lib.forex_helpers.display_candle
        self.get_currency_list = lib.forex_av_model.get_currency_list
        self.hist = lib.forex_av_model.get_historical
        self.load = lib.forex_helpers.load
        self.quote = lib.forex_av_model.get_quote
        self.quote_view = lib.forex_av_view.display_quote

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(\n"
            f"    oanda={self.oanda!r},\n"
            f"    candle={self.candle!r},\n"
            f"    get_currency_list={self.get_currency_list!r},\n"
            f"    hist={self.hist!r},\n"
            f"    load={self.load!r},\n"
            f"    quote={self.quote!r},\n"
            f"    quote_view={self.quote_view!r},\n)"
        )


def forex_quote(to_symbol: str = "USD", from_symbol: str = "EUR", source: str = "yf"):
    """Get the current quote for a given currency pair.

    Args:
        to_symbol (str, optional): The currency to convert to. Defaults to "USD".
        from_symbol (str, optional): The currency to convert from. Defaults to "EUR".
        source (str, optional): The source to get the quote from. Defaults to "yf".

    Returns:
        dict: A dictionary containing the quote information.
    """
    if source == "yf":
        return lib.forex_helpers.load(
            to_symbol,
            from_symbol,
            resolution="i",
            interval="1min",
            start_date=(datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
        )
    elif source == "oanda":
        return lib.forex_av_model.get_quote(to_symbol, from_symbol)
    else:
        raise ValueError("Source not supported.")


##################################################################
#                         Econometrics                           #
##################################################################


class Econometrics(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.clean = lib.econometrics_model.clean
        self.coint = (
            lib.econometrics_model.get_engle_granger_two_step_cointegration_test
        )
        self.coint_view = lib.econometrics_view.display_cointegration_test
        self.granger = lib.econometrics_model.get_granger_causality
        self.granger_view = lib.econometrics_view.display_granger
        self.norm = lib.econometrics_model.get_normality
        self.norm_view = lib.econometrics_view.display_norm
        self.options = lib.econometrics_model.get_options
        self.options_view = lib.econometrics_view.show_options
        self.root = lib.econometrics_model.get_root
        self.root_view = lib.econometrics_view.display_root
        self.load = lib.common_model.load
        self.bgod = lib.econometrics_regression_model.get_bgod
        self.bgod_view = lib.econometrics_regression_view.display_bgod
        self.bols = lib.econometrics_regression_model.get_bols
        self.bpag = lib.econometrics_regression_model.get_bpag
        self.bpag_view = lib.econometrics_regression_view.display_bpag
        self.comparison = lib.econometrics_regression_model.get_comparison
        self.dwat = lib.econometrics_regression_model.get_dwat
        self.dwat_view = lib.econometrics_regression_view.display_dwat
        self.fdols = lib.econometrics_regression_model.get_fdols
        self.fe = lib.econometrics_regression_model.get_fe
        self.ols = lib.econometrics_regression_model.get_ols
        self.pols = lib.econometrics_regression_model.get_pols
        self.re = lib.econometrics_regression_model.get_re
        self.get_regression_data = lib.econometrics_regression_model.get_regression_data
        self.panel = lib.econometrics_regression_model.get_regressions_results
        self.panel_view = lib.econometrics_regression_view.display_panel


##################################################################
#                           Economy                              #
##################################################################


class Economy(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.cpi = lib.economy_alphavantage_model.get_cpi
        self.cpi_view = lib.economy_alphavantage_view.display_cpi
        self.gdpc = lib.economy_alphavantage_model.get_gdp_capita
        self.gdpc_view = lib.economy_alphavantage_view.display_gdp_capita
        self.inf = lib.economy_alphavantage_model.get_inflation
        self.inf_view = lib.economy_alphavantage_view.display_inflation
        self.gdp = lib.economy_alphavantage_model.get_real_gdp
        self.gdp_view = lib.economy_alphavantage_view.display_real_gdp
        self.rtps = lib.economy_alphavantage_model.get_sector_data
        self.rtps_view = lib.economy_alphavantage_view.realtime_performance_sector
        self.tyld = lib.economy_alphavantage_model.get_treasury_yield
        self.tyld_view = lib.economy_alphavantage_view.display_treasury_yield
        self.unemp = lib.economy_alphavantage_model.get_unemployment
        self.unemp_view = lib.economy_alphavantage_view.display_unemployment
        self.macro = lib.economy_econdb_model.get_aggregated_macro_data
        self.macro_view = lib.economy_econdb_view.show_macro_data
        self.macro_parameters = lib.economy_econdb_model.get_macro_parameters
        self.macro_countries = lib.economy_econdb_model.get_macro_countries
        self.treasury = lib.economy_econdb_model.get_treasuries
        self.treasury_view = lib.economy_econdb_view.show_treasuries
        self.treasury_maturities = lib.economy_econdb_model.get_treasury_maturities
        self.future = lib.economy_finviz_model.get_futures
        self.spectrum = lib.economy_finviz_model.get_spectrum_data
        self.spectrum_view = lib.economy_finviz_view.display_spectrum
        self.valuation = lib.economy_finviz_model.get_valuation_data
        self.performance = lib.economy_finviz_model.get_performance_data
        self.performance_view = lib.economy_finviz_view.display_performance
        self.prefmap = lib.economy_finviz_model.get_performance_map
        self.fred_series = lib.economy_fred_model.get_aggregated_series_data
        self.fred_series_view = lib.economy_fred_view.display_fred_series
        self.friend_ids = lib.economy_fred_model.get_series_ids
        self.fred_notes = lib.economy_fred_model.get_series_notes
        self.fred_yeild_curve = lib.economy_fred_model.get_yield_curve
        self.fred_yeild_curve_view = lib.economy_fred_view.display_yield_curve
        self.get_events_countries = lib.economy_investingcom_model.get_events_countries
        self.events = lib.economy_investingcom_model.get_economic_calendar
        self.get_ycrv_countries = lib.economy_investingcom_model.get_ycrv_countries
        self.ycrv = lib.economy_investingcom_model.get_yieldcurve
        self.ycrv_view = lib.economy_investingcom_view.display_yieldcurve
        self.spread = lib.economy_investingcom_model.get_spread_matrix
        self.spread_view = lib.economy_investingcom_view.display_spread_matrix
        self.country_codes = lib.economy_nasdaq_model.get_country_codes
        self.bigmac = lib.economy_nasdaq_model.get_big_mac_indices
        self.bigmac_view = lib.economy_nasdaq_view.display_big_mac_index
        self.glbonds = lib.economy_wsj_model.global_bonds
        self.currencies = lib.economy_wsj_model.global_currencies
        self.overview = lib.economy_wsj_model.market_overview
        self.futures = lib.economy_wsj_model.top_commodities
        self.usbonds = lib.economy_wsj_model.us_bonds
        self.indices = lib.economy_wsj_model.us_indices
        self.index = lib.economy_yfinance_model.get_indices
        self.index_view = lib.economy_yfinance_view.show_indices
        self.available_indices = lib.economy_yfinance_model.get_available_indices
        self.search_index = lib.economy_yfinance_model.get_search_indices


##################################################################
#                             ETFs                               #
##################################################################


class ETFDiscovery(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.mover = lib.etf_discovery_wsj_model.etf_movers
        self.mover_view = lib.etf_discovery_wsj_view.show_top_mover


class ETFScreen(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.screen = lib.etf_screener_model.etf_screener
        self.view = lib.etf_screener_view.view_screener


class ETF:
    """OpenBB SDK ETF Module"""

    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.by_category = lib.etf_financedatabase_model.get_etfs_by_category
        self.by_category_view = lib.etf_financedatabase_view.display_etf_by_category
        self.ld = lib.etf_financedatabase_model.get_etfs_by_description
        self.ld_view = lib.etf_financedatabase_view.display_etf_by_description
        self.ln = lib.etf_financedatabase_model.get_etfs_by_name
        self.ln_view = lib.etf_financedatabase_view.display_etf_by_name
        self.holdings = lib.etf_stockanalysis_model.get_etf_holdings
        self.holdings_view = lib.etf_stockanalysis_view.view_holdings
        self.symbols = lib.etf_stockanalysis_model.get_all_names_symbols
        self.overview = lib.etf_stockanalysis_model.get_etf_overview
        self.overview_view = lib.etf_stockanalysis_view.view_overview
        self.by_name = lib.etf_stockanalysis_model.get_etfs_by_name
        self.by_name_view = lib.etf_stockanalysis_view.display_etf_by_name
        self.weights = lib.etf_yfinance_model.get_etf_sector_weightings
        self.weights_view = lib.etf_yfinance_view.display_etf_weightings
        self.summary = lib.etf_yfinance_model.get_etf_summary_description
        self.summary_view = lib.etf_yfinance_view.display_etf_description
        self.news = lib.common_newsapi_model.get_news
        self.news_view = lib.common_newsapi_view.display_news
        self.load = lib.stocks_helper.load
        self.candle = lib.stocks_helper.display_candle

    @property
    def disc(self):
        """ETF Discovery Module

        Attributes:
            `mover`: Scrape data for top etf movers.\n
            `mover_view`: Show top ETF movers from wsj.com\n
        """
        return ETFDiscovery()

    @property
    def scr(self):
        """ETF Screener Module

        Attributes:
            `screen`: Get ETFs based of screener preset.\n
            `view`: Display screener output\n
        """
        return ETFScreen()

    def __repr__(self):
        attrs = [
            (f"    {k}: {clean_attr_desc(v)}\n")
            for k, v in self.__dict__.items()
            if v.__doc__ and not k.startswith("_")
        ]
        return (
            f"{self.__class__.__name__}(\n"
            f"disc={self.disc!r},\n"
            f"scr={self.scr!r},\n"
            f"{''.join(attrs)})"
        )


class Stocks:
    """OpenBB SDK Stocks Module.

    Submodules:
        `ba`: Behavioral Analysis Module
        `screener`: Stocks Screener Module
        `sia`: Stocks Sentiment Analysis Module
        `qa`: Quantitative Analysis Module
        `ta`: Technical Analysis Module
    Attributes:
        `load`: Load Stock Data
        `candle`: Display Candlestick Chart
        `process_candle`: Process DataFrame into candle style plot
        `quote`: Get Ticker Quote
        `tob`: Get top of book bid and ask for ticker on exchange [CBOE.com]
        `search`: Search selected query for tickers.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.load = lib.stocks_helper.load
        self.candle = lib.stocks_helper.display_candle
        self.process_candle = lib.stocks_helper.process_candle
        self.quote = lib.stocks_views.display_quote
        self.tob = lib.stocks_cboe_model.get_top_of_book
        self.search = lib.stocks_helper.search

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(\n"
            f"    ba={self.ba!r},\n"
            f"    ca={self.ca!r},\n"
            f"    dd={self.dd!r},\n"
            f"    disc={self.disc!r},\n"
            f"    dps={self.dps!r},\n"
            f"    fa={self.fa!r},\n"
            f"    options={self.options!r},\n"
            f"    qa={self.qa!r},\n"
            f"    screener={self.screener!r},\n"
            f"    sia={self.sia!r},\n"
            f"    ta={self.ta!r},\n"
            f"    th={self.th!r},\n"
            f"    load: Loads stock OHLCV data\n"
            f"    candle: Displays candlestick chart\n"
            f"    process_candle: Processes DataFrame into candle style plot\n"
            f"    quote: Gets ticker quote\n"
            f"    tob: Gets top of book bid and ask for ticker on exchange [CBOE.com]\n"
            f"    search: Searches selected query for tickers.\n)"
        )

    @property
    def ba(self):
        """Stocks Behavioral Analysis Module

        Attributes:
            `headlines`: Gets Sentiment analysis provided by FinBrain's API [Source: finbrain]\n
            `headlines_view`: Sentiment analysis from FinBrain\n
            `mentions`: Get interest over time from google api [Source: google]\n
            `mentions_view`: Plot weekly bars of stock's interest over time. other users watchlist. [Source: Google]\n
            `queries`: Get related queries from google api [Source: google]\n
            `regions`: Get interest by region from google api [Source: google]\n
            `regions_view`: Plot bars of regions based on stock's interest. [Source: Google]\n
            `rise`: Get top rising related queries with this stock's query [Source: google]\n
            `rise_view`: Print top rising related queries with this stock's query. [Source: Google]\n
            `getdd`: Gets due diligence posts from list of subreddits [Source: reddit]\n
            `popular`: Get popular tickers from list of subreddits [Source: reddit]\n
            `popular_view`: Print latest popular tickers. [Source: Reddit]\n
            `redditsent`: Finds posts related to a specific search term in Reddit\n
            `redditsent_view`: Determine Reddit sentiment about a search term\n
            `text_sent`: Find the sentiment of a post and related comments\n
            `spac`: Get posts containing SPAC from top subreddits [Source: reddit]\n
            `spacc`: Get top tickers from r/SPACs [Source: reddit]\n
            `watchlist`: Get reddit users watchlists [Source: reddit]\n
            `watchlist_view`: Print other users watchlist. [Source: Reddit]\n
            `wsb`: Get wsb posts [Source: reddit]\n
            `hist`: Get hour-level sentiment data for the chosen symbol\n
            `hist_view`: Display historical sentiment data of a ticker,\n
            `trend`: Get sentiment data on the most talked about tickers\n
            `trend_view`: Display most talked about tickers within\n
            `bullbear`: Gets bullbear sentiment for ticker [Source: stocktwits]\n
            `bullbear_view`: \n
            `messages`: Get last messages for a given ticker [Source: stocktwits]\n
            `messages_view`: Print up to 30 of the last messages on the board. [Source: Stocktwits]\n
            `stalker`: Gets messages from given user [Source: stocktwits]\n
            `trending`: Get trending tickers from stocktwits [Source: stocktwits]\n
            `infer`: Load tweets from twitter API and analyzes using VADER\n
            `infer_view`: Infer sentiment from past n tweets\n
            `sentiment`: Get sentiments from symbol\n
            `sentiment_view`: Plot sentiments from symbol\n
        """
        return StocksBehavioralAnalysis()

    @property
    def ca(self):
        """Stocks Comparison Analysis Module

        Attributes:
            `sentiment`: Gets Sentiment analysis from several symbols provided by FinBrain's API\n
            `sentiment_view`: Display sentiment for all ticker. [Source: FinBrain]\n
            `scorr`: Get correlation sentiments across similar companies. [Source: FinBrain]\n
            `scorr_view`: Plot correlation sentiments heatmap across similar companies. [Source: FinBrain]\n
            `finnhub_peers`: Get similar companies from Finhub\n
            `screener`: Screener Overview\n
            `finviz_peers`: Get similar companies from Finviz\n
            `balance`: Get balance data. [Source: Marketwatch]\n
            `cashflow`: Get cashflow data. [Source: Marketwatch]\n
            `income`: Get income data. [Source: Marketwatch]\n
            `income_view`: Display income data. [Source: Marketwatch]\n
            `polygon_peers`: Get similar companies from Polygon\n
            `hist`: Get historical prices for all comparison stocks\n
            `hist_view`: Display historical stock prices. [Source: Yahoo Finance]\n
            `hcorr`: \n
            `hcorr_view`: \n
            `volume`: Get stock volume. [Source: Yahoo Finance]\n
            `volume_view`: Display stock volume. [Source: Yahoo Finance]\n
        """
        return StocksComparisonAnalysis()

    @property
    def dd(self):
        """Stocks Due Diligence Module

        Attributes:
            `arktrades`: Gets a dataframe of ARK trades for ticker\n
            `est`: Get analysts' estimates for a given ticker. [Source: Business Insider]\n
            `pt`: Get analysts' price targets for a given stock. [Source: Business Insider]\n
            `pt_view`: Display analysts' price targets for a given stock. [Source: Business Insider]\n
            `customer`: Print customers from ticker provided\n
            `supplier`: Get suppliers from ticker provided. [Source: CSIMarket]\n
            `rot`: Get rating over time data. [Source: Finnhub]\n
            `rot_view`: Rating over time (monthly). [Source: Finnhub]\n
            `analyst`: Get analyst data. [Source: Finviz]\n
            `news`: Get news from Finviz\n
            `rating`: Get ratings for a given ticker. [Source: Financial Modeling Prep]\n
            `sec`: Get SEC filings for a given stock ticker. [Source: Market Watch]\n
            `sec_view`: Display SEC filings for a given stock ticker. [Source: Market Watch]\n
        """
        return StocksDueDiligence()

    @property
    def disc(self):
        """Stocks Discovery Module

        Attributes:
            `arkord`: Returns ARK orders in a Dataframe\n
            `ipo`: Get IPO calendar\n
            `pipo`: Past IPOs dates. [Source: Finnhub]\n
            `fipo`: Future IPOs dates. [Source: Finnhub]\n
            `dividends`: Gets dividend calendar for given date.  Date represents Ex-Dividend Date\n
            `rtat`: Gets the top 10 retail stocks per day\n
            `news`: Gets news. [Source: SeekingAlpha]\n
            `upcoming`: Returns a DataFrame with upcoming earnings\n
            `trending`: Returns a list of trending articles\n
            `lowfloat`: Returns low float DataFrame\n
            `hotpenny`: Returns today hot penny stocks\n
            `active`: Get stocks ordered in descending order by intraday trade volume. [Source: Yahoo Finance]\n
            `asc`: Get Yahoo Finance small cap stocks with earnings growth rates better than 25%.\n
            `gainers`: Get top gainers. [Source: Yahoo Finance]\n
            `gtech`: Get technology stocks with revenue and earnings growth in excess of 25%. [Source: Yahoo Finance]\n
            `losers`: Get top losers. [Source: Yahoo Finance]\n
            `ugs`: Get stocks with earnings growth rates better than 25% and relatively low PE and PEG ratios.\n
            `ulc`: Get Yahoo Finance potentially undervalued large cap stocks.\n
        """
        return StocksDiscovery()

    @property
    def dps(self):
        """Stocks Darkpool Shorts Module

        Attributes:
            `prom`: Get all FINRA ATS data, and parse most promising tickers based on linear regression\n
            `prom_view`: Display dark pool (ATS) data of tickers with growing trades activity. [Source: FINRA]\n
            `dpotc`: Get all FINRA data associated with a ticker\n
            `dpotc_view`: Display barchart of dark pool (ATS) and OTC (Non ATS) data. [Source: FINRA]\n
            `ctb`: Get stocks with highest cost to borrow [Source: Interactive Broker]\n
            `volexch`: Gets short data for 5 exchanges [https://ftp.nyse.com] starting at 1/1/2021\n
            `volexch_view`: Display short data by exchange\n
            `psi_q`: Plots the short interest of a stock. This corresponds to the\n
            `psi_q_view`: Plots the short interest of a stock. This corresponds to the\n
            `ftd`: Display fails-to-deliver data for a given ticker. [Source: SEC]\n
            `ftd_view`: Display fails-to-deliver data for a given ticker. [Source: SEC]\n
            `hsi`: Returns a high short interest DataFrame\n
            `pos`: Get dark pool short positions. [Source: Stockgrid]\n
            `spos`: Get net short position. [Source: Stockgrid]\n
            `spos_view`: Plot net short position. [Source: Stockgrid]\n
            `sidtc`: Get short interest and days to cover. [Source: Stockgrid]\n
            `psi_sg`: Get price vs short interest volume. [Source: Stockgrid]\n
            `psi_sg_view`: Plot price vs short interest volume. [Source: Stockgrid]\n
            `shorted`: Get most shorted stock screener [Source: Yahoo Finance]\n
        """
        return StocksDarkPoolShorts()

    @property
    def options(self):
        """Stocks Options Module

        Submodules:
            `screen`: Options Screener Module
            `hedge`: Options Hedge Module

        Attributes:
            `pcr`: Gets put call ratio over last time window [Source: AlphaQuery.com]\n
            `pcr_view`: Display put call ratio [Source: AlphaQuery.com]\n
            `info`: Get info for a given ticker\n
            `info_view`: Scrapes Barchart.com for the options information\n
            `hist_ce`: Historic prices for a specific option [chartexchange]\n
            `hist_ce_view`: Return raw stock data[chartexchange]\n
            `unu`: Get unusual option activity from fdscanner.com\n
            `unu_view`: Displays the unusual options table\n
            `grhist`: Get histoical option greeks\n
            `grhist_view`: Plots historical greeks for a given option. [Source: Syncretism]\n
            `hist_tr`: \n
            `hist_tr_view`: Plot historical option prices\n
            `chains_tr`: Display option chains [Source: Tradier]"\n
            `chains_tr_view`: Display option chain\n
            `chains_yf`: Get full option chains with calculated greeks\n
            `chains_yf_view`: Display option chains for given ticker and expiration\n
            `last_price`: Makes api request for last price\n
            `option_expirations`: Get available expiration dates for given ticker\n
            `process_chains`: Function to take in the requests.get and return a DataFrame\n
            `generate_data`: Gets x values, and y values before and after premiums\n
            `closing`: Get closing prices for a given ticker\n
            `dividend`: Gets option chain from yf for given ticker and expiration\n
            `dte`: Gets days to expiration from yfinance option date\n
            `vsurf`: Gets IV surface for calls and puts for ticker\n
            `vsurf_view`: Display vol surface\n
            `vol_yf`: Plot volume\n
            `vol_yf_view`: Plot volume\n
            `voi_yf`: Plot volume and open interest\n
            `voi_yf_view`: Plot volume and open interest\n
            `option_chain`: Gets option chain from yf for given ticker and expiration\n
            `price`: Get current price for a given ticker\n
            `x_values`: Generates different price values that need to be tested\n
            `y_values`: Generates y values for corresponding x values\n
        """
        return StocksOptions()

    @property
    def qa(self):
        """Stocks Quant Analysis Module

        Attributes:
            `capm_information`: Provides information that relates to the CAPM model\n
            `fama_raw`: Gets base Fama French data to calculate risk\n
            `historical_5`: Get 5 year monthly historical performance for a ticker with dividends filtered\n
        """
        return StocksQuantitativeAnalysis()

    @property
    def screener(self):
        """Stocks Screener Module

        Attributes:
            `screener_data`: Screener data for one of the following: overview, valuation, financial, ownership, performance, technical.\n
            `screener_view`: Display screener data for one of the following: overview, valuation, financial, ownership, performance, technical.\n
            `historical`: Gets historical price of stocks that meet preset\n
            `historical_view`: View historical price of stocks that meet preset\n
        """
        return StocksScreener()

    @property
    def sia(self):
        """Stocks Sentiment Analysis Module

        Attributes:
            `filter_stocks`: Filter stocks based on country, sector, industry, market cap and exclude exchanges.\n
            `cpci`: Get number of companies per country in a specific industry (and specific market cap).\n
            `cpci_view`: Display number of companies per country in a specific industry. [Source: Finance Database]\n
            `cpcs`: Get number of companies per country in a specific sector (and specific market cap).\n
            `cpcs_view`: Display number of companies per country in a specific sector. [Source: Finance Database]\n
            `cpic`: Get number of companies per industry in a specific country (and specific market cap).\n
            `cpic_view`: Display number of companies per industry in a specific country. [Source: Finance Database]\n
            `cpis`: Get number of companies per industry in a specific sector (and specific market cap).\n
            `cpis_view`: Display number of companies per industry in a specific sector. [Source: Finance Database]\n
            `cps`: Get number of companies per sector in a specific country (and specific market cap). [Source: Finance Database]\n
            `cps_view`: Display number of companies per sector in a specific country (and market cap). [Source: Finance Database]\n
            `countries`: Get all countries in Yahoo Finance data based on sector or industry. [Source: Finance Database]\n
            `industries`: Get all industries in Yahoo Finance data based on country or sector. [Source: Finance Database]\n
            `marketcap`: Get all market cap division in Yahoo Finance data. [Source: Finance Database]\n
            `sectors`: Get all sectors in Yahoo Finance data based on country or industry. [Source: Finance Database]\n
            `stocks_data`: Get stocks data based on a list of stocks and the finance key. The function searches for the
                correct financial statement automatically. [Source: StockAnalysis]\n
        """
        return StocksSIA()

    @property
    def ta(self):
        """Stocks Technical Analysis Module

        Attributes:
            `summary`: Get technical summary report provided by FinBrain's API\n
            `view`: Get finviz image for given ticker\n
            `recom`: Get tradingview recommendation based on technical indicators\n
        """
        return StocksTechnicalAnalysis()

    @property
    def th(self):
        """Stocks Trading Hours Module

        Attributes:
            `check_if_open`: Check if market open helper function\n
            `all`: Get all exchanges.\n
            `all_view`: Display all exchanges.\n
            `closed`: Get closed exchanges.\n
            `closed_view`: Display closed exchanges.\n
            `open`: Get open exchanges.\n
            `open_view`: Display open exchanges.\n
            `exchange`: Get current exchange open hours.\n
            `exchange_view`: Display current exchange trading hours.\n
        """
        return StocksTradingHours()

    @property
    def fa(self):
        """Stocks Fundamental Analysis Module

        Attributes:
            `av_balance`: Get balance sheets for company\n
            `av_cash`: Get cash flows for company\n
            `av_cash_view`: Alpha Vantage income statement\n
            `dupont`: Get dupont ratios\n
            `earnings`: Get earnings calendar for ticker\n
            `fraud`: Get fraud ratios based on fundamentals\n
            `av_income`: Get income statements for company\n
            `av_metrics`: Get key metrics from overview\n
            `av_overview`: Get alpha vantage company overview\n
            `mgmt`: Get company managers from Business Insider\n
            `fama_coe`: Use Fama and French to get the cost of equity for a company\n
            `fama_raw`: Get Fama French data\n
            `historical_5`: Get 5 year monthly historical performance for a ticker with dividends filtered\n
            `similar_dfs`: Get dataframes for similar companies\n
            `analysis`: Save time reading SEC filings with the help of machine learning. [Source: https://eclect.us]\n
            `fmp_balance`: Get balance sheets\n
            `fmp_cash`: Get cash flow\n
            `dcf`: Get stocks dcf from FMP\n
            `enterprise`: Financial Modeling Prep ticker enterprise\n
            `growth`: Get financial statement growth\n
            `fmp_income`: Get income statements\n
            `fmp_metrics`: Get key metrics\n
            `fmp_ratios`: Get key ratios\n
            `profile`: Get ticker profile from FMP\n
            `quote`: Gets ticker quote from FMP\n
            `score`: Gets value score from fmp\n
            `data`: Get fundamental data from finviz\n
            `poly_financials`: Get ticker financial statements from polygon\n
            `poly_financials_view`: Display tickers balance sheet or income statement\n
            `cal`: Get calendar earnings for ticker symbol\n
            `divs`: Get historical dividend for ticker\n
            `yf_financials`: Get cashflow statement for company\n
            `yf_financials_view`: Display tickers balance sheet, income statement or cash-flow\n
            `hq`: Gets google map url for headquarter\n
            `info`: Gets ticker symbol info\n
            `mktcap`: Get market cap over time for ticker. [Source: Yahoo Finance]\n
            `shrs`: Get shareholders from yahoo\n
            `splits`: Get splits and reverse splits events. [Source: Yahoo Finance]\n
            `splits_view`: Display splits and reverse splits events. [Source: Yahoo Finance]\n
            `sust`: Get sustainability metrics from yahoo\n
            `website`: Gets website of company from yfinance\n
        """
        return StocksFundamentalAnalysis()


class Common:
    """OpenBB SDK Common Module.

    Submodules:
        `qa`: Quantitative Analysis Module
        `ta`: Technical Analysis Module

    Attributes:
        `news`: Get news for a given term and source. [Source: Feedparser]
        `news_view`: Display news for a given term and source. [Source: Feedparser]
    """

    def __init__(self):
        self.news = lib.common_feedparser_model.get_news
        self.news_view = lib.common_feedparser_view.display_news

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(\n"
            f"    ta={self.ta!r},\n"
            f"    qa={self.qa!r},\n)"
        )

    @property
    def ta(self):
        """Technical Analysis Module

        Attributes:
            `ad`: Calculate AD technical indicator\n
            `ad_view`: Plots AD technical indicator\n
            `adosc`: Calculate AD oscillator technical indicator\n
            `adosc_view`: Plots AD Osc Indicator\n
            `aroon`: Aroon technical indicator\n
            `aroon_view`: Plots Aroon indicator\n
            `adx`: ADX technical indicator\n
            `adx_view`: Plots ADX indicator\n
            `atr`: Average True Range\n
            `atr_view`: Plots ATR\n
            `bbands`: Calculate Bollinger Bands\n
            `bbands_view`: Plots bollinger bands\n
            `donchian`: Calculate Donchian Channels\n
            `donchian_view`: Plots donchian channels\n
            `ema`: Gets exponential moving average (EMA) for stock\n
            `fib`: Calculate Fibonacci levels\n
            `fib_view`: Plots fibonacci retracement levels\n
            `fisher`: Fisher Transform\n
            `hma`: Gets hull moving average (HMA) for stock\n
            `kc`: Keltner Channels\n
            `kc_view`: Plots Keltner Channels Indicator\n
            `ma`: Plots MA technical indicator\n
            `macd`: Moving average convergence divergence\n
            `macd_view`: Plots MACD signal\n
            `obv`: On Balance Volume\n
            `obv_view`: Plots OBV technical indicator\n
            `rsi`: Relative strength index\n
            `rsi_view`: Plots RSI Indicator\n
            `sma`: Gets simple moving average (EMA) for stock\n
            `stoch`: Stochastic oscillator\n
            `stoch_view`: Plots stochastic oscillator signal\n
            `vwap`: Gets volume weighted average price (VWAP)\n
            `vwap_view`: Plots VWMA technical indicator\n
            `wma`: Gets weighted moving average (WMA) for stock\n
            `zlma`: Gets zero-lagged exponential moving average (ZLEMA) for stock\n
        """
        return CommonTechnicalAnalysis()

    @property
    def qa(self):
        """Quantitative Analysis Module

        Attributes:
            `candle`: Display Candlestick Chart\n
            `process_candle`: Process DataFrame into candle style plot\n
            `quote`: Get Ticker Quote\n
            `tob`: Get top of book bid and ask for ticker on exchange [CBOE.com]\n
            `search`: Search selected query for tickers.\n
        """
        return CommonQuantitativeAnalysis()


class Crypto:
    """OpenBB SDK Crypto Module.

    Submodules:
        `defi`: DeFi Module
        `disc`: Discovery Module
        `dd`: Due Diligence Module
        `onchain`: On-Chain Module
        `ov`: Overview Module
        `tools`: Tools Module

    Attributes:
        `load`: Load Crypto Data
        `find`: Find similar coin by coin name, symbol or id
        `chart`: Display Chart
        `candle`: Display Candlestick Chart
    """

    def __init__(self):
        self.disc = CryptoDiscovery()
        self.onchain = CryptoOnChain()
        self.ov = CryptoOverview()
        self.tools = CryptoTools()
        self.load = lib.crypto_helpers.load
        self.find = lib.crypto_helpers.find
        self.chart = lib.crypto_helpers.plot_chart
        self.candles = lib.crypto_helpers.plot_candles

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(\n"
            f"    defi={self.defi!r},\n"
            f"    disc={self.disc!r},\n"
            f"    dd={self.dd!r},\n"
            f"    onchain={self.onchain!r},\n"
            f"    ov={self.ov!r},\n"
            f"    tools={self.tools!r},\n)"
        )

    @property
    def dd(self):
        """Crypto Due Diligence Module

        Attributes:
            `active`: Returns active addresses of a certain symbol\n
            `active_view`: Display active addresses of a certain symbol over time\n
            `basic_info`: Basic coin information [Source: CoinPaprika]\n
            `balance_view`: Get account holdings for asset. [Source: Binance]\n
            `balance`: Get account holdings for asset. [Source: Binance]\n
            `binance_available_quotes_for_each_coin`: Helper methods that for every coin available on Binance add all quote assets. [Source: Binance]\n
            `book`: Get order book for currency. [Source: Binance]\n
            `book_view`: Get order book for currency. [Source: Binance]\n
            `btcrb`: Get bitcoin price data\n
            `btcrb_view`: Displays bitcoin rainbow chart\n
            `candles`: Get candles for chosen trading pair and time interval. [Source: Coinbase]\n
            `candles_view`: Get candles for chosen trading pair and time interval. [Source: Coinbase]\n
            `cbbook`: Get orders book for chosen trading pair. [Source: Coinbase]\n
            `cbbook_view`: Displays a list of available currency pairs for trading. [Source: Coinbase]\n
            `change`: Returns 30d change of the supply held in exchange wallets of a certain symbol.\n
            `change_view`: Display 30d change of the supply held in exchange wallets.\n
            `check_valid_binance_string`: Check if symbol is in defined binance. [Source: Binance]\n
            `close`: Returns the price of a cryptocurrency\n
            `coin`: Get coin by id [Source: CoinPaprika]\n
            `events`: Get all events related to given coin like conferences, start date of futures trading etc.\n
            `events_view`: Get all events for given coin id. [Source: CoinPaprika]\n
            `ex`: Get all exchanges for given coin id. [Source: CoinPaprika]\n
            `ex_view`: Get all exchanges for given coin id. [Source: CoinPaprika]\n
            `exchanges`: Helper method to get all the exchanges supported by ccxt\n
            `trading_pairs`: Helper method that return all trading pairs on binance. Methods ause this data for input for e.g\n
            `get_binance_trading_pairs`: Returns all available pairs on Binance in DataFrame format. DataFrame has 3 columns symbol, baseAsset, quoteAsset\n
            `show_available_pairs_for_given_symbol`: Return all available quoted assets for given symbol. [Source: Binance]\n
            `stats`: Get 24 hr stats for the product. Volume is in base currency units.\n
            `stats_view`: Get 24 hr stats for the product. Volume is in base currency units.\n
            `trades`: Get last N trades for chosen trading pair. [Source: Coinbase]\n
            `trades_view`: Display last N trades for chosen trading pair. [Source: Coinbase]\n
            `trading_pair_info`: Get information about chosen trading pair. [Source: Coinbase]\n
            `oi`: Returns open interest by exchange for a certain symbol\n
            `oi_view`: Displays open interest by exchange for a certain cryptocurrency\n
            `mkt`: All markets for given coin and currency [Source: CoinPaprika]\n
            `mkt_view`: Get all markets for given coin id. [Source: CoinPaprika]\n
            `twitter`: Get twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]\n
            `twitter_view`: Get twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]\n
            `ohlc_historical`:\n
            `ps`: Get all most important ticker related information for given coin id [Source: CoinPaprika]\n
            `ps_view`: Get ticker information for single coin [Source: CoinPaprika]\n
            `news`: Get recent posts from CryptoPanic news aggregator platform. [Source: https://cryptopanic.com/]\n
            `news_view`: Display recent posts from CryptoPanic news aggregator platform.\n
            `headlines`: Gets Sentiment analysis provided by FinBrain's API [Source: finbrain]\n
            `headlines_view`: Sentiment analysis from FinBrain for Cryptocurrencies\n
            `eb`: Returns the total amount of coins held on exchange addresses in units and percentage.\n
            `eb_view`: Display total amount of coins held on exchange addresses in units and percentage.\n
            `nonzero`: Returns addresses with non-zero balance of a certain symbol\n
            `nonzero_view`: Display addresses with non-zero balance of a certain symbol\n
            `get_mt`: Returns available messari timeseries\n
            `get_mt_view`: Display messari timeseries list\n
            `fr`: Returns coin fundraising\n
            `fr_view`: Display coin fundraising\n
            `gov`: Returns coin governance\n
            `gov_view`: Display coin governance\n
            `inv`: Returns coin investors\n
            `inv_view`: Display coin investors\n
            `links`: Returns asset's links\n
            `links_view`: Display coin links\n
            `mcapdom`: Returns market dominance of a coin over time\n
            `mcapdom_view`: Display market dominance of a coin over time\n
            `mt`: Returns messari timeseries\n
            `mt_view`: Display messari timeseries\n
            `pi`: Returns coin product info\n
            `pi_view`: Display project info\n
            `rm`: Returns coin roadmap\n
            `rm_view`: Display coin roadmap\n
            `team`: Returns coin team\n
            `team_view`: Display coin team\n
            `tk`: Returns coin tokenomics\n
            `tk_view`: Display coin tokenomics\n
            `coin_market_chart`: Get prices for given coin. [Source: CoinGecko]\n
            `pr`: Fetch data to calculate potential returns of a certain coin. [Source: CoinGecko]\n
            `pr_view`: Displays potential returns of a certain coin. [Source: CoinGecko]\n
            `tokenomics`: Get tokenomics for given coin. [Source: CoinGecko]\n
            `gh`: Returns  a list of developer activity for a given coin and time interval.\n
            `gh_view`: Returns a list of github activity for a given coin and time interval.\n
        """
        return CryptoDueDiligence()

    @property
    def defi(self):
        """Crypto Defi related methods

        Attributes:
            `dpi`: Scrapes data from DeFi Pulse with all DeFi Pulse crypto protocols.\n
            `dpi_view`: Displays all DeFi Pulse crypto protocols.\n
            `swaps`: Get the last 100 swaps done on Uniswap [Source: https://thegraph.com/en/]\n
            `swaps_view`: Displays last swaps done on Uniswap\n
            `pools`: Get uniswap pools by volume. [Source: https://thegraph.com/en/]\n
            `pools_view`: Displays uniswap pools by volume.\n
            `tokens`: Get list of tokens trade-able on Uniswap DEX. [Source: https://thegraph.com/en/]\n
            `tokens_view`: Displays tokens trade-able on Uniswap DEX.\n
            `pairs`: Get lastly added trade-able pairs on Uniswap with parameters like:\n
            `pairs_view`: Displays Lastly added pairs on Uniswap DEX.\n
            `stats`: Get base statistics about Uniswap DEX. [Source: https://thegraph.com/en/]\n
            `stats_view`: Displays base statistics about Uniswap DEX. [Source: https://thegraph.com/en/]\n
            `dtvl`: Returns information about historical tvl of a defi protocol.\n
            `dtvl_view`: Displays historical TVL of different dApps\n
            `ldapps`: Returns information about listed DeFi protocols, their current TVL and changes to it in the last hour/day/week.\n
            `ldapps_view`: Display information about listed DeFi protocols, their current TVL and changes to it in\n
            `stvl`: Returns historical values of the total sum of TVLs from all listed protocols.\n
            `stvl_view`: Displays historical values of the total sum of TVLs from all listed protocols.\n
            `gdapps`: Display top dApps (in terms of TVL) grouped by chain.\n
            `gdapps_view`: Display top dApps (in terms of TVL) grouped by chain.\n
            `luna_supply`: Get supply history of the Terra ecosystem\n
            `luna_supply_view`: Display Luna circulating supply stats\n
            `newsletters`: Scrape all substack newsletters from url list.\n
            `newsletters_view`: Display DeFi related substack newsletters.\n
            `aterra`: Returns historical data of an asset in a certain terra address\n
            `aterra_view`: Displays the 30-day history of specified asset in terra address\n
            `ayr`: Displays the 30-day history of the Anchor Yield Reserve.\n
            `ayr_view`: Displays the 30-day history of the Anchor Yield Reserve.\n
            `gacc`: Get terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]\n
            `gacc_view`: Display terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]\n
            `gov_proposals`: Get terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]\n
            `gov_proposals_view`: Display terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]\n
            `sinfo`: Get staking info for provided terra account [Source: https://fcd.terra.dev/swagger]\n
            `sinfo_view`: Display staking info for provided terra account address [Source: https://fcd.terra.dev/swagger]\n
            `sratio`: Get terra blockchain staking ratio history [Source: https://fcd.terra.dev/swagger]\n
            `sratio_view`: Display terra blockchain staking ratio history [Source: https://fcd.terra.dev/v1]\n
            `sreturn`: Get terra blockchain staking returns history [Source: https://fcd.terra.dev/v1]\n
            `sreturn_view`: Display terra blockchain staking returns history [Source: https://fcd.terra.dev/swagger]\n
            `validators`: Get information about terra validators [Source: https://fcd.terra.dev/swagger]\n
            `validators_view`: Display information about terra validators [Source: https://fcd.terra.dev/swagger]\n
        """
        return CryptoDefi()


class Futures:
    """Futures related methods

    Attributes:
        `search`: Search for futures contracts.\n
        `seach_view`: Displays search results for futures contracts.\n
        `historical`: Get historical data for futures contracts.\n
        `historical_view`: Displays historical data for futures contracts.\n
        `curve`: Get futures curve data for futures contracts.\n
        `curve_view`: Displays futures curve data for futures contracts.\n
    """

    def __init__(self):
        self.search = lib.futures_yfinance_model.get_search_futures
        self.search_view = lib.futures_yfinance_view.display_search
        self.historical = lib.futures_yfinance_model.get_historical_futures
        self.historical_view = lib.futures_yfinance_view.display_historical
        self.curve = lib.futures_yfinance_model.get_curve_futures
        self.curve_view = lib.futures_yfinance_view.display_curve


class Forecasting(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        if lib.forecasting:
            self.load = lib.common_model.load
            self.show = lib.forecast_view.show_df
            self.plot = lib.forecast_view.display_plot
            self.clean = lib.forecast_model.clean
            self.combine = lib.forecast_model.combine_dfs
            self.desc = lib.forecast_model.describe_df
            self.corr = lib.forecast_model.corr_df
            self.corr_view = lib.forecast_view.display_corr
            self.season = lib.forecast_view.display_seasonality
            self.delete = lib.forecast_model.delete_column
            self.rename = lib.forecast_model.rename_column
            self.export = lib.forecast_view.export_df
            self.signal = lib.forecast_model.add_signal
            self.atr = lib.forecast_model.add_atr
            self.ema = lib.forecast_model.add_ema
            self.sto = lib.forecast_model.add_sto
            self.rsi = lib.forecast_model.add_rsi
            self.roc = lib.forecast_model.add_roc
            self.mom = lib.forecast_model.add_momentum
            self.delta = lib.forecast_model.add_delta
            self.expo = lib.forecast_expo_model.get_expo_data
            self.expo_view = lib.forecast_expo_view.display_expo_forecast
            self.theta = lib.forecast_theta_model.get_theta_data
            self.theta_view = lib.forecast_theta_view.display_theta_forecast
            self.linregr = lib.forecast_linregr_model.get_linear_regression_data
            self.linregr_view = lib.forecast_linregr_view.display_linear_regression
            self.regr = lib.forecast_regr_model.get_regression_data
            self.regr_view = lib.forecast_regr_view.display_regression
            self.rnn = lib.forecast_rnn_model.get_rnn_data
            self.rnn_view = lib.forecast_rnn_view.display_rnn_forecast
            self.brnn = lib.forecast_brnn_model.get_brnn_data
            self.brnn_view = lib.forecast_brnn_view.display_brnn_forecast
            self.nbeats = lib.forecast_nbeats_model.get_NBEATS_data
            self.nbeats_view = lib.forecast_nbeats_view.display_nbeats_forecast
            self.tcn = lib.forecast_tcn_model.get_tcn_data
            self.tcn_view = lib.forecast_tcn_view.display_tcn_forecast
            self.trans = lib.forecast_trans_model.get_trans_data
            self.trans_view = lib.forecast_trans_view.display_trans_forecast
            self.tft = lib.forecast_tft_model.get_tft_data
            self.tft_view = lib.forecast_tft_view.display_tft_forecast
            self.nhits = lib.forecast_nhits_model.get_nhits_data
            self.nhits_view = lib.forecast_nhits_view.display_nhits_forecast


class KeysModel(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.mykeys = lib.keys_model.get_keys
        self.set_keys = lib.keys_model.set_keys
        self.get_keys_info = lib.keys_model.get_keys_info
        self.av = lib.keys_model.set_av_key
        self.fmp = lib.keys_model.set_fmp_key
        self.quandl = lib.keys_model.set_quandl_key
        self.polygon = lib.keys_model.set_polygon_key
        self.fred = lib.keys_model.set_fred_key
        self.news = lib.keys_model.set_news_key
        self.tradier = lib.keys_model.set_tradier_key
        self.cmc = lib.keys_model.set_cmc_key
        self.finnhub = lib.keys_model.set_finnhub_key
        self.iex = lib.keys_model.set_iex_key
        self.reddit = lib.keys_model.set_reddit_key
        self.twitter = lib.keys_model.set_twitter_key
        self.rh = lib.keys_model.set_rh_key
        self.degiro = lib.keys_model.set_degiro_key
        self.oanda = lib.keys_model.set_oanda_key
        self.binance = lib.keys_model.set_binance_key
        self.bitquery = lib.keys_model.set_bitquery_key
        self.si = lib.keys_model.set_si_key
        self.coinbase = lib.keys_model.set_coinbase_key
        self.walert = lib.keys_model.set_walert_key
        self.glassnode = lib.keys_model.set_glassnode_key
        self.coinglass = lib.keys_model.set_coinglass_key
        self.cpanic = lib.keys_model.set_cpanic_key
        self.ethplorer = lib.keys_model.set_ethplorer_key
        self.smartstake = lib.keys_model.set_smartstake_key
        self.github = lib.keys_model.set_github_key
        self.messari = lib.keys_model.set_messari_key
        self.eodhd = lib.keys_model.set_eodhd_key
        self.santiment = lib.keys_model.set_santiment_key
        self.tokenterminal = lib.keys_model.set_tokenterminal_key
        self.shroom = lib.keys_model.set_shroom_key


class SDK:
    """OpenBB SDK.

    Modules:
        `alt`: Alternative Module
        `common`: Common Module
        `crypto`: Cryptocurrency Module
        `econometrics`: Econometrics Module
        `economy`: Economy Module
        `etf`: ETF Module
        `forex`: Forex Module
        `futures`: Futures Module
        `keys`: Keys Module
        `stocks`: Stocks Module
    """

    def __init__(self, suppress_logging: bool = False):
        self.__suppress_logging = suppress_logging
        self.__check_initialize_logging()

    def __check_initialize_logging(self):
        if not self.__suppress_logging:
            self.__initialize_logging()

    @staticmethod
    def __initialize_logging():
        cfg.LOGGING_SUB_APP = "sdk"
        setup_logging()
        log_all_settings()

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(\n    "
            f"    alt={self.alt!r},\n"
            f"    common={self.common!r},\n"
            f"    crypto={self.crypto!r},\n"
            f"    econometrics={self.econometrics!r},\n"
            f"    economy={self.economy!r},\n"
            f"    etf={self.etf!r},\n"
            f"    stocks={self.stocks!r},\n)"
        )

    def __str__(self):
        return """OpenBB SDK.

        Modules:
            `alt`: Alternative Module
            `common`: Common Module
            `crypto`: Cryptocurrency Module
            `econometrics`: Econometrics Module
            `economy`: Economy Module
            `etf`: ETF Module
            `stocks`: Stocks Module
        """

    @property
    def stocks(self):
        """OpenBB SDK Stocks Module.

        Submodules:
            `ba`: Behavioral Analysis Module
            `ca`: Comparison Analysis Module
            `dd`: Due Diligence Module
            `disc`: Discovery Module
            `dps`: Darkpool Shorts Module
            `options`: Options Module
            `qa`: Quantitative Analysis Module
            `screener`: Screener Module
            `sia`: Sentiment Analysis Module
            `ta`: Technical Analysis Module
            `th`: Trading Hours Module

        Attributes:
            `load`: Load Stock Data
            `candle`: Display Candlestick Chart
            `process_candle`: Process DataFrame into candle style plot
            `quote`: Get Ticker Quote
            `tob`: Get top of book bid and ask for ticker on exchange [CBOE.com]
            `search`: Search selected query for tickers.
        """
        return Stocks()

    @property
    def common(self):
        """OpenBB SDK Common Module.

        Submodules:
            `qa`: Quantitative Analysis Module
            `ta`: Technical Analysis Module
        """
        return Common()

    @property
    def etf(self):
        """OpenBB SDK ETF Module.

        Submodules:
            `disc`: ETF Discovery Module
            `scr`: ETF Screener Module

        Attributes:
            `etf_by_category`: Get ETFs by Category\n
            `etf_by_category_view`: Display ETFs by Category\n
            `ld`: Get ETFs by Description\n
            `ld_view`: Display ETFs by Description\n
            `ln`: Get ETFs by Name\n
            `ln_view`: Display ETFs by Name\n
            `holdings`: Get ETF Holdings\n
            `holdings_view`: Display ETF Holdings\n
            `symbols`: Get All ETF Symbols\n
            `overview`: Get ETF Overview\n
            `overview_view`: Display ETF Overview\n
            `etf_by_name`: Get ETFs by Name\n
            `etf_by_name_view`: Display ETFs by Name\n
            `weights`: Get ETF Sector Weightings\n
            `weights_view`: Display ETF Sector Weightings\n
            `summary`: Get ETF Summary Description\n
            `summary_view`: Display ETF Summary Description\n
            `news`: Get ETF News\n
            `news_view`: Display ETF News\n
        """
        return ETF()

    @property
    def futures(self):
        """OpenBB SDK Futures Module.

        Attributes:
            `search`: Search for futures contracts.\n
            `seach_view`: Displays search results for futures contracts.\n
            `historical`: Get historical data for futures contracts.\n
            `historical_view`: Displays historical data for futures contracts.\n
            `curve`: Get futures curve data for futures contracts.\n
            `curve_view`: Displays futures curve data for futures contracts.\n
        """
        return Futures()

    @property
    def forex(self):
        """OpenBB SDK Forex Module.

        Attributes:
            `search`: Search for forex pairs.\n
            `seach_view`: Displays search results for forex pairs.\n
            `historical`: Get historical data for forex pairs.\n
            `historical_view`: Displays historical data for forex pairs.\n
            `quote`: Get quote for forex pairs.\n
            `quote_view`: Displays quote for forex pairs.\n
        """
        return Forex()

    @property
    def alt(self):
        """OpenBB SDK Common Module.

        Submodules:
            `covid`: COVID-19 Module
            `oss`: Open Source Software Module
        """
        return Alternative()

    @property
    def crypto(self):
        """OpenBB SDK Crypto Module.

        Submodules:
            `defi`: DeFi Module
            `disc`: Discovery Module
            `dd`: Due Diligence Module
            `onchain`: On-Chain Module
            `ov`: Overview Module
            `tools`: Tools Module

        Attributes:
            `load`: Load Crypto Data
            `chart`: Display Chart
            `candle`: Display Candlestick Chart
        """
        return Crypto()

    @property
    def econometrics(self):
        """OpenBB SDK Econometrics Module.

        Submodules:
            `defi`: DeFi Module
            `disc`: Discovery Module
            `dd`: Due Diligence Module
            `onchain`: On-Chain Module
            `ov`: Overview Module
            `tools`: Tools Module

        Attributes:
            `clean`: Clean up NaNs from the dataset\n
            `coint`: Estimates long-run and short-run cointegration relationship for series y and x and apply\n
            `coint_view`: Estimates long-run and short-run cointegration relationship for series y and x and apply\n
            `granger`: Calculate granger tests\n
            `granger_view`: Show granger tests\n
            `norm`: The distribution of returns and generate statistics on the relation to the normal curve.\n
            `norm_view`: Determine the normality of a timeseries.\n
            `options`: Obtain columns-dataset combinations from loaded in datasets that can be used in other commands\n
            `options_view`: Plot custom data\n
            `root`: Calculate test statistics for unit roots\n
            `root_view`: Show test statistics for unit roots\n
            `load`: Load custom file into dataframe.\n
            `bgod`: Calculate test statistics for autocorrelation\n
            `bgod_view`: Show Breusch-Godfrey autocorrelation test\n
            `bols`: The between estimator is an alternative, usually less efficient estimator, can can be used to\n
            `bpag`: Calculate test statistics for heteroscedasticity\n
            `bpag_view`: Show Breusch-Pagan heteroscedasticity test\n
            `comparison`: Compare regression results between Panel Data regressions.\n
            `dwat`: Calculate test statistics for Durbing Watson autocorrelation\n
            `dwat_view`: Show Durbin-Watson autocorrelation tests\n
            `fdols`: First differencing is an alternative to using fixed effects when there might be correlation.\n
            `fe`: When effects are correlated with the regressors the RE and BE estimators are not consistent.\n
            `ols`: Performs an OLS regression on timeseries data. [Source: Statsmodels]\n
            `pols`: PooledOLS is just plain OLS that understands that various panel data structures.\n
            `re`: The random effects model is virtually identical to the pooled OLS model except that is accounts for the\n
            `get_regression_data`: This function creates a DataFrame with the required regression data as\n
            `panel`: Based on the regression type, this function decides what regression to run.\n
            `panel_view`: Show regression results.\n
        """
        return Econometrics()

    @property
    def economy(self):
        """OpenBB SDK Economy Module.

        Attributes:
            `cpi`: Get Consumer Price Index from Alpha Vantage\n
            `cpi_view`: Display US consumer price index (CPI) from AlphaVantage\n
            `gdpc`: Real GDP per Capita for United States\n
            `gdpc_view`: Display US GDP per Capita from AlphaVantage\n
            `inf`: Get historical Inflation for United States from AlphaVantage\n
            `inf_view`: Display US Inflation from AlphaVantage\n
            `gdp`: Get annual or quarterly Real GDP for US\n
            `gdp_view`: Display US GDP from AlphaVantage\n
            `rtps`: Get real-time performance sector data\n
            `rtps_view`: Display Real-Time Performance sector. [Source: AlphaVantage]\n
            `tyld`: Get historical yield for a given maturity\n
            `tyld_view`: Display historical treasury yield for given maturity\n
            `unemp`: Get historical unemployment for United States\n
            `unemp_view`: Display US unemployment AlphaVantage\n
            `macro`: This functions groups the data queried from the EconDB database [Source: EconDB]\n
            `macro_view`: Show the received macro data about a company [Source: EconDB]\n
            `macro_parameters`: This function returns the available macro parameters with detail.\n
            `macro_countries`: This function returns the available countries and respective currencies.\n
            `treasury`: Get U.S. Treasury rates [Source: EconDB]\n
            `treasury_view`: Display U.S. Treasury rates [Source: EconDB]\n
            `treasury_maturities`: Get treasury maturity options [Source: EconDB]\n
            `future`: Get futures data. [Source: Finviz]\n
            `spectrum`: Get group (sectors, industry or country) valuation/performance data. [Source: Finviz]\n
            `spectrum_view`: Display finviz spectrum in system viewer [Source: Finviz]\n
            `valuation`: Get group (sectors, industry or country) valuation data. [Source: Finviz]\n
            `performance`: Get group (sectors, industry or country) performance data. [Source: Finviz]\n
            `performance_view`: View group (sectors, industry or country) performance data. [Source: Finviz]\n
            `prefmap`: Opens Finviz map website in a browser. [Source: Finviz]\n
            `fred_series`: Get Series data. [Source: FRED]\n
            `fred_series_view`: Display (multiple) series from https://fred.stlouisfed.org. [Source: FRED]\n
            `friend_ids`: Get Series IDs. [Source: FRED]\n
            `fred_notes`: Get series notes. [Source: FRED]\n
            `fred_yeild_curve`: Gets yield curve data from FRED\n
            `fred_yeild_curve_view`: Display yield curve based on US Treasury rates for a specified date.\n
            `get_events_countries`: Get available countries for events command.\n
            `events`: Get economic calendar [Source: Investing.com]\n
            `get_ycrv_countries`: Get available countries for ycrv command.\n
            `ycrv`: Get yield curve for specified country. [Source: Investing.com]\n
            `ycrv_view`: Display yield curve for specified country. [Source: Investing.com]\n
            `spread`: Get spread matrix. [Source: Investing.com]\n
            `spread_view`: Display spread matrix. [Source: Investing.com]\n
            `country_codes`: Get available country codes for Bigmac index\n
            `bigmac`: Display Big Mac Index for given countries\n
            `bigmac_view`: Display Big Mac Index for given countries\n
            `glbonds`: Scrape data for global bonds\n
            `currencies`: Scrape data for global currencies\n
            `overview`: Scrape data for market overview\n
            `futures`: Scrape data for top commodities\n
            `usbonds`: Scrape data for us bonds\n
            `indices`: Get the top US indices\n
            `index`: Get data on selected indices over time [Source: Yahoo Finance]\n
            `index_view`: Load (and show) the selected indices over time [Source: Yahoo Finance]\n
            `available_indices`: Get available indices\n
            `search_index`: Search indices by keyword. [Source: FinanceDatabase]\n
        """
        return Economy()

    @property
    def keys(self):
        """OpenBB SDK Keys Module.

        Attributes:
            `mykeys`: Get currently set API keys.\n
            `set_keys`: Set API keys in bundle.\n
            `get_keys_info`: Get info on available APIs to use in set_keys.\n
            `av`: Set Alpha Vantage key\n
            `fmp`: Set Financial Modeling Prep key\n
            `quandl`: Set Quandl key\n
            `polygon`: Set Polygon key\n
            `fred`: Set FRED key\n
            `news`: Set News key\n
            `tradier`: Set Tradier key\n
            `cmc`: Set Coinmarketcap key\n
            `finnhub`: Set Finnhub key\n
            `iex`: Set IEX Cloud key\n
            `reddit`: Set Reddit key\n
            `twitter`: Set Twitter key\n
            `rh`: Set Robinhood key\n
            `degiro`: Set Degiro key\n
            `oanda`: Set Oanda key\n
            `binance`: Set Binance key\n
            `bitquery`: Set Bitquery key\n
            `si`: Set Sentimentinvestor key.\n
            `coinbase`: Set Coinbase key\n
            `walert`: Set Walert key\n
            `glassnode`: Set Glassnode key.\n
            `coinglass`: Set Coinglass key.\n
            `cpanic`: Set Cpanic key.\n
            `ethplorer`: Set Ethplorer key.\n
            `smartstake`: Set Smartstake key.\n
            `github`: Set GitHub key.\n
            `messari`: Set Messari key.\n
            `eodhd`: Set Eodhd key.\n
            `santiment`: Set Santiment key.\n
            `tokenterminal`: Set Token Terminal key.\n
            `shroom`: Set Shroom key\n
        """
        return KeysModel()

    @property
    def forecast(self):
        if lib.forecasting:
            return Forecasting()
        return (
            "Forecasting is not installed. Find more info at"
            "[https://github.com/OpenBB-finance/OpenBBTerminal/blob/main"
            "/openbb_terminal/README.md#installing-the-terminal]"
        )


openbb = SDK(
    suppress_logging=check_suppress_logging(suppress_dict=SUPPRESS_LOGGING_CLASSES),
)
