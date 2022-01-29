# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
try:
    from gamestonk_terminal.economy.fred.prediction import pred_controller
except ImportError:
    pytest.skip(allow_module_level=True)

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111

CURRENT_SERIES = {
    "GDPC1": {
        "title": "MOCK_TITLE_11",
        "units_short": "MOCK_UNITS_SHORT_11",
    }
}
GET_SERIES_DATA = pd.Series(
    data={
        pd.Timestamp("2020-01-01 00:00:00"): 18951.992,
        pd.Timestamp("2020-04-01 00:00:00"): 17258.205,
        pd.Timestamp("2020-07-01 00:00:00"): 18560.774,
        pd.Timestamp("2020-10-01 00:00:00"): 18767.778,
        pd.Timestamp("2021-01-01 00:00:00"): 19055.655,
        pd.Timestamp("2021-04-01 00:00:00"): 19368.31,
        pd.Timestamp("2021-07-01 00:00:00"): 19478.893,
        pd.Timestamp("2021-10-01 00:00:00"): 19805.962,
    }
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.vcr(record_mode="none")
def test_completer(mocker):
    path_controller = "gamestonk_terminal.economy.fred.prediction.pred_controller"

    # MOCK GTFF
    mocker.patch(
        target=f"{path_controller}.gtff.USE_PROMPT_TOOLKIT",
        new=True,
    )

    # MOCK SESSION
    mocker.patch(
        target=f"{path_controller}.session",
    )

    # MOCK GET_SERIES_DATA
    mocker.patch(
        target=f"{path_controller}.fred_model.get_series_data",
        return_value=GET_SERIES_DATA,
    )

    pred_controller.PredictionTechniquesController(
        current_series=CURRENT_SERIES, queue=None
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "current_series, expected",
    [(CURRENT_SERIES, ["economy", "fred", "pred", "add GDPC1"]), ({}, [])],
)
def test_custom_reset(current_series, expected, mocker):
    path_controller = "gamestonk_terminal.economy.fred.prediction.pred_controller"

    # MOCK GET_SERIES_DATA
    mocker.patch(
        target=f"{path_controller}.fred_model.get_series_data",
        return_value=GET_SERIES_DATA,
    )

    controller = pred_controller.PredictionTechniquesController(
        current_series=CURRENT_SERIES, queue=None
    )
    controller.current_series = current_series

    result = controller.custom_reset()

    assert result == expected


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help(mocker):
    path_controller = "gamestonk_terminal.economy.fred.prediction.pred_controller"

    # MOCK GET_SERIES_DATA
    mocker.patch(
        target=f"{path_controller}.fred_model.get_series_data",
        return_value=GET_SERIES_DATA,
    )

    controller = pred_controller.PredictionTechniquesController(
        current_series=CURRENT_SERIES, queue=None
    )

    controller.long_id = len("MOCK_SERIES_ID_1")
    controller.current_series["MOCK_SERIES_ID_1"] = {
        "title": "MOCK_TITLE_11",
        "units_short": "MOCK_UNITS_SHORT_11",
    }
    controller.current_series["MOCK_SERIES_ID_2"] = {
        "title": "MOCK_TITLE_21",
        "units_short": "MOCK_UNITS_SHORT_21",
    }
    controller.print_help()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_ets",
            [],
            "ets_view.display_exponential_smoothing",
            [],
            dict(),
        ),
        (
            "call_knn",
            [
                "--input=100",
                "--days=2",
                "--jumps=3",
                "--neighbors=4",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_knn",
            [
                "--input=1",
                "--days=2",
                "--jumps=3",
                "--neighbors=4",
            ],
            "knn_view.display_k_nearest_neighbors",
            [],
            dict(),
        ),
        (
            "call_mlp",
            [
                "--input=100",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_mlp",
            [
                "--input=1",
            ],
            "neural_networks_view.display_mlp",
            [],
            dict(),
        ),
        (
            "call_rnn",
            [
                "--input=100",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_rnn",
            [
                "--input=1",
            ],
            "neural_networks_view.display_rnn",
            [],
            dict(),
        ),
        (
            "call_lstm",
            [
                "--input=100",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_lstm",
            [
                "--input=1",
            ],
            "neural_networks_view.display_lstm",
            [],
            dict(),
        ),
        (
            "call_conv1d",
            [
                "--input=100",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_conv1d",
            [
                "--input=1",
            ],
            "neural_networks_view.display_conv1d",
            [],
            dict(),
        ),
        (
            "call_mc",
            [],
            "mc_view.display_mc_forecast",
            [],
            dict(),
        ),
    ],
)
def test_call_func(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "gamestonk_terminal.economy.fred.prediction.pred_controller"

    # MOCK GET_SERIES_DATA
    mocker.patch(
        target=f"{path_controller}.fred_model.get_series_data",
        return_value=GET_SERIES_DATA,
    )

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = pred_controller.PredictionTechniquesController(
            current_series=CURRENT_SERIES, queue=None
        )

        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = pred_controller.PredictionTechniquesController(
            current_series=CURRENT_SERIES, queue=None
        )

        getattr(controller, tested_func)(other_args)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_call_load(mocker):
    path_controller = "gamestonk_terminal.economy.fred.prediction.pred_controller"

    # MOCK GET_SERIES_DATA
    mocker.patch(
        target=f"{path_controller}.fred_model.get_series_data",
        return_value=GET_SERIES_DATA,
    )

    controller = pred_controller.PredictionTechniquesController(
        current_series=CURRENT_SERIES, queue=None
    )

    other_args = [
        "GDPC1",
        "-s=2020-01-01",
    ]
    controller.call_load(other_args=other_args)
