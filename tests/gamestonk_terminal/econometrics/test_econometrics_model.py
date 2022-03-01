# IMPORTATION STANDARD
import pandas as pd

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.econometrics import econometrics_model


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "file, file_types, data_files, data_examples",
    [
        ("wage_panel", ["csv", "xlsx"], {}, {"wage_panel": "wage_panel"}),
        ("sunspots", ["csv", "xlsx"], {}, {"sunspots": "sunspots"}),
    ],
)
def test_load(recorder, file, file_types, data_files, data_examples):
    result = econometrics_model.load(
        file=file,
        file_types=file_types,
        data_files=data_files,
        data_examples=data_examples,
    )

    recorder.capture(result)


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "datasets, dataset_name",
    [
        (
            {
                "heart": econometrics_model.load(
                    "heart", ["csv", "xlsx"], {}, {"heart": "heart"}
                )
            },
            "heart",
        ),
        (
            {
                "heart": econometrics_model.load(
                    "heart", ["csv", "xlsx"], {}, {"heart": "heart"}
                ),
                "macrodata": econometrics_model.load(
                    "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
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
            econometrics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            "rfill",
            None,
            5,
        ),
        (
            econometrics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            "cfill",
            None,
            5,
        ),
        (
            econometrics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            "rbfill",
            None,
            5,
        ),
        (
            econometrics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            "cbfill",
            None,
            5,
        ),
        (
            econometrics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            "rffill",
            None,
            5,
        ),
        (
            econometrics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            "cffill",
            None,
            5,
        ),
        (
            econometrics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            None,
            "rdrop",
            5,
        ),
        (
            econometrics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            None,
            "cdrop",
            5,
        ),
        (
            econometrics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            "rfill",
            "rdrop",
            5,
        ),
        (
            econometrics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            "rfill",
            "cdrop",
            5,
        ),
        (
            econometrics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            "rfill",
            None,
            10,
        ),
        (
            econometrics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
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
        (
            econometrics_model.load(
                "sunspots", ["csv", "xlsx"], {}, {"sunspots": "sunspots"}
            )["SUNACTIVITY"]
        ),
        (
            econometrics_model.load(
                "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
            )["infl"]
        ),
        (
            econometrics_model.load(
                "elnino", ["csv", "xlsx"], {}, {"elnino": "elnino"}
            )["JAN"]
        ),
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
            econometrics_model.load(
                "sunspots", ["csv", "xlsx"], {}, {"sunspots": "sunspots"}
            )["SUNACTIVITY"],
            "c",
            "c",
        ),
        (
            econometrics_model.load(
                "sunspots", ["csv", "xlsx"], {}, {"sunspots": "sunspots"}
            )["SUNACTIVITY"],
            "c",
            "ct",
        ),
        (
            econometrics_model.load(
                "sunspots", ["csv", "xlsx"], {}, {"sunspots": "sunspots"}
            )["SUNACTIVITY"],
            "ct",
            "c",
        ),
        (
            econometrics_model.load(
                "sunspots", ["csv", "xlsx"], {}, {"sunspots": "sunspots"}
            )["SUNACTIVITY"],
            "ctt",
            "c",
        ),
        (
            econometrics_model.load(
                "sunspots", ["csv", "xlsx"], {}, {"sunspots": "sunspots"}
            )["SUNACTIVITY"],
            "nc",
            "c",
        ),
    ],
)
def test_get_root(recorder, df, fuller_reg, kpss_reg):
    result = econometrics_model.get_root(
        df=df, fuller_reg=fuller_reg, kpss_reg=kpss_reg
    )

    recorder.capture(result, float_format="%.5f")


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "time_series_y, time_series_x, lags",
    [
        (
            econometrics_model.load(
                "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
            )["realgdp"],
            econometrics_model.load(
                "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
            )["pop"],
            3,
        ),
        (
            econometrics_model.load(
                "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
            )["realgovt"],
            econometrics_model.load(
                "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
            )["realinv"],
            2,
        ),
        (
            econometrics_model.load(
                "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
            )["realdpi"],
            econometrics_model.load(
                "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
            )["cpi"],
            1,
        ),
    ],
)
def test_get_granger_causality(recorder, time_series_y, time_series_x, lags):
    result = econometrics_model.get_granger_causality(
        time_series_y=time_series_y, time_series_x=time_series_x, lags=lags
    )

    # The first item is taken since the second item contains Statsmodels
    # objects (which change their identifier on every iteration)
    recorder.capture_list(result[lags][0])


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "y, x",
    [
        (
            econometrics_model.load(
                "interest_inflation",
                ["csv", "xlsx"],
                {},
                {"interest_inflation": "interest_inflation"},
            )["Dp"],
            econometrics_model.load(
                "interest_inflation",
                ["csv", "xlsx"],
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
    ) = econometrics_model.get_engle_granger_two_step_cointegration_test(y=y, x=x)

    result = pd.DataFrame([c, gamma, alpha, adfstat, pvalue])

    recorder.capture(result, float_format="%.5f")
    recorder.capture(z, float_format="%.5f")
