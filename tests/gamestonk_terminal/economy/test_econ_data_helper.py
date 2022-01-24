# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.economy import econ_data_helper

STOCK_DF = pd.DataFrame(
    data={
        "Open": {
            pd.Timestamp("2022-01-20 00:00:00"): 101.05999755859375,
            pd.Timestamp("2022-01-21 00:00:00"): 102.63999938964844,
        },
        "High": {
            pd.Timestamp("2022-01-20 00:00:00"): 102.77999877929688,
            pd.Timestamp("2022-01-21 00:00:00"): 103.75,
        },
        "Low": {
            pd.Timestamp("2022-01-20 00:00:00"): 100.68000030517578,
            pd.Timestamp("2022-01-21 00:00:00"): 102.33000183105469,
        },
        "Close": {
            pd.Timestamp("2022-01-20 00:00:00"): 102.0199966430664,
            pd.Timestamp("2022-01-21 00:00:00"): 102.91999816894531,
        },
        "Adj Close": {
            pd.Timestamp("2022-01-20 00:00:00"): 102.0199966430664,
            pd.Timestamp("2022-01-21 00:00:00"): 102.91999816894531,
        },
        "Volume": {
            pd.Timestamp("2022-01-20 00:00:00"): 5589700,
            pd.Timestamp("2022-01-21 00:00:00"): 5423100,
        },
        "date_id": {
            pd.Timestamp("2022-01-20 00:00:00"): 1,
            pd.Timestamp("2022-01-21 00:00:00"): 2,
        },
        "OC_High": {
            pd.Timestamp("2022-01-20 00:00:00"): 102.0199966430664,
            pd.Timestamp("2022-01-21 00:00:00"): 102.91999816894531,
        },
        "OC_Low": {
            pd.Timestamp("2022-01-20 00:00:00"): 101.05999755859375,
            pd.Timestamp("2022-01-21 00:00:00"): 102.63999938964844,
        },
        "OC_High_trend": {
            pd.Timestamp("2022-01-20 00:00:00"): 102.0199966430664,
            pd.Timestamp("2022-01-21 00:00:00"): 102.91999816894531,
        },
        "OC_Low_trend": {
            pd.Timestamp("2022-01-20 00:00:00"): 101.05999755859375,
            pd.Timestamp("2022-01-21 00:00:00"): 102.63999938964844,
        },
    }
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
            ("date", "MOCK_DATE"),
        ],
    }


@pytest.mark.vcr
def test_draw_graph(mocker):
    # MOCK PLOT
    mock_plot = mocker.Mock()
    mocker.patch(
        target="gamestonk_terminal.economy.econ_data_helper.mpf.plot",
        new=mock_plot,
    )

    econ_data_helper.draw_graph(
        ticker="PM",
        report_cache_dir=None,
        time_delta=3,
        line_type="candle",
        draw_mas=(20, 50),
        draw_volume=True,
        high_trend=True,
        low_trend=True,
    )

    mock_plot.assert_called_once()


@pytest.mark.vcr(record_mode="none")
def test_draw_graph_cache_with_file(mocker):
    # MOCK IS_FILE
    mocker.patch(
        target="gamestonk_terminal.economy.econ_data_helper.os.path.isfile",
        return_value=True,
    )

    # MOCK READ_PICKLE
    mocker.patch(
        target="gamestonk_terminal.economy.econ_data_helper.pd.read_pickle",
        return_value=STOCK_DF,
    )

    # MOCK PLOT
    mock_plot = mocker.Mock()
    mocker.patch(
        target="gamestonk_terminal.economy.econ_data_helper.mpf.plot",
        new=mock_plot,
    )

    # MOCK CACHE_DIR
    mock_cache_dir = "MOCK_CACHE_DIR"

    econ_data_helper.draw_graph(
        ticker="PM",
        report_cache_dir=mock_cache_dir,
        time_delta=3,
        line_type="candle",
        draw_mas=(20, 50),
        draw_volume=True,
        high_trend=True,
        low_trend=True,
    )

    mock_plot.assert_called_once()


@pytest.mark.vcr(record_mode="none")
def test_draw_graph_cache_without_file(mocker):
    # MOCK IS_FILE
    mocker.patch(
        target="gamestonk_terminal.economy.econ_data_helper.os.path.isfile",
        return_value=False,
    )

    # MOCK LOAD_TICKER
    mocker.patch(
        target="gamestonk_terminal.economy.econ_data_helper.stocks_helper.load_ticker",
        return_value=STOCK_DF,
    )

    # MOCK FIND_TRENDLINE
    mocker.patch(
        target="gamestonk_terminal.economy.econ_data_helper.stocks_helper.find_trendline",
        return_value=STOCK_DF,
    )

    # MOCK TO_PICKLE
    mocker.patch(
        target="gamestonk_terminal.economy.econ_data_helper.pd.DataFrame.to_pickle",
        return_value=STOCK_DF,
    )

    # MOCK PLOT
    mock_plot = mocker.Mock()
    mocker.patch(
        target="gamestonk_terminal.economy.econ_data_helper.mpf.plot",
        new=mock_plot,
    )

    # MOCK CACHE_DIR
    mock_cache_dir = "MOCK_CACHE_DIR"

    econ_data_helper.draw_graph(
        ticker="PM",
        report_cache_dir=mock_cache_dir,
        time_delta=3,
        line_type="candle",
        draw_mas=(20, 50),
        draw_volume=True,
        high_trend=True,
        low_trend=True,
    )

    mock_plot.assert_called_once()
