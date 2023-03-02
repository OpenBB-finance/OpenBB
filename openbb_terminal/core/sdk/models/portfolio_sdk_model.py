# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.sdk_helpers import Category
import openbb_terminal.core.sdk.sdk_init as lib


class PortfolioRoot(Category):
    """Portfolio Module

    Attributes:
        `bench`: Load benchmark into portfolio\n
        `distr`: Display daily returns\n
        `distr_chart`: Display daily returns\n
        `dret`: Get daily returns\n
        `dret_chart`: Display daily returns\n
        `es`: Get portfolio expected shortfall\n
        `holdp`: Get holdings of assets (in percentage)\n
        `holdp_chart`: Display holdings of assets (in percentage)\n
        `holdv`: Get holdings of assets (absolute value)\n
        `holdv_chart`: Display holdings of assets (absolute value)\n
        `load`: Get PortfolioEngine object\n
        `maxdd`: Calculate the drawdown (MDD) of historical series.  Note that the calculation is done\n
        `maxdd_chart`: Display maximum drawdown curve\n
        `mret`: Get monthly returns\n
        `mret_chart`: Display monthly returns\n
        `om`: Get omega ratio\n
        `om_chart`: Display omega ratio\n
        `perf`: Get portfolio performance vs the benchmark\n
        `rbeta`: Get rolling beta using portfolio and benchmark returns\n
        `rbeta_chart`: Display rolling beta\n
        `rsharpe`: Get rolling sharpe ratio\n
        `rsharpe_chart`: Display rolling sharpe\n
        `rsort`: Get rolling sortino\n
        `rsort_chart`: Display rolling sortino\n
        `rvol`: Get rolling volatility\n
        `rvol_chart`: Display rolling volatility\n
        `show`: Get portfolio transactions\n
        `summary`: Get portfolio and benchmark returns summary\n
        `var`: Get portfolio VaR\n
        `yret`: Get yearly returns\n
        `yret_chart`: Display yearly returns\n
    """

    _location_path = "portfolio"

    def __init__(self):
        super().__init__()
        self.bench = lib.portfolio_model.set_benchmark
        self.distr = lib.portfolio_model.get_distribution_returns
        self.distr_chart = lib.portfolio_view.display_distribution_returns
        self.dret = lib.portfolio_model.get_daily_returns
        self.dret_chart = lib.portfolio_view.display_daily_returns
        self.es = lib.portfolio_model.get_es
        self.holdp = lib.portfolio_model.get_holdings_percentage
        self.holdp_chart = lib.portfolio_view.display_holdings_percentage
        self.holdv = lib.portfolio_model.get_holdings_value
        self.holdv_chart = lib.portfolio_view.display_holdings_value
        self.load = lib.portfolio_model.generate_portfolio
        self.maxdd = lib.portfolio_model.get_maximum_drawdown
        self.maxdd_chart = lib.portfolio_view.display_maximum_drawdown
        self.mret = lib.portfolio_model.get_monthly_returns
        self.mret_chart = lib.portfolio_view.display_monthly_returns
        self.om = lib.portfolio_model.get_omega
        self.om_chart = lib.portfolio_view.display_omega
        self.perf = lib.portfolio_model.get_performance_vs_benchmark
        self.rbeta = lib.portfolio_model.get_rolling_beta
        self.rbeta_chart = lib.portfolio_view.display_rolling_beta
        self.rsharpe = lib.portfolio_model.get_rolling_sharpe
        self.rsharpe_chart = lib.portfolio_view.display_rolling_sharpe
        self.rsort = lib.portfolio_model.get_rolling_sortino
        self.rsort_chart = lib.portfolio_view.display_rolling_sortino
        self.rvol = lib.portfolio_model.get_rolling_volatility
        self.rvol_chart = lib.portfolio_view.display_rolling_volatility
        self.show = lib.portfolio_model.get_transactions
        self.summary = lib.portfolio_model.get_summary
        self.var = lib.portfolio_model.get_var
        self.yret = lib.portfolio_model.get_yearly_returns
        self.yret_chart = lib.portfolio_view.display_yearly_returns


class PortfolioAlloc(Category):
    """Alloc Module.

    Attributes:
        `assets`: Display portfolio asset allocation compared to the benchmark\n
        `countries`: Display portfolio country allocation compared to the benchmark\n
        `regions`: Display portfolio region allocation compared to the benchmark\n
        `sectors`: Display portfolio sector allocation compared to the benchmark\n
    """

    _location_path = "portfolio.alloc"

    def __init__(self):
        super().__init__()
        self.assets = lib.portfolio_model.get_assets_allocation
        self.countries = lib.portfolio_model.get_countries_allocation
        self.regions = lib.portfolio_model.get_regions_allocation
        self.sectors = lib.portfolio_model.get_sectors_allocation


