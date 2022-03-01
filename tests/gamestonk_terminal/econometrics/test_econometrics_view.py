# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.econometrics import econometrics_model, econometrics_view


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "datasets, dataset_name",
    [
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
        )
    ],
)
def test_show_options(datasets, dataset_name):
    econometrics_view.show_options(datasets=datasets, dataset_name=dataset_name)


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "data, dataset, column, plot",
    [
        (
            econometrics_model.load(
                "sunspots", ["csv", "xlsx"], {}, {"sunspots": "sunspots"}
            )["SUNACTIVITY"],
            "Sunset",
            "Sunactivity",
            False,
        ),
        (
            econometrics_model.load(
                "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
            )["infl"],
            "Macrodata",
            "Inflation",
            False,
        ),
        (
            econometrics_model.load(
                "elnino", ["csv", "xlsx"], {}, {"elnino": "elnino"}
            )["JAN"],
            "El Nino",
            "January",
            False,
        ),
    ],
)
def test_display_norm(data, dataset, column, plot):
    econometrics_view.display_norm(data=data, dataset=dataset, column=column, plot=plot)


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "df, dataset_name, column_name, fuller_reg, kpss_reg",
    [
        (
            econometrics_model.load(
                "sunspots", ["csv", "xlsx"], {}, {"sunspots": "sunspots"}
            )["SUNACTIVITY"],
            "Sunspot",
            "Sunactivity",
            "c",
            "c",
        ),
        (
            econometrics_model.load(
                "sunspots", ["csv", "xlsx"], {}, {"sunspots": "sunspots"}
            )["SUNACTIVITY"],
            "Sunspot",
            "Sunactivity",
            "c",
            "ct",
        ),
        (
            econometrics_model.load(
                "sunspots", ["csv", "xlsx"], {}, {"sunspots": "sunspots"}
            )["SUNACTIVITY"],
            "Sunspot",
            "Sunactivity",
            "ct",
            "c",
        ),
        (
            econometrics_model.load(
                "sunspots", ["csv", "xlsx"], {}, {"sunspots": "sunspots"}
            )["SUNACTIVITY"],
            "Sunspot",
            "Sunactivity",
            "ctt",
            "c",
        ),
        (
            econometrics_model.load(
                "sunspots", ["csv", "xlsx"], {}, {"sunspots": "sunspots"}
            )["SUNACTIVITY"],
            "Sunspot",
            "Sunactivity",
            "nc",
            "c",
        ),
    ],
)
def test_display_root(df, dataset_name, column_name, fuller_reg, kpss_reg):
    econometrics_view.display_root(
        df=df,
        dataset_name=dataset_name,
        column_name=column_name,
        fuller_reg=fuller_reg,
        kpss_reg=kpss_reg,
    )


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "time_series_y, time_series_x, lags, confidence_level",
    [
        (
            econometrics_model.load(
                "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
            )["realgdp"],
            econometrics_model.load(
                "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
            )["pop"],
            3,
            0.05,
        ),
        (
            econometrics_model.load(
                "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
            )["realgovt"],
            econometrics_model.load(
                "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
            )["realinv"],
            2,
            0.10,
        ),
        (
            econometrics_model.load(
                "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
            )["realdpi"],
            econometrics_model.load(
                "macrodata", ["csv", "xlsx"], {}, {"macrodata": "macrodata"}
            )["cpi"],
            1,
            0.01,
        ),
    ],
)
def test_display_granger(time_series_y, time_series_x, lags, confidence_level):
    econometrics_view.display_granger(
        time_series_y=time_series_y,
        time_series_x=time_series_x,
        lags=lags,
        confidence_level=confidence_level,
    )


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "datasets, significant, plot",
    [
        (
            {
                "y": econometrics_model.load(
                    "interest_inflation",
                    ["csv", "xlsx"],
                    {},
                    {"interest_inflation": "interest_inflation"},
                )["Dp"],
                "x": econometrics_model.load(
                    "interest_inflation",
                    ["csv", "xlsx"],
                    {},
                    {"interest_inflation": "interest_inflation"},
                )["R"],
            },
            True,
            False,
        ),
        (
            {
                "y": econometrics_model.load(
                    "interest_inflation",
                    ["csv", "xlsx"],
                    {},
                    {"interest_inflation": "interest_inflation"},
                )["Dp"],
                "x": econometrics_model.load(
                    "interest_inflation",
                    ["csv", "xlsx"],
                    {},
                    {"interest_inflation": "interest_inflation"},
                )["R"],
            },
            False,
            False,
        ),
    ],
)
def test_get_engle_granger_two_step_cointegration_test(datasets, significant, plot):
    econometrics_view.display_cointegration_test(
        datasets=datasets, significant=significant, plot=plot
    )
