# IMPORTATION STANDARD
import pandas as pd

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.econometrics import regression_model, econometrics_model


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data",
    [
        (
            ["longley.TOTEMP", "longley.GNP", "longley.ARMED", "longley.POP"],
            {
                "longley": econometrics_model.load(
                    "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
                )
            },
        )
    ],
)
def test_get_regression_data(recorder, regression_variables, data):
    (
        regression_df,
        dependent_variable,
        independent_variables,
    ) = regression_model.get_regression_data(
        regression_variables=regression_variables, data=data
    )

    recorder.capture(
        pd.DataFrame([regression_df, dependent_variable, independent_variables])
    )


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data, show_regression",
    [
        (
            ["longley.TOTEMP", "longley.GNP", "longley.ARMED", "longley.POP"],
            {
                "longley": econometrics_model.load(
                    "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
                )
            },
            True,
        ),
        (
            ["longley.TOTEMP", "longley.GNP", "longley.ARMED", "longley.POP"],
            {
                "longley": econometrics_model.load(
                    "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
                )
            },
            False,
        ),
    ],
)
def test_get_ols(recorder, regression_variables, data, show_regression):
    _, _, _, model = regression_model.get_ols(
        regression_variables=regression_variables,
        data=data,
        show_regression=show_regression,
    )

    result = pd.DataFrame([model.params])

    recorder.capture(result, float_format="%.5f")


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data",
    [
        (
            [
                "wage_panel.educ",
                "wage_panel.married",
                "wage_panel.lwage",
                "wage_panel.hisp",
                "wage_panel.black",
            ],
            {
                "wage_panel": econometrics_model.load(
                    "wage_panel", ["csv", "xlsx"], {}, {"wage_panel": "wage_panel"}
                ).set_index(["nr", "year"])
            },
        )
    ],
)
def test_get_pols(recorder, regression_variables, data):
    _, _, _, model = regression_model.get_pols(
        regression_variables=regression_variables,
        data=data,
    )

    result = pd.DataFrame([model.params])

    recorder.capture(result, float_format="%.5f")


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data",
    [
        (
            [
                "wage_panel.married",
                "wage_panel.lwage",
                "wage_panel.hisp",
                "wage_panel.black",
            ],
            {
                "wage_panel": econometrics_model.load(
                    "wage_panel", ["csv", "xlsx"], {}, {"wage_panel": "wage_panel"}
                ).set_index(["nr", "year"])
            },
        )
    ],
)
def test_get_re(recorder, regression_variables, data):
    _, _, _, model = regression_model.get_re(
        regression_variables=regression_variables,
        data=data,
    )

    result = pd.DataFrame([model.params])

    recorder.capture(result, float_format="%.5f")


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data",
    [
        (
            [
                "wage_panel.educ",
                "wage_panel.married",
                "wage_panel.lwage",
                "wage_panel.hisp",
                "wage_panel.black",
            ],
            {
                "wage_panel": econometrics_model.load(
                    "wage_panel", ["csv", "xlsx"], {}, {"wage_panel": "wage_panel"}
                ).set_index(["nr", "year"])
            },
        )
    ],
)
def test_get_bols(recorder, regression_variables, data):
    _, _, _, model = regression_model.get_bols(
        regression_variables=regression_variables,
        data=data,
    )

    result = pd.DataFrame([model.params])

    recorder.capture(result, float_format="%.5f")


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data",
    [
        (
            [
                "wage_panel.educ",
                "wage_panel.married",
                "wage_panel.lwage",
                "wage_panel.hisp",
                "wage_panel.black",
            ],
            {
                "wage_panel": econometrics_model.load(
                    "wage_panel", ["csv", "xlsx"], {}, {"wage_panel": "wage_panel"}
                ).set_index(["nr", "year"])
            },
        )
    ],
)
def test_get_fe(recorder, regression_variables, data):
    _, _, _, model = regression_model.get_fe(
        regression_variables=regression_variables,
        data=data,
    )

    result = pd.DataFrame([model.params])

    recorder.capture(result, float_format="%.5f")


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data",
    [
        (
            ["wage_panel.lwage", "wage_panel.married"],
            {
                "wage_panel": econometrics_model.load(
                    "wage_panel", ["csv", "xlsx"], {}, {"wage_panel": "wage_panel"}
                ).set_index(["nr", "year"])
            },
        )
    ],
)
def test_get_fdols(recorder, regression_variables, data):
    _, _, _, model = regression_model.get_fdols(
        regression_variables=regression_variables,
        data=data,
    )

    result = pd.DataFrame([model.params])

    recorder.capture(result, float_format="%.5f")


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data",
    [
        (
            [
                "wage_panel.married",
                "wage_panel.lwage",
                "wage_panel.hisp",
                "wage_panel.black",
            ],
            {
                "wage_panel": econometrics_model.load(
                    "wage_panel", ["csv", "xlsx"], {}, {"wage_panel": "wage_panel"}
                ).set_index(["nr", "year"])
            },
        )
    ],
)
def test_get_comparison(recorder, regression_variables, data):
    regressions = {"RE": {}, "FE": {}}

    _, _, _, regressions["RE"]["model"] = regression_model.get_re(
        regression_variables=regression_variables,
        data=data,
    )

    _, _, _, regressions["FE"]["model"] = regression_model.get_fe(
        regression_variables=regression_variables,
        data=data,
    )

    comparison_result = regression_model.get_comparison(regressions)

    recorder.capture(comparison_result.params, float_format="%.5f")


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data, show_regression",
    [
        (
            ["longley.TOTEMP", "longley.GNP", "longley.ARMED", "longley.POP"],
            {
                "longley": econometrics_model.load(
                    "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
                )
            },
            True,
        ),
        (
            ["longley.GNP", "longley.ARMED", "longley.POP"],
            {
                "longley": econometrics_model.load(
                    "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
                )
            },
            True,
        ),
    ],
)
def test_get_dwat(recorder, regression_variables, data, show_regression):
    _, _, _, model = regression_model.get_ols(
        regression_variables=regression_variables,
        data=data,
        show_regression=show_regression,
    )

    result = regression_model.get_dwat(model.resid).round(5)

    recorder.capture(result)


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data, show_regression, lags",
    [
        (
            ["longley.ARMED", "longley.GNP", "longley.TOTEMP", "longley.POP"],
            {
                "longley": econometrics_model.load(
                    "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
                )
            },
            True,
            3,
        ),
        (
            ["longley.GNP", "longley.POP"],
            {
                "longley": econometrics_model.load(
                    "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
                )
            },
            True,
            1,
        ),
    ],
)
def test_get_bgod(recorder, regression_variables, data, show_regression, lags):
    _, _, _, model = regression_model.get_ols(
        regression_variables=regression_variables,
        data=data,
        show_regression=show_regression,
    )

    lm_stat, p_value, f_stat, fp_value = regression_model.get_bgod(model, lags)

    result = pd.DataFrame([lm_stat, p_value, f_stat, fp_value])

    recorder.capture(result, float_format="%.5f")


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data, show_regression",
    [
        (
            ["longley.GNP", "longley.TOTEMP", "longley.POP"],
            {
                "longley": econometrics_model.load(
                    "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
                )
            },
            True,
        ),
        (
            ["longley.POP", "longley.GNP"],
            {
                "longley": econometrics_model.load(
                    "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
                )
            },
            True,
        ),
    ],
)
def test_get_bpag(recorder, regression_variables, data, show_regression):
    _, _, _, model = regression_model.get_ols(
        regression_variables=regression_variables,
        data=data,
        show_regression=show_regression,
    )

    lm_stat, p_value, f_stat, fp_value = regression_model.get_bpag(model)

    result = pd.DataFrame([lm_stat, p_value, f_stat, fp_value])

    recorder.capture(result, float_format="%.5f")
