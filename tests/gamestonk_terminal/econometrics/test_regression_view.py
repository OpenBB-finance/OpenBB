# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.econometrics import (
    regression_model,
    econometrics_model,
    regression_view,
)


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "regression_variables, data, datasets, show_regression, lags",
    [
        (
            ["TOTEMP-longley", "GNP-longley", "ARMED-longley", "POP-longley"],
            {
                "longley": econometrics_model.load(
                    "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
                )
            },
            {
                "TOTEMP-longley": {"TOTEMP": None, "longley": None},
                "GNP-longley": {"GNP": None, "longley": None},
                "ARMED-longley": {"ARMED": None, "longley": None},
                "POP-longley": {"POP": None, "longley": None},
            },
            False,
            1,
        ),
        (
            ["TOTEMP-longley", "GNP-longley", "ARMED-longley", "POP-longley"],
            {
                "longley": econometrics_model.load(
                    "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
                )
            },
            {
                "TOTEMP-longley": {"TOTEMP": None, "longley": None},
                "GNP-longley": {"GNP": None, "longley": None},
                "ARMED-longley": {"ARMED": None, "longley": None},
                "POP-longley": {"POP": None, "longley": None},
            },
            False,
            2,
        ),
    ],
)
def test_display_bgod(regression_variables, data, datasets, show_regression, lags):
    _, _, _, model = regression_model.get_ols(
        regression_variables=regression_variables,
        data=data,
        datasets=datasets,
        show_regression=show_regression,
    )

    regression_view.display_bgod(model=model, lags=lags)


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "regression_variables, data, datasets, show_regression",
    [
        (
            ["TOTEMP-longley", "ARMED-longley", "POP-longley"],
            {
                "longley": econometrics_model.load(
                    "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
                )
            },
            {
                "TOTEMP-longley": {"TOTEMP": None, "longley": None},
                "GNP-longley": {"GNP": None, "longley": None},
                "ARMED-longley": {"ARMED": None, "longley": None},
                "POP-longley": {"POP": None, "longley": None},
            },
            False,
        ),
        (
            ["GNP-longley", "ARMED-longley", "POP-longley"],
            {
                "longley": econometrics_model.load(
                    "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
                )
            },
            {
                "TOTEMP-longley": {"TOTEMP": None, "longley": None},
                "GNP-longley": {"GNP": None, "longley": None},
                "ARMED-longley": {"ARMED": None, "longley": None},
                "POP-longley": {"POP": None, "longley": None},
            },
            False,
        ),
    ],
)
def test_display_bpag(regression_variables, data, datasets, show_regression):
    _, _, _, model = regression_model.get_ols(
        regression_variables=regression_variables,
        data=data,
        datasets=datasets,
        show_regression=show_regression,
    )

    regression_view.display_bpag(model=model)
