### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Union

import numpy
import pandas
import typing_extensions
from annotated_types import Ge, Gt
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_provider.abstract.data import Data
from openbb_qa.qa_models import (
    CAPMModel,
    NormalityModel,
    OmegaModel,
    SummaryModel,
    UnitRootModel,
)


class ROUTER_qa(Container):
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

    @validate(config=dict(arbitrary_types_allowed=True))
    def capm(
        self,
        data: Union[
            list,
            dict,
            pandas.DataFrame,
            List[pandas.DataFrame],
            pandas.core.series.Series,
            List[pandas.core.series.Series],
            numpy.ndarray,
            Data,
            List[Data],
        ],
        target: str,
    ) -> OBBject[CAPMModel]:
        """Get Capital Asset Pricing Model."""  # noqa: E501

        inputs = filter_inputs(
            data=data,
            target=target,
            data_processing=True,
        )

        return self._run(
            "/qa/capm",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def kurtosis(
        self,
        data: Union[
            list,
            dict,
            pandas.DataFrame,
            List[pandas.DataFrame],
            pandas.core.series.Series,
            List[pandas.core.series.Series],
            numpy.ndarray,
            Data,
            List[Data],
        ],
        target: str,
        window: typing_extensions.Annotated[int, Gt(gt=0)],
    ) -> OBBject[List[Data]]:
        """Get the Kurtosis.

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
            data_processing=True,
        )

        return self._run(
            "/qa/kurtosis",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def normality(
        self,
        data: Union[
            list,
            dict,
            pandas.DataFrame,
            List[pandas.DataFrame],
            pandas.core.series.Series,
            List[pandas.core.series.Series],
            numpy.ndarray,
            Data,
            List[Data],
        ],
        target: str,
    ) -> OBBject[NormalityModel]:
        """Get Normality Statistics.

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
            data_processing=True,
        )

        return self._run(
            "/qa/normality",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def om(
        self,
        data: Union[
            list,
            dict,
            pandas.DataFrame,
            List[pandas.DataFrame],
            pandas.core.series.Series,
            List[pandas.core.series.Series],
            numpy.ndarray,
            Data,
            List[Data],
        ],
        target: str,
        threshold_start: float = 0.0,
        threshold_end: float = 1.5,
    ) -> OBBject[List[OmegaModel]]:
        """Calculate the Omega Ratio.

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
            data_processing=True,
        )

        return self._run(
            "/qa/om",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def quantile(
        self,
        data: Union[
            list,
            dict,
            pandas.DataFrame,
            List[pandas.DataFrame],
            pandas.core.series.Series,
            List[pandas.core.series.Series],
            numpy.ndarray,
            Data,
            List[Data],
        ],
        target: str,
        window: typing_extensions.Annotated[int, Gt(gt=0)],
        quantile_pct: typing_extensions.Annotated[float, Ge(ge=0)] = 0.5,
    ) -> OBBject[List[Data]]:
        """Get Quantile.

        Parameters
        ----------
        data : List[Data]
            Time series data.
        target : str
            Target column name.
        window : PositiveInt
            Window size.
        quantile_pct : NonNegativeFloat, optional
            Quantile percentage, by default 0.5

        Returns
        -------
        OBBject[List[Data]]
            Quantile.
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            target=target,
            window=window,
            quantile_pct=quantile_pct,
            data_processing=True,
        )

        return self._run(
            "/qa/quantile",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def sh(
        self,
        data: Union[
            list,
            dict,
            pandas.DataFrame,
            List[pandas.DataFrame],
            pandas.core.series.Series,
            List[pandas.core.series.Series],
            numpy.ndarray,
            Data,
            List[Data],
        ],
        target: str,
        rfr: float = 0.0,
        window: typing_extensions.Annotated[int, Gt(gt=0)] = 252,
    ) -> OBBject[List[Data]]:
        """Get Sharpe Ratio.

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
            data_processing=True,
        )

        return self._run(
            "/qa/sh",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def skew(
        self,
        data: Union[
            list,
            dict,
            pandas.DataFrame,
            List[pandas.DataFrame],
            pandas.core.series.Series,
            List[pandas.core.series.Series],
            numpy.ndarray,
            Data,
            List[Data],
        ],
        target: str,
        window: typing_extensions.Annotated[int, Gt(gt=0)],
    ) -> OBBject[List[Data]]:
        """Get Skewness.

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
            data_processing=True,
        )

        return self._run(
            "/qa/skew",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def so(
        self,
        data: Union[
            list,
            dict,
            pandas.DataFrame,
            List[pandas.DataFrame],
            pandas.core.series.Series,
            List[pandas.core.series.Series],
            numpy.ndarray,
            Data,
            List[Data],
        ],
        target: str,
        target_return: float = 0.0,
        window: typing_extensions.Annotated[int, Gt(gt=0)] = 252,
        adjusted: bool = False,
    ) -> OBBject[List[Data]]:
        """Get Sortino Ratio.

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
            data_processing=True,
        )

        return self._run(
            "/qa/so",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def summary(
        self,
        data: Union[
            list,
            dict,
            pandas.DataFrame,
            List[pandas.DataFrame],
            pandas.core.series.Series,
            List[pandas.core.series.Series],
            numpy.ndarray,
            Data,
            List[Data],
        ],
        target: str,
    ) -> OBBject[SummaryModel]:
        """Get Summary Statistics.

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
            data_processing=True,
        )

        return self._run(
            "/qa/summary",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def unitroot(
        self,
        data: Union[
            list,
            dict,
            pandas.DataFrame,
            List[pandas.DataFrame],
            pandas.core.series.Series,
            List[pandas.core.series.Series],
            numpy.ndarray,
            Data,
            List[Data],
        ],
        target: str,
        fuller_reg: Literal["c", "ct", "ctt", "nc", "c"] = "c",
        kpss_reg: Literal["c", "ct"] = "c",
    ) -> OBBject[UnitRootModel]:
        """Get Unit Root Test.

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
            data_processing=True,
        )

        return self._run(
            "/qa/unitroot",
            **inputs,
        )
