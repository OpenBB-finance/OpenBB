# IMPORTATION STANDARD
import os
from datetime import datetime

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
pred_controller = pytest.importorskip(
    modname="gamestonk_terminal.stocks.prediction_techniques.pred_controller",
    reason="Requires prediction dependencies, like tensorflow",
)

# pylint: disable=E1101
# pylint: disable=W0603

# pytest.skip(allow_module_level=True)


DF_STOCK = pd.DataFrame.from_dict(
    data={
        pd.Timestamp("2020-11-30 00:00:00"): {
            "Open": 75.69999694824219,
            "High": 76.08999633789062,
            "Low": 75.41999816894531,
            "Close": 75.75,
            "Adj Close": 71.90919494628906,
            "Volume": 5539100,
            "date_id": 1,
            "OC_High": 75.75,
            "OC_Low": 75.69999694824219,
        },
        pd.Timestamp("2020-12-01 00:00:00"): {
            "Open": 76.0199966430664,
            "High": 77.12999725341797,
            "Low": 75.69000244140625,
            "Close": 77.02999877929688,
            "Adj Close": 73.1242904663086,
            "Volume": 6791700,
            "date_id": 2,
            "OC_High": 77.02999877929688,
            "OC_Low": 76.0199966430664,
        },
    },
    orient="index",
)
EMPTY_DF = pd.DataFrame()

