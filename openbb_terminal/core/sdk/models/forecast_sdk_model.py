# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.sdk_helpers import Category
import openbb_terminal.core.sdk.sdk_init as lib


class ForecastRoot(Category):
    """Forecasting Module

    Attributes:
        `anom`: Get Quantile Anomaly Detection Data\n
        `anom_chart`: Display Quantile Anomaly Detection\n
        `atr`: Calculate the Average True Range of a variable based on a a specific stock ticker.\n
        `autoarima`: Performs Automatic ARIMA forecasting\n
        `autoarima_chart`: Display Automatic ARIMA model.\n
        `autoces`: Performs Automatic Complex Exponential Smoothing forecasting\n
        `autoces_chart`: Display Automatic Complex Exponential Smoothing Model\n
        `autoets`: Performs Automatic ETS forecasting\n
        `autoets_chart`: Display Automatic ETS (Error, Trend, Sesonality) Model\n
        `autoselect`: Performs Automatic Statistical forecasting\n
        `autoselect_chart`: Display Automatic Statistical Forecasting Model\n
        `brnn`: Performs Block RNN forecasting\n
        `brnn_chart`: Display BRNN forecast\n
        `clean`: Clean up NaNs from the dataset\n
        `combine`: Adds the given column of df2 to df1\n
        `corr`: Returns correlation for a given df\n
        `corr_chart`: Plot correlation coefficients for dataset features\n
        `delete`: Delete a column from a dataframe\n
        `delta`: Calculate the %change of a variable based on a specific column\n
        `desc`: Returns statistics for a given df\n
        `desc_chart`: Show descriptive statistics for a dataframe\n
        `ema`: A moving average provides an indication of the trend of the price movement\n
        `expo`: Performs Probabilistic Exponential Smoothing forecasting\n
        `expo_chart`: Display Probabilistic Exponential Smoothing forecast\n
        `export`: Export a dataframe to a file\n
        `linregr`: Perform Linear Regression Forecasting\n
        `linregr_chart`: Display Linear Regression Forecasting\n
        `load`: Load custom file into dataframe.\n
        `mom`: A momentum oscillator, which measures the percentage change between the current\n
        `mstl`: Performs MSTL forecasting\n
        `mstl_chart`: Display MSTL Model\n
        `nbeats`: Perform NBEATS Forecasting\n
        `nbeats_chart`: Display NBEATS forecast\n
        `nhits`: Performs Nhits forecasting\n
        `nhits_chart`: Display Nhits forecast\n
        `plot`: Plot data from a dataset\n
        `plot_chart`: Plot data from a dataset\n
        `regr`: Perform Regression Forecasting\n
        `regr_chart`: Display Regression Forecasting\n
        `rename`: Rename a column in a dataframe\n
        `rnn`: Perform RNN forecasting\n
        `rnn_chart`: Display RNN forecast\n
        `roc`: A momentum oscillator, which measures the percentage change between the current\n
        `rsi`: A momentum indicator that measures the magnitude of recent price changes to evaluate\n
        `rwd`: Performs Random Walk with Drift forecasting\n
        `rwd_chart`: Display Random Walk with Drift Model\n
        `season_chart`: Plot seasonality from a dataset\n
        `seasonalnaive`: Performs Seasonal Naive forecasting\n
        `seasonalnaive_chart`: Display SeasonalNaive Model\n
        `show`: Show a dataframe in a table\n
        `signal`: A price signal based on short/long term price.\n
        `sto`: Stochastic Oscillator %K and %D : A stochastic oscillator is a momentum indicator comparing a particular closing\n
        `tcn`: Perform TCN forecasting\n
        `tcn_chart`: Display TCN forecast\n
        `tft`: Performs Temporal Fusion Transformer forecasting\n
        `tft_chart`: Display Temporal Fusion Transformer forecast\n
        `theta`: Performs Theta forecasting\n
        `theta_chart`: Display Theta forecast\n
        `trans`: Performs Transformer forecasting\n
        `trans_chart`: Display Transformer forecast\n
    """

    _location_path = "forecast"

    def __init__(self):
        super().__init__()

        if not lib.FORECASTING_TOOLKIT_ENABLED:
            # pylint: disable=C0415
            from openbb_terminal.rich_config import console

            console.print(lib.FORECASTING_TOOLKIT_WARNING)

        if lib.FORECASTING_TOOLKIT_ENABLED:
            self.anom = lib.forecast_anom_model.get_anomaly_detection_data
            self.anom_chart = lib.forecast_anom_view.display_anomaly_detection
            self.atr = lib.forecast_model.add_atr
            self.autoarima = lib.forecast_autoarima_model.get_autoarima_data
            self.autoarima_chart = (
                lib.forecast_autoarima_view.display_autoarima_forecast
            )
            self.autoces = lib.forecast_autoces_model.get_autoces_data
            self.autoces_chart = lib.forecast_autoces_view.display_autoces_forecast
            self.autoets = lib.forecast_autoets_model.get_autoets_data
            self.autoets_chart = lib.forecast_autoets_view.display_autoets_forecast
            self.autoselect = lib.forecast_autoselect_model.get_autoselect_data
            self.autoselect_chart = (
                lib.forecast_autoselect_view.display_autoselect_forecast
            )
            self.brnn = lib.forecast_brnn_model.get_brnn_data
            self.brnn_chart = lib.forecast_brnn_view.display_brnn_forecast
            self.clean = lib.forecast_model.clean
            self.combine = lib.forecast_model.combine_dfs
            self.corr = lib.forecast_model.corr_df
            self.corr_chart = lib.forecast_view.display_corr
            self.delete = lib.forecast_model.delete_column
            self.delta = lib.forecast_model.add_delta
            self.desc = lib.forecast_model.describe_df
            self.desc_chart = lib.forecast_view.describe_df
            self.ema = lib.forecast_model.add_ema
            self.expo = lib.forecast_expo_model.get_expo_data
            self.expo_chart = lib.forecast_expo_view.display_expo_forecast
            self.export = lib.forecast_view.export_df
            self.linregr = lib.forecast_linregr_model.get_linear_regression_data
            self.linregr_chart = lib.forecast_linregr_view.display_linear_regression
            self.load = lib.common_model.load
            self.mom = lib.forecast_model.add_momentum
            self.mstl = lib.forecast_mstl_model.get_mstl_data
            self.mstl_chart = lib.forecast_mstl_view.display_mstl_forecast
            self.nbeats = lib.forecast_nbeats_model.get_NBEATS_data
            self.nbeats_chart = lib.forecast_nbeats_view.display_nbeats_forecast
            self.nhits = lib.forecast_nhits_model.get_nhits_data
            self.nhits_chart = lib.forecast_nhits_view.display_nhits_forecast
            self.plot = lib.forecast_view.display_plot
            self.plot_chart = lib.forecast_view.display_plot
            self.regr = lib.forecast_regr_model.get_regression_data
            self.regr_chart = lib.forecast_regr_view.display_regression
            self.rename = lib.forecast_model.rename_column
            self.rnn = lib.forecast_rnn_model.get_rnn_data
            self.rnn_chart = lib.forecast_rnn_view.display_rnn_forecast
            self.roc = lib.forecast_model.add_roc
            self.rsi = lib.forecast_model.add_rsi
            self.rwd = lib.forecast_rwd_model.get_rwd_data
            self.rwd_chart = lib.forecast_rwd_view.display_rwd_forecast
            self.season_chart = lib.forecast_view.display_seasonality
            self.seasonalnaive = lib.forecast_seasonalnaive_model.get_seasonalnaive_data
            self.seasonalnaive_chart = (
                lib.forecast_seasonalnaive_view.display_seasonalnaive_forecast
            )
            self.show = lib.forecast_view.show_df
            self.signal = lib.forecast_model.add_signal
            self.sto = lib.forecast_model.add_sto
            self.tcn = lib.forecast_tcn_model.get_tcn_data
            self.tcn_chart = lib.forecast_tcn_view.display_tcn_forecast
            self.tft = lib.forecast_tft_model.get_tft_data
            self.tft_chart = lib.forecast_tft_view.display_tft_forecast
            self.theta = lib.forecast_theta_model.get_theta_data
            self.theta_chart = lib.forecast_theta_view.display_theta_forecast
            self.trans = lib.forecast_trans_model.get_trans_data
            self.trans_chart = lib.forecast_trans_view.display_trans_forecast
            self.whisper = lib.forecast_whisper_model.transcribe_and_summarize
