# IMPORTATION STANDARD
import pandas as pd

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.econometrics import econometrics_model
from openbb_terminal.common import common_model


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "file, data_files, data_examples",
    [
        ("wage_panel", {}, {"wage_panel": "wage_panel"}),
        ("sunspots", {}, {"sunspots": "sunspots"}),
    ],
)
def test_load(recorder, file, data_files, data_examples):
    result = common_model.load(
        file=file,
        data_files=data_files,
        data_examples=data_examples,
    )

    recorder.capture(result)


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "datasets, dataset_name",
    [
        (
            {"heart": common_model.load("heart", {}, {"heart": "heart"})},
            "heart",
        ),
        (
            {
                "heart": common_model.load("heart", {}, {"heart": "heart"}),
                "macrodata": common_model.load(
                    "macrodata", {}, {"macrodata": "macrodata"}
                ),
            },
            None,
        ),
    ],
)
def test_options(recorder, datasets, dataset_name):
    result = econometrics_model.get_options(
        datasets=datasets, dataset_name=dataset_name
    )

    recorder.capture_list(result.values())


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "dataset, fill, drop, limit",
    [
        (
            common_model.load("longley", {}, {"longley": "longley"}),
            "rfill",
            None,
            5,
        ),
        (
            common_model.load("longley", {}, {"longley": "longley"}),
            "cfill",
            None,
            5,
        ),
        (
            common_model.load("longley", {}, {"longley": "longley"}),
            "rbfill",
            None,
            5,
        ),
        (
            common_model.load("longley", {}, {"longley": "longley"}),
            "cbfill",
            None,
            5,
        ),
        (
            common_model.load("longley", {}, {"longley": "longley"}),
            "rffill",
            None,
            5,
        ),
        (
            common_model.load("longley", {}, {"longley": "longley"}),
            "cffill",
            None,
            5,
        ),
        (
            common_model.load("longley", {}, {"longley": "longley"}),
            None,
            "rdrop",
            5,
        ),
        (
            common_model.load("longley", {}, {"longley": "longley"}),
            None,
            "cdrop",
            5,
        ),
        (
            common_model.load("longley", {}, {"longley": "longley"}),
            "rfill",
            "rdrop",
            5,
        ),
        (
            common_model.load("longley", {}, {"longley": "longley"}),
            "rfill",
            "cdrop",
            5,
        ),
        (
            common_model.load("longley", {}, {"longley": "longley"}),
            "rfill",
            None,
            10,
        ),
        (
            common_model.load("longley", {}, {"longley": "longley"}),
            None,
            "rdrop",
            10,
        ),
    ],
)
def test_clean(recorder, dataset, fill, drop, limit):
    result = econometrics_model.clean(
        dataset=dataset, fill=fill, drop=drop, limit=limit
    )

    recorder.capture(result)


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "data",
    [
        (common_model.load("sunspots", {}, {"sunspots": "sunspots"})["SUNACTIVITY"]),
        (common_model.load("macrodata", {}, {"macrodata": "macrodata"})["infl"]),
        (common_model.load("elnino", {}, {"elnino": "elnino"})["JAN"]),
    ],
)
def test_get_normality(recorder, data):
    result = econometrics_model.get_normality(data=data)

    recorder.capture(result, float_format="%.5f")


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "df, fuller_reg, kpss_reg",
    [
        (
            common_model.load("sunspots", {}, {"sunspots": "sunspots"})["SUNACTIVITY"],
            "c",
            "c",
        ),
        (
            common_model.load("sunspots", {}, {"sunspots": "sunspots"})["SUNACTIVITY"],
            "c",
            "ct",
        ),
        (
            common_model.load("sunspots", {}, {"sunspots": "sunspots"})["SUNACTIVITY"],
            "ct",
            "c",
        ),
        (
            common_model.load("sunspots", {}, {"sunspots": "sunspots"})["SUNACTIVITY"],
            "ctt",
            "c",
        ),
        (
            common_model.load("sunspots", {}, {"sunspots": "sunspots"})["SUNACTIVITY"],
            "n",
            "c",
        ),
    ],
)
def test_get_root(recorder, df, fuller_reg, kpss_reg):
    result = econometrics_model.get_root(
        data=df, fuller_reg=fuller_reg, kpss_reg=kpss_reg
    )

    recorder.capture(result, float_format="%.5f")


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "time_series_y, time_series_x, lags",
    [
        (
            common_model.load("macrodata", {}, {"macrodata": "macrodata"})["realgdp"],
            common_model.load("macrodata", {}, {"macrodata": "macrodata"})["pop"],
            3,
        ),
        (
            common_model.load("macrodata", {}, {"macrodata": "macrodata"})["realgovt"],
            common_model.load("macrodata", {}, {"macrodata": "macrodata"})["realinv"],
            2,
        ),
        (
            common_model.load("macrodata", {}, {"macrodata": "macrodata"})["realdpi"],
            common_model.load("macrodata", {}, {"macrodata": "macrodata"})["cpi"],
            1,
        ),
    ],
)
def test_get_granger_causality(recorder, time_series_y, time_series_x, lags):
    result = econometrics_model.get_granger_causality(
        dependent_series=time_series_y, independent_series=time_series_x, lags=lags
    ).applymap(lambda x: round(float(x), 5) if x != "-" else x)

    recorder.capture(result)


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "y, x",
    [
        (
            common_model.load(
                "interest_inflation",
                {},
                {"interest_inflation": "interest_inflation"},
            )["Dp"],
            common_model.load(
                "interest_inflation",
                {},
                {"interest_inflation": "interest_inflation"},
            )["R"],
        )
    ],
)
def test_get_engle_granger_two_step_cointegration_test(recorder, y, x):
    (
        c,
        gamma,
        alpha,
        z,
        adfstat,
        pvalue,
    ) = econometrics_model.get_engle_granger_two_step_cointegration_test(
        dependent_series=y, independent_series=x
    )

    result = pd.DataFrame([c, gamma, alpha, adfstat, pvalue])

    recorder.capture(result, float_format="%.5f")
    recorder.capture(z, float_format="%.5f")
