### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import Dict, List, Literal, Union

import openbb_provider
import openbb_provider.abstract.data
import pandas
import pydantic
import pydantic.types
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs
from pydantic import validate_arguments


class CLASS_econometrics(Container):
    """/econometrics
    bgot
    coint
    corr
    dwat
    granger
    ols
    ols_summary
    unitroot
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def bgot(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        y_column: str,
        x_columns: List[str],
        lags: pydantic.types.PositiveInt = 1,
    ) -> OBBject[openbb_provider.abstract.data.Data]:
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
        )

        return self._command_runner.run(
            "/econometrics/bgot",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def coint(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        columns: List[str],
    ) -> OBBject[openbb_provider.abstract.data.Data]:
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
        )

        return self._command_runner.run(
            "/econometrics/coint",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def corr(
        self, data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame]
    ) -> OBBject[List]:
        """Get the corrlelation matrix of an input dataset.

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
        )

        return self._command_runner.run(
            "/econometrics/corr",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def dwat(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        y_column: str,
        x_columns: List[str],
    ) -> OBBject[Dict]:
        """Perform Durbin-Watson test for autocorrelation

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
        )

        return self._command_runner.run(
            "/econometrics/dwat",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def granger(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        y_column: str,
        x_column: str,
        lag: pydantic.types.PositiveInt = 3,
    ) -> OBBject[openbb_provider.abstract.data.Data]:
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
        )

        return self._command_runner.run(
            "/econometrics/granger",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def ols(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
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
        )

        return self._command_runner.run(
            "/econometrics/ols",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def ols_summary(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        y_column: str,
        x_columns: List[str],
    ) -> OBBject[openbb_provider.abstract.data.Data]:
        """Perform OLS regression.  This returns the summary object from statsmodels.

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
        )

        return self._command_runner.run(
            "/econometrics/ols_summary",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def unitroot(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        column: str,
        regression: Literal["c", "ct", "ctt"] = "c",
    ) -> OBBject[openbb_provider.abstract.data.Data]:
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
        )

        return self._command_runner.run(
            "/econometrics/unitroot",
            **inputs,
        )
