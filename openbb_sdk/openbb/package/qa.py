### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Union

import numpy
import openbb_qa.qa_models
import pandas
import pydantic
import pydantic.types
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs
from openbb_provider.abstract.data import Data
from pydantic import validate_arguments


class CLASS_qa(Container):
    """/qa
    capm
    kurtosis
    normality
    om
    quantile
    sh
    skew
    so
    summary
    unitroot
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def capm(
        self,
        data: Union[
            list,
            dict,
            pandas.DataFrame,
            List[pandas.DataFrame],
            pandas.Series,
            List[pandas.Series],
            numpy.ndarray,
            Data,
            List[Data],
        ],
        target: str,
    ) -> OBBject[openbb_qa.qa_models.CAPMModel]:
        """Capital Asset Pricing Model."""  # noqa: E501

        inputs = filter_inputs(
            data=data,
            target=target,
        )

        return self._command_runner.run(
            "/qa/capm",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def kurtosis(
        self,
        data: Union[
            list,
            dict,
            pandas.DataFrame,
            List[pandas.DataFrame],
            pandas.Series,
            List[pandas.Series],
            numpy.ndarray,
            Data,
            List[Data],
        ],
        target: str,
        window: pydantic.types.PositiveInt,
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
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            target=target,
            window=window,
        )

        return self._command_runner.run(
            "/qa/kurtosis",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def normality(
        self,
        data: Union[
            list,
            dict,
            pandas.DataFrame,
            List[pandas.DataFrame],
            pandas.Series,
            List[pandas.Series],
            numpy.ndarray,
            Data,
            List[Data],
        ],
        target: str,
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
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            target=target,
        )

        return self._command_runner.run(
            "/qa/normality",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def om(
        self,
        data: Union[
            list,
            dict,
            pandas.DataFrame,
            List[pandas.DataFrame],
            pandas.Series,
            List[pandas.Series],
            numpy.ndarray,
            Data,
            List[Data],
        ],
        target: str,
        threshold_start: float = 0.0,
        threshold_end: float = 1.5,
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
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            target=target,
            threshold_start=threshold_start,
            threshold_end=threshold_end,
        )

        return self._command_runner.run(
            "/qa/om",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def quantile(
        self,
        data: Union[
            list,
            dict,
            pandas.DataFrame,
            List[pandas.DataFrame],
            pandas.Series,
            List[pandas.Series],
            numpy.ndarray,
            Data,
            List[Data],
        ],
        target: str,
        window: pydantic.types.PositiveInt,
        quantile_pct: pydantic.types.NonNegativeFloat = 0.5,
    ) -> OBBject[List]:
        """Quantile."""  # noqa: E501

        inputs = filter_inputs(
            data=data,
            target=target,
            window=window,
            quantile_pct=quantile_pct,
        )

        return self._command_runner.run(
            "/qa/quantile",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def sh(
        self,
        data: Union[
            list,
            dict,
            pandas.DataFrame,
            List[pandas.DataFrame],
            pandas.Series,
            List[pandas.Series],
            numpy.ndarray,
            Data,
            List[Data],
        ],
        target: str,
        rfr: float = 0.0,
        window: pydantic.types.PositiveInt = 252,
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
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            target=target,
            rfr=rfr,
            window=window,
        )

        return self._command_runner.run(
            "/qa/sh",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def skew(
        self,
        data: Union[
            list,
            dict,
            pandas.DataFrame,
            List[pandas.DataFrame],
            pandas.Series,
            List[pandas.Series],
            numpy.ndarray,
            Data,
            List[Data],
        ],
        target: str,
        window: pydantic.types.PositiveInt,
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
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            target=target,
            window=window,
        )

        return self._command_runner.run(
            "/qa/skew",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def so(
        self,
        data: Union[
            list,
            dict,
            pandas.DataFrame,
            List[pandas.DataFrame],
            pandas.Series,
            List[pandas.Series],
            numpy.ndarray,
            Data,
            List[Data],
        ],
        target: str,
        target_return: float = 0.0,
        window: pydantic.types.PositiveInt = 252,
        adjusted: bool = False,
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
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            target=target,
            target_return=target_return,
            window=window,
            adjusted=adjusted,
        )

        return self._command_runner.run(
            "/qa/so",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def summary(
        self,
        data: Union[
            list,
            dict,
            pandas.DataFrame,
            List[pandas.DataFrame],
            pandas.Series,
            List[pandas.Series],
            numpy.ndarray,
            Data,
            List[Data],
        ],
        target: str,
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
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            target=target,
        )

        return self._command_runner.run(
            "/qa/summary",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def unitroot(
        self,
        data: Union[
            list,
            dict,
            pandas.DataFrame,
            List[pandas.DataFrame],
            pandas.Series,
            List[pandas.Series],
            numpy.ndarray,
            Data,
            List[Data],
        ],
        target: str,
        fuller_reg: Literal["c", "ct", "ctt", "nc", "c"] = "c",
        kpss_reg: Literal["c", "ct"] = "c",
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
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            target=target,
            fuller_reg=fuller_reg,
            kpss_reg=kpss_reg,
        )

        return self._command_runner.run(
            "/qa/unitroot",
            **inputs,
        )
