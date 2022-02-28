# IMPORTATION STANDARD
import pandas as pd

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.statistics import statistics_model


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "file, file_types, data_files, data_examples",
    [
        ("wage_panel", ["csv", "xlsx"], {}, {"wage_panel": "wage_panel"}),
        ("sunspots", ["csv", "xlsx"], {}, {"sunspots": "sunspots"}),
    ],
)
def test_load(recorder, file, file_types, data_files, data_examples):
    result = statistics_model.load(
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
                "heart": statistics_model.load(
                    "heart", ["csv", "xlsx"], {}, {"heart": "heart"}
                )
            },
            "heart",
        ),
        (
            {
                "heart": statistics_model.load(
                    "heart", ["csv", "xlsx"], {}, {"heart": "heart"}
                ),
                "macrodata": statistics_model.load(
                    "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
                ),
            },
            None,
        ),
    ],
)
def test_options(recorder, datasets, dataset_name):
    result = statistics_model.get_options(datasets=datasets, dataset_name=dataset_name)

    recorder.capture_list(result.values())


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "dataset, fill, drop, limit",
    [
        (
            statistics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            "rfill",
            None,
            5,
        ),
        (
            statistics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            "cfill",
            None,
            5,
        ),
        (
            statistics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            "rbfill",
            None,
            5,
        ),
        (
            statistics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            "cbfill",
            None,
            5,
        ),
        (
            statistics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            "rffill",
            None,
            5,
        ),
        (
            statistics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            "cffill",
            None,
            5,
        ),
        (
            statistics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            None,
            "rdrop",
            5,
        ),
        (
            statistics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            None,
            "cdrop",
            5,
        ),
        (
            statistics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            "rfill",
            "rdrop",
            5,
        ),
        (
            statistics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            "rfill",
            "cdrop",
            5,
        ),
        (
            statistics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            "rfill",
            None,
            10,
        ),
        (
            statistics_model.load(
                "longley", ["csv", "xlsx"], {}, {"longley": "longley"}
            ),
            None,
            "rdrop",
            10,
        ),
    ],
)
def test_clean(recorder, dataset, fill, drop, limit):
    result = statistics_model.clean(dataset=dataset, fill=fill, drop=drop, limit=limit)

    recorder.capture(result)


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "data",
    [
        (
            statistics_model.load(
                "sunspots", ["csv", "xlsx"], {}, {"sunspots": "sunspots"}
            )["SUNACTIVITY"]
        ),
        (
            statistics_model.load(
                "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
            )["infl"]
        ),
        (
            statistics_model.load("elnino", ["csv", "xlsx"], {}, {"elnino": "elnino"})[
                "JAN"
            ]
        ),
    ],
)
def test_get_normality(recorder, data):
    result = statistics_model.get_normality(data=data)

    recorder.capture(result)


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "df, fuller_reg, kpss_reg",
    [
        (
            statistics_model.load(
                "sunspots", ["csv", "xlsx"], {}, {"sunspots": "sunspots"}
            )["SUNACTIVITY"],
            "c",
            "c",
        ),
        (
            statistics_model.load(
                "sunspots", ["csv", "xlsx"], {}, {"sunspots": "sunspots"}
            )["SUNACTIVITY"],
            "c",
            "ct",
        ),
        (
            statistics_model.load(
                "sunspots", ["csv", "xlsx"], {}, {"sunspots": "sunspots"}
            )["SUNACTIVITY"],
            "ct",
            "c",
        ),
        (
            statistics_model.load(
                "sunspots", ["csv", "xlsx"], {}, {"sunspots": "sunspots"}
            )["SUNACTIVITY"],
            "ctt",
            "c",
        ),
        (
            statistics_model.load(
                "sunspots", ["csv", "xlsx"], {}, {"sunspots": "sunspots"}
            )["SUNACTIVITY"],
            "nc",
            "c",
        ),
    ],
)
def test_get_root(recorder, df, fuller_reg, kpss_reg):
    result = statistics_model.get_root(df=df, fuller_reg=fuller_reg, kpss_reg=kpss_reg)

    recorder.capture(result)


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "time_series_y, time_series_x, lags",
    [
        (
            statistics_model.load(
                "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
            )["realgdp"],
            statistics_model.load(
                "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
            )["pop"],
            3,
        ),
        (
            statistics_model.load(
                "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
            )["realgovt"],
            statistics_model.load(
                "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
            )["realinv"],
            2,
        ),
        (
            statistics_model.load(
                "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
            )["realdpi"],
            statistics_model.load(
                "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
            )["cpi"],
            1,
        ),
    ],
)
def test_get_granger_causality(recorder, time_series_y, time_series_x, lags):
    result = statistics_model.get_granger_causality(
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
            statistics_model.load(
                "interest_inflation",
                ["csv", "xlsx"],
                {},
                {"interest_inflation": "interest_inflation"},
            )["Dp"],
            statistics_model.load(
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
    ) = statistics_model.get_engle_granger_two_step_cointegration_test(y=y, x=x)

    recorder.capture(pd.DataFrame([c, gamma, alpha, z, adfstat, pvalue]))
