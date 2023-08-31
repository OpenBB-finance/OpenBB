### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import Dict, List, Union

import openbb_provider
import openbb_provider.abstract.data
import pandas
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs
from pydantic import validate_arguments


class CLASS_econometrics(Container):
    """/econometrics
    corr
    dwat
    ols
    ols_summary
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def corr(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        chart: bool = False,
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
            chart=chart,
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
        chart: bool = False,
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
            chart=chart,
        )

        return self._command_runner.run(
            "/econometrics/dwat",
            **inputs,
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def ols(
        self,
        data: Union[List[openbb_provider.abstract.data.Data], pandas.DataFrame],
        y_column: str,
        x_columns: List[str],
        chart: bool = False,
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
            chart=chart,
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
        chart: bool = False,
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
            chart=chart,
        )

        return self._command_runner.run(
            "/econometrics/ols_summary",
            **inputs,
        )
