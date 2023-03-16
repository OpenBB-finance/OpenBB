# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.sdk_helpers import Category
import openbb_terminal.core.sdk.sdk_init as lib


class FmpRoot(Category):
    """Fmp Module

    Attributes:
        `active`: Get most active stocks\n
        `all_symbols`: Get all symbols\n
        `balance`: Get historical balance sheet data\n
        `balance_growth`: Get historical balance sheet growth\n
        `cash`: Get historical cash flow data\n
        `cash_growth`: Get historical cash flow growth\n
        `divcal`: Get company dividend calendar\n
        `dow_companies`: Get Dow Jones companies\n
        `earnings`: Get upgrades and downgrades for a company\n
        `esg`: Get ESG data from symbol\n
        `exec_comp`: Get executive compensation\n
        `ftd`: Get company ftds\n
        `gainers`: Get top gainers\n
        `income`: Get historical income statement data\n
        `income_growth`: Get historical income statement growth\n
        `industry_pe`: Get industry PE ratios\n
        `insider`: Get insider trading data\n
        `institutional`: Get institutional ownership data\n
        `institutional_holders`: Get institutional ownership data at a given quarter\n
        `key`: Get historical key metrics\n
        `key_execs`: Get key executives from company\n
        `losers`: Get top losers\n
        `market_risk_premium`: Get market risk premium\n
        `marketcap`: Get historical marketcap\n
        `news`: Get news for a company\n
        `notes`: Get company notes\n
        `peers`: Get company peers\n
        `price_targets`: Get price targets for a company\n
        `prices`: Get end of day prices for company\n
        `pt_summary`: Get price target summary for a company\n
        `ratios`: Get historical ratios\n
        `revgeo`: Get sales revenue by geography\n
        `revseg`: Get sales revenue by segment\n
        `scores`: Get stock financial scores\n
        `sector_performance`: Get sector performance\n
        `sectors_pe`: Get sectors PE ratios\n
        `senate`: Get company senate trading\n
        `sp500_companies`: Get S&P 500 companies\n
        `splits`: Get company splits\n
        `statements`: Get historical full financial statement as reported\n
        `upgradedowngrade`: Get upgrades and downgrades for a company\n
    """

    _location_path = "fmp"

    def __init__(self):
        super().__init__()
        self.active = lib.fmp_core.most_active
        self.all_symbols = lib.fmp_core.all_symbols
        self.balance = lib.fmp_core.balance
        self.balance_growth = lib.fmp_core.balance_growth
        self.cash = lib.fmp_core.cash_flow
        self.cash_growth = lib.fmp_core.cash_flow_growth
        self.divcal = lib.fmp_core.divcal
        self.dow_companies = lib.fmp_core.dow_companies
        self.earnings = lib.fmp_core.earnings
        self.esg = lib.fmp_core.esg
        self.exec_comp = lib.fmp_core.executive_compensation
        self.ftd = lib.fmp_core.ftd
        self.gainers = lib.fmp_core.gainers
        self.income = lib.fmp_core.income
        self.income_growth = lib.fmp_core.income_growth
        self.industry_pe = lib.fmp_core.industry_pe_ratios
        self.insider = lib.fmp_core.insider
        self.institutional = lib.fmp_core.institutional
        self.institutional_holders = lib.fmp_core.institutional_holders
        self.key = lib.fmp_core.key_metrics
        self.key_execs = lib.fmp_core.key_execs
        self.losers = lib.fmp_core.losers
        self.market_risk_premium = lib.fmp_core.market_risk_premium
        self.marketcap = lib.fmp_core.marketcap
        self.news = lib.fmp_core.news
        self.notes = lib.fmp_core.company_notes
        self.peers = lib.fmp_core.peers
        self.price_targets = lib.fmp_core.price_targets
        self.prices = lib.fmp_core.eod_prices
        self.pt_summary = lib.fmp_core.price_target_summary
        self.ratios = lib.fmp_core.ratios
        self.revgeo = lib.fmp_core.revgeo
        self.revseg = lib.fmp_core.revseg
        self.scores = lib.fmp_core.scores
        self.sector_performance = lib.fmp_core.sector_performance
        self.sectors_pe = lib.fmp_core.sectors_pe_ratios
        self.senate = lib.fmp_core.senate_trading
        self.sp500_companies = lib.fmp_core.sp500_companies
        self.splits = lib.fmp_core.splits
        self.statements = lib.fmp_core.full_statement
        self.upgradedowngrade = lib.fmp_core.upgrade_downgrade
