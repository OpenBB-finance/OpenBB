# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.sdk_helpers import Category
import openbb_terminal.sdk_core.sdk_init as lib


class PortfolioRoot(Category):
    """OpenBB SDK Portfolio Module

    Attributes:
        `calmar`: Get calmar ratio\n
        `commonsense`: Get common sense ratio\n
        `distr`: Display daily returns\n
        `distr_view`: Display daily returns\n
        `dret`: Get daily returns\n
        `dret_view`: Display daily returns\n
        `es`: Get portfolio expected shortfall\n
        `gaintopain`: Get Pain-to-Gain ratio based on historical data\n
        `holdp`: Get holdings of assets (in percentage)\n
        `holdp_view`: Display holdings of assets (in percentage)\n
        `holdv`: Get holdings of assets (absolute value)\n
        `holdv_view`: Display holdings of assets (absolute value)\n
        `information`: Get information ratio\n
        `jensens`: Get jensen's alpha\n
        `kelly`: Gets kelly criterion\n
        `kurtosis`: Class method that retrieves kurtosis for portfolio and benchmark selected\n
        `maxdd`: Calculate the drawdown (MDD) of historical series.  Note that the calculation is done\n
        `maxdd_view`: Display maximum drawdown curve\n
        `mret`: Get monthly returns\n
        `mret_view`: Display monthly returns\n
        `om`: Get omega ratio\n
        `om_view`: Display omega ratio\n
        `payoff`: Gets payoff ratio\n
        `perf`: Get portfolio performance vs the benchmark\n
        `rbeta`: Get rolling beta using portfolio and benchmark returns\n
        `rbeta_view`: Display rolling beta\n
        `rsharpe`: Get rolling sharpe ratio\n
        `rsharpe_view`: Display rolling sharpe\n
        `rsort`: Get rolling sortino\n
        `rsort_view`: Display rolling sortino\n
        `rvol`: Get rolling volatility\n
        `rvol_view`: Display rolling volatility\n
        `summary`: Get summary portfolio and benchmark returns\n
        `var`: Get portfolio VaR\n
        `yret`: Get yearly returns\n
        `yret_view`: Display yearly returns\n
    """

    def __init__(self):
        super().__init__()
        self.calmar = lib.portfolio_model.get_calmar_ratio
        self.commonsense = lib.portfolio_model.get_common_sense_ratio
        self.distr = lib.portfolio_model.get_distribution_returns
        self.distr_view = lib.portfolio_view.display_distribution_returns
        self.dret = lib.portfolio_model.get_daily_returns
        self.dret_view = lib.portfolio_view.display_daily_returns
        self.es = lib.portfolio_model.get_es
        self.gaintopain = lib.portfolio_model.get_gaintopain_ratio
        self.holdp = lib.portfolio_model.get_holdings_percentage
        self.holdp_view = lib.portfolio_view.display_holdings_percentage
        self.holdv = lib.portfolio_model.get_holdings_value
        self.holdv_view = lib.portfolio_view.display_holdings_value
        self.information = lib.portfolio_model.get_information_ratio
        self.jensens = lib.portfolio_model.get_jensens_alpha
        self.kelly = lib.portfolio_model.get_kelly_criterion
        self.kurtosis = lib.portfolio_model.get_kurtosis
        self.maxdd = lib.portfolio_model.get_maximum_drawdown
        self.maxdd_view = lib.portfolio_view.display_maximum_drawdown
        self.mret = lib.portfolio_model.get_monthly_returns
        self.mret_view = lib.portfolio_view.display_monthly_returns
        self.om = lib.portfolio_model.get_omega
        self.om_view = lib.portfolio_view.display_omega
        self.payoff = lib.portfolio_model.get_payoff_ratio
        self.perf = lib.portfolio_model.get_performance_vs_benchmark
        self.rbeta = lib.portfolio_model.get_rolling_beta
        self.rbeta_view = lib.portfolio_view.display_rolling_beta
        self.rsharpe = lib.portfolio_model.get_rolling_sharpe
        self.rsharpe_view = lib.portfolio_view.display_rolling_sharpe
        self.rsort = lib.portfolio_model.get_rolling_sortino
        self.rsort_view = lib.portfolio_view.display_rolling_sortino
        self.rvol = lib.portfolio_model.get_rolling_volatility
        self.rvol_view = lib.portfolio_view.display_rolling_volatility
        self.summary = lib.portfolio_model.get_summary
        self.var = lib.portfolio_model.get_var
        self.yret = lib.portfolio_model.get_yearly_returns
        self.yret_view = lib.portfolio_view.display_yearly_returns


