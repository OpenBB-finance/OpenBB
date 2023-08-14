### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import typing
from typing import List, Literal, Union

import openbb_provider
import openbb_qa.qa_models
import pandas
import pydantic
import pydantic.types
from pydantic import validate_arguments

import openbb_core.app.model.results.empty
from openbb_core.app.model.obbject import Obbject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_qa(Container):
    @filter_call
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def normality(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        target: str,
        chart: bool = False,
    ) -> Obbject[openbb_qa.qa_models.NormalityModel]:
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
        Obbject[NormalityModel]
            Normality tests summary. See qa_models.NormalityModel for details.
        """
        inputs = filter_inputs(
            data=data,
            target=target,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/normality",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def capm(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        target: str,
        chart: bool = False,
    ) -> Obbject[openbb_qa.qa_models.CAPMModel]:
        """Capital Asset Pricing Model."""
        inputs = filter_inputs(
            data=data,
            target=target,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/capm",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def qqplot(
        self, chart: bool = False
    ) -> Obbject[openbb_core.app.model.results.empty.Empty]:
        """QQ Plot."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/qqplot",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def om(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        target: str,
        threshold_start: float = 0.0,
        threshold_end: float = 1.5,
        chart: bool = False,
    ) -> Obbject[typing.List]:
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
        Obbject[List[OmegaModel]]
            Omega ratios.
        """
        inputs = filter_inputs(
            data=data,
            target=target,
            threshold_start=threshold_start,
            threshold_end=threshold_end,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/om",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def kurtosis(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        target: str,
        window: pydantic.types.PositiveInt,
        chart: bool = False,
    ) -> Obbject[typing.List]:
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
        Obbject[List[Data]]
            Kurtosis.
        """
        inputs = filter_inputs(
            data=data,
            target=target,
            window=window,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/kurtosis",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def pick(
        self, chart: bool = False
    ) -> Obbject[openbb_core.app.model.results.empty.Empty]:
        """Pick."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/pick",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def spread(
        self, chart: bool = False
    ) -> Obbject[openbb_core.app.model.results.empty.Empty]:
        """Spread."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/spread",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def rolling(
        self, chart: bool = False
    ) -> Obbject[openbb_core.app.model.results.empty.Empty]:
        """Rolling."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/rolling",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def var(
        self, chart: bool = False
    ) -> Obbject[openbb_core.app.model.results.empty.Empty]:
        """Value at Risk."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/var",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def line(
        self, chart: bool = False
    ) -> Obbject[openbb_core.app.model.results.empty.Empty]:
        """Line."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/line",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def hist(
        self, chart: bool = False
    ) -> Obbject[openbb_core.app.model.results.empty.Empty]:
        """Histogram."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/hist",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def unitroot(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        target: str,
        fuller_reg: Literal["c", "ct", "ctt", "nc"] = "c",
        kpss_reg: Literal["c", "ct"] = "c",
        chart: bool = False,
    ) -> Obbject[openbb_qa.qa_models.UnitRootModel]:
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
        Obbject[UnitRootModel]
            Unit root tests summary.
        """
        inputs = filter_inputs(
            data=data,
            target=target,
            fuller_reg=fuller_reg,
            kpss_reg=kpss_reg,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/unitroot",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def beta(
        self, chart: bool = False
    ) -> Obbject[openbb_core.app.model.results.empty.Empty]:
        """Beta."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/beta",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def sh(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        target: str,
        rfr: float = 0.0,
        window: pydantic.types.PositiveInt = 252,
        chart: bool = False,
    ) -> Obbject[typing.List]:
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
        Obbject[List[Data]]
            Sharpe ratio.
        """
        inputs = filter_inputs(
            data=data,
            target=target,
            rfr=rfr,
            window=window,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/sh",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def so(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        target: str,
        target_return: float = 0.0,
        window: pydantic.types.PositiveInt = 252,
        adjusted: bool = False,
        chart: bool = False,
    ) -> Obbject[typing.List]:
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
        Obbject[List[Data]]
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

        o = self._command_runner_session.run(
            "/qa/so",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def cusum(
        self, chart: bool = False
    ) -> Obbject[openbb_core.app.model.results.empty.Empty]:
        """Cumulative Sum."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/cusum",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def raw(
        self, chart: bool = False
    ) -> Obbject[openbb_core.app.model.results.empty.Empty]:
        """Raw."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/raw",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def cdf(
        self, chart: bool = False
    ) -> Obbject[openbb_core.app.model.results.empty.Empty]:
        """Cumulative Distribution Function."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/cdf",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def decompose(
        self, chart: bool = False
    ) -> Obbject[openbb_core.app.model.results.empty.Empty]:
        """Decompose."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/decompose",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def skew(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        target: str,
        window: pydantic.types.PositiveInt,
        chart: bool = False,
    ) -> Obbject[typing.List]:
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
        Obbject[List[Data]]
            Skewness.
        """
        inputs = filter_inputs(
            data=data,
            target=target,
            window=window,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/skew",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def quantile(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        target: str,
        window: pydantic.types.PositiveInt,
        quantile_pct: pydantic.types.NonNegativeFloat = 0.5,
        chart: bool = False,
    ) -> Obbject[typing.List]:
        """Quantile."""
        inputs = filter_inputs(
            data=data,
            target=target,
            window=window,
            quantile_pct=quantile_pct,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/quantile",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def bw(
        self, chart: bool = False
    ) -> Obbject[openbb_core.app.model.results.empty.Empty]:
        """Bandwidth."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/bw",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def es(
        self, chart: bool = False
    ) -> Obbject[openbb_core.app.model.results.empty.Empty]:
        """Expected Shortfall."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/es",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def acf(
        self, chart: bool = False
    ) -> Obbject[openbb_core.app.model.results.empty.Empty]:
        """Autocorrelation Function."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/acf",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def summary(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        target: str,
        chart: bool = False,
    ) -> Obbject[openbb_qa.qa_models.SummaryModel]:
        """Summary.

        Parameters
        ----------
        data : List[Data]
            Time series data.
        target : str
            Target column name.

        Returns
        -------
        Obbject[SummaryModel]
            Summary table.
        """
        inputs = filter_inputs(
            data=data,
            target=target,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/qa/summary",
            **inputs,
        ).output

        return filter_output(o)
