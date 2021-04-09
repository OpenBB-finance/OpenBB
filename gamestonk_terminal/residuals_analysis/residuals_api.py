""" Residuals API """
__docformat__ = "numpy"

import argparse
from typing import List
from matplotlib import pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import seaborn as sns
import scipy.stats as stats
import statsmodels.api as sm
from collections import OrderedDict
import matplotlib.gridspec as gridspec
from statsmodels.graphics.gofplots import qqplot
from statsmodels.tsa.stattools import adfuller, kpss, bds
from statsmodels.stats.diagnostic import het_arch
from scipy.stats import skewtest, kurtosistest, skew, kurtosis
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
    check_positive,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff


register_matplotlib_converters()


def fit(
    other_args: List[str],
    ticker: str,
    stock: pd.Series,
    model_name: str,
    model: pd.Series,
):
    """Plot model fitting

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    ticker : str
        Ticker of the stock
    stock : pd.Series
        Stock data
    model_name : str
        Model fitting name in use
    model : pd.Series
        Model fit data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="fit",
        description="""
            Plot model fitting
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

        plt.plot(stock)
        plt.plot(model)
        plt.title(f"{model_name} model fit on {ticker}")
        plt.xlim(stock.index[0], stock.index[-1])
        plt.xlabel("Time")
        plt.ylabel("Share Price ($)")
        plt.legend([ticker, model_name])
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")
        return


def res(
    other_args: List[str],
    ticker: str,
    stock: pd.Series,
    model_name: str,
    residuals: List[float],
):
    """Plot residuals

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    ticker : str
        Ticker of the stock
    stock : pd.Series
        Stock data
    model_name : str
        Model fitting name in use
    residuals : List[float]
        Residuals data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="res",
        description="""
            Plot residuals
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

        plt.plot(stock[1:].index, residuals)
        plt.title(f"Residuals from {model_name} model fit on {ticker}")
        plt.xlim(stock[1:].index[0], stock.index[-1])
        plt.xlabel("Time")
        plt.ylabel("Share Price ($)")
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")
        return


def hist(
    other_args: List[str],
    ticker: str,
    model_name: str,
    residuals: List[float],
):
    """Histogram and density curve

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    ticker : str
        Ticker of the stock
    model_name : str
        Model fitting name in use
    residuals : List[float]
        Residuals data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="hist",
        description="""
            Histogram and density curve
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI, constrained_layout=True)

        sns.distplot(
            residuals,
            bins=35,
            color="blue",
            hist=True,
            hist_kws={"edgecolor": "black"},
            kde=True,
            kde_kws={"color": "black", "lw": 3, "label": "KDE"},
            rug=True,
            rug_kws={"edgecolor": "orange"},
        )
        plt.title(f"Histogram with Density from {model_name} fit on {ticker}")
        plt.ylabel("Density")
        plt.xlabel("Share Price")
        plt.grid(True)

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")
        return


def plot_qqplot(
    other_args: List[str],
    ticker: str,
    model_name: str,
    residuals: List[float],
):
    """Qqplot time series against a standard normal curve

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    ticker : str
        Ticker of the stock
    model_name : str
        Model fitting name in use
    residuals : List[float]
        Residuals data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="qqplot",
        description="""
            Qqplot time series against a standard normal curve
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI, constrained_layout=True)

        qqplot(residuals, stats.distributions.norm, fit=True, line="45", ax=plt.gca())
        plt.title(f"Q-Q plot residuals from {model_name} on {ticker}")
        plt.ylabel("Sample quantiles")
        plt.xlabel("Theoretical quantiles")
        plt.grid(True)

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")
        return


def acf(
    other_args: List[str],
    ticker: str,
    model_name: str,
    residuals: List[float],
):
    """Plot (partial) auto-correlation function

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    ticker : str
        Ticker of the stock
    model_name : str
        Model fitting name in use
    residuals : List[float]
        Residuals data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="acf",
        description="""
            Plot (partial) auto-correlation function
        """,
    )
    parser.add_argument(
        "-l",
        "--lags",
        dest="lags",
        type=check_positive,
        default=40,
        help="maximum lags to display in plots",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        fig = plt.figure(
            figsize=plot_autoscale(), dpi=PLOT_DPI, constrained_layout=True
        )
        spec = gridspec.GridSpec(ncols=1, nrows=2, figure=fig)

        # Auto-correlation function for original time series
        ax_acf = fig.add_subplot(spec[0, 0])
        sm.graphics.tsa.plot_acf(residuals, lags=ns_parser.lags, ax=ax_acf)
        plt.title(
            f"Auto-Correlation function applied to Residuals from {model_name} on {ticker}"
        )
        # Partial auto-correlation function for original time series
        ax_pacf = fig.add_subplot(spec[1, 0])
        sm.graphics.tsa.plot_pacf(residuals, lags=ns_parser.lags, ax=ax_pacf)
        plt.title(
            f"Partial Auto-Correlation function applied to Residuals from {model_name} on {ticker}"
        )

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")
        return


def normality(
    other_args: List[str],
    residuals: List[float],
):
    """Normality tests

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    residuals : List[float]
        Residuals data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="normality",
        description="""
            Normality tests
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        # Kurtosis
        # Measures height and sharpness of the central peak relative to that of a standard bell curve
        k, kpval = kurtosistest(residuals)

        # Skewness
        # Measure of the asymmetry of the probability distribution of a random variable about its mean
        s, spval = skewtest(residuals)

        # Jarque-Bera goodness of fit test on sample data
        # Tests if the sample data has the skewness and kurtosis matching a normal distribution
        jb, jbpval = stats.jarque_bera(residuals)

        # Shapiro
        # The Shapiro-Wilk test tests the null hypothesis that the data was drawn from a normal distribution.
        sh, shpval = stats.shapiro(residuals)

        l_statistic = [k, s, jb, sh]
        l_pvalue = [kpval, spval, jbpval, shpval]

        print(
            pd.DataFrame(
                [l_statistic, l_pvalue],
                columns=["Kurtosis", "Skewness", "Jarque-Bera", "Shapiro-Wilk"],
                index=["Statistic", "p-value"],
            )
            .round(5)
            .to_string()
        )

        print("")
        kurtosis_val = kurtosis(residuals, fisher=True)
        print("Kurtosis value: %.4f" % kurtosis_val)
        skew_val = skew(residuals)
        print("Skewness value: %.4f" % skew_val)
        print("")

    except Exception as e:
        print(e, "\n")
        return


def goodness(
    other_args: List[str],
    residuals: List[float],
):
    """Goodness of fit tests

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    residuals : List[float]
        Residuals data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="goodness",
        description="""
            Goodness of fit tests
        """,
    )
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        # Kolmogorov-Smirnov Test goodness of fit test on sample data
        ks, kspval = stats.kstest(residuals, "norm")
        print("Kolmogorov-Smirnov Test")
        print("Statistic: %.4f" % ks)
        print("p-value: %.4f" % kspval)
        print("")

    except Exception as e:
        print(e, "\n")
        return


