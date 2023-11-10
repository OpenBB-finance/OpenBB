### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import Dict, List, Literal, Union

import numpy
import pandas
import typing_extensions
from annotated_types import Gt
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_provider.abstract.data import Data


class ROUTER_econometrics(Container):
    """/econometrics
    autocorrelation
    causality
    cointegration
    correlation_matrix
    ols_regression
    ols_regression_summary
    panel_between
    panel_first_difference
    panel_fixed
    panel_fmac
    panel_pooled
    panel_random_effects
    residual_autocorrelation
    unit_root
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate(config=dict(arbitrary_types_allowed=True))
    def autocorrelation(
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
        y_column: str,
        x_columns: List[str],
    ) -> OBBject[Dict]:
        """Perform Durbin-Watson test for autocorrelation.

        Parameters
        ----------
        data: List[Data]
            Input dataset.
        y_column: str
            Target column.
        x_columns: str
            List of columns to use as exogenous variables.

        Returns
        -------
        OBBject[Data]
            OBBject with the results being the score from the test.
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            y_column=y_column,
            x_columns=x_columns,
            data_processing=True,
        )

        return self._run(
            "/econometrics/autocorrelation",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def causality(
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
        y_column: str,
        x_column: str,
        lag: typing_extensions.Annotated[int, Gt(gt=0)] = 3,
    ) -> OBBject[Data]:
        """Perform Granger causality test to determine if X "causes" y.

        Parameters
        ----------
        data: List[Data]
            Input dataset.
        y_column: str
            Target column.
        x_column: str
            Columns to use as exogenous variables.
        lag: PositiveInt
            Number of lags to use in the test.

        Returns
        -------
        OBBject[Data]
            OBBject with the results being the score from the test.
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            y_column=y_column,
            x_column=x_column,
            lag=lag,
            data_processing=True,
        )

        return self._run(
            "/econometrics/causality",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def cointegration(
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
        columns: List[str],
    ) -> OBBject[Data]:
        """Show co-integration between two timeseries using the two step Engle-Granger test.

        Parameters
        ----------
        data: List[Data]
            Input dataset.
        columns: List[str]
            Data columns to check cointegration
        maxlag: PositiveInt
            Number of lags to use in the test.

        Returns
        -------
        OBBject[Data]
            OBBject with the results being the score from the test.
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            columns=columns,
            data_processing=True,
        )

        return self._run(
            "/econometrics/cointegration",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def correlation_matrix(
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
    ) -> OBBject[List[Data]]:
        """Get the correlation matrix of an input dataset.

        Parameters
        ----------
        data : List[Data]
            Input dataset.

        Returns
        -------
        OBBject[List[Data]]
            Correlation matrix.
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            data_processing=True,
        )

        return self._run(
            "/econometrics/correlation_matrix",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def ols_regression(
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
        y_column: str,
        x_columns: List[str],
    ) -> OBBject[Dict]:
        """Perform OLS regression.  This returns the model and results objects from statsmodels.

        Parameters
        ----------
        data: List[Data]
            Input dataset.
        y_column: str
            Target column.
        x_columns: str
            List of columns to use as exogenous variables.

        Returns
        -------
        OBBject[Dict]
            OBBject with the results being model and results objects.
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            y_column=y_column,
            x_columns=x_columns,
            data_processing=True,
        )

        return self._run(
            "/econometrics/ols_regression",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def ols_regression_summary(
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
        y_column: str,
        x_columns: List[str],
    ) -> OBBject[Data]:
        """Perform OLS regression. This returns the summary object from statsmodels.

        Parameters
        ----------
        data: List[Data]
            Input dataset.
        y_column: str
            Target column.
        x_columns: str
            List of columns to use as exogenous variables.

        Returns
        -------
        OBBject[Dict]
            OBBject with the results being summary object.
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            y_column=y_column,
            x_columns=x_columns,
            data_processing=True,
        )

        return self._run(
            "/econometrics/ols_regression_summary",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def panel_between(
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
        y_column: str,
        x_columns: List[str],
    ) -> OBBject[Dict]:
        """Perform a Between estimator regression on panel data.

        Parameters
        ----------
        data: List[Data]
            Input dataset.
        y_column: str
            Target column.
        x_columns: str
            List of columns to use as exogenous variables.

        Returns
        -------
        OBBject[Dict]
            OBBject with the fit model returned
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            y_column=y_column,
            x_columns=x_columns,
            data_processing=True,
        )

        return self._run(
            "/econometrics/panel_between",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def panel_first_difference(
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
        y_column: str,
        x_columns: List[str],
    ) -> OBBject[Dict]:
        """Perform a first-difference estimate for panel data.

        Parameters
        ----------
        data: List[Data]
            Input dataset.
        y_column: str
            Target column.
        x_columns: str
            List of columns to use as exogenous variables.

        Returns
        -------
        OBBject[Dict]
            OBBject with the fit model returned
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            y_column=y_column,
            x_columns=x_columns,
            data_processing=True,
        )

        return self._run(
            "/econometrics/panel_first_difference",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def panel_fixed(
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
        y_column: str,
        x_columns: List[str],
    ) -> OBBject[Dict]:
        """One- and two-way fixed effects estimator for panel data.

        Parameters
        ----------
        data: List[Data]
            Input dataset.
        y_column: str
            Target column.
        x_columns: str
            List of columns to use as exogenous variables.

        Returns
        -------
        OBBject[Dict]
            OBBject with the fit model returned
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            y_column=y_column,
            x_columns=x_columns,
            data_processing=True,
        )

        return self._run(
            "/econometrics/panel_fixed",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def panel_fmac(
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
        y_column: str,
        x_columns: List[str],
    ) -> OBBject[Dict]:
        """Fama-MacBeth estimator for panel data.

        Parameters
        ----------
        data: List[Data]
            Input dataset.
        y_column: str
            Target column.
        x_columns: str
            List of columns to use as exogenous variables.

        Returns
        -------
        OBBject[Dict]
            OBBject with the fit model returned
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            y_column=y_column,
            x_columns=x_columns,
            data_processing=True,
        )

        return self._run(
            "/econometrics/panel_fmac",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def panel_pooled(
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
        y_column: str,
        x_columns: List[str],
    ) -> OBBject[Dict]:
        """Perform a Pooled coefficient estimator regression on panel data.

        Parameters
        ----------
        data: List[Data]
            Input dataset.
        y_column: str
            Target column.
        x_columns: str
            List of columns to use as exogenous variables.

        Returns
        -------
        OBBject[Dict]
            OBBject with the fit model returned
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            y_column=y_column,
            x_columns=x_columns,
            data_processing=True,
        )

        return self._run(
            "/econometrics/panel_pooled",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def panel_random_effects(
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
        y_column: str,
        x_columns: List[str],
    ) -> OBBject[Dict]:
        """Perform One-way Random Effects model for panel data.

        Parameters
        ----------
        data: List[Data]
            Input dataset.
        y_column: str
            Target column.
        x_columns: str
            List of columns to use as exogenous variables.

        Returns
        -------
        OBBject[Dict]
            OBBject with the fit model returned
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            y_column=y_column,
            x_columns=x_columns,
            data_processing=True,
        )

        return self._run(
            "/econometrics/panel_random_effects",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def residual_autocorrelation(
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
        y_column: str,
        x_columns: List[str],
        lags: typing_extensions.Annotated[int, Gt(gt=0)] = 1,
    ) -> OBBject[Data]:
        """Perform Breusch-Godfrey Lagrange Multiplier tests for residual autocorrelation.

        Parameters
        ----------
        data: List[Data]
            Input dataset.
        y_column: str
            Target column.
        x_columns: str
            List of columns to use as exogenous variables.
        lags: PositiveInt
            Number of lags to use in the test.

        Returns
        -------
        OBBject[Data]
            OBBject with the results being the score from the test.
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            y_column=y_column,
            x_columns=x_columns,
            lags=lags,
            data_processing=True,
        )

        return self._run(
            "/econometrics/residual_autocorrelation",
            **inputs,
        )

    @validate(config=dict(arbitrary_types_allowed=True))
    def unit_root(
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
        column: str,
        regression: Literal["c", "ct", "ctt"] = "c",
    ) -> OBBject[Data]:
        """Perform Augmented Dickey-Fuller unit root test.

        Parameters
        ----------
        data: List[Data]
            Input dataset.
        column: str
            Data columns to check unit root
        regression: str
            Regression type to use in the test.  Either "c" for constant only, "ct" for constant and trend, or "ctt" for
            constant, trend, and trend-squared.

        Returns
        -------
        OBBject[Data]
            OBBject with the results being the score from the test.
        """  # noqa: E501

        inputs = filter_inputs(
            data=data,
            column=column,
            regression=regression,
            data_processing=True,
        )

        return self._run(
            "/econometrics/unit_root",
            **inputs,
        )