PRED_CONTROLLER = pred_controller.PredictionTechniquesController(
    ticker="MOCK_TICKER",
    start=datetime.strptime("2020-12-15", "%Y-%m-%d"),
    interval="1440min",
    stock=DF_STOCK,
)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_menu_quick_exit(mocker):
    mocker.patch("builtins.input", return_value="quit")
    mocker.patch(
        "gamestonk_terminal.stocks.prediction_techniques.pred_controller.session"
    )
    mocker.patch(
        "gamestonk_terminal.stocks.prediction_techniques.pred_controller.session.prompt",
        return_value="quit",
    )

    result_menu = pred_controller.menu(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
        interval="1440min",
        stock=DF_STOCK,
    )

    assert result_menu


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_menu_system_exit(mocker):
    class SystemExitSideEffect:
        def __init__(self):
            self.first_call = True

        def __call__(self, *args, **kwargs):
            if self.first_call:
                self.first_call = False
                raise SystemExit()
            return True

    mock_switch = mocker.Mock(side_effect=SystemExitSideEffect())
    mocker.patch("builtins.input", return_value="quit")
    mocker.patch(
        "gamestonk_terminal.stocks.prediction_techniques.pred_controller.session"
    )
    mocker.patch(
        "gamestonk_terminal.stocks.prediction_techniques.pred_controller.session.prompt",
        return_value="quit",
    )
    mocker.patch(
        "gamestonk_terminal.stocks.prediction_techniques.pred_controller.PredictionTechniquesController.switch",
        new=mock_switch,
    )

    pred_controller.menu(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
        interval="1440min",
        stock=DF_STOCK,
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = pred_controller.PredictionTechniquesController(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
        interval="1440min",
        stock=DF_STOCK,
    )
    controller.print_help()


@pytest.mark.vcr(record_mode="none")
def test_switch_empty():
    controller = pred_controller.PredictionTechniquesController(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
        interval="1440min",
        stock=DF_STOCK,
    )
    result = controller.switch(an_input="")

    assert result is None


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_switch_help():
    controller = pred_controller.PredictionTechniquesController(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
        interval="1440min",
        stock=DF_STOCK,
    )
    result = controller.switch(an_input="?")

    assert result is None


@pytest.mark.vcr(record_mode="none")
def test_switch_cls(mocker):
    mocker.patch("os.system")
    controller = pred_controller.PredictionTechniquesController(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
        interval="1440min",
        stock=DF_STOCK,
    )
    result = controller.switch(an_input="cls")

    assert result is None
    os.system.assert_called_once_with("cls||clear")


@pytest.mark.vcr(record_mode="none")
def test_call_q():
    controller = pred_controller.PredictionTechniquesController(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
        interval="1440min",
        stock=DF_STOCK,
    )
    other_args = list()
    result = controller.call_q(other_args)

    assert result is False


@pytest.mark.vcr(record_mode="none")
def test_call_quit():
    controller = pred_controller.PredictionTechniquesController(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
        interval="1440min",
        stock=DF_STOCK,
    )
    other_args = list()
    result = controller.call_quit(other_args)

    assert result is True


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, mocked_func, other_args, called_with",
    [
        (
            "call_ets",
            "ets_view.display_exponential_smoothing",
            [
                "--day=1",
                "--trend=A",
                "--seasonal=M",
                "--period=2",
                "--end=2020-12-15",
                "--export=png",
            ],
            dict(
                ticker="MOCK_TICKER",
                values=PRED_CONTROLLER.stock["AdjClose"],
                n_predict=1,
                trend="A",
                seasonal="M",
                seasonal_periods=2,
                s_end_date=datetime.strptime("2020-12-15", "%Y-%m-%d"),
                export="png",
            ),
        ),
        (
            "call_knn",
            "knn_view.display_k_nearest_neighbors",
            [
                "--input=1",
                "--days=2",
                "--jumps=3",
                "--neighbors=4",
                "--end=2020-12-01",
                "--test_size=0.1",
                "--no_shuffle",
            ],
            dict(
                ticker="MOCK_TICKER",
                data=PRED_CONTROLLER.stock["AdjClose"],
                n_neighbors=4,
                n_input_days=1,
                n_predict_days=2,
                test_size=0.1,
                end_date=datetime.strptime("2020-12-01", "%Y-%m-%d"),
                no_shuffle=False,
            ),
        ),
        (
            "call_regression",
            "regression_view.display_regression",
            [
                "4",
                "--input=1",
                "--days=2",
                "--jumps=3",
                "--end=2020-12-15",
                "--export=png",
            ],
            dict(
                dataset="MOCK_TICKER",
                values=PRED_CONTROLLER.stock["AdjClose"],
                poly_order=4,
                n_input=1,
                n_predict=2,
                n_jumps=3,
                s_end_date=datetime.strptime("2020-12-15", "%Y-%m-%d"),
                export="png",
            ),
        ),
        (
            "call_arima",
            "arima_view.display_arima",
            [
                "--days=1",
                "--ic=bic",
                "--seasonal",
                "--order=p,q,d",
                "--results",
                "--end=2020-12-15",
                "--export=png",
            ],
            dict(
                dataset="MOCK_TICKER",
                values=PRED_CONTROLLER.stock["AdjClose"],
                arima_order="p,q,d",
                n_predict=1,
                seasonal=True,
                ic="bic",
                results=True,
                s_end_date=datetime.strptime("2020-12-15", "%Y-%m-%d"),
                export="png",
            ),
        ),
        (
            "call_mlp",
            "neural_networks_view.display_mlp",
            [
                "--days=1",
                "--input=2",
                "--epochs=3",
                "--end=2020-12-15",
                "--batch_size=4",
                "--loops=5",
                # "--valid", "0.1",
                "--lr=0.01",
                "--no_shuffle",
            ],
            dict(
                dataset="MOCK_TICKER",
                data=PRED_CONTROLLER.stock["AdjClose"],
                n_input_days=2,
                n_predict_days=1,
                learning_rate=0.01,
                epochs=3,
                batch_size=4,
                test_size=0.1,
                n_loops=5,
                no_shuffle=False,
            ),
        ),
        (
            "call_rnn",
            "neural_networks_view.display_rnn",
            [
                "--days=1",
                "--input=2",
                "--epochs=3",
                "--end=2020-12-15",
                "--batch_size=4",
                "--loops=5",
                # "--valid", "0.1",
                "--lr=0.01",
                "--no_shuffle",
            ],
            dict(
                dataset="MOCK_TICKER",
                data=PRED_CONTROLLER.stock["AdjClose"],
                n_input_days=2,
                n_predict_days=1,
                learning_rate=0.01,
                epochs=3,
                batch_size=4,
                test_size=0.1,
                n_loops=5,
                no_shuffle=False,
            ),
        ),
        (
            "call_lstm",
            "neural_networks_view.display_lstm",
            [
                "--days=1",
                "--input=2",
                "--epochs=3",
                "--end=2020-12-15",
                "--batch_size=4",
                "--loops=5",
                # "--valid", "0.1",
                "--lr=0.01",
                "--no_shuffle",
            ],
            dict(
                dataset="MOCK_TICKER",
                data=PRED_CONTROLLER.stock["AdjClose"],
                n_input_days=2,
                n_predict_days=1,
                learning_rate=0.01,
                epochs=3,
                batch_size=4,
                test_size=0.1,
                n_loops=5,
                no_shuffle=False,
            ),
        ),
        (
            "call_conv1d",
            "neural_networks_view.display_conv1d",
            [
                "--days=1",
                "--input=2",
                "--epochs=3",
                "--end=2020-12-15",
                "--batch_size=4",
                "--loops=5",
                # "--valid", "0.1",
                "--lr=0.01",
                "--no_shuffle",
            ],
            dict(
                dataset="MOCK_TICKER",
                data=PRED_CONTROLLER.stock["AdjClose"],
                n_input_days=2,
                n_predict_days=1,
                learning_rate=0.01,
                epochs=3,
                batch_size=4,
                test_size=0.1,
                n_loops=5,
                no_shuffle=False,
            ),
        ),
        (
            "call_mc",
            "mc_view.display_mc_forecast",
            [
                "--days=1",
                # "--num=2",
                "--dist=normal",
                "--export=png",
            ],
            dict(
                data=PRED_CONTROLLER.stock["AdjClose"],
                n_future=1,
                n_sims=100,
                use_log=False,
                export="png",
            ),
        ),
    ],
)
def test_call_func(tested_func, mocked_func, other_args, called_with, mocker):
    mock = mocker.Mock()
    mocker.patch(
        "gamestonk_terminal.stocks.prediction_techniques.pred_controller."
        + mocked_func,
        new=mock,
    )
    getattr(PRED_CONTROLLER, tested_func)(other_args=other_args)

    if isinstance(called_with, dict):
        mock.assert_called_once_with(**called_with)
    elif isinstance(called_with, list):
        mock.assert_called_once_with(*called_with)
    else:
        mock.assert_called_once()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_load",
        "call_ets",
        "call_knn",
        "call_regression",
        "call_arima",
        "call_mlp",
        "call_rnn",
        "call_lstm",
        "call_conv1d",
        "call_mc",
    ],
)
def test_call_func_no_parser(func, mocker):
    mock = mocker.Mock(return_value=None)
    mocker.patch.object(
        target=pred_controller,
        attribute="parse_known_args_and_warn",
        new=mock,
    )
    mocker.patch.object(
        target=pred_controller.pred_helper,
        attribute="parse_known_args_and_warn",
        new=mock,
    )
    controller = pred_controller.PredictionTechniquesController(
        ticker="MOCK_TICKER",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
        interval="1440min",
        stock=DF_STOCK.copy(),
    )

    func_result = getattr(controller, func)(other_args=["PM"])
    assert func_result is None
    getattr(pred_controller, "parse_known_args_and_warn").assert_called_once()