def arch(
    other_args: List[str],
    residuals: List[float],
):
    """Autoregressive conditional heteroscedasticity with Engle's test

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    residuals : List[float]
        Residuals data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="arch",
        description="""
            Autoregressive conditional heteroscedasticity with Engle's test
        """,
    )
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        # Engle's Test for Autoregressive Conditional Heteroscedasticity (ARCH)
        lm, lmpval, fval, fpval = het_arch(residuals)
        print("Lagrange multiplier test statistic")
        print("Statistic: %.4f" % lm)
        print("p-value: %.4f" % lmpval)
        print("")
        print("fstatistic for F test")
        print("Statistic: %.4f" % fval)
        print("p-value: %.4f" % fpval)
        print("")

    except Exception as e:
        print(e, "\n")
        return


def unitroot(
    other_args: List[str],
    residuals: List[float],
):
    """Unit root test / stationarity (ADF, KPSS)

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    residuals : List[float]
        Residuals data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="arch",
        description="""
            Unit root test / stationarity (ADF, KPSS)
        """,
    )
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        # The Augmented Dickey-Fuller test
        # Used to test for a unit root in a univariate process in the presence of serial correlation.
        # regression{‘c’,’ct’,’ctt’,’nc’} 'c' - Constant and 't'-trend order to include in regression
        # Note: 'ct' - The data is stationary around a trend
        result = adfuller(residuals, regression="c")
        print("Augmented Dickey Fuller Test")
        print("ADF Statistic: %.4f" % result[0])
        print("p-value: %.4f" % result[1])
        print("Used lags: %d" % result[2])
        print("Num obs: %d" % result[3])
        print("Critical Values:")
        d = OrderedDict(sorted(result[4].items(), key=lambda t: t[1]))
        for key, value in d.items():
            print(f"\t{key}: {value:.3f}")
        print("")

        # Kwiatkowski-Phillips-Schmidt-Shin test
        # Test for level or trend stationarity
        # Note: regressionstr{‘c’, ‘ct’}
        # regressionstr{‘c’, ‘ct’} where:
        # ‘c’  : The data is stationary around a constant (default).
        # ‘ct’ : The data is stationary around a trend.
        # lags{None, ‘auto’, ‘legacy’}
        # see: https://www.statsmodels.org/dev/generated/statsmodels.tsa.stattools.kpss.html
        print("Kwiatkowski-Phillips-Schmidt-Shin Test")
        result = kpss(residuals, regression="c", nlags="auto")
        print("KPSS Statistic: %.4f" % result[0])
        print("Critical Values:")
        d = OrderedDict(sorted(result[3].items(), key=lambda t: t[1], reverse=True))
        for key, value in d.items():
            print(f"\t{key}: {value:.3f}")
        print("")

    except Exception as e:
        print(e, "\n")
        return


def independence(
    other_args: List[str],
    residuals: List[float],
):
    """Tests independent and identically distributed (i.i.d.) time series (BDS)

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    residuals : List[float]
        Residuals data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="independence",
        description="""
            Tests independent and identically distributed (i.i.d.) time series (BDS)
        """,
    )
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        result = bds(residuals, max_dim=6)
        print("BDS Test")
        print(f"Dim 2: z-static {result[0][0]:.4f} Prob {result[1][0]:.4f}")
        print(f"Dim 3: z-static {result[0][1]:.4f} Prob {result[1][1]:.4f}")
        print(f"Dim 4: z-static {result[0][2]:.4f} Prob {result[1][2]:.4f}")
        print(f"Dim 5: z-static {result[0][3]:.4f} Prob {result[1][3]:.4f}")
        print(f"Dim 6: z-static {result[0][4]:.4f} Prob {result[1][4]:.4f}")

        print("")

    except Exception as e:
        print(e, "\n")
        return
