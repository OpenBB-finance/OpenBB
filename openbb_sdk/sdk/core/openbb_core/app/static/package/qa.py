### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Union

import openbb_provider
import openbb_qa.qa_models
import pandas
import pydantic
import pydantic.types
from pydantic import validate_arguments

import openbb_core.app.model.results.empty
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs


class CLASS_qa(Container):
    """/qa
    acf
    beta
    bw
    capm
    cdf
    cusum
    decompose
    es
    hist
    kurtosis
    line
    normality
    om
    pick
    qqplot
    quantile
    raw
    rolling
    sh
    skew
    so
    spread
    summary
    unitroot
    var
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate_arguments
    def acf(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Autocorrelation Function."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/acf",
            **inputs,
        )

    @validate_arguments
    def beta(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Beta."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/beta",
            **inputs,
        )

    @validate_arguments
    def bw(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Bandwidth."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/bw",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def capm(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        target: str,
        chart: bool = False,
    ) -> OBBject[openbb_qa.qa_models.CAPMModel]:
        """Capital Asset Pricing Model."""

        inputs = filter_inputs(
            data=data,
            target=target,
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/capm",
            **inputs,
        )

    @validate_arguments
    def cdf(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Cumulative Distribution Function."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/cdf",
            **inputs,
        )

    @validate_arguments
    def cusum(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Cumulative Sum."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/cusum",
            **inputs,
        )

    @validate_arguments
    def decompose(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Decompose."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/decompose",
            **inputs,
        )

    @validate_arguments
    def es(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Expected Shortfall."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/es",
            **inputs,
        )

    @validate_arguments
    def hist(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Histogram."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/hist",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def kurtosis(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        target: str,
        window: pydantic.types.PositiveInt,
        chart: bool = False,
    ) -> OBBject[List]:
        """Kurtosis.

        Parameters
        ----------
        data : List[Data]
            Time series data.
        target : str
            Target column name.
        window : PositiveInt
            Window size.

        Returns
        -------
        OBBject[List[Data]]
            Kurtosis.
        """

        inputs = filter_inputs(
            data=data,
            target=target,
            window=window,
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/kurtosis",
            **inputs,
        )

    @validate_arguments
    def line(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Line."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/line",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def normality(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        target: str,
        chart: bool = False,
    ) -> OBBject[openbb_qa.qa_models.NormalityModel]:
        """
        Normality Statistics.

        - **Kurtosis**: whether the kurtosis of a sample differs from the normal distribution.
        - **Skewness**: whether the skewness of a sample differs from the normal distribution.
        - **Jarque-Bera**: whether the sample data has the skewness and kurtosis matching a normal distribution.
        - **Shapiro-Wilk**: whether a random sample comes from a normal distribution.
        - **Kolmogorov-Smirnov**: whether two underlying one-dimensional probability distributions differ.

        Parameters
        ----------
        data : List[Data]
            Time series data.
        target : str
            Target column name.

        Returns
        -------
        OBBject[NormalityModel]
            Normality tests summary. See qa_models.NormalityModel for details.
        """

        inputs = filter_inputs(
            data=data,
            target=target,
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/normality",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def om(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        target: str,
        threshold_start: float = 0.0,
        threshold_end: float = 1.5,
        chart: bool = False,
    ) -> OBBject[List]:
        """Omega Ratio.

        Parameters
        ----------
        data : List[Data]
            Time series data.
        target : str
            Target column name.
        threshold_start : float, optional
            Start threshold, by default 0.0
        threshold_end : float, optional
            End threshold, by default 1.5

        Returns
        -------
        OBBject[List[OmegaModel]]
            Omega ratios.
        """

        inputs = filter_inputs(
            data=data,
            target=target,
            threshold_start=threshold_start,
            threshold_end=threshold_end,
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/om",
            **inputs,
        )

    @validate_arguments
    def pick(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Pick."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/pick",
            **inputs,
        )

    @validate_arguments
    def qqplot(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """QQ Plot."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/qqplot",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def quantile(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        target: str,
        window: pydantic.types.PositiveInt,
        quantile_pct: pydantic.types.NonNegativeFloat = 0.5,
        chart: bool = False,
    ) -> OBBject[List]:
        """Quantile."""

        inputs = filter_inputs(
            data=data,
            target=target,
            window=window,
            quantile_pct=quantile_pct,
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/quantile",
            **inputs,
        )

    @validate_arguments
    def raw(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Raw."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/raw",
            **inputs,
        )

    @validate_arguments
    def rolling(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Rolling."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/rolling",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def sh(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        target: str,
        rfr: float = 0.0,
        window: pydantic.types.PositiveInt = 252,
        chart: bool = False,
    ) -> OBBject[List]:
        """Sharpe Ratio.

        Parameters
        ----------
        data : List[Data]
            Time series data.
        target : str
            Target column name.
        rfr : float, optional
            Risk-free rate, by default 0.0
        window : PositiveInt, optional
            Window size, by default 252

        Returns
        -------
        OBBject[List[Data]]
            Sharpe ratio.
        """

        inputs = filter_inputs(
            data=data,
            target=target,
            rfr=rfr,
            window=window,
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/sh",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def skew(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        target: str,
        window: pydantic.types.PositiveInt,
        chart: bool = False,
    ) -> OBBject[List]:
        """Skewness.

        Parameters
        ----------
        data : List[Data]
            Time series data.
        target : str
            Target column name.
        window : PositiveInt
            Window size.

        Returns
        -------
        OBBject[List[Data]]
            Skewness.
        """

        inputs = filter_inputs(
            data=data,
            target=target,
            window=window,
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/skew",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def so(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        target: str,
        target_return: float = 0.0,
        window: pydantic.types.PositiveInt = 252,
        adjusted: bool = False,
        chart: bool = False,
    ) -> OBBject[List]:
        """Sortino Ratio.

        For method & terminology see: http://www.redrockcapital.com/Sortino__A__Sharper__Ratio_Red_Rock_Capital.pdf

        Parameters
        ----------
        data : List[Data]
            Time series data.
        target : str
            Target column name.
        target_return : float, optional
            Target return, by default 0.0
        window : PositiveInt, optional
            Window size, by default 252
        adjusted : bool, optional
            Adjust sortino ratio to compare it to sharpe ratio, by default False

        Returns
        -------
        OBBject[List[Data]]
            Sortino ratio.
        """

        inputs = filter_inputs(
            data=data,
            target=target,
            target_return=target_return,
            window=window,
            adjusted=adjusted,
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/so",
            **inputs,
        )

    @validate_arguments
    def spread(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Spread."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/spread",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def summary(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        target: str,
        chart: bool = False,
    ) -> OBBject[openbb_qa.qa_models.SummaryModel]:
        """Summary.

        Parameters
        ----------
        data : List[Data]
            Time series data.
        target : str
            Target column name.

        Returns
        -------
        OBBject[SummaryModel]
            Summary table.
        """

        inputs = filter_inputs(
            data=data,
            target=target,
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/summary",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def unitroot(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        target: str,
        fuller_reg: Literal["c", "ct", "ctt", "nc", "c"] = "c",
        kpss_reg: Literal["c", "ct"] = "c",
        chart: bool = False,
    ) -> OBBject[openbb_qa.qa_models.UnitRootModel]:
        """Unit Root Test.

        Augmented Dickey-Fuller test for unit root.
        Kwiatkowski-Phillips-Schmidt-Shin test for unit root.

        Parameters
        ----------
        data : List[Data]
            Time series data.
        target : str
            Target column name.
        fuller_reg : Literal["c", "ct", "ctt", "nc", "c"]
            Regression type for ADF test.
        kpss_reg : Literal["c", "ct"]
            Regression type for KPSS test.

        Returns
        -------
        OBBject[UnitRootModel]
            Unit root tests summary.
        """

        inputs = filter_inputs(
            data=data,
            target=target,
            fuller_reg=fuller_reg,
            kpss_reg=kpss_reg,
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/unitroot",
            **inputs,
        )

    @validate_arguments
    def var(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Value at Risk."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/qa/var",
            **inputs,
        )
