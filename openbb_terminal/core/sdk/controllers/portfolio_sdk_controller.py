# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.models import portfolio_sdk_model as model


class PortfolioController(model.PortfolioRoot):
    """Portfolio Module.

    Submodules:
        `alloc`: Alloc Module
        `metric`: Metric Module
        `po`: Portfolio Optimization Module

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

    @property
    def alloc(self):
        """Portfolio Alloc Submodule

        Attributes:
            `assets`: Display portfolio asset allocation compared to the benchmark\n
            `countries`: Display portfolio country allocation compared to the benchmark\n
            `regions`: Display portfolio region allocation compared to the benchmark\n
            `sectors`: Display portfolio sector allocation compared to the benchmark\n
        """

        return model.PortfolioAlloc()

    @property
    def metric(self):
        """Portfolio Metric Submodule

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

        return model.PortfolioMetric()

    @property
    def po(self):
        """Portfolio Portfolio Optimization Submodule

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

        return model.PortfolioPortfolioOptimization()