class PortfolioMetric(Category):
    """OpenBB SDK Metric Module.

    Attributes:
        `calmar`: Get calmar ratio\n
        `commonsense`: Get common sense ratio\n
        `gaintopain`: Get Pain-to-Gain ratio based on historical data\n
        `information`: Get information ratio\n
        `jensens`: Get jensen's alpha\n
        `kelly`: Gets kelly criterion\n
        `kurtosis`: Class method that retrieves kurtosis for portfolio and benchmark selected\n
        `maxdrawdown`: Class method that retrieves maximum drawdown ratio for portfolio and benchmark selected\n
        `payoff`: Gets payoff ratio\n
        `profitfactor`: Gets profit factor\n
        `rsquare`: Class method that retrieves R2 Score for portfolio and benchmark selected\n
        `sharpe`: Class method that retrieves sharpe ratio for portfolio and benchmark selected\n
        `skew`: Class method that retrieves skewness for portfolio and benchmark selected\n
        `sortino`: Class method that retrieves sortino ratio for portfolio and benchmark selected\n
        `tail`: Get tail ratio\n
        `trackerr`: Get tracking error\n
        `volatility`: Class method that retrieves volatility for portfolio and benchmark selected\n
    """

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
    """OpenBB SDK Portfolio Optimization Module.

    Attributes:
        `blacklitterman`: Builds a maximal diversification portfolio\n
        `blacklitterman_view`: Builds a black litterman portfolio\n
        `ef`: Get efficient frontier\n
        `ef_view`: Display efficient frontier\n
        `equal`: Equally weighted portfolio, where weight = 1/# of symbols\n
        `get_properties`: Get properties to use on property optimization.\n
        `hcp`: Builds hierarchical clustering based portfolios\n
        `hcp_view`: Builds a hierarchical clustering portfolio\n
        `herc`: Builds a hierarchical risk parity portfolio\n
        `herc_view`: Builds a hierarchical equal risk contribution portfolio\n
        `hrp`: Builds a hierarchical risk parity portfolio\n
        `hrp_view`: Builds a hierarchical risk parity portfolio\n
        `load`: Load in the Excel file to determine the allocation that needs to be set.\n
        `load_bls_view`: Load a Excel file with views for Black Litterman model.\n
        `maxdecorr`: Builds a maximal decorrelation portfolio\n
        `maxdecorr_view`: Builds a maximal decorrelation portfolio\n
        `maxdiv`: Builds a maximal diversification portfolio\n
        `maxdiv_view`: Builds a maximal diversification portfolio\n
        `maxret`: Builds a maximal return/risk ratio portfolio\n
        `maxret_view`: Builds a maximal return portfolio\n
        `maxsharpe`: Builds a maximal return/risk ratio portfolio\n
        `maxsharpe_view`: Builds a maximal return/risk ratio portfolio\n
        `maxutil`: Builds a maximal return/risk ratio portfolio\n
        `maxutil_view`: Builds a maximal risk averse utility portfolio\n
        `meanrisk`: Builds a mean risk optimal portfolio\n
        `meanrisk_view`: Builds a mean risk optimal portfolio\n
        `minrisk`: Builds a maximal return/risk ratio portfolio\n
        `minrisk_view`: Builds a minimum risk portfolio\n
        `nco`: Builds a hierarchical risk parity portfolio\n
        `nco_view`: Builds a hierarchical equal risk contribution portfolio\n
        `plot`: Plot additional charts\n
        `plot_view`: Plot additional charts\n
        `property`: Calculate portfolio weights based on selected property\n
        `property_view`: Builds a portfolio weighted by selected property\n
        `relriskparity`: Builds a relaxed risk parity portfolio using the least squares approach\n
        `relriskparity_view`: Builds a relaxed risk parity portfolio using the least squares approach\n
        `riskparity`: Builds a risk parity portfolio using the risk budgeting approach\n
        `riskparity_view`: Builds a risk parity portfolio using the risk budgeting approach\n
    """

    def __init__(self):
        super().__init__()
        self.blacklitterman = (
            lib.portfolio_optimization_optimizer_model.get_black_litterman_portfolio
        )
        self.blacklitterman_view = (
            lib.portfolio_optimization_optimizer_view.display_black_litterman
        )
        self.ef = lib.portfolio_optimization_optimizer_model.get_ef
        self.ef_view = lib.portfolio_optimization_optimizer_view.display_ef
        self.equal = lib.portfolio_optimization_optimizer_model.get_equal_weights
        self.get_properties = lib.portfolio_optimization_optimizer_model.get_properties
        self.hcp = lib.portfolio_optimization_optimizer_model.get_hcp_portfolio
        self.hcp_view = lib.portfolio_optimization_optimizer_view.display_hcp
        self.herc = lib.portfolio_optimization_optimizer_model.get_herc
        self.herc_view = lib.portfolio_optimization_optimizer_view.display_herc
        self.hrp = lib.portfolio_optimization_optimizer_model.get_hrp
        self.hrp_view = lib.portfolio_optimization_optimizer_view.display_hrp
        self.load = lib.portfolio_optimization_excel_model.load_allocation
        self.load_bls_view = lib.portfolio_optimization_excel_model.load_bl_views
        self.maxdecorr = (
            lib.portfolio_optimization_optimizer_model.get_max_decorrelation_portfolio
        )
        self.maxdecorr_view = (
            lib.portfolio_optimization_optimizer_view.display_max_decorr
        )
        self.maxdiv = (
            lib.portfolio_optimization_optimizer_model.get_max_diversification_portfolio
        )
        self.maxdiv_view = lib.portfolio_optimization_optimizer_view.display_max_div
        self.maxret = lib.portfolio_optimization_optimizer_model.get_max_ret
        self.maxret_view = lib.portfolio_optimization_optimizer_view.display_max_ret
        self.maxsharpe = lib.portfolio_optimization_optimizer_model.get_max_sharpe
        self.maxsharpe_view = (
            lib.portfolio_optimization_optimizer_view.display_max_sharpe
        )
        self.maxutil = lib.portfolio_optimization_optimizer_model.get_max_util
        self.maxutil_view = lib.portfolio_optimization_optimizer_view.display_max_util
        self.meanrisk = (
            lib.portfolio_optimization_optimizer_model.get_mean_risk_portfolio
        )
        self.meanrisk_view = lib.portfolio_optimization_optimizer_view.display_mean_risk
        self.minrisk = lib.portfolio_optimization_optimizer_model.get_min_risk
        self.minrisk_view = lib.portfolio_optimization_optimizer_view.display_min_risk
        self.nco = lib.portfolio_optimization_optimizer_model.get_nco
        self.nco_view = lib.portfolio_optimization_optimizer_view.display_nco
        self.plot = lib.portfolio_optimization_optimizer_view.additional_plots
        self.plot_view = lib.portfolio_optimization_optimizer_view.additional_plots
        self.property = lib.portfolio_optimization_optimizer_model.get_property_weights
        self.property_view = (
            lib.portfolio_optimization_optimizer_view.display_property_weighting
        )
        self.relriskparity = (
            lib.portfolio_optimization_optimizer_model.get_rel_risk_parity_portfolio
        )
        self.relriskparity_view = (
            lib.portfolio_optimization_optimizer_view.display_rel_risk_parity
        )
        self.riskparity = (
            lib.portfolio_optimization_optimizer_model.get_risk_parity_portfolio
        )
        self.riskparity_view = (
            lib.portfolio_optimization_optimizer_view.display_risk_parity
        )
