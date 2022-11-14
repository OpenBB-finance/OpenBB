# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.models import portfolio_sdk_model as model


class PortfolioController(model.PortfolioRoot):
    """OpenBB SDK Portfolio Module.

    Submodules:
        `metric`: Metric Module
        `po`: Portfolio Optimization Module

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

    @property
    def metric(self):
        """OpenBB SDK Portfolio Metric Submodule

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

        return model.PortfolioMetric()

    @property
    def po(self):
        """OpenBB SDK Portfolio Portfolio Optimization Submodule

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

        return model.PortfolioPortfolioOptimization()
