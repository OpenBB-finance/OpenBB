# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.econometrics import (
    regression_model,
    econometrics_model,
    regression_view,
)


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "regression_variables, data, show_regression, lags",
    [
        (
            ["longley.TOTEMP", "longley.ARMED", "longley.POP", "longley.GNP"],
            {
                "longley": econometrics_model.load(
                    "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
                )
            },
            False,
            1,
        ),
        (
            ["longley.TOTEMP", "longley.ARMED", "longley.POP", "longley.GNP"],
            {
                "longley": econometrics_model.load(
                    "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
                )
            },
            False,
            2,
        ),
    ],
)
def test_display_bgod(regression_variables, data, show_regression, lags):
    _, _, _, model = regression_model.get_ols(
        regression_variables=regression_variables,
        data=data,
        show_regression=show_regression,
    )

    regression_view.display_bgod(model=model, lags=lags)


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "regression_variables, data, show_regression",
    [
        (
            ["longley.TOTEMP", "longley.ARMED", "longley.POP"],
            {
                "longley": econometrics_model.load(
                    "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
                )
            },
            False,
        ),
        (
            ["longley.GNP", "longley.ARMED", "longley.POP"],
            {
                "longley": econometrics_model.load(
                    "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
                )
            },
            False,
        ),
    ],
)
def test_display_bpag(regression_variables, data, show_regression):
    _, _, _, model = regression_model.get_ols(
        regression_variables=regression_variables,
        data=data,
        show_regression=show_regression,
    )

    regression_view.display_bpag(model=model)
