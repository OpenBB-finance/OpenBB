# IMPORTATION STANDARD
import pandas as pd

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.econometrics import regression_model, econometrics_model


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data, datasets",
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
        )
    ],
)
def test_get_regression_data(recorder, regression_variables, data, datasets):
    (
        regression_df,
        dependent_variable,
        independent_variables,
    ) = regression_model.get_regression_data(
        regression_variables=regression_variables, data=data, datasets=datasets
    )

    recorder.capture(
        pd.DataFrame([regression_df, dependent_variable, independent_variables])
    )


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data, datasets, show_regression",
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
            True,
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
        ),
    ],
)
def test_get_ols(recorder, regression_variables, data, datasets, show_regression):
    _, _, _, model = regression_model.get_ols(
        regression_variables=regression_variables,
        data=data,
        datasets=datasets,
        show_regression=show_regression,
    )

    result = pd.DataFrame([model.params])

    recorder.capture(result, float_format="%.5f")


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data, datasets",
    [
        (
            [
                "educ-wage_panel",
                "married-wage_panel",
                "lwage-wage_panel",
                "hisp-wage_panel",
                "black-wage_panel",
            ],
            {
                "wage_panel": econometrics_model.load(
                    "wage_panel", ["csv", "xlsx"], {}, {"wage_panel": "wage_panel"}
                ).set_index(["nr", "year"])
            },
            {
                "educ-wage_panel": {"educ": None, "wage_panel": None},
                "married-wage_panel": {"married": None, "wage_panel": None},
                "lwage-wage_panel": {"lwage": None, "wage_panel": None},
                "hisp-wage_panel": {"hisp": None, "wage_panel": None},
                "black-wage_panel": {"black": None, "wage_panel": None},
            },
        )
    ],
)
def test_get_pols(recorder, regression_variables, data, datasets):
    _, _, _, model = regression_model.get_pols(
        regression_variables=regression_variables,
        data=data,
        datasets=datasets,
    )

    result = pd.DataFrame([model.params])

    recorder.capture(result, float_format="%.5f")


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data, datasets",
    [
        (
            [
                "married-wage_panel",
                "lwage-wage_panel",
                "hisp-wage_panel",
                "black-wage_panel",
            ],
            {
                "wage_panel": econometrics_model.load(
                    "wage_panel", ["csv", "xlsx"], {}, {"wage_panel": "wage_panel"}
                ).set_index(["nr", "year"])
            },
            {
                "educ-wage_panel": {"educ": None, "wage_panel": None},
                "married-wage_panel": {"married": None, "wage_panel": None},
                "lwage-wage_panel": {"lwage": None, "wage_panel": None},
                "hisp-wage_panel": {"hisp": None, "wage_panel": None},
                "black-wage_panel": {"black": None, "wage_panel": None},
            },
        )
    ],
)
def test_get_re(recorder, regression_variables, data, datasets):
    _, _, _, model = regression_model.get_re(
        regression_variables=regression_variables,
        data=data,
        datasets=datasets,
    )

    result = pd.DataFrame([model.params])

    recorder.capture(result, float_format="%.5f")


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data, datasets",
    [
        (
            [
                "educ-wage_panel",
                "married-wage_panel",
                "lwage-wage_panel",
                "hisp-wage_panel",
                "black-wage_panel",
            ],
            {
                "wage_panel": econometrics_model.load(
                    "wage_panel", ["csv", "xlsx"], {}, {"wage_panel": "wage_panel"}
                ).set_index(["nr", "year"])
            },
            {
                "educ-wage_panel": {"educ": None, "wage_panel": None},
                "married-wage_panel": {"married": None, "wage_panel": None},
                "lwage-wage_panel": {"lwage": None, "wage_panel": None},
                "hisp-wage_panel": {"hisp": None, "wage_panel": None},
                "black-wage_panel": {"black": None, "wage_panel": None},
            },
        )
    ],
)
def test_get_bols(recorder, regression_variables, data, datasets):
    _, _, _, model = regression_model.get_bols(
        regression_variables=regression_variables,
        data=data,
        datasets=datasets,
    )

    result = pd.DataFrame([model.params])

    recorder.capture(result, float_format="%.5f")


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data, datasets",
    [
        (
            [
                "educ-wage_panel",
                "married-wage_panel",
                "lwage-wage_panel",
                "hisp-wage_panel",
                "black-wage_panel",
            ],
            {
                "wage_panel": econometrics_model.load(
                    "wage_panel", ["csv", "xlsx"], {}, {"wage_panel": "wage_panel"}
                ).set_index(["nr", "year"])
            },
            {
                "educ-wage_panel": {"educ": None, "wage_panel": None},
                "married-wage_panel": {"married": None, "wage_panel": None},
                "lwage-wage_panel": {"lwage": None, "wage_panel": None},
                "hisp-wage_panel": {"hisp": None, "wage_panel": None},
                "black-wage_panel": {"black": None, "wage_panel": None},
            },
        )
    ],
)
def test_get_fe(recorder, regression_variables, data, datasets):
    _, _, _, model = regression_model.get_fe(
        regression_variables=regression_variables,
        data=data,
        datasets=datasets,
    )

    result = pd.DataFrame([model.params])

    recorder.capture(result, float_format="%.5f")


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data, datasets",
    [
        (
            ["lwage-wage_panel", "married-wage_panel"],
            {
                "wage_panel": econometrics_model.load(
                    "wage_panel", ["csv", "xlsx"], {}, {"wage_panel": "wage_panel"}
                ).set_index(["nr", "year"])
            },
            {
                "married-wage_panel": {"married": None, "wage_panel": None},
                "lwage-wage_panel": {"lwage": None, "wage_panel": None},
            },
        )
    ],
)
def test_get_fdols(recorder, regression_variables, data, datasets):
    _, _, _, model = regression_model.get_fdols(
        regression_variables=regression_variables,
        data=data,
        datasets=datasets,
    )

    result = pd.DataFrame([model.params])

    recorder.capture(result, float_format="%.5f")


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data, datasets",
    [
        (
            [
                "married-wage_panel",
                "lwage-wage_panel",
                "hisp-wage_panel",
                "black-wage_panel",
            ],
            {
                "wage_panel": econometrics_model.load(
                    "wage_panel", ["csv", "xlsx"], {}, {"wage_panel": "wage_panel"}
                ).set_index(["nr", "year"])
            },
            {
                "educ-wage_panel": {"educ": None, "wage_panel": None},
                "married-wage_panel": {"married": None, "wage_panel": None},
                "lwage-wage_panel": {"lwage": None, "wage_panel": None},
                "hisp-wage_panel": {"hisp": None, "wage_panel": None},
                "black-wage_panel": {"black": None, "wage_panel": None},
            },
        )
    ],
)
def test_get_comparison(recorder, regression_variables, data, datasets):
    regressions = {"RE": {}, "FE": {}}

    _, _, _, regressions["RE"]["model"] = regression_model.get_re(
        regression_variables=regression_variables,
        data=data,
        datasets=datasets,
    )

    _, _, _, regressions["FE"]["model"] = regression_model.get_fe(
        regression_variables=regression_variables,
        data=data,
        datasets=datasets,
    )

    comparison_result = regression_model.get_comparison(regressions)

    recorder.capture(comparison_result.params, float_format="%.5f")


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data, datasets, show_regression",
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
            True,
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
            True,
        ),
    ],
)
def test_get_dwat(recorder, regression_variables, data, datasets, show_regression):
    _, _, _, model = regression_model.get_ols(
        regression_variables=regression_variables,
        data=data,
        datasets=datasets,
        show_regression=show_regression,
    )

    result = regression_model.get_dwat(model.resid).round(5)

    recorder.capture(result)


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data, datasets, show_regression, lags",
    [
        (
            ["ARMED-longley", "GNP-longley", "TOTEMP-longley", "POP-longley"],
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
            True,
            3,
        ),
        (
            ["GNP-longley", "POP-longley"],
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
            True,
            1,
        ),
    ],
)
def test_get_bgod(
    recorder, regression_variables, data, datasets, show_regression, lags
):
    _, _, _, model = regression_model.get_ols(
        regression_variables=regression_variables,
        data=data,
        datasets=datasets,
        show_regression=show_regression,
    )

    lm_stat, p_value, f_stat, fp_value = regression_model.get_bgod(model, lags)

    result = pd.DataFrame([lm_stat, p_value, f_stat, fp_value])

    recorder.capture(result, float_format="%.5f")


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "regression_variables, data, datasets, show_regression",
    [
        (
            ["GNP-longley", "TOTEMP-longley", "POP-longley"],
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
            True,
        ),
        (
            ["POP-longley", "GNP-longley"],
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
            True,
        ),
    ],
)
def test_get_bpag(recorder, regression_variables, data, datasets, show_regression):
    _, _, _, model = regression_model.get_ols(
        regression_variables=regression_variables,
        data=data,
        datasets=datasets,
        show_regression=show_regression,
    )

    lm_stat, p_value, f_stat, fp_value = regression_model.get_bpag(model)

    result = pd.DataFrame([lm_stat, p_value, f_stat, fp_value])

    recorder.capture(result, float_format="%.5f")
