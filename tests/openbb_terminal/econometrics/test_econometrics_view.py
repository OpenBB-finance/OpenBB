# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.econometrics import econometrics_view
from openbb_terminal.common import common_model


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "datasets, dataset_name",
    [
        (
            {
                "heart": common_model.load("heart", {}, {"heart": "heart"}),
                "macrodata": common_model.load(
                    "macrodata", {}, {"macrodata": "macrodata"}
                ),
            },
            None,
        )
    ],
)
def test_show_options(datasets, dataset_name):
    econometrics_view.show_options(datasets=datasets, dataset_name=dataset_name)


@pytest.mark.skip
@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "data, dataset, column, plot",
    [
        (
            common_model.load("sunspots", {}, {"sunspots": "sunspots"})["SUNACTIVITY"],
            "Sunset",
            "Sunactivity",
            False,
        ),
        (
            common_model.load("macrodata", {}, {"macrodata": "macrodata"})["infl"],
            "Macrodata",
            "Inflation",
            False,
        ),
        (
            common_model.load("elnino", {}, {"elnino": "elnino"})["JAN"],
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
            common_model.load("sunspots", {}, {"sunspots": "sunspots"})["SUNACTIVITY"],
            "Sunspot",
            "Sunactivity",
            "c",
            "c",
        ),
        (
            common_model.load("sunspots", {}, {"sunspots": "sunspots"})["SUNACTIVITY"],
            "Sunspot",
            "Sunactivity",
            "c",
            "ct",
        ),
        (
            common_model.load("sunspots", {}, {"sunspots": "sunspots"})["SUNACTIVITY"],
            "Sunspot",
            "Sunactivity",
            "ct",
            "c",
        ),
        (
            common_model.load("sunspots", {}, {"sunspots": "sunspots"})["SUNACTIVITY"],
            "Sunspot",
            "Sunactivity",
            "ctt",
            "c",
        ),
        (
            common_model.load("sunspots", {}, {"sunspots": "sunspots"})["SUNACTIVITY"],
            "Sunspot",
            "Sunactivity",
            "n",
            "c",
        ),
    ],
)
def test_display_root(df, dataset_name, column_name, fuller_reg, kpss_reg):
    econometrics_view.display_root(
        data=df,
        dataset=dataset_name,
        column=column_name,
        fuller_reg=fuller_reg,
        kpss_reg=kpss_reg,
    )


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "time_series_y, time_series_x, lags, confidence_level",
    [
        (
            common_model.load("macrodata", {}, {"macrodata": "macrodata"})["realgdp"],
            common_model.load("macrodata", {}, {"macrodata": "macrodata"})["pop"],
            3,
            0.05,
        ),
        (
            common_model.load("macrodata", {}, {"macrodata": "macrodata"})["realgovt"],
            common_model.load("macrodata", {}, {"macrodata": "macrodata"})["realinv"],
            2,
            0.10,
        ),
        (
            common_model.load("macrodata", {}, {"macrodata": "macrodata"})["realdpi"],
            common_model.load("macrodata", {}, {"macrodata": "macrodata"})["cpi"],
            1,
            0.01,
        ),
    ],
)
def test_display_granger(time_series_y, time_series_x, lags, confidence_level):
    econometrics_view.display_granger(
        dependent_series=time_series_y,
        independent_series=time_series_x,
        lags=lags,
        confidence_level=confidence_level,
    )


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "datasets, significant, plot",
    [
        (
            [
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
            ],
            True,
            False,
        ),
        (
            [
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
            ],
            False,
            False,
        ),
    ],
)
def test_get_engle_granger_two_step_cointegration_test(datasets, significant, plot):
    econometrics_view.display_cointegration_test(
        *datasets, significant=significant, plot=plot
    )