class PortfolioMetric(Category):
    """Metric Module.

    Attributes:
        `calmar`: Get calmar ratio\n
        `commonsense`: Get common sense ratio\n
        `gaintopain`: Get Pain-to-Gain ratio based on historical data\n
        `information`: Get information ratio\n
        `jensens`: Get jensen's alpha\n
        `kelly`: Get kelly criterion\n
        `kurtosis`: Get kurtosis for portfolio and benchmark selected\n
        `maxdrawdown`: Get maximum drawdown ratio for portfolio and benchmark selected\n
        `payoff`: Get payoff ratio\n
        `profitfactor`: Get profit factor\n
        `rsquare`: Get R2 Score for portfolio and benchmark selected\n
        `sharpe`: Get sharpe ratio for portfolio and benchmark selected\n
        `skew`: Get skewness for portfolio and benchmark selected\n
        `sortino`: Get sortino ratio for portfolio and benchmark selected\n
        `tail`: Get tail ratio\n
        `trackerr`: Get tracking error\n
        `volatility`: Get volatility for portfolio and benchmark selected\n
    """

    _location_path = "portfolio.metric"

    def __init__(self):
        super().__init__()
        self.calmar = lib.portfolio_model.get_calmar_ratio
        self.commonsense = lib.portfolio_model.get_common_sense_ratio
        self.gaintopain = lib.portfolio_model.get_gaintopain_ratio
        self.information = lib.portfolio_model.get_information_ratio
        self.jensens = lib.portfolio_model.get_jensens_alpha
        self.kelly = lib.portfolio_model.get_kelly_criterion
        self.kurtosis = lib.portfolio_model.get_kurtosis
        self.maxdrawdown = lib.portfolio_model.get_maximum_drawdown_ratio
        self.payoff = lib.portfolio_model.get_payoff_ratio
        self.profitfactor = lib.portfolio_model.get_profit_factor
        self.rsquare = lib.portfolio_model.get_r2_score
        self.sharpe = lib.portfolio_model.get_sharpe_ratio
        self.skew = lib.portfolio_model.get_skewness
        self.sortino = lib.portfolio_model.get_sortino_ratio
        self.tail = lib.portfolio_model.get_tail_ratio
        self.trackerr = lib.portfolio_model.get_tracking_error
        self.volatility = lib.portfolio_model.get_volatility


class PortfolioPortfolioOptimization(Category):
    """Portfolio Optimization Module.

    Attributes:
        `blacklitterman`: Optimize decorrelation weights\n
        `ef`: Get Efficient Frontier\n
        `ef_chart`: Display efficient frontier\n
        `file`: Load portfolio optimization engine from file\n
        `herc`: Optimize with Hierarchical Equal Risk Contribution (HERC) method.\n
        `hrp`: Optimize with Hierarchical Risk Parity\n
        `load`: Load portfolio optimization engine\n
        `load_bl_views`: Load a Excel file with views for Black Litterman model.\n
        `maxdecorr`: Optimize decorrelation weights\n
        `maxdiv`: Optimize diversification weights\n
        `maxret`: Optimize maximum return weights\n
        `maxsharpe`: Optimize Sharpe ratio weights\n
        `maxutil`: Optimize maximum utility weights\n
        `minrisk`: Optimize minimum risk weights\n
        `nco`: Optimize with Non-Convex Optimization (NCO) model.\n
        `plot`: Display efficient frontier\n
        `plot_chart`: Display efficient frontier\n
        `relriskparity`: Optimize with Relaxed Risk Parity using the least squares approach\n
        `riskparity`: Optimize with Risk Parity using the risk budgeting approach\n
        `show`: Show portfolio optimization results\n
    """

    _location_path = "portfolio.po"

    def __init__(self):
        super().__init__()

        if not lib.OPTIMIZATION_TOOLKIT_ENABLED:
            # pylint: disable=C0415
            from openbb_terminal.rich_config import console

            console.print(lib.OPTIMIZATION_TOOLKIT_WARNING)

        if lib.OPTIMIZATION_TOOLKIT_ENABLED:
            self.blacklitterman = lib.portfolio_optimization_po_model.get_blacklitterman
            self.ef = lib.portfolio_optimization_po_model.get_ef
            self.ef_chart = lib.portfolio_optimization_po_view.display_ef
            self.file = lib.portfolio_optimization_po_model.load_parameters_file
            self.herc = lib.portfolio_optimization_po_model.get_herc
            self.hrp = lib.portfolio_optimization_po_model.get_hrp
            self.load = lib.portfolio_optimization_po_model.generate_portfolio
            self.load_bl_views = lib.portfolio_optimization_excel_model.load_bl_views
            self.maxdecorr = lib.portfolio_optimization_po_model.get_maxdecorr
            self.maxdiv = lib.portfolio_optimization_po_model.get_maxdiv
            self.maxret = lib.portfolio_optimization_po_model.get_maxret
            self.maxsharpe = lib.portfolio_optimization_po_model.get_maxsharpe
            self.maxutil = lib.portfolio_optimization_po_model.get_maxutil
            self.minrisk = lib.portfolio_optimization_po_model.get_minrisk
            self.nco = lib.portfolio_optimization_po_model.get_nco
            self.plot = lib.portfolio_optimization_po_view.display_plot
            self.plot_chart = lib.portfolio_optimization_po_view.display_plot
            self.relriskparity = lib.portfolio_optimization_po_model.get_relriskparity
            self.riskparity = lib.portfolio_optimization_po_model.get_riskparity
            self.show = lib.portfolio_optimization_po_model.show
